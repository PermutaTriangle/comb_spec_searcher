"""
A database for rules.
"""
import abc
from collections import defaultdict
from typing import Dict, Iterable, Iterator, List, MutableMapping, Optional, Set, Tuple

import tabulate
from logzero import logger

from comb_spec_searcher.equiv_db import EquivalenceDB
from comb_spec_searcher.exception import SpecificationNotFound
from comb_spec_searcher.strategies import AbstractStrategy, VerificationRule
from comb_spec_searcher.strategies.rule import AbstractRule
from comb_spec_searcher.tree_searcher import (
    Node,
    iterative_proof_tree_finder,
    iterative_prune,
    proof_tree_generator_dfs,
    prune,
    random_proof_tree,
    smallish_random_proof_tree,
)
from comb_spec_searcher.typing import RuleKey

__all__ = ["RuleDBBase", "RuleDB"]


class RuleDBBase(abc.ABC):
    """A database for rules found."""

    def __init__(self) -> None:
        self.equivdb = EquivalenceDB()

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
        ends = tuple(sorted(ends))
        if isinstance(rule, VerificationRule):
            self.set_verified(start)
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
        return bool(self.equivdb.is_verified(label))

    def set_verified(self, label: int) -> None:
        """Mark label as verified."""
        self.equivdb.set_verified(label)

    def are_equivalent(self, label: int, other: int) -> bool:
        """Return true if label and other are equivalent."""
        return bool(self.equivdb.equivalent(label, other))

    def set_equivalent(self, label: int, other: int) -> None:
        """Mark label and other as equivalent."""
        self.equivdb.add_two_way_edge(label, other)

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

    def all_rules(self) -> Iterator[Tuple[int, Tuple[int, ...], AbstractStrategy]]:
        """Yield all the rules found so far."""
        for start, ends in self:
            yield start, ends, self.rule_to_strategy[(start, ends)]

    def __iter__(self) -> Iterator[Tuple[int, Tuple[int, ...]]]:
        """Iterate through rules as the pairs (start, end)."""
        for start, ends in self.rule_to_strategy:
            yield start, ends

    def contains(self, start: int, ends: Tuple[int, ...]) -> bool:
        """Return true if the rule start -> ends is in the database."""
        ends = tuple(sorted(ends))
        return (start, ends) in self.rule_to_strategy or (
            start,
            ends,
        ) in self.eqv_rule_to_strategy

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

    def has_specification(self, label: int) -> bool:
        """Return True if a specification has been found, false otherwise."""
        return self.is_verified(label)

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
        self, eqv_rules: List[RuleKey]
    ) -> Dict[RuleKey, RuleKey]:
        """
        Return a dictionary pointing from an equivalence rule to an actual rule.
        """
        res: Dict[RuleKey, RuleKey] = {}
        for start, ends in self.rule_to_strategy:
            eqv_start = self.equivdb[start]
            eqv_ends = tuple(sorted(map(self.equivdb.__getitem__, ends)))
            eqv_key = (eqv_start, eqv_ends)
            if eqv_key in eqv_rules:
                res[eqv_key] = (start, ends)
        return res

    def find_specification(
        self, label: int, minimization_time_limit: float, iterative: bool = False
    ) -> Node:
        """Search for a specification based on current data found."""
        rules_dict = self.rules_up_to_equivalence()
        # Prune all unverified labels (recursively)
        if iterative:
            rules_dict = iterative_prune(rules_dict, root=label)
        else:
            prune(rules_dict)  # this function removes rules not in a specification.

        # only verified labels in rules_dict, in particular, there is a
        # specification if a label is in the rules_dict
        for ver_label in rules_dict.keys():
            self.set_verified(ver_label)

        if self.equivdb[label] in rules_dict:
            logger.info("Specification detected.")
            if iterative:
                specification = iterative_proof_tree_finder(
                    rules_dict, root=self.equivdb[label]
                )
            else:
                logger.info(
                    "Minimizing for %s seconds.", round(minimization_time_limit)
                )
                specification = smallish_random_proof_tree(
                    rules_dict, self.equivdb[label], minimization_time_limit
                )
            logger.info(
                "Found specification with %s rules.", len(specification.labels())
            )
        else:
            raise SpecificationNotFound("No specification for label {}".format(label))
        return specification

    def all_specifications(self, label: int, iterative: bool = False) -> Iterator[Node]:
        """
        A generator that yields all specifications in the universe for
        the given label.
        """
        if iterative:
            raise NotImplementedError(
                "There is no method for yielding all iterative proof trees."
            )
        rules_dict = self.rules_up_to_equivalence()
        # Prune all unverified labels (recursively)
        prune(rules_dict)

        if self.equivdb[label] in rules_dict:
            yield from proof_tree_generator_dfs(rules_dict, root=self.equivdb[label])

    def get_smallest_specification(self, label: int, iterative: bool = False) -> Node:
        """
        Return the smallest specification in the universe for label. It uses
        exponential search to find it.
        This doesn't consider the length of the equivalence paths.
        """
        if iterative:
            raise NotImplementedError(
                "There is no method for finding smallest iterative proof trees."
            )
        rules_dict = self.rules_up_to_equivalence()
        prune(rules_dict)

        if not self.equivdb[label] in rules_dict:
            raise SpecificationNotFound("No specification for label {}".format(label))
        tree = random_proof_tree(rules_dict, root=self.equivdb[label])
        minimum = 1
        maximum = len(tree)
        logger.info(
            "Found a specification of size %s. Looking for the smallest.", len(tree)
        )
        # Binary search to find a smallest proof tree.
        while minimum < maximum:
            middle = (minimum + maximum) // 2
            logger.info("Looking for specification of size %s", middle)
            try:
                tree = next(
                    proof_tree_generator_dfs(
                        rules_dict, root=self.equivdb[label], maximum=middle
                    )
                )
                maximum = min(middle, len(tree))
            except StopIteration:
                minimum = middle + 1
        logger.info("The smallest specification is of size %s.", len(tree))
        return tree


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
