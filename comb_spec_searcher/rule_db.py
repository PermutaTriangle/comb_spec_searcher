"""
A database for rules.
"""
from collections import defaultdict
from typing import Any, Dict, Set, Tuple
from .equiv_db import EquivalenceDB
from .strategies.constructor import DisjointUnion
from .strategies.rule import Rule


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
        self.rule_to_strategy = {}
        self.equivdb = EquivalenceDB()

    def __eq__(self, other) -> bool:
        """Check if all stored information is the same."""
        return self.rule_to_strategy == other.rule_to_strategy

    def to_dict(self) -> Dict[str, Any]:
        """Return dictionary object of self that is JSON serializable."""
        return {
            "rule_to_strategy": [
                [x, strat.to_dict()] for x, strat in self.rule_to_strategy.items()
            ],
            "equivdb": self.equivdb.to_dict(),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]):
        """Return RuleDB object from dictionary."""
        ruledb = RuleDB()
        ruledb.rule_to_strategy = {
            tuple(x[0], tuple(x[1])): strat.from_dict()
            for x, strat in d["rule_to_strategy"]
        }
        ruledb.equivdb = d["equivdb"].from_dict()
        return ruledb

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

    def __iter__(self):
        """Iterate through rules as the pairs (start, end)."""
        for start, ends in self.rule_to_strategy.keys():
            if len(ends) != 1 or not self.are_equivalent(start, ends[0]):
                yield start, ends

    def contains(self, start, ends):
        """Return true if the rule start -> ends is in the database."""
        ends = tuple(sorted(ends))
        return (start, ends) in self.rule_to_strategy
