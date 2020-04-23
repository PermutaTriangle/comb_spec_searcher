from itertools import chain
from typing import Iterable, Iterator
from .combinatorial_class import CombinatorialClass, CombinatorialObject
from .strategies import Strategy
from .strategies import EmptyStrategy, Rule

from sympy import Eq, Function
import sympy


__all__ = ("CombinatorialSpecification",)


class CombinatorialSpecification:
    def __init__(self, root: CombinatorialClass, rules: Iterable[Strategy]):
        # TODO: Think more about equivalence, its going to come back to bite you soon!
        # you really want to store the paths needed
        self.root = root
        self.rules_dict = {}
        self.rules_dict = {comb_class: rule(comb_class) for comb_class, rule in rules}
        for rule in list(
            self.rules_dict.values()
        ):  # list as we lazily assign empty rules
            rule.set_subrecs(self.get_rule)
        self.labels = {}

    def get_rule(self, comb_class: CombinatorialClass) -> Rule:
        if comb_class.is_empty():
            self.rules_dict[comb_class] = EmptyStrategy()(comb_class)
        return self.rules_dict[comb_class]

    @property
    def root_rule(self):
        return self.rules_dict[self.root]

    def get_label(self, comb_class: CombinatorialClass) -> int:
        res = self.labels.get(comb_class)
        if res is None:
            res = len(self.labels)
            self.labels[comb_class] = res
        return res

    def get_function(self, comb_class: CombinatorialClass) -> Function:
        # TODO: this should be combclass method, so as to determine necessary variables
        return Function("F_{}".format(self.get_label(comb_class)))(sympy.abc.x)

    def get_equations(self) -> Iterator[Eq]:
        for comb_class, rule in self.rules_dict.items():
            lhs_func = self.get_function(comb_class)
            rhs_funcs = [self.get_function(comb_class) for comb_class in rule.children]
            yield rule.get_equation(lhs_func, rhs_funcs)

    def count_objects_of_size(self, size: int) -> int:
        return self.root_rule.count_objects_of_size(n=size)

    def generate_objects_of_size(self, size: int) -> Iterator[CombinatorialObject]:
        for obj in self.root_rule.generate_objects_of_size(n=size):
            yield obj

    def __str__(self):
        res = "A combinatorial specification with {} rules.".format(
            len(self.rules_dict)
        )
        for c, r in self.rules_dict.items():
            start_label = self.get_label(c)
            end_labels = tuple(self.get_label(c) for c in r.children)
            res += "\n\n"
            res += "{} -> {}\n".format(start_label, end_labels)
            res += str(r)
        # TODO: don't print equations...
        res += "\n\nEquations:"
        for eq in self.get_equations():
            res += "\n{} = {}".format(eq.lhs, eq.rhs)
        return res
