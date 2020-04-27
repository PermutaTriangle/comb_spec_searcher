"""
A database for rules.
"""
from collections import defaultdict
from typing import Any, Dict, Set, Tuple
from .equiv_db import EquivalenceDB
from .exception import SpecificationNotFound
from .strategies.constructor import DisjointUnion
from .strategies.rule import Rule
from .tree_searcher import (
    iterative_proof_tree_finder,
    iterative_prune,
    Node,
    proof_tree_generator_dfs,
    prune,
    random_proof_tree,
)


class RuleDB:
    """A database for rules found."""

    def __init__(self):
        """
        Initialise.

        - The rules dict keep all rules, where keys are start and items are
        sets of ends.
        - The explanations give reason/formal steps for rules. Call for an
        explanation of rule start->ends with d[start][ends].
        - Some strategies require back maps, these are stored in the back maps
        dictionary. Calling works the same way as explanations.
        """
        # the values are needed for finding the specification in post-processing
        self.rule_to_strategy = {}
        self.equivdb = EquivalenceDB()

    def __eq__(self, other) -> bool:
        """Check if all stored information is the same."""
        return self.rule_to_strategy == other.rule_to_strategy

    def add(self, start: int, ends: Tuple[int, ...], rule: Rule):
        """
        Add a rule to the database.

        - start is a single integer.
        - ends is a tuple of integers.
        - rule is a Rule that creates start -> ends.
        """
        ends = tuple(sorted(ends))
        if not ends:  # size 0, so verification rule
            self.set_verified(start)
        if len(ends) == 1 and rule.constructor.is_equivalence():
            self.set_equivalent(start, ends[0])
        self.rule_to_strategy[(start, ends)] = rule.strategy

    def is_verified(self, label):
        """Return True if label has been verified."""
        return self.equivdb.is_verified(label)

    def set_verified(self, label):
        """Mark label as verified."""
        self.equivdb.set_verified(label)

    def are_equivalent(self, label, other):
        """Return true if label and other are equivalent."""
        return self.equivdb.equivalent(label, other)

    def set_equivalent(self, label, other):
        """Mark label and other as equivalent."""
        self.equivdb.union(label, other)

    def rules_up_to_equivalence(self) -> Dict[int, Set[Tuple[int, ...]]]:
        """Return a defaultdict containing all rules up to the equivalence."""
        rules_dict = defaultdict(set)
        for start, ends in self:
            rules_dict[self.equivdb[start]].add(
                tuple(sorted(self.equivdb[e] for e in ends))
            )
        return rules_dict

    def all_rules(self):
        for start, ends in self:
            yield start, ends, self.rule_to_strategy[(start, ends)]

    def __iter__(self):
        """Iterate through rules as the pairs (start, end)."""
        for start, ends in self.rule_to_strategy.keys():
            if len(ends) != 1 or not self.are_equivalent(start, ends[0]):
                yield start, ends

    def contains(self, start, ends):
        """Return true if the rule start -> ends is in the database."""
        ends = tuple(sorted(ends))
        return (start, ends) in self.rule_to_strategy

    ################################################################
    # Below are methods for finding a combinatorial specification. #
    ################################################################

    def has_proof_tree(self, label):
        """Return True if a proof tree has been found, false otherwise."""
        return self.is_verified(label)

    def rule_from_equivalence_rule(self, eqv_start, eqv_ends):
        """Return a rule that satisfies the equivalence rule."""
        eqv_start = self.equivdb[eqv_start]
        eqv_ends = tuple(sorted(self.equivdb[l] for l in eqv_ends))
        for rule in self:
            start, ends = rule
            temp_start = self.equivdb[start]
            temp_ends = tuple(sorted(self.equivdb[l] for l in ends))
            if eqv_start == temp_start and eqv_ends == temp_ends:
                return start, ends

    def find_proof_tree(self, label: int, iterative: bool = False):
        """Search for a proof tree based on current data found."""
        rules_dict = self.rules_up_to_equivalence()
        # Prune all unverified labels (recursively)
        if iterative:
            rules_dict = iterative_prune(rules_dict, root=label)
        else:
            rules_dict = prune(rules_dict)

        # only verified labels in rules_dict, in particular, there is a
        # specification if a label is in the rules_dict
        for l in rules_dict.keys():
            self.set_verified(l)

        if self.equivdb[label] in rules_dict:
            if iterative:
                proof_tree = iterative_proof_tree_finder(
                    rules_dict, root=self.equivdb[label]
                )
            else:
                proof_tree = random_proof_tree(rules_dict, root=self.equivdb[label])
        else:
            raise SpecificationNotFound("No specification for label {}".format(label))
        return proof_tree

    def get_specification_rules(self, label: int, iterative: bool = False):
        """
        Return a list of pairs (label, rule) which form a specification.
        The specification returned is random, so two calls to the function
        may result in a a different output.
        """
        proof_tree_node = self.find_proof_tree(label=label, iterative=iterative)
        return self._get_specification_rules(label, proof_tree_node)

    def _get_specification_rules(self, label: int, proof_tree_node: Node):
        res = []
        # We will need to add equivalence rules from each internal label to its
        # equivalent label as a start.
        children = dict()
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
            for label in internal_nodes:
                if self.are_equivalent(start, label):
                    path = self.equivdb.find_path(label, start)
                    for a, b in zip(path[:-1], path[1:]):
                        try:
                            rule = self.rule_to_strategy[(a, (b,))]
                            res.append((a, rule))
                        except KeyError:
                            rule = self.rule_to_strategy[(b, (a,))]
                            res.append((b, rule))
                    if len(path) > 1:
                        eqv_paths.append(path)
            rule = self.rule_to_strategy[(start, ends)]
            res.append((start, rule))
        return res, eqv_paths

    def all_specifications(self, label, iterative: bool = False):
        """
        A generator that yields all specifications in the universe for
        the given label.
        """
        rules_dict = self.tree_search_prep()
        # Prune all unverified labels (recursively)
        if iterative:
            rules_dict = iterative_prune(rules_dict, root=self.equivdb[label])
        else:
            rules_dict = prune(rules_dict)

        if self.equivdb[self.start_label] in rules_dict:
            if self.iterative:
                raise NotImplementedError(
                    "There is no method for yielding all iterative proof trees."
                )
            proof_trees = proof_tree_generator_dfs(rules_dict, root=self.equivdb[label])
        for proof_tree_node in proof_trees:
            yield self._get_specification_rules(label, proof_tree_node)

    def get_smallest_specification(self, label: int, iterative: bool = False):
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
        rules_dict = prune(rules_dict)

        if not self.equivdb[label] in rules_dict:
            raise SpecificationNotFound("No specification for label {}".format(label))
        tree = random_proof_tree(rules_dict, root=self.equivdb[label])
        minimum = 1
        maximum = len(tree)
        # Binary search to find a smallest proof tree.
        while minimum < maximum:
            middle = (minimum + maximum) // 2
            try:
                tree = next(
                    proof_tree_generator_dfs(
                        rules_dict, root=self.equivdb[label], maximum=middle
                    )
                )
                maximum = min(middle, len(tree))
            except StopIteration:
                minimum = middle + 1
        return self._get_specification_rules(label, tree)
