"""
A combinatorial specification is a set rules of the form a -> b1, ..., bk
where each of the bi appear exactly once on the left hand side of some rule.
"""
from copy import copy
from functools import reduce
from operator import mul
from typing import Dict, Generic, Iterable, Iterator, List, Optional, Set, Union

import sympy
from logzero import logger
from sympy import Eq, Expr, Function, Number, solve, var

from comb_spec_searcher.exception import SpecificationNotFound
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
from .isomorphism import Bijection, Isomorphism
from .specification_drawer import SpecificationDrawer
from .strategies import (
    EmptyStrategy,
    EquivalencePathRule,
    Rule,
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
        rules: Iterable[AbstractRule[CombinatorialClassType, CombinatorialObjectType]],
        group_equiv: bool = True,
    ):
        self.root = root
        self.rules_dict = {rule.comb_class: rule for rule in rules}
        self.labels: Dict[CombinatorialClassType, int] = {}
        self._label_to_tiling: Dict[int, CombinatorialClassType] = {}
        if group_equiv:
            self._group_equiv_in_path()
        self._set_subrules()

    def _set_subrules(self) -> None:
        """Tells the subrules which children's recurrence methods it should use."""
        for rule in list(
            self.rules_dict.values()
        ):  # list as we lazily assign empty rules
            rule.set_subrecs(self.get_rule)

    def _group_equiv_in_path(self) -> None:
        """
        Group chain of equivalence rules of the specification into equivalence paths.
        """
        self._ungroup_equiv_path()
        not_hidden_classes = {self.root}
        for rule in self.rules_dict.values():
            if rule.is_equivalence():
                continue
            not_hidden_classes.add(rule.comb_class)
            not_hidden_classes.update(rule.children)
        # Creating paths
        comb_class_stack = [self.root]
        visited: Set[CombinatorialClassType] = set()
        path_rules: List[Rule] = []
        eqv_path_rules: Dict[CombinatorialClassType, EquivalencePathRule] = {}
        while comb_class_stack:
            if path_rules and path_rules[-1].children[0] in not_hidden_classes:
                new_rule: EquivalencePathRule = EquivalencePathRule(path_rules)
                eqv_path_rules[new_rule.comb_class] = new_rule
                path_rules.clear()
            comb_class = comb_class_stack.pop()
            if comb_class in not_hidden_classes and comb_class in visited:
                continue
            visited.add(comb_class)
            rule = self.get_rule(comb_class)
            comb_class_stack.extend(rule.children)
            if rule.is_equivalence() and not isinstance(rule, EquivalencePathRule):
                assert isinstance(rule, Rule)
                assert not path_rules or path_rules[-1].children[0] == rule.comb_class
                path_rules.append(rule)
        # Clearing the equivalences and replacing by paths
        self.rules_dict = {
            comb_class: rule
            for comb_class, rule in self.rules_dict.items()
            if comb_class in not_hidden_classes
        }
        self.rules_dict.update(eqv_path_rules)
        assert self._is_valid_spec()

    def _ungroup_equiv_path(self) -> None:
        """
        Remove the equiv path and replacing only with normal rules.
        """
        new_rules: Dict[CombinatorialClassType, Rule] = {}
        for rule in self.rules_dict.values():
            if not isinstance(rule, EquivalencePathRule):
                continue
            for r in rule.rules:
                new_rules[r.comb_class] = r
        self.rules_dict.update(new_rules)

    def expand_verified(
        self,
    ) -> "CombinatorialSpecification[CombinatorialClassType, CombinatorialObjectType]":
        """
        Will expand all verified classes with respect to the strategy packs
        given by the VerificationStrategies.
        """
        new_spec = self
        while True:
            try:
                class_to_expand = next(new_spec.unexpanded_verified_classes())
            except StopIteration:
                return new_spec
            rule = new_spec.rules_dict[class_to_expand]
            assert isinstance(rule, VerificationRule)
            pack = rule.pack()
            new_spec = new_spec.expand_comb_class(class_to_expand, pack)

    def unexpanded_verified_classes(self) -> Iterator[CombinatorialClassType]:
        """
        Returns the verified classes so you can determine which classes still
        need to be expanded.
        """
        for comb_class, rule in self.rules_dict.items():
            if isinstance(rule, VerificationRule):
                try:
                    rule.pack()
                except InvalidOperationError:
                    continue
                yield comb_class

    def expand_comb_class(
        self,
        comb_class: Union[int, CombinatorialClassType],
        pack: StrategyPack,
        max_expansion_time: Optional[float] = None,
    ) -> "CombinatorialSpecification[CombinatorialClassType, CombinatorialObjectType]":
        """
        Will try to expand a particular class with respect to the given strategy pack.
        """
        # pylint: disable=import-outside-toplevel
        from permuta import Perm

        from .comb_spec_searcher import CombinatorialSpecificationSearcher
        from .rule_db import RuleDBForest

        print(comb_class)
        if isinstance(comb_class, int):
            comb_class = self._label_to_tiling[comb_class]

        spec_rules = tuple(
            rule for cc, rule in self.rules_dict.items() if cc != comb_class
        )
        ruledb = RuleDBForest(reverse=False, rule_cache=spec_rules)
        pack = pack.add_basis([Perm((0, 2, 1))])
        css = CombinatorialSpecificationSearcher(
            self.root, pack, ruledb=ruledb, debug=True
        )
        for rule in spec_rules:
            start_label = css.classdb.get_label(rule.comb_class)
            end_labels = tuple(map(css.classdb.get_label, rule.children))
            ruledb.add(start_label, end_labels, rule)
        css.classqueue.set_stop_yielding(css.classdb.get_label(self.root))
        css.classqueue.add(css.classdb.get_label(comb_class))
        # logger.info(CSS.run_information())
        spec_rule = css._auto_search_rules(max_expansion_time=max_expansion_time)
        if spec_rule is not None:
            new_spec = CombinatorialSpecification(self.root, spec_rule)
        else:
            raise SpecificationNotFound("Expansion unsuccessful")
        new_spec.show()
        return new_spec

    def _is_valid_spec(self) -> bool:
        """Checks that each class is on a left hand side."""
        comb_classes = set()
        for rule in self.rules_dict.values():
            comb_classes.add(rule.comb_class)
            comb_classes.update(rule.children)
        return self.root in comb_classes and all(
            c in self.rules_dict or c.is_empty() for c in comb_classes
        )

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
            assert (
                comb_class.is_empty()
            ), f"rule not in the spec and not empty\n{comb_class}"
            empty_strat = EmptyStrategy[
                CombinatorialClassType, CombinatorialObjectType
            ]()
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
        """
        return comb_class.get_function(self.get_label)

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
            tuple(eq.lhs for eq in eqs),
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
        if not self._is_valid_spec():
            return False

        for rule in self.rules_dict.values():
            try:
                for n in range(length + 1):
                    if not rule.sanity_check(n):
                        return False
            except NotImplementedError:
                logger.warning(
                    "Can't sanity check the rule %s -> %s, which is\n" "%s",
                    self.get_label(rule.comb_class),
                    tuple(self.get_label(child) for child in rule.children),
                    rule,
                )

        return True

    def get_bijection_to(
        self, other: "CombinatorialSpecification"
    ) -> Optional[Bijection]:
        """Get bijection from self to other."""
        return Bijection.construct(self, other)

    def are_isomorphic(self, other: "CombinatorialSpecification") -> bool:
        """Check if self is isomorphic to other."""
        return Isomorphism.check(self, other)

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
        file_url = sd.share()
        print(f"The specification is available at {file_url}.")

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
        return {
            "root": self.root.to_jsonable(),
            "rules": [rule.to_jsonable() for rule in self.rules_dict.values()],
        }

    @classmethod
    def from_dict(cls, d):
        """
        Return the specification with the dictionary outputter by the
        'to_jsonable' method
        """
        root = CombinatorialClass.from_dict(d.pop("root"))
        rules = [AbstractRule.from_dict(rule_dict) for rule_dict in d.pop("rules")]
        return CombinatorialSpecification(root, rules, group_equiv=False)


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
