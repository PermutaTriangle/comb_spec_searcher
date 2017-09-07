"""
A database to keep track of all batch rules made by strategies. Each rule comes
with an explanantion.
"""
from collections import defaultdict
from collections import Iterable

class RuleDB(object):
    """A database for rules found."""

    def __init__(self):
        self.rules_dict = defaultdict(set)
        self.explanations = {}
        self.back_maps = {}

    def add(self, start, end, explanation):
        if not isinstance(start, int):
            raise TypeError("A rule is an integer and an iterable of integers it goes to.")
        if not isinstance(end, Iterable):
            raise TypeError("A rule is an integer and an iterable of integers it goes to.")
        if any(not isinstance(x, int) for x in end):
            raise TypeError("A rule is an integer and an iterable of integers it goes to.")
        if not isinstance(explanation, str):
            raise TypeError("A rule requires a string for an explanation.")
        end = tuple(sorted(end))
        self.rules_dict[start] |= set((end,))
        if start in self.explanations:
            self.explanations[start][end] = explanation
        else:
            self.explanations[start] = {end: explanation}

    def __iter__(self):
        for start, ends in self.rules_dict.items():
            for end in ends:
                yield start, end

    def explanation(self, start, end):
        end = tuple(sorted(end))
        if start not in self.explanations:
            raise KeyError("No such strategy.")
        if end not in self.explanations[start]:
            raise KeyError("No such strategy.")
        return self.explanations[start][end]
