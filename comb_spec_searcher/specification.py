"""
A combinatorial specification is a set rules of the form a -> b1, ..., bk
where each of the bi appear exactly once on the left hand side of some rule.
"""
from copy import copy
from functools import reduce
from operator import mul
from typing import Dict, Generic, Iterable, Iterator, List, Sequence, Set, Tuple, Union

import sympy
from logzero import logger
from sympy import Eq, Expr, Function, Number, solve, var

from comb_spec_searcher.typing import (
    CombinatorialClassType,
    CombinatorialObjectType,
    Objects,
    Terms,
)

from .combinatorial_class import CombinatorialClass, CombinatorialObject
from .exception import (
    IncorrectGeneratingFunctionError,
    InvalidOperationError,
    TaylorExpansionError,
)
from .specification_drawer import SpecificationDrawer
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
        self.rules_dict: Dict[CombinatorialClassType, AbstractRule] = {}
        self._populate_rules_dict(strategies, equivalence_paths)
        self._remove_redundant_rules()
        self.labels: Dict[CombinatorialClassType, int] = {}
        self._label_to_tiling: Dict[int, CombinatorialClassType] = {}
        self._set_subrules()

    def _set_subrules(self) -> None:
        """Tells the subrules which children's recurrence methods it should use."""
        for rule in list(
            self.rules_dict.values()
        ):  # list as we lazily assign empty rules
            rule.set_subrecs(self.get_rule)

    def _populate_rules_dict(
        self,
        strategies: Iterable[
            Tuple[
                CombinatorialClassType,
                AbstractStrategy[CombinatorialClassType, CombinatorialObjectType],
            ]
        ],
        equivalence_paths: Iterable[Sequence[CombinatorialClassType]],
    ) -> None:
        logger.info("Creating rules.")
        equivalence_rules: Dict[
            Tuple[CombinatorialClassType, CombinatorialClassType], Rule
        ] = {}
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
            elif non_empty_children or isinstance(rule, VerificationRule):
                self.rules_dict[comb_class] = rule
            else:
                raise ValueError("Non verification rule has no children.")
        self._add_equivalence_path_rules(equivalence_paths, equivalence_rules)

    def expand_verified(self) -> None:
        """
        Will expand all verified classes with respect to the strategy packs
        given by the VerificationStrategies.
        """
        verification_packs: Dict[CombinatorialClassType, StrategyPack] = {}
        for comb_class, rule in self.rules_dict.items():
            if isinstance(rule, VerificationRule):
                try:
                    verification_packs[comb_class] = rule.pack()
                except InvalidOperationError:
                    logger.info("Can't expand the rule:\n%s", rule)
        if verification_packs:
            for comb_class in verification_packs:
                self.rules_dict.pop(comb_class)
            self._expand_verified_comb_classes(verification_packs)
            self.expand_verified()
            self._set_subrules()

    def expand_comb_class(self, comb_class: Union[int, CombinatorialClassType]) -> None:
        """
        Will try to expand a particular class with respect to the strategy pack
        that the VerificationStrategy has.
        """
        rule = self.get_rule(comb_class)
        if isinstance(rule, VerificationRule):
            try:
                pack = rule.pack()
            except InvalidOperationError:
                logger.info("Can't expand the rule:\n%s", rule)
                return
            self.rules_dict.pop(rule.comb_class)
            self._expand_verified_comb_classes({rule.comb_class: pack})
        else:
            logger.info("Can't expand the rule:\n%s", rule)

    def _add_equivalence_path_rules(
        self,
        equivalence_paths: Iterable[Sequence[CombinatorialClassType]],
        equivalence_rules: Dict[
            Tuple[CombinatorialClassType, CombinatorialClassType], Rule
        ],
    ) -> None:
        logger.info("Creating equivalence path rules.")
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

    def _remove_redundant_rules(self) -> None:
        """
        Any redundant rules passed to the __init__ method are removed using
        this method.
        """
        rules_dict = copy(self.rules_dict)

        def prune(comb_class: CombinatorialClassType) -> None:
            try:
                rule = rules_dict.pop(comb_class)
            except KeyError:
                assert comb_class in self.rules_dict or comb_class.is_empty()
                return
            if isinstance(rule, EquivalencePathRule):
                try:
                    rule = rules_dict.pop(rule.children[0])
                except KeyError:
                    assert comb_class in self.rules_dict
                    return
            for child in rule.children:
                prune(child)

        prune(self.root)

        logger.info("Removed %s redundant rules.", len(rules_dict.values()))
        for rule in rules_dict.values():
            self.rules_dict.pop(rule.comb_class)

    def _expand_verified_comb_classes(
        self, verification_packs: Dict[CombinatorialClassType, StrategyPack]
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
            # pylint: disable=protected-access
            comb_class_rules, comb_class_eqv_paths = css._auto_search_rules()
            self._populate_rules_dict(comb_class_rules, comb_class_eqv_paths)
        self._remove_redundant_rules()

    def get_rule(
        self, comb_class: Union[int, CombinatorialClassType]
    ) -> AbstractRule[CombinatorialClassType, CombinatorialObjectType]:
        """Return the rule with comb class on the left."""
        if isinstance(comb_class, int):
            try:
                comb_class = self._label_to_tiling[comb_class]
            except KeyError as e:
                raise InvalidOperationError(
                    f"The label {comb_class} does not correspond to a tiling"
                    " in the specification."
                ) from e
        if comb_class not in self.rules_dict:
            assert comb_class.is_empty(), "rule not in the spec and not empty"
            empty_strat = EmptyStrategy()
            self.rules_dict[comb_class] = empty_strat(comb_class)
        return self.rules_dict[comb_class]

    def comb_classes(self) -> Set[CombinatorialClassType]:
        """
        Return a set containing all the combinatorial classes of the specification.
        """
        res: Set[CombinatorialClassType] = set()
        for rule in self.rules_dict.values():
            res.update(rule.children)
            res.add(rule.comb_class)
            if isinstance(rule, EquivalencePathRule):
                for parent, _ in rule.eqv_path_rules():
                    res.add(parent)
        return res

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
            self._label_to_tiling[res] = comb_class
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
        raise IncorrectGeneratingFunctionError(
            "Failed to compute the generating function for the specification."
        )

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

    def get_terms(self, n: int) -> Terms:
        """
        Return the terms for given n.
        """
        return self.root_rule.get_terms(n)

    def get_objects(self, n: int) -> Objects:
        """
        Return the objects for given n.
        """
        return self.root_rule.get_objects(n)

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
            all(rule.sanity_check(n) for rule in self.rules_dict.values())
            for n in range(length + 1)
        )

    def show(
        self, levels_shown: int = 0, levels_expand: int = 0, verbose: bool = False
    ) -> None:
        """
        Displays a tree representing this object in the web browser
        OTHER INPUT:
            - 'levels_shown': number of levels displayed at the start.
            If 0 then the whole tree is displayed
            - 'levels_expand': number of levels displayed after expanding a node.
            If 0 then the rest of the tree is displayed
            - 'verbose': displays formal step below the node
            and json representation in tooltips
        """
        sd = SpecificationDrawer(
            self,
            levels_shown=levels_shown,
            levels_expand=levels_expand,
            verbose=verbose,
        )
        sd.show()

    def share(
        self, levels_shown: int = 0, levels_expand: int = 0, verbose: bool = False
    ) -> None:
        """
        Uploads the html representation of the specification to a sharing website and
        display the link to the file.

        INPUT:
            - 'levels_shown': number of levels displayed at the start.
            If 0 then the whole tree is displayed
            - 'levels_expand': number of levels displayed after expanding a node.
            If 0 then the rest of the tree is displayed
            - 'verbose': displays formal step below the node
            and json representation in tooltips
        """
        sd = SpecificationDrawer(
            self,
            levels_shown=levels_shown,
            levels_expand=levels_expand,
            verbose=verbose,
        )
        sd.share()

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
                assert comb_class in self.rules_dict or comb_class.is_empty()
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
        assert not rules_dict
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
