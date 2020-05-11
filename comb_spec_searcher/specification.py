"""
A combinatorial specification is a set rules of the form a -> b1, ..., bk
where each of the bi appear exactly once on the left hand side of some rule.
"""
from typing import Dict, Generic, Iterable, Iterator, Sequence, Tuple

import sympy
from logzero import logger
from sympy import Eq, Expr, Function, solve, var

from .combinatorial_class import (
    CombinatorialClass,
    CombinatorialClassType,
    CombinatorialObjectType,
)
from .exception import IncorrectGeneratingFunctionError, TaylorExpansionError
from .strategies import (
    AbstractStrategy,
    EmptyStrategy,
    EquivalencePathRule,
    ReverseRule,
    Rule,
    Strategy,
    VerificationStrategy,
)
from .strategies.rule import AbstractRule
from .utils import maple_equations, taylor_expand

__all__ = ("CombinatorialSpecification",)


class CombinatorialSpecification(
    Generic[CombinatorialClassType, CombinatorialObjectType]
):
    """
    A combinatorial specification is a set rules of the form a -> b1, ..., bk
    where each of the bi appear exactly once on the left hand side of some
    rule.
    """

    def __init__(
        self,
        root: CombinatorialClassType,
        strategies: Iterable[
            Tuple[
                CombinatorialClassType,
                AbstractStrategy[CombinatorialClassType, CombinatorialObjectType],
            ]
        ],
        equivalence_paths: Iterable[Sequence[CombinatorialClassType]],
    ):
        self.root = root
        equivalence_rules: Dict[
            Tuple[CombinatorialClassType, CombinatorialClassType], Rule
        ] = {}
        self.rules_dict: Dict[CombinatorialClassType, AbstractRule] = {}
        for comb_class, strategy in strategies:
            rule = strategy(comb_class)
            non_empty_children = rule.non_empty_children()
            if (
                isinstance(rule, Rule)
                and len(non_empty_children) == 1
                and rule.constructor.is_equivalence()
            ):
                equivalence_rules[(comb_class, non_empty_children[0])] = (
                    rule if len(rule.children) == 1 else rule.to_equivalence_rule()
                )
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
        self.labels: Dict[CombinatorialClassType, int] = {}

    def get_rule(
        self, comb_class: CombinatorialClassType
    ) -> AbstractRule[CombinatorialClassType, CombinatorialObjectType]:
        """Return the rule with comb class on the left."""
        if comb_class.is_empty():
            empty_strat = EmptyStrategy()
            self.rules_dict[comb_class] = empty_strat(comb_class)
        return self.rules_dict[comb_class]

    @property
    def root_rule(
        self,
    ) -> AbstractRule[CombinatorialClassType, CombinatorialObjectType]:
        """Return the rule of the root comb class."""
        return self.rules_dict[self.root]

    def get_label(self, comb_class: CombinatorialClassType) -> int:
        """Return a unique label for the comb class."""
        res = self.labels.get(comb_class)
        if res is None:
            res = len(self.labels)
            self.labels[comb_class] = res
        return res

    def get_function(self, comb_class: CombinatorialClassType) -> Function:
        """
        Return a sympy function for the comb class, using the label it is
        assigned.

        TODO: call comb_class for its parameters - 'x' is reserved for size.
        """
        x = var("x")
        return Function("F_{}".format(self.get_label(comb_class)))(x)

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
                x = var("x")
                yield Eq(
                    self.get_function(rule.comb_class),
                    sympy.Function("NOTIMPLEMENTED")(x),
                )

    def get_genf(self, check: int = 6) -> Expr:
        """
        Return the generating function for the root comb class.

        # TODO: consider what to do if multiple variables.
        """
        eqs = set(self.get_equations())
        root_func = self.get_function(self.root)
        initial_conditions = [self.count_objects_of_size(n=i) for i in range(check + 1)]
        logger.info(maple_equations(root_func, initial_conditions, eqs,),)
        logger.info("Solving...")
        solutions = solve(
            eqs,
            tuple([eq.lhs for eq in eqs]),
            dict=True,
            cubics=False,
            quartics=False,
            quintics=False,
        )
        for solution in solutions:
            genf = solution[root_func]
            logger.info("Checking initial conditions for: %s", genf)
            try:
                expansion = taylor_expand(genf, check)
            except TaylorExpansionError:
                continue
            if expansion == initial_conditions:
                return genf
        raise IncorrectGeneratingFunctionError

    def count_objects_of_size(self, n: int, **parameters) -> int:
        """
        Return the number of objects with the given parameters.
        Note, 'n' is reserved for the size of the object.
        """
        return self.root_rule.count_objects_of_size(n, **parameters)

    def generate_objects_of_size(
        self, n: int, **parameters
    ) -> Iterator[CombinatorialObjectType]:
        """
        Return the objects with the given parameters.
        Note, 'n' is reserved for the size of the object.
        """
        for obj in self.root_rule.generate_objects_of_size(n, **parameters):
            yield obj

    def random_sample_object_of_size(
        self, n: int, **parameters: int
    ) -> CombinatorialObjectType:
        """
        Return a uniformly random object of the given size. This is done using
        the "recursive" method.
        """
        return self.root_rule.random_sample_object_of_size(n, **parameters)

    def number_of_rules(self) -> int:
        return len(self.rules_dict)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CombinatorialSpecification):
            return NotImplemented
        return bool(self.root == other.root and self.rules_dict == other.rules_dict)

    def __str__(self) -> str:
        res = "A combinatorial specification with {} rules.".format(
            self.number_of_rules()
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
    def from_dict(cls, d):
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
