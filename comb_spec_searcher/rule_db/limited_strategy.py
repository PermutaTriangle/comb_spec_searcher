"""
    An alternative ruledb that permits restricting the number of applications of a given
    set of strategies to a given limit.
"""
from copy import deepcopy
from itertools import combinations
from typing import Iterable, Set, Type

from logzero import logger

from comb_spec_searcher.exception import SpecificationNotFound
from comb_spec_searcher.rule_db import RuleDB
from comb_spec_searcher.strategies import AbstractStrategy
from comb_spec_searcher.tree_searcher import (
    Node,
    iterative_proof_tree_finder,
    iterative_prune,
    prune,
    smallish_random_proof_tree,
)
from comb_spec_searcher.typing import RuleKey


class LimitedStrategyRuleDB(RuleDB):
    """
    An alternative ruledb that permits restricting the number of applications of a
    given set of strategies to a given limit. The limit is a single limit for the
    total number of strategies whose type is in the given set; it is not a per-type
    limit.
    """

    def __init__(
        self,
        strategies_to_limit: Iterable[Type[AbstractStrategy]],
        limit: int,
        mark_verified: bool,
    ) -> None:
        self.strategies_to_limit = set(strategies_to_limit)
        self.limit = limit
        self.mark_verified = mark_verified
        super().__init__()

    def get_rules_up_to_equiv_using_strategies(self) -> Set[RuleKey]:
        """
        returns a set of rules, up to equivalence, that come from
        <self.strategies_to_limit>
        """
        eqv_rules_using_strategies: Set[RuleKey] = set()
        for label_rule in self:
            rule_strat = self.rule_to_strategy[label_rule]
            start, ends = label_rule
            if isinstance(rule_strat, tuple(self.strategies_to_limit)):
                temp_start = self.equivdb[start]
                temp_ends = tuple(sorted(map(self.equivdb.__getitem__, ends)))
                eqv_rules_using_strategies.add((temp_start, temp_ends))
        return eqv_rules_using_strategies

    def find_specification(
        self, label: int, minimization_time_limit: float, iterative: bool = False
    ) -> Node:
        """Search for a specification based on current data found."""
        rules_dict = self.rules_up_to_equivalence()
        # Prune all unverified labels (recursively)
        # Afterward, only verified labels remain in rules_dict. In particular, there
        # is a specification if <label> is in the rules_dict
        if iterative:
            rules_dict = iterative_prune(rules_dict, root=label)
        else:
            prune(rules_dict)  # this function removes rules not in a specification.

        # if the root is not in the pruned dict, then there's nothing to be done
        if self.equivdb[label] not in rules_dict:
            raise SpecificationNotFound("No specification for label {}".format(label))

        # find the rules that we want to limit, and consider only those in a spec
        rules_to_isolate = self.get_rules_up_to_equiv_using_strategies()
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

            if self.mark_verified:
                for ver_label in temp_rules_dict.keys():
                    self.set_verified(ver_label)

            if self.equivdb[label] in temp_rules_dict:
                for label_in_spec in temp_rules_dict.keys():
                    self.set_verified(label_in_spec)
                if iterative:
                    specification = iterative_proof_tree_finder(
                        temp_rules_dict, root=self.equivdb[label]
                    )
                else:
                    specification = smallish_random_proof_tree(
                        temp_rules_dict, self.equivdb[label], minimization_time_limit
                    )
                return specification

        raise SpecificationNotFound("No specification for label {}".format(label))
