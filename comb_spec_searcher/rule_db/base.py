"""
A database to search for tree.
"""
import abc
import itertools
from collections import defaultdict
from typing import Dict, Iterable, Iterator, List, MutableMapping, Optional, Set, Tuple

import sympy
import tabulate
from logzero import logger

from comb_spec_searcher.equiv_db import EquivalenceDB
from comb_spec_searcher.exception import InvalidOperationError
from comb_spec_searcher.rule_db.abstract import RuleDBAbstract, ensure_specification
from comb_spec_searcher.specification_extrator import SpecificationRuleExtractor
from comb_spec_searcher.strategies import AbstractStrategy, VerificationRule
from comb_spec_searcher.strategies.rule import AbstractRule
from comb_spec_searcher.tree_searcher import (
    Node,
    iterative_proof_tree_finder,
    iterative_prune,
    proof_tree_generator_dfs,
    prune,
    smallish_random_proof_tree,
)
from comb_spec_searcher.typing import RuleKey, RulesDict

__all__ = ["RuleDBBase", "RuleDB"]


class RuleDBBase(RuleDBAbstract):
    """
    A database to find specification using the pruning method.
    """

    def __init__(self) -> None:
        super().__init__()
        self.equivdb = EquivalenceDB()
        # Store the pruned dict. Should be set back to None every time the ruledb is
        # edited. Use the propertu for clean access.
        self._pruned_dict: Optional[RulesDict] = None

    @property
    def iterative(self) -> bool:
        """
        Indicate whether we are searching for an iterative specification.
        """
        return self.strategy_pack.iterative

    @property
    def pruned_dict(self) -> RulesDict:
        """
        Returned the prune dict of all the rules that are in a specification.

        The dict needs to be recomputed every time the database changes and it
        is costly to so. Call with moderation.
        """
        if self._pruned_dict is None:
            rules_dict = self.rules_up_to_equivalence()
            if self.iterative:
                rules_dict = iterative_prune(rules_dict, root=self.root_label)
            else:
                prune(rules_dict)
            self._pruned_dict = rules_dict
            for ver_label in rules_dict.keys():
                self.equivdb.set_verified(ver_label)
        return self._pruned_dict

    @property
    @abc.abstractmethod
    def rule_to_strategy(self) -> MutableMapping[RuleKey, AbstractStrategy]:
        pass

    @property
    @abc.abstractmethod
    def eqv_rule_to_strategy(self) -> MutableMapping[RuleKey, AbstractStrategy]:
        pass

    def __eq__(self, other: object) -> bool:
        """Check if all stored information is the same."""
        if not isinstance(other, self.__class__):
            return NotImplemented
        return (
            self.rule_to_strategy == other.rule_to_strategy
            and self.eqv_rule_to_strategy == other.eqv_rule_to_strategy
        )

    def add(self, start: int, ends: Tuple[int, ...], rule: AbstractRule) -> None:
        """
        Add a rule to the database.

        - start is a single integer.
        - ends is a tuple of integers, representing the non-empty children.
        - rule is a Rule that creates start -> ends.
        """
        self._pruned_dict = None
        ends = tuple(sorted(ends))
        if isinstance(rule, VerificationRule):
            self.equivdb.set_verified(start)
        if len(ends) == 1:
            if rule.is_two_way():
                self.equivdb.add_two_way_edge(start, ends[0])
                self.eqv_rule_to_strategy[(start, ends)] = rule.strategy
                self.rule_to_strategy.pop((start, ends), None)
                self.rule_to_strategy.pop((ends[0], (start,)), None)
            else:
                self.equivdb.add_one_way_edge(start, ends[0])
                self.rule_to_strategy[(start, ends)] = rule.strategy
        else:
            self.rule_to_strategy[(start, ends)] = rule.strategy

    def is_verified(self, label: int) -> bool:
        """Return True if label has been verified."""
        return self.equivdb.is_verified(label)

    def are_equivalent(self, label: int, other: int) -> bool:
        """Return true if label and other are equivalent."""
        return self.equivdb.equivalent(label, other)

    def rules_up_to_equivalence(self) -> Dict[int, Set[Tuple[int, ...]]]:
        """Return a defaultdict containing all rules up to the equivalence."""
        self.equivdb.connect_cycles()
        rules_dict: Dict[int, Set[Tuple[int, ...]]] = defaultdict(set)
        for start, ends in self:
            if len(ends) == 1 and self.are_equivalent(start, ends[0]):
                continue
            rules_dict[self.equivdb[start]].add(
                tuple(sorted(self.equivdb[e] for e in ends))
            )
        return rules_dict

    def __iter__(self) -> Iterator[Tuple[int, Tuple[int, ...]]]:
        """Iterate through rules as the pairs (start, ends)."""
        return itertools.chain(self.rule_to_strategy, self.eqv_rule_to_strategy)

    def contains(self, start: int, ends: Tuple[int, ...]) -> bool:
        """Return true if the rule start -> ends is in the database."""
        key = (start, sorted(ends))
        return key in self.rule_to_strategy or key in self.eqv_rule_to_strategy

    def status(self, elaborate: bool) -> str:
        """Return a string describing the status of the rule database."""
        status = "RuleDB status:\n"
        table: List[Tuple[str, str]] = []
        table.append(("Combinatorial rules", f"{len(self.rule_to_strategy):,d}"))
        table.append(("Equivalence rules", f"{len(self.eqv_rule_to_strategy):,d}"))
        if elaborate:
            eqv_labels = set()
            strategy_verified_labels = set()
            verified_labels = set()
            eqv_rules = set()
            for start, ends in self.rule_to_strategy:
                if not ends:
                    strategy_verified_labels.add(start)
                if self.is_verified(start):
                    verified_labels.add(start)
                eqv_start = self.equivdb[start]
                eqv_ends = tuple(sorted(self.equivdb[label] for label in ends))
                eqv_labels.add(eqv_start)
                eqv_labels.update(eqv_ends)
                eqv_rules.add((eqv_start, eqv_ends))
            table.append(
                ("Combintorial rules up to equivalence", f"{len(eqv_rules):,d}")
            )
            table.append(
                (
                    "Strategy verified combinatorial classes",
                    f"{len(strategy_verified_labels):,d}",
                )
            )
            table.append(
                (
                    "Verified combinatorial classes",
                    f"{len(verified_labels):,d}",
                )
            )
            table.append(
                (
                    "combinatorial classes up to equivalence",
                    f"{len(eqv_labels):,d}",
                )
            )
        status += "    "
        status += tabulate.tabulate(
            table, headers=("", "Total number"), colalign=("left", "right")
        ).replace("\n", "\n    ")
        time_taken = round(self.equivdb.func_times["find_paths"], 2)
        status += (
            f"\n\tCalled find equiv path {self.equivdb.func_calls['find_paths']}"
            + f" times, for total time of {time_taken}"
            + " seconds.\n"
        )
        return status

    ################################################################
    # Below are methods for finding a combinatorial specification. #
    ################################################################

    def has_specification(self) -> bool:
        """Return True if a specification has been found, false otherwise."""
        if self.equivdb[self.root_label] in self.pruned_dict:
            logger.info("Specification detected.")
            return True
        return False

    def rule_from_equivalence_rule(
        self, eqv_start: int, eqv_ends: Iterable[int]
    ) -> Optional[Tuple[int, Tuple[int, ...]]]:
        """
        Return a rule that satisfies the equivalence rule.

        Returns None if no such rule exists.
        """
        eqv_start = self.equivdb[eqv_start]
        eqv_ends = tuple(sorted(map(self.equivdb.__getitem__, eqv_ends)))
        for rule in self:
            start, ends = rule
            temp_start = self.equivdb[start]
            temp_ends = tuple(sorted(map(self.equivdb.__getitem__, ends)))
            if eqv_start == temp_start and eqv_ends == temp_ends:
                return start, ends
        return None

    def rule_from_equivalence_rule_dict(
        self, eqv_rules: Iterable[RuleKey]
    ) -> Dict[RuleKey, RuleKey]:
        """
        Return a dictionary pointing from an equivalence rule to an actual rule.
        """
        eqv_rules = set(eqv_rules)
        res: Dict[RuleKey, RuleKey] = {}
        for start, ends in self.rule_to_strategy:
            eqv_start = self.equivdb[start]
            eqv_ends = tuple(sorted(map(self.equivdb.__getitem__, ends)))
            eqv_key = (eqv_start, eqv_ends)
            if eqv_key in eqv_rules:
                res[eqv_key] = (start, ends)
        return res

    @ensure_specification
    def get_specification_rules(
        self,
        *,
        minimization_time_limit: float = 10,
        smallest: bool = False,
        **kwargs,
    ) -> Iterator[AbstractRule]:
        node = self._get_specification_node(minimization_time_limit, smallest)
        logger.info("Found specification with %s rules.", len(node.labels()))
        spec_extractor = SpecificationRuleExtractor(
            self.root_label, node, self, self.classdb
        )
        return spec_extractor.rules()

    @ensure_specification
    def _get_specification_node(
        self, minimization_time_limit: float, smallest: bool
    ) -> Node:
        """
        Return a specification node for the given label.
        """
        if self.iterative:
            if smallest:
                raise InvalidOperationError("can't use iterative and smallest")
            node = self._get_iterative_node()
        else:
            if smallest:
                node = self._get_smallest_node(minimization_time_limit)
            else:
                node = self._get_smallish_node(
                    minimization_time_limit=minimization_time_limit,
                )
        return node

    @ensure_specification
    def _get_iterative_node(self) -> Node:
        if not self.iterative:
            raise InvalidOperationError("Not supported in non-iterative mode")
        return iterative_proof_tree_finder(
            self.pruned_dict, root=self.equivdb[self.root_label]
        )

    @ensure_specification
    def _get_smallish_node(self, minimization_time_limit: float) -> Node:
        """Search for a smallish node for the given minimization time."""
        if self.iterative:
            raise InvalidOperationError("Not supported in iterative mode.")
        logger.info("Minimizing for %s seconds.", round(minimization_time_limit))
        return smallish_random_proof_tree(
            self.pruned_dict, self.equivdb[self.root_label], minimization_time_limit
        )

    @ensure_specification
    def _get_smallest_node(self, minimization_time_limit: float) -> Node:
        """
        Return the smallest specification node in the universe.

        Will look for a smallish spec for minimization_time_limit and then use
        binary search to find it to find the smallest one.

        This doesn't consider the length of the equivalence paths.
        """
        if self.iterative:
            raise InvalidOperationError("Not supported in iterative mode.")
        node = self._get_smallish_node(minimization_time_limit)
        minimum = 1
        maximum = len(node)
        logger.info(
            "Found a specification of size %s. Looking for the smallest.", len(node)
        )
        # Binary search to find a smallest proof tree.
        while minimum < maximum:
            middle = (minimum + maximum) // 2
            logger.info("Looking for specification of size %s", middle)
            try:
                node = next(
                    proof_tree_generator_dfs(
                        self.pruned_dict,
                        root=self.equivdb[self.root_label],
                        maximum=middle,
                    )
                )
                maximum = min(middle, len(node))
            except StopIteration:
                minimum = middle + 1
        logger.info("The smallest specification is of size %s.", len(node))
        return node

    @ensure_specification
    def _all_nodes(self, iterative: bool = False) -> Iterator[Node]:
        """
        A generator that yields all specifications in the universe for
        the given label.
        """
        if self.iterative:
            raise NotImplementedError(
                "There is no method for yielding all iterative proof trees."
            )
        yield from proof_tree_generator_dfs(
            self.pruned_dict, root=self.equivdb[self.root_label]
        )


class RuleDB(RuleDBBase):
    def __init__(self) -> None:
        super().__init__()
        self._rule_to_strategy: Dict[Tuple[int, Tuple[int, ...]], AbstractStrategy] = {}
        self._eqv_rule_to_strategy: Dict[
            Tuple[int, Tuple[int, ...]], AbstractStrategy
        ] = {}

    @property
    def rule_to_strategy(self) -> Dict[Tuple[int, Tuple[int, ...]], AbstractStrategy]:
        return self._rule_to_strategy

    @property
    def eqv_rule_to_strategy(
        self,
    ) -> Dict[Tuple[int, Tuple[int, ...]], AbstractStrategy]:
        return self._eqv_rule_to_strategy

    def all_rules(self) -> Iterator[AbstractRule]:
        """Yield all the rules found so far."""
        for rulekey in self:
            parent = self.classdb.get_class(rulekey[0])
            try:
                strategy = self.rule_to_strategy[rulekey]
            except KeyError:
                strategy = self.eqv_rule_to_strategy[rulekey]
            yield strategy(parent)

    def all_equations(self) -> Set[sympy.Eq]:
        """
        Returns a set of equations for all rules currently found.
        """

        def get_function(comb_class) -> sympy.Function:
            return comb_class.get_function(self.classdb.get_label)

        eqs = set()
        for rule in self.all_rules():
            try:
                eq = rule.get_equation(get_function)
            except NotImplementedError:
                logger.info(
                    "can't find generating function for %s." " The comb class is:\n%s",
                    get_function(rule.comb_class),
                    rule.comb_class,
                )
                eq = sympy.Eq(
                    get_function(rule.comb_class),
                    sympy.Function("NOTIMPLEMENTED")(sympy.var("x")),
                )
            eqs.add(eq)
        return eqs
