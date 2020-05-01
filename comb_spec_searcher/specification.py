"""
A combinatorial specification is a set rules of the form a -> b1, ..., bk
where each of the bi appear exactly once on the left hand side of some rule.
"""
from typing import Any, Dict, Iterable, Iterator, Sequence, Tuple
from logzero import logger
from sympy import Eq, Function
import sympy
from .combinatorial_class import CombinatorialClass, CombinatorialObject
from .strategies import Strategy, VerificationStrategy
from .strategies import EmptyStrategy, EquivalencePathRule, ReverseRule, Rule
from .strategies.strategy import StrategyType


__all__ = ("CombinatorialSpecification",)


class CombinatorialSpecification:
    """
    A combinatorial specification is a set rules of the form a -> b1, ..., bk
    where each of the bi appear exactly once on the left hand side of some
    rule.
    """

    def __init__(
        self,
        root: CombinatorialClass,
        strategies: Iterable[Tuple[CombinatorialClass, StrategyType]],
        equivalence_paths: Iterable[Sequence[CombinatorialClass]],
    ):
        self.root = root
        equivalence_rules: Dict[
            Tuple[CombinatorialClass, CombinatorialClass], Rule
        ] = {}
        self.rules_dict: Dict[CombinatorialClass, Rule] = {}
        for comb_class, strategy in strategies:
            rule = strategy(comb_class)
            if len(rule.children) == 1 and rule.constructor.is_equivalence():
                equivalence_rules[(comb_class, rule.children[0])] = rule
            else:
                self.rules_dict[comb_class] = strategy(comb_class)
        for eqv_path in equivalence_paths:
            if len(eqv_path) > 1:
                start = eqv_path[0]
                rules = []
                for a, b in zip(eqv_path[:-1], eqv_path[1:]):
                    try:
                        rule = equivalence_rules[(a, b)]
                    except KeyError:
                        rule = equivalence_rules[(b, a)].to_reverse_rule()
                    rules.append(rule)
                self.rules_dict[start] = EquivalencePathRule(rules)

        for rule in list(
            self.rules_dict.values()
        ):  # list as we lazily assign empty rules
            rule.set_subrecs(self.get_rule)
        self.labels: Dict[CombinatorialClass, int] = {}

    def get_rule(self, comb_class: CombinatorialClass) -> Rule:
        """Return the rule with comb class on the left."""
        if comb_class.is_empty():
            self.rules_dict[comb_class] = EmptyStrategy()(comb_class)
        return self.rules_dict[comb_class]

    @property
    def root_rule(self) -> Rule:
        """Return the rule of the root comb class."""
        return self.rules_dict[self.root]

    def get_label(self, comb_class: CombinatorialClass) -> int:
        """Return a unique label for the comb class."""
        res = self.labels.get(comb_class)
        if res is None:
            res = len(self.labels)
            self.labels[comb_class] = res
        return res

    def get_function(self, comb_class: CombinatorialClass) -> Function:
        """
        Return a sympy function for the comb class, using the label it is
        assigned.
        """
        return Function("F_{}".format(self.get_label(comb_class)))(sympy.abc.x)

    def get_equations(self) -> Iterator[Eq]:
        """
        Yield all equations on the (ordinary) generating function that the
        rules of the specification imply.
        """
        for rule in self.rules_dict.values():
            try:
                eq = rule.get_equation(self.get_function)
                if not isinstance(eq, bool):
                    yield eq
            except NotImplementedError:
                logger.info(
                    "can't find generating function label %s."
                    " The comb class is:\n%s",
                    self.get_label(rule.comb_class),
                    rule.comb_class,
                )
                yield Eq(
                    self.get_function(rule.comb_class),
                    sympy.Function("NOTIMPLEMENTED")(sympy.abc.x),
                )

    def get_genf(self) -> Any:
        """Return the generating function for the root comb class."""
        raise NotImplementedError

    def count_objects_of_size(self, size: int) -> int:
        """
        Return the number of objects of given size in the root comb_class.

        # TODO: update for arbitrary parameters
        """
        return self.root_rule.count_objects_of_size(n=size)

    def generate_objects_of_size(self, size: int) -> Iterator[CombinatorialObject]:
        """
        Return the objects of given size in the root comb_class.

        # TODO: update for arbitrary parameters
        """
        for obj in self.root_rule.generate_objects_of_size(n=size):
            yield obj

    def __eq__(self, other) -> bool:
        return bool(self.root == other.root and self.rules_dict == other.rules_dict)

    def __str__(self) -> str:
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

    def equations_string(self) -> str:
        """
        Return a convenient to read string version of the equations returned by
        'get_equations' method.
        """
        res = ""
        for eq in sorted(
            self.get_equations(),
            key=lambda eq: int(str(eq.lhs).split("_")[1].split("(")[0]),
        ):
            res += "\n{} = {}".format(eq.lhs, eq.rhs)
        return res

    # JSON methods

    def to_jsonable(self) -> dict:
        """Return a JSON serializable dictionary for the specification."""
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
    def from_dict(cls, d: dict) -> "CombinatorialSpecification":
        """
        Return the specification with the dictionary outputter by the
        'to_jsonable' method
        """
        strategies = []
        for comb_class_dict, strategy_dict in d["strategies"]:
            comb_class = CombinatorialClass.from_dict(comb_class_dict)
            strategy = Strategy.from_dict(strategy_dict)
            assert isinstance(strategy, (Strategy, VerificationStrategy))
            strategies.append((comb_class, strategy))
        return cls(
            root=CombinatorialClass.from_dict(d["root"]),
            strategies=strategies,
            equivalence_paths=[
                [CombinatorialClass.from_dict(class_dict) for class_dict in eqv_path]
                for eqv_path in d["eqv_paths"]
            ],
        )
