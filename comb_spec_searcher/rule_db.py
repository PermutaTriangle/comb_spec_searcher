"""
A database for rules.

Use to keep track of all batch rules made by strategies. Each rule comes with
an explanation.
"""
from collections import defaultdict
from collections.abc import Iterable

from comb_spec_searcher.utils import CompressedStringDict


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
        self.rules_dict = defaultdict(set)
        self.explanations = {}
        self.constructors = {}

    def __eq__(self, other):
        """Check if all stored information is the same."""
        return (
            self.rules_dict == other.rules_dict
            and self.explanations == other.explanations
            and self.constructors == other.constructors
        )

    def to_dict(self):
        """Return dictionary object of self that is JSON serializable."""
        return {
            "rules_dict": [
                [x, [list(z) for z in y]] for x, y in self.rules_dict.items()
            ],
            "explanations": [
                [x, [[list(y), z] for y, z in d.items()]]
                for x, d in self.explanations.items()
            ],
            "constructors": [
                [x, [[list(y), z] for y, z in d.items()]]
                for x, d in self.constructors.items()
            ],
        }

    @classmethod
    def from_dict(cls, dict_):
        """Return RuleDB object from dictionary."""
        ruledb = RuleDB()
        for start, ends in dict_["rules_dict"]:
            ruledb.rules_dict[start].update(map(tuple, ends))
        for x, d in dict_["explanations"]:
            new_dict = {tuple(y): z for y, z in d}
            ruledb.explanations[x] = CompressedStringDict(new_dict)
            # for y, z in d:
            # ruledb.explanations[x][tuple(y)] = z
        for x, d in dict_["constructors"]:
            new_dict = {tuple(y): z for y, z in d}
            ruledb.constructors[x] = CompressedStringDict(new_dict)
            # for y, z in d:
            # ruledb.constructors[x][tuple(y)] = z
        return ruledb

    def add(self, start, end, explanation, constructor):
        """
        Add a rule to the database.

        - start is a single integer.
        - end is a tuple of integers.
        - explanation is a string which describes the rule (formal step).
        """
        if not isinstance(start, int):
            raise TypeError("Rule is integer and an iterable of integers.")
        if not isinstance(end, Iterable):
            raise TypeError("Rule is integer and an iterable of integers.")
        if any(not isinstance(x, int) for x in end):
            raise TypeError("Rule is integer and an iterable of integers.")
        if not isinstance(explanation, str):
            raise TypeError("A rule requires a string for an explanation.")
        if not isinstance(constructor, str):
            raise TypeError("A rule requires a string for a constructor.")
        end = tuple(sorted(end))
        self.rules_dict[start] |= set((end,))
        self.explanations[start][end] = explanation
        self.constructors[start][end] = constructor

    def remove(self, start, end):
        """Remove rule from database."""
        if not isinstance(start, int):
            raise TypeError("Rule is integer and an iterable of integers.")
        if not isinstance(end, Iterable):
            raise TypeError("Rule is integer and an iterable of integers.")
        if any(not isinstance(x, int) for x in end):
            raise TypeError("Rule is integer and an iterable of integers.")
        if start in self.explanations:
            if end in self.explanations[start]:
                self.explanations[start].pop(end)
                if not self.explanations[start]:
                    self.explanations.pop(start)
        if start in self.constructors:
            if end in self.constructors[start]:
                self.constructors[start].pop(end)
                if not self.constructors[start]:
                    self.constructors.pop(start)
        if start in self.rules_dict:
            if end in self.rules_dict[start]:
                self.rules_dict[start].remove(end)
                if not self.rules_dict[start]:
                    self.rules_dict.pop(start)

    def __iter__(self):
        """Iterate through rules as the pairs (start, end)."""
        for start, ends in self.rules_dict.items():
            for end in ends:
                yield start, end

    def explanation(self, start, end):
        """Return the explanation of the rule start -> end."""
        end = tuple(sorted(end))
        if start not in self.explanations or end not in self.explanations[start]:
            raise KeyError("No such rule.")
        return self.explanations[start][end]

    def constructor(self, start, end):
        """Return the constructor of the rule start -> end."""
        end = tuple(sorted(end))
        if start not in self.constructors or end not in self.constructors[start]:
            raise KeyError("No such rule.")
        return self.constructors[start][end]

    def contains(self, start, end):
        """Return true if the rule start -> end is in the database."""
        end = tuple(sorted(end))
        return start in self.rules_dict and end in self.rules_dict[start]
