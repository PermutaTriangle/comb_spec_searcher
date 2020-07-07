"""
A database for rules.
"""
import abc
from collections import defaultdict
from typing import Dict, Iterable, Iterator, List, MutableMapping, Optional, Set, Tuple

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

__all__ = ["RuleDBBase", "RuleDB"]

Specification = Tuple[List[Tuple[int, AbstractStrategy]], List[List[int]]]
RuleKey = Tuple[int, Tuple[int, ...]]


class RuleDBBase(abc.ABC):
    """A database for rules found."""

    def __init__(self) -> None:
        self.equivdb = EquivalenceDB()

    @property
    @abc.abstractmethod
    def rule_to_strategy(self,) -> MutableMapping[RuleKey, AbstractStrategy]:
        pass

    def __eq__(self, other: object) -> bool:
        """Check if all stored information is the same."""
        if not isinstance(other, self.__class__):
            return NotImplemented
        return bool(self.rule_to_strategy == other.rule_to_strategy)

    def add(self, start: int, ends: Iterable[int], rule: AbstractRule) -> None:
        """
        Add a rule to the database.

        - start is a single integer.
        - ends is a tuple of integers.
        - rule is a Rule that creates start -> ends.
        """
        ends = tuple(sorted(ends))
        if isinstance(rule, VerificationRule):
            self.set_verified(start)
        is_equiv = rule.is_equivalence()
        if is_equiv:
            self.set_equivalent(start, ends[0])
        if len(ends) != 1 or is_equiv or not self.are_equivalent(start, ends[0]):
            # to avoid overwriting an equivalence rule with a non-equivalence
            # rule, we only save if an equivalence rule, or does not have the
            # same start -> ends as some equivalence rule.
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
        self.equivdb.union(label, other)

    def rules_up_to_equivalence(self) -> Dict[int, Set[Tuple[int, ...]]]:
        """Return a defaultdict containing all rules up to the equivalence."""
        rules_dict: Dict[int, Set[Tuple[int, ...]]] = defaultdict(set)
        for start, ends in self:
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
            if len(ends) != 1 or not self.are_equivalent(start, ends[0]):
                yield start, ends

    def contains(self, start: int, ends: Tuple[int, ...]) -> bool:
        """Return true if the rule start -> ends is in the database."""
        ends = tuple(sorted(ends))
        return (start, ends) in self.rule_to_strategy

    def status(self) -> str:
        """Return a string describing the status of the rule database."""
        status = "RuleDB status:\n"
        status += "\tTotal number of combinatorial rules is {}".format(
            len(self.rule_to_strategy)
        )
        # TODO: strategy verified, verified, equivalence sets?
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
            if iterative:
                specification = iterative_proof_tree_finder(
                    rules_dict, root=self.equivdb[label]
                )
            else:
                specification = smallish_random_proof_tree(
                    rules_dict, self.equivdb[label], minimization_time_limit
                )
        else:
            raise SpecificationNotFound("No specification for label {}".format(label))
        return specification

    def get_specification_rules(
        self, label: int, minimization_time_limit: float, iterative: bool = False
    ) -> Specification:
        """
        Return a list of pairs (label, rule) which form a specification.
        The specification returned is random, so two calls to the function
        may result in a a different output.
        """
        proof_tree_node = self.find_specification(
            label=label,
            iterative=iterative,
            minimization_time_limit=minimization_time_limit,
        )
        return self._get_specification_rules(label, proof_tree_node)

    def _get_specification_rules(
        self, label: int, proof_tree_node: Node
    ) -> Specification:
        children: Dict[int, Tuple[int, ...]] = dict()
        internal_nodes = set([label])
        for node in proof_tree_node.nodes():
            eqv_start, eqv_ends = (
                node.label,
                tuple(child.label for child in node.children),
            )
            rule = self.rule_from_equivalence_rule(eqv_start, eqv_ends)
            if rule is not None:
                start, ends = rule
                children[start] = ends
                internal_nodes.update(ends)
        res = []
        eqv_paths = []
        for start, ends in children.items():
            for eqv_label in internal_nodes:
                if self.are_equivalent(start, eqv_label):
                    path = self.equivdb.find_path(eqv_label, start)
                    for a, b in zip(path[:-1], path[1:]):
                        try:
                            strategy = self.rule_to_strategy[(a, (b,))]
                            res.append((a, strategy))
                        except KeyError:
                            strategy = self.rule_to_strategy[(b, (a,))]
                            res.append((b, strategy))
                    if len(path) > 1:
                        eqv_paths.append(path)
            strategy = self.rule_to_strategy[(start, ends)]
            res.append((start, strategy))
        return res, eqv_paths

    def all_specifications(
        self, label: int, iterative: bool = False
    ) -> Iterator[Specification]:
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
            proof_trees = proof_tree_generator_dfs(rules_dict, root=self.equivdb[label])
        for proof_tree_node in proof_trees:
            yield self._get_specification_rules(label, proof_tree_node)

    def get_smallest_specification(
        self, label: int, iterative: bool = False
    ) -> Specification:
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
        return self._get_specification_rules(label, tree)


class RuleDB(RuleDBBase):
    def __init__(self) -> None:
        super().__init__()
        self._rule_to_strategy: Dict[Tuple[int, Tuple[int, ...]], AbstractStrategy] = {}

    @property
    def rule_to_strategy(self) -> Dict[Tuple[int, Tuple[int, ...]], AbstractStrategy]:
        return self._rule_to_strategy
