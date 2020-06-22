"""
    An alternative ruledb that permits restricting the number of applications of a given
    set of strategies to a given limit.
"""
from copy import deepcopy
from itertools import combinations
from time import time
from typing import Dict, Set, Tuple, Type

from logzero import logger

from comb_spec_searcher.rule_db import RuleDB
from comb_spec_searcher.strategies import AbstractStrategy

from .exception import SpecificationNotFound
from .tree_searcher import (
    Node,
    iterative_proof_tree_finder,
    iterative_prune,
    prune,
    random_proof_tree,
)

LabelRule = Tuple[int, Tuple[int, ...]]
RulesDict = Dict[int, Set[Tuple[int, ...]]]


class LimitedStrategyRuleDB(RuleDB):
    def __init__(
        self,
        strategies_to_limit: Set[Type[AbstractStrategy]],
        limit: int,
        mark_verified: bool,
        minimization_time_limit: int,
    ) -> None:
        self.strategies_to_limit = strategies_to_limit
        self.limit = limit
        self.mark_verified = mark_verified
        self.minimization_time_limit = minimization_time_limit
        super().__init__()

    def get_eqv_rules_using_strategies(self) -> Set[LabelRule]:
        """
        returns a set of rules, up to equivalence, that come from
        <self.strategies_to_limit>
        """
        eqv_rules_using_strategies: Set[LabelRule] = set()
        for label_rule in self:
            rule_strat = self.rule_to_strategy[label_rule]
            start, ends = label_rule
            if any(isinstance(rule_strat, strat) for strat in self.strategies_to_limit):
                temp_start = self.equivdb[start]
                temp_ends = tuple(sorted(map(self.equivdb.__getitem__, ends)))
                eqv_rules_using_strategies.add((temp_start, temp_ends))
        return eqv_rules_using_strategies

    def find_specification(self, label: int, iterative: bool = False) -> Node:
        """Search for a specification based on current data found."""
        rules_dict = self.rules_up_to_equivalence()
        # Prune all unverified labels (recursively)
        # Afterward, only verified labels remain in rules_dict. In particular, there
        # is a specification if <label> is in the rules_dict
        if iterative:
            rules_dict = iterative_prune(rules_dict, root=label)
        else:
            prune(rules_dict)  # this function removes rules not in a specification.

        if self.mark_verified:
            for ver_label in rules_dict.keys():
                self.set_verified(ver_label)

        # find the rules that we want to limit, and consider only those in a spec
        rules_to_isolate = self.get_eqv_rules_using_strategies()
        rules_to_isolate = set(
            (lhs, rhs)
            for (lhs, rhs) in rules_to_isolate
            if lhs in rules_dict and rhs in rules_dict[lhs]
        )

        logger.debug("Found %s rules to isolate.", len(rules_to_isolate))

        if len(rules_to_isolate) < self.limit:
            rule_combos = [tuple(rules_to_isolate)]
        else:
            rule_combos = list(combinations(rules_to_isolate, self.limit))
        num_combos = len(rule_combos)
        logger.debug("%s combinations to check", num_combos)

        # for each combination of <self.limit> rules, remove all but those and
        # reprune to see if a spec still exists
        for i, combo in enumerate(rule_combos):
            logger.debug("[ %s / %s ]", i + 1, num_combos)
            temp_rules_dict = deepcopy(rules_dict)
            for lhs, rhs in rules_to_isolate:
                if (lhs, rhs) in combo:
                    continue
                try:
                    temp_rules_dict[lhs].remove(rhs)
                except KeyError:
                    pass
                if len(temp_rules_dict[lhs]) == 0:
                    del temp_rules_dict[lhs]
            prune(temp_rules_dict)

            if self.equivdb[label] in temp_rules_dict:
                for label_in_spec in temp_rules_dict.keys():
                    self.set_verified(label_in_spec)
                if iterative:
                    specification = iterative_proof_tree_finder(
                        temp_rules_dict, root=self.equivdb[label]
                    )
                else:
                    specification = self.smallish_random_proof_tree(
                        temp_rules_dict, self.equivdb[label],
                    )
                return specification

        raise SpecificationNotFound("No specification for label {}".format(label))

    def smallish_random_proof_tree(self, rules_dict: RulesDict, root: int) -> Node:
        """Searches a rule_dict known to contain at least one specification for a
        small specification. Spends self.minimization_time_limit seconds searching."""

        def tree_size(tree):
            return len(list(tree.nodes()))

        start_time = time()
        smallest_so_far = random_proof_tree(rules_dict, root=root)
        smallest_size = tree_size(smallest_so_far)

        logger.info("Found tree with %s nodes.", smallest_size)
        logger.debug(
            "Looking for a smaller one for %s seconds", self.minimization_time_limit
        )

        num_searches = 1
        while time() - start_time < self.minimization_time_limit:
            num_searches += 1
            next_tree = random_proof_tree(rules_dict, root=root)
            next_tree_size = tree_size(next_tree)
            if next_tree_size < smallest_size:
                smallest_so_far = next_tree
                smallest_size = next_tree_size

        logger.info(
            "After %s searches, the smallest has %s nodes.", num_searches, smallest_size
        )

        return smallest_so_far
