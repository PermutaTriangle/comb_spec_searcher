"""
A combinatorial specification is a set rules of the form a -> b1, ..., bk
where each of the bi appear exactly once on the left hand side of some rule.
"""
import logging
from copy import copy
from functools import reduce
from operator import mul
from typing import Dict, Generic, Iterable, Iterator, List, Sequence, Tuple

import sympy
from logzero import logger
from sympy import Eq, Expr, Function, Number, solve, var

from .combinatorial_class import (
    CombinatorialClass,
    CombinatorialClassType,
    CombinatorialObject,
    CombinatorialObjectType,
)
from .exception import (
    IncorrectGeneratingFunctionError,
    InvalidOperationError,
    NoMoreClassesToExpandError,
    SpecificationNotFound,
    TaylorExpansionError,
)
from .strategies import (
    AbstractStrategy,
    EmptyStrategy,
    EquivalencePathRule,
    ReverseRule,
    Rule,
    Strategy,
    StrategyPack,
    VerificationRule,
    VerificationStrategy,
)
from .strategies.rule import AbstractRule
from .utils import (
    DisableLogging,
    RecursionLimit,
    maple_equations,
    pretty_print_equations,
    taylor_expand,
)

__all__ = ("CombinatorialSpecification",)


class CombinatorialSpecification(
    Generic[CombinatorialClassType, CombinatorialObjectType]
):
    """
    A combinatorial specification is a set rules of the form a -> b1, ..., bk
    where each of the bi appear exactly once on the left hand side of some
    rule.

    The default is to expand verified classes, but this can be turned off by
    setting expand_verified to False.
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
        expand_verified: bool = True,
    ):
        self.root = root
        self.rules_dict: Dict[CombinatorialClassType, AbstractRule] = {}
        self._populate_rules_dict(strategies, equivalence_paths, expand_verified)
        for rule in list(
            self.rules_dict.values()
        ):  # list as we lazily assign empty rules
            rule.set_subrecs(self.get_rule)
        self.labels: Dict[CombinatorialClassType, int] = {}

    def _populate_rules_dict(
        self,
        strategies: Iterable[
            Tuple[
                CombinatorialClassType,
                AbstractStrategy[CombinatorialClassType, CombinatorialObjectType],
            ]
        ],
        equivalence_paths: Iterable[Sequence[CombinatorialClassType]],
        expand_verified: bool,
    ) -> None:
        equivalence_rules: Dict[
            Tuple[CombinatorialClassType, CombinatorialClassType], Rule
        ] = {}
        verification_packs: Dict[CombinatorialClassType, StrategyPack] = {}
        for comb_class, strategy in strategies:
            if isinstance(strategy, AlreadyVerified):
                continue
            rule = strategy(comb_class)
            non_empty_children = rule.non_empty_children()
            if rule.is_equivalence():
                assert isinstance(rule, Rule)
                equivalence_rules[(comb_class, non_empty_children[0])] = (
                    rule if len(rule.children) == 1 else rule.to_equivalence_rule()
                )
            elif non_empty_children:
                self.rules_dict[comb_class] = rule
            elif isinstance(rule, VerificationRule):
                if expand_verified:
                    try:
                        verification_packs[comb_class] = rule.pack()
                    except InvalidOperationError:
                        self.rules_dict[comb_class] = strategy(comb_class)
                else:
                    self.rules_dict[comb_class] = strategy(comb_class)
            else:
                raise ValueError("Non verification rule has no children.")
        self._add_equivalence_path_rules(equivalence_paths, equivalence_rules)
        self._expand_verified_comb_classes(verification_packs)

    def _add_equivalence_path_rules(
        self,
        equivalence_paths: Iterable[Sequence[CombinatorialClassType]],
        equivalence_rules: Dict[
            Tuple[CombinatorialClassType, CombinatorialClassType], Rule
        ],
    ) -> None:
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

    def _expand_verified_comb_classes(
        self, verification_packs: Dict[CombinatorialClassType, StrategyPack],
    ) -> None:
        for comb_class, pack in verification_packs.items():
            # pylint: disable=import-outside-toplevel
            from .comb_spec_searcher import CombinatorialSpecificationSearcher

            css = CombinatorialSpecificationSearcher(
                comb_class,
                pack.add_verification(
                    AlreadyVerified(self.rules_dict), apply_first=True
                ),
            )
            logger.info(css.run_information())
            while True:
                try:
                    css.do_level()
                except NoMoreClassesToExpandError:
                    with DisableLogging(logging.INFO):
                        new_rules = css.ruledb.get_smallest_specification(
                            css.start_label
                        )
                    break
                try:
                    with DisableLogging(logging.INFO):
                        new_rules = css.ruledb.get_smallest_specification(
                            css.start_label
                        )
                    break
                except SpecificationNotFound:
                    pass
            rules, eqv_paths = new_rules
            comb_class_eqv_paths = tuple(
                tuple(map(css.classdb.get_class, path)) for path in eqv_paths
            )
            comb_class_rules = [
                (css.classdb.get_class(label), rule) for label, rule in rules
            ]
            self._populate_rules_dict(comb_class_rules, comb_class_eqv_paths, True)

    def get_rule(
        self, comb_class: CombinatorialClassType
    ) -> AbstractRule[CombinatorialClassType, CombinatorialObjectType]:
        """Return the rule with comb class on the left."""
        if comb_class not in self.rules_dict:
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
        extra_parameters = [var(k) for k in comb_class.extra_parameters]
        return Function("F_{}".format(self.get_label(comb_class)))(x, *extra_parameters)

    def get_equations(self) -> Iterator[Eq]:
        """
        Yield all equations on the (ordinary) generating function that the
        rules of the specification imply.
        """
        funcs: Dict[CombinatorialClass, Function] = {
            comb_class: self.get_function(comb_class)
            for comb_class, rule in self.rules_dict.items()
            if not isinstance(rule, VerificationRule)
        }
        for _, rule in sorted(
            self.rules_dict.items(), key=lambda x: self.get_label(x[0])
        ):
            try:
                if isinstance(rule, VerificationRule):
                    eq = rule.get_equation(self.get_function, funcs)
                else:
                    eq = rule.get_equation(self.get_function)
                if not isinstance(eq, bool):
                    yield eq
            except NotImplementedError:
                logger.info(
                    "can't find generating function for the rule %s -> %s. "
                    "The rule was:\n%s",
                    self.get_label(rule.comb_class),
                    tuple(self.get_label(child) for child in rule.children),
                    rule,
                )
                x = var("x")
                yield Eq(
                    self.get_function(rule.comb_class),
                    sympy.Function("NOTIMPLEMENTED")(x),
                )

    def get_initial_conditions(self, check: int = 6) -> List[Expr]:
        """
        Compute the initial conditions of the root class. It will use the
        `count_objects_of_size` method if implemented, else resort to
        the method on the `initial_conditions` method on `CombinatorialClass.
        """
        logger.info("Computing initial conditions")
        try:
            return [
                sum(
                    Number(self.count_objects_of_size(n=n, **parameters))
                    * reduce(mul, [var(k) ** val for k, val in parameters.items()], 1)
                    for parameters in self.root.possible_parameters(n)
                )
                for n in range(check + 1)
            ]
        except NotImplementedError as e:
            logger.info(
                "Reverting to generating objects from root for initial "
                "conditions due to:\nNotImplementedError: %s",
                e,
            )
        return self.root.initial_conditions(check)

    def get_genf(self, check: int = 6) -> Expr:
        """
        Return the generating function for the root comb class.

        # TODO: consider what to do if multiple variables.
        """
        eqs = tuple(self.get_equations())
        root_func = self.get_function(self.root)
        logger.info("Computing initial conditions")
        initial_conditions = self.get_initial_conditions(check)
        logger.info(pretty_print_equations(root_func, initial_conditions, eqs))
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
                return sympy.simplify(genf)
        raise IncorrectGeneratingFunctionError

    def get_maple_equations(self, check: int = 6) -> str:
        """
        Convert the systems of equations to version that can be copy pasted to maple.
        """
        eqs = tuple(self.get_equations())
        root_func = self.get_function(self.root)
        initial_conditions = self.get_initial_conditions(check)
        maple_eqs = maple_equations(root_func, initial_conditions, eqs)
        return maple_eqs

    def get_pretty_equations(self, check: int = 6) -> str:
        """
        Convert the systems of equations to a more readable format.
        """
        eqs = tuple(self.get_equations())
        root_func = self.get_function(self.root)
        initial_conditions = self.get_initial_conditions(check)
        return pretty_print_equations(root_func, initial_conditions, eqs)

    def count_objects_of_size(self, n: int, **parameters) -> int:
        """
        Return the number of objects with the given parameters.
        Note, 'n' is reserved for the size of the object.
        """
        limit = n * self.number_of_rules()
        with RecursionLimit(limit):
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
        limit = n * self.number_of_rules()
        with RecursionLimit(limit):
            return self.root_rule.random_sample_object_of_size(n, **parameters)

    def number_of_rules(self) -> int:
        return len(self.rules_dict)

    def sanity_check(self, length: int = 5) -> bool:
        """
        Sanity check the specification to the given length.

        Raise an SanityCheckFailure error if it fails.
        """
        return all(
            all(
                rule.sanity_check(n, **parameters)
                for rule in self.rules_dict.values()
                for parameters in rule.comb_class.possible_parameters(n)
            )
            for n in range(length + 1)
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CombinatorialSpecification):
            return NotImplemented
        return bool(self.root == other.root and self.rules_dict == other.rules_dict)

    def __str__(self) -> str:
        res = "A combinatorial specification with {} rules.".format(
            self.number_of_rules()
        )
        rules_dict = copy(self.rules_dict)

        def update_res(comb_class: CombinatorialClassType, res: str):
            try:
                rule = rules_dict.pop(comb_class)
            except KeyError:
                assert comb_class in self.rules_dict
                return res
            if isinstance(rule, EquivalencePathRule):
                child_label = self.get_label(rule.comb_class)
                child_eqv_label = self.get_label(rule.children[0])
                labels = "{} = {}\n".format(child_label, child_eqv_label)
                res += "\n{}\n".format("-" * (len(labels) - 1))
                res += labels
                res += str(rule)
                try:
                    rule = rules_dict.pop(rule.children[0])
                except KeyError:
                    assert comb_class in self.rules_dict
                    return res
            start_label = self.get_label(rule.comb_class)
            end_labels = tuple(self.get_label(c) for c in rule.children)
            labels = "{} -> {}\n".format(start_label, end_labels)
            res += "\n{}\n".format("-" * (len(labels) - 1))
            res += labels
            res += str(rule)
            for child in rule.children:
                res = update_res(child, res)
            return res

        res = update_res(self.root, res)
        return res + "\n"

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
    def from_dict(cls, d, expand_verified=False):
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
            expand_verified=expand_verified,
        )


class AlreadyVerified(VerificationStrategy[CombinatorialClass, CombinatorialObject]):
    def __init__(self, verfied_comb_classes: Iterable[CombinatorialClass]):
        self.verified_classes = frozenset(verfied_comb_classes)
        super().__init__()

    def verified(self, comb_class: CombinatorialClass) -> bool:
        return comb_class in self.verified_classes

    @staticmethod
    def formal_step() -> str:
        return "already verified"

    def to_jsonable(self) -> dict:
        d: dict = super().to_jsonable()
        d["comb_classes"] = [c.to_jsonable() for c in self.verified_classes]
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "AlreadyVerified":
        return cls([CombinatorialClass.from_dict(c) for c in d["comb_classes"]])
