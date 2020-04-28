from itertools import chain
from typing import Iterable, Iterator
from .combinatorial_class import CombinatorialClass, CombinatorialObject
from .strategies import Strategy
from .strategies import EmptyStrategy, EquivalencePathRule, ReverseRule, Rule

from logzero import logger
from sympy import Eq, Function
import sympy


__all__ = ("CombinatorialSpecification",)


class CombinatorialSpecification:
    def __init__(
        self,
        root: CombinatorialClass,
        strategies: Iterable[Strategy],
        equivalence_paths: Iterable[Iterable[CombinatorialClass]],
    ):
        # TODO: Think more about equivalence, its going to come back to bite you soon!
        # you really want to store the paths needed
        self.root = root
        equivalence_stratgies = {}
        self.rules_dict = {}
        for comb_class, strategy in strategies:
            rule = strategy(comb_class)
            if len(rule.children) == 1 and rule.constructor.is_equivalence():
                equivalence_stratgies[(comb_class, rule.children[0])] = rule
            else:
                self.rules_dict[comb_class] = strategy(comb_class)
        for eqv_path in equivalence_paths:
            if len(eqv_path) > 1:
                start = eqv_path[0]
                rules = []
                for a, b in zip(eqv_path[:-1], eqv_path[1:]):
                    try:
                        rule = equivalence_stratgies[(a, b)]
                    except KeyError:
                        rule = equivalence_stratgies[(b, a)].to_reverse_rule()
                    rules.append(rule)
                self.rules_dict[start] = EquivalencePathRule(rules)

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
        for rule in self.rules_dict.values():
            try:
                eq = rule.get_equation(self.get_function)
                if eq != True:
                    yield eq
            except NotImplementedError:
                logger.info(
                    "can't find generating function label {}."
                    " The comb class is:\n{}".format(
                        self.get_label(rule.comb_class), rule.comb_class
                    )
                )
                yield Eq(
                    self.get_function(rule.comb_class),
                    sympy.Function("NOTIMPLEMENTED")(sympy.abc.x),
                )

    def count_objects_of_size(self, size: int) -> int:
        return self.root_rule.count_objects_of_size(n=size)

    def generate_objects_of_size(self, size: int) -> Iterator[CombinatorialObject]:
        for obj in self.root_rule.generate_objects_of_size(n=size):
            yield obj

    def __eq__(self, other):
        return self.root == other.root and self.rules_dict == other.rules_dict

    def __str__(self):
        res = "A combinatorial specification with {} rules.".format(
            len(self.rules_dict)
        )
        eqv_paths = {
            rule.comb_class: rule
            for rule in self.rules_dict.values()
            if isinstance(rule, EquivalencePathRule)
        }
        for c, r in self.rules_dict.items():
            if isinstance(r, EquivalencePathRule):
                continue
            start_label = self.get_label(c)
            end_labels = tuple(self.get_label(c) for c in r.children)
            res += "\n\n"
            res += "{} -> {}\n".format(start_label, end_labels)
            res += str(r)
            for child in r.children:
                if child in eqv_paths:
                    eqv_rule = eqv_paths.pop(child)
                    child_label = self.get_label(eqv_rule.comb_class)
                    child_eqv_label = self.get_label(eqv_rule.children[0])
                    res += "\n\n"
                    res += "{} = {}\n".format(child_label, child_eqv_label)
                    res += str(eqv_rule)
        assert not eqv_paths
        return res

    def equations_string(self):
        res = ""
        for eq in sorted(
            self.get_equations(),
            key=lambda eq: int(str(eq.lhs).split("_")[1].split("(")[0]),
        ):
            res += "\n{} = {}".format(eq.lhs, eq.rhs)
        return res

    # JSON methods

    def to_jsonable(self):
        rules = [
            rule
            for rule in self.rules_dict.values()
            if not isinstance(rule, EquivalencePathRule)
        ]
        eqv_paths = []
        for rule in self.rules_dict.values():
            if isinstance(rule, EquivalencePathRule):
                eqv_path = []
                for c, r in rule.eqv_path_rules():
                    rules.append(r)
                    eqv_path.append(c.to_jsonable())
                eqv_path.append(rule.children[0].to_jsonable())
                eqv_paths.append(eqv_path)
        strategies = [
            (rule.children[0].to_jsonable(), rule.strategy.to_jsonable())
            if isinstance(rule, ReverseRule)
            else (rule.comb_class.to_jsonable(), rule.strategy.to_jsonable())
            for rule in rules
        ]
        return {
            "root": self.root.to_jsonable(),
            "strategies": strategies,
            "eqv_paths": eqv_paths,
        }

    @classmethod
    def from_dict(cls, d: dict, comb_class: type):
        return cls(
            root=comb_class.from_dict(d["root"]),
            strategies=[
                (comb_class.from_dict(class_dict), Strategy.from_dict(strat_dict))
                for class_dict, strat_dict in d["strategies"]
            ],
            equivalence_paths=[
                [comb_class.from_dict(class_dict) for class_dict in eqv_path]
                for eqv_path in d["eqv_paths"]
            ],
        )
