"""
The rule class is used for a specific application of a strategy on a combinatorial
class. This is not something the user should implement, as it is just a wrapper for
calling the Strategy class and storing its results.

A CombinatorialSpecification is (more or less) a set of Rule.
"""
import abc
from collections import defaultdict
from itertools import chain, product
from random import randint
from typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    Generic,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    cast,
)

from sympy import Eq, Function

from comb_spec_searcher.typing import (
    Objects,
    ObjectsCache,
    SubObjects,
    SubTerms,
    Terms,
    TermsCache,
)

from ..combinatorial_class import CombinatorialClassType, CombinatorialObjectType
from ..exception import SanityCheckFailure, StrategyDoesNotApply
from .constructor import Constructor, DisjointUnion

if TYPE_CHECKING:
    from .strategy import AbstractStrategy, Strategy, VerificationStrategy
    from .strategy_pack import StrategyPack

__all__ = ("Rule", "VerificationRule")


class AbstractRule(abc.ABC, Generic[CombinatorialClassType, CombinatorialObjectType]):
    """
    An instance of Rule is created by the __call__ method of strategy.
    """

    def __init__(
        self,
        strategy: "AbstractStrategy[CombinatorialClassType, CombinatorialObjectType]",
        comb_class: CombinatorialClassType,
        children: Optional[Tuple[CombinatorialClassType, ...]] = None,
    ):
        self.comb_class = comb_class
        self._strategy = strategy
        self.terms_cache: TermsCache = []
        self.objects_cache: ObjectsCache = []
        self.subrecs: Optional[Tuple[Callable[..., int], ...]] = None
        self.subgenerators: Optional[
            Tuple[Callable[..., Iterator[CombinatorialObjectType]], ...]
        ] = None
        self.subsamplers: Optional[Tuple[Callable[..., CombinatorialObjectType], ...]]
        self.subterms: Optional[SubTerms] = None
        self.subobjects: Optional[SubObjects] = None
        self._children = children
        self._non_empty_children: Optional[Tuple[CombinatorialClassType, ...]] = None

    @property
    def strategy(
        self,
    ) -> "AbstractStrategy[CombinatorialClassType, CombinatorialObjectType]":
        return self._strategy

    @property
    def ignore_parent(self) -> bool:
        """
        Return True if it is not worth expanding the parent/comb_class if
        this rule is found.
        """
        return self._strategy.ignore_parent

    @property
    def inferrable(self) -> bool:
        """
        Return True if the children could change using inferral strategies.
        """
        return self._strategy.inferrable

    @property
    def possibly_empty(self) -> bool:
        """
        Return True if it is possible that a child is empty.
        """
        return self._strategy.possibly_empty

    @property
    def workable(self) -> bool:
        """
        Return True if the children can expanded using other strategies.
        """
        return self._strategy.workable

    def set_subrecs(
        self,
        get_subrule: Callable[
            [CombinatorialClassType],
            "AbstractRule[CombinatorialClassType, CombinatorialObjectType]",
        ],
    ) -> None:
        """
        In general a rule comes in the context of a set of rules, e.g. in a
        CombinatorialSpecification. In order to count, generate, etc using the
        rule we must set the subfunctions that the children refer to.
        """
        self.subrecs = tuple(
            get_subrule(child).count_objects_of_size for child in self.children
        )
        self.subsamplers = tuple(
            get_subrule(child).random_sample_object_of_size for child in self.children
        )
        self.subobjects = tuple(
            get_subrule(child).get_objects for child in self.children
        )
        self.subterms = tuple(get_subrule(child).get_terms for child in self.children)

    @property
    def children(self) -> Tuple[CombinatorialClassType, ...]:
        """
        Return the tuple of CombinatorialClass that are found by applying the
        decomposition function of the strategy to the parent.
        """
        if self._children is None:
            self._children = self._strategy.decomposition_function(self.comb_class)
            if self._children is None:
                raise StrategyDoesNotApply("{} does not apply".format(self._strategy))
        return self._children

    @property
    def formal_step(self) -> str:
        """
        Return a string with a short explanation about the rule.
        """
        return self._strategy.formal_step()

    @abc.abstractmethod
    def is_equivalence(self) -> bool:
        """
        Returns True if the rule is an equivalence.
        """

    def non_empty_children(self) -> Tuple[CombinatorialClassType, ...]:
        """
        Return the tuple of non-empty combinatorial classes that are found
        by applying the decomposition function.
        """
        if self._non_empty_children is None:
            self._non_empty_children = tuple(
                child for child in self.children if not child.is_empty()
            )
        return self._non_empty_children

    @abc.abstractmethod
    def _ensure_level(self, n: int) -> None:
        """
        Ensures the terms are computed and in the terms_cache upto size n.
        """

    def get_terms(self, n: int) -> Terms:
        """
        Return the terms for the given n.
        """
        self._ensure_level(n)
        return self.terms_cache[n]

    def count_objects_of_size(self, n: int, **parameters: int) -> int:
        """
        The function count the objects with respect to the parameters. The
        result is cached.
        """
        terms = self.get_terms(n)
        params_tuple = tuple(parameters[k] for k in self.comb_class.extra_parameters)
        return terms[params_tuple]

    @abc.abstractmethod
    def get_equation(
        self, get_function: Callable[[CombinatorialClassType], Function]
    ) -> Eq:
        """
        Return the equation for the (ordinary) generating function.
        """

    @abc.abstractmethod
    def _ensure_level_objects(self, n: int) -> None:
        """
        Ensures the objects are computed and in the objects cache upto size n.
        """

    def get_objects(self, n: int) -> Objects:
        """
        Return the objects for the given n.
        """
        self._ensure_level_objects(n)
        return self.objects_cache[n]

    def generate_objects_of_size(
        self, n: int, **parameters: int
    ) -> Iterator[CombinatorialObjectType]:
        """
        Generate the objects by using the underlying bijection between the
        parent and children.
        """
        objects = self.get_objects(n)
        params_tuple = tuple(parameters[k] for k in self.comb_class.extra_parameters)
        yield from objects[params_tuple]

    @abc.abstractmethod
    def random_sample_object_of_size(
        self, n: int, **parameters: int
    ) -> CombinatorialObjectType:
        """Return a random objects of the give size."""

    @abc.abstractmethod
    def sanity_check(self, n: int) -> bool:
        """
        Sanity check that this is a valid rule.

        Raise a SanityCheckFailure error if the sanity_check fails.
        """
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AbstractRule):
            return NotImplemented
        return (
            isinstance(other, self.__class__)
            and self.comb_class == other.comb_class
            and self._strategy == other._strategy
        )

    def __str__(self) -> str:
        def frontpad(res, height):
            n = max(len(s) for s in res)
            for _ in range(height - len(res)):
                res.append(" " * n)

        def backpad(res):
            n = max(len(s) for s in res)
            for i, s in enumerate(res):
                res[i] = s + " " * (n - len(s))

        def join(res, new):
            backpad(new)
            backpad(res)
            frontpad(res, len(new))
            for i, s in enumerate(new):
                res[i] += s

        res = str(self.comb_class).split("\n")
        backpad(res)
        if isinstance(self, Rule):
            children = [str(child).split("\n") for child in self.children]
            symbol_height = min(1, len(res) - 1)
            eq_symbol = (
                ["     " for i in range(symbol_height)]
                + ["  {}  ".format(self.strategy.get_eq_symbol())]
                + ["     " for i in range(symbol_height)]
            )
            join(res, eq_symbol)
            join(res, children[0])
            if len(children) > 1:
                op_symbol = (
                    ["     " for i in range(symbol_height)]
                    + ["  {}  ".format(self.strategy.get_op_symbol())]
                    + ["     " for i in range(symbol_height)]
                )
                for child in children[1:]:
                    join(res, op_symbol)
                    join(res, child)
        return f"{self.formal_step}\n" + "\n".join(x for x in res)


class Rule(AbstractRule[CombinatorialClassType, CombinatorialObjectType]):
    def __init__(
        self,
        strategy: "Strategy[CombinatorialClassType, CombinatorialObjectType]",
        comb_class: CombinatorialClassType,
        children: Optional[Tuple[CombinatorialClassType, ...]] = None,
    ):
        super().__init__(strategy, comb_class, children)
        self._constructor: Optional[Constructor] = None

    @property
    def strategy(self) -> "Strategy[CombinatorialClassType, CombinatorialObjectType]":
        return cast(
            "Strategy[CombinatorialClassType, CombinatorialObjectType]",
            super().strategy,
        )

    @property
    def constructor(
        self,
    ) -> Constructor[CombinatorialClassType, CombinatorialObjectType]:
        """
        Return the constructor, that contains all the information about how to
        count/generate objects from the rule.
        """
        if self._constructor is None:
            self._constructor = self.strategy.constructor(
                self.comb_class, self.children
            )
            if self._constructor is None:
                raise StrategyDoesNotApply("{} does not apply".format(self.strategy))
        return self._constructor

    def is_equivalence(self):
        return self.strategy.can_be_equivalent() and len(self.non_empty_children()) == 1

    def backward_map(
        self, objs: Tuple[Optional[CombinatorialObjectType], ...]
    ) -> Iterator[CombinatorialObjectType]:
        """
        This encodes the backward map of the underlying bijection that the
        strategy implies.
        """
        yield from self.strategy.backward_map(self.comb_class, objs, self.children)

    def forward_map(
        self, obj: CombinatorialObjectType
    ) -> Tuple[Optional[CombinatorialObjectType], ...]:
        """
        This encodes the forward map of the underlying bijection that the
        strategy implies.
        """
        return self.strategy.forward_map(self.comb_class, obj, self.children)

    def to_equivalence_rule(self) -> "EquivalenceRule":
        """
        Return the reverse rule. At this stage, reverse rules can only be
        created for equivalence rules.
        """
        assert (
            self.is_equivalence()
        ), f"EquivalenceRule can only be created for equivalence rules\n{self}"
        return EquivalenceRule(self)

    def to_reverse_rule(self) -> "ReverseRule":
        """
        Return the reverse rule. At this stage, reverse rules can only be
        created for equivalence rules.
        """
        assert (
            self.is_equivalence()
        ), "reverse rule can only be created for equivalence rules"
        return ReverseRule(self)

    def _ensure_level(self, n: int) -> None:
        if self.subterms is None:
            raise RuntimeError("set_subrecs must be set first")
        while n >= len(self.terms_cache):
            terms = self.constructor.get_terms(self.subterms, len(self.terms_cache))
            self.terms_cache.append(terms)

    def get_equation(
        self, get_function: Callable[[CombinatorialClassType], Function]
    ) -> Eq:
        """
        Return the equation for the (ordinary) generating function.
        """
        lhs_func = get_function(self.comb_class)
        rhs_funcs = tuple(get_function(comb_class) for comb_class in self.children)
        return self.constructor.get_equation(lhs_func, rhs_funcs)

    def _ensure_level_objects(self, n: int) -> None:
        if self.subobjects is None:
            raise RuntimeError("set_subrecs must be set first")
        while n >= len(self.objects_cache):
            objects: Objects = defaultdict(list)
            for parameters, subobjects in self.constructor.get_sub_objects(
                self.subobjects, len(self.objects_cache)
            ):
                for sub_objs in product(*subobjects):
                    objects[parameters].extend(self.backward_map(sub_objs))
            self.objects_cache.append(objects)

    def random_sample_object_of_size(
        self, n: int, **parameters: int
    ) -> CombinatorialObjectType:
        assert self.subrecs is not None, "you must call the set_subrecs function first"
        assert (
            self.subsamplers is not None
        ), "you must call the set_subrecs function first"
        total_count = self.count_objects_of_size(n=n, **parameters)
        subobjs = self.constructor.random_sample_sub_objects(
            total_count, self.subsamplers, self.subrecs, n, **parameters
        )
        objs = tuple(self.backward_map(subobjs))
        idx = randint(0, len(objs) - 1)
        return objs[idx]

    def sanity_check(self, n: int) -> bool:
        try:
            return self._sanity_check_count(n) and self._sanity_check_objects(n)
        except SanityCheckFailure as e:
            raise e

    def _sanity_check_count(self, n: int) -> bool:
        """
        Sanity check that the count given by the rule matches the brute force count.
        """
        # pylint: disable=access-member-before-definition
        # pylint: disable=attribute-defined-outside-init
        actual_terms = self.comb_class.get_terms(n)
        temp_subterms = self.subterms
        self.subterms = tuple(child.get_terms for child in self.children)
        rule_terms = self.get_terms(n)
        self.subterms = temp_subterms
        if actual_terms != rule_terms:
            raise SanityCheckFailure(
                f"The following rule failed sanity check:\n"
                f"{self}\n"
                f"Failed for size {n}\n"
                f"The actual count is {actual_terms}.\n"
                f"The rule count is {rule_terms}.",
            )
        return True

    def _sanity_check_objects(self, n: int) -> bool:
        """
        Sanity check that the object given by the rule matches the brute force
        generated objects.
        """
        # pylint: disable=access-member-before-definition
        # pylint: disable=attribute-defined-outside-init
        tempobjects = self.subobjects
        self.subobjects = tuple(child.get_objects for child in self.children)
        try:
            rule_objects = self.get_objects(n)
        except NotImplementedError:
            # Skipping testing rules that have not implemented object generation.
            return True
        self.subobjects = tempobjects
        actual_objects = self.comb_class.get_objects(n)
        for obj_list in chain(rule_objects.values(), actual_objects.values()):
            obj_list.sort()
        if actual_objects != rule_objects:
            raise SanityCheckFailure(
                f"The following rule failed sanity check:\n"
                f"{self}\n"
                f"Failed for size {n}:\n"
                f"The actual objects are {actual_objects}\n"
                f"The rule generated objects {rule_objects}."
            )
        return True


class EquivalenceRule(Rule[CombinatorialClassType, CombinatorialObjectType]):
    def __init__(self, rule: Rule):
        non_empty_children = rule.non_empty_children()
        assert rule.is_equivalence(), "not an equivalence rule: {}".format(str(rule))
        child = non_empty_children[0]
        super().__init__(rule.strategy, rule.comb_class, (child,))
        self.child_idx = rule.children.index(child)
        self.actual_children = rule.children
        self._constructor: Optional[DisjointUnion] = None

    @property
    def constructor(self) -> DisjointUnion:
        """
        Return the constructor, that contains all the information about how to
        count/generate objects from the rule.
        """
        if self._constructor is None:
            original_constructor = cast(
                DisjointUnion,
                self.strategy.constructor(self.comb_class, self.actual_children),
            )
            assert isinstance(original_constructor, DisjointUnion)
            self._constructor = DisjointUnion(
                self.comb_class,
                self.children,
                (original_constructor.extra_parameters[self.child_idx],),
            )
        return self._constructor

    @staticmethod
    def is_equivalence() -> bool:
        return True

    @property
    def formal_step(self) -> str:
        return "{} but only the child at index {} is non-empty".format(
            self.strategy.formal_step(), self.child_idx
        )

    def backward_map(
        self, objs: Tuple[Optional[CombinatorialObjectType], ...]
    ) -> Iterator[CombinatorialObjectType]:
        actual_objs = tuple(
            objs[0] if i == self.child_idx else None
            for i in range(len(self.actual_children))
        )
        yield from self.strategy.backward_map(
            self.comb_class, actual_objs, self.actual_children
        )

    def forward_map(
        self, obj: CombinatorialObjectType
    ) -> Tuple[Optional[CombinatorialObjectType], ...]:
        return (
            self.strategy.forward_map(self.comb_class, obj, self.actual_children)[
                self.child_idx
            ],
        )


class EquivalencePathRule(Rule[CombinatorialClassType, CombinatorialObjectType]):
    """
    A class for shortening a chain of equivalence rules into a single Rule.
    """

    def __init__(self, rules: Sequence[Rule]):
        assert all(rule.is_equivalence() for rule in rules)
        super().__init__(rules[0].strategy, rules[0].comb_class, rules[-1].children)
        self.rules = rules
        self._constructor: Optional[DisjointUnion] = None

    @property
    def constructor(self) -> DisjointUnion:
        if self._constructor is None:
            extra_parameters: Dict[str, str] = {
                k: k for k in self.comb_class.extra_parameters
            }
            for rule in self.rules:
                original_constructor = rule.constructor
                assert isinstance(original_constructor, DisjointUnion)
                rules_parameters = original_constructor.extra_parameters[0]
                extra_parameters = {
                    parent_var: rules_parameters[child_var]
                    for parent_var, child_var in extra_parameters.items()
                    if child_var in rules_parameters
                }
            fixed_values = {
                k: 0
                for k in self.children[0].extra_parameters
                if k not in extra_parameters.values()
            }
            self._constructor = DisjointUnion(
                self.comb_class, self.children, (extra_parameters,), (fixed_values,)
            )
        return self._constructor

    @staticmethod
    def is_equivalence() -> bool:
        return True

    @property
    def formal_step(self) -> str:
        return ", then ".join(rule.formal_step for rule in self.rules)

    def eqv_path_rules(self) -> List[Tuple[CombinatorialClassType, Rule]]:
        """
        Returns the list of (parent, rule) pairs that make up the equivalence
        path.
        """
        eqv_path_rules = []
        curr = self.comb_class
        for rule in self.rules:
            eqv_path_rules.append((curr, rule))
            curr = rule.children[0]
        return eqv_path_rules

    def backward_map(
        self, objs: Tuple[Optional[CombinatorialObjectType], ...]
    ) -> Iterator[CombinatorialObjectType]:
        res = cast(Tuple[CombinatorialObjectType], objs)
        for rule in reversed(self.rules):
            try:
                res = (next(rule.backward_map(res)),)
            except StopIteration:
                return
        yield res[0]

    def forward_map(
        self, obj: CombinatorialObjectType
    ) -> Tuple[Optional[CombinatorialObjectType], ...]:
        res = cast(CombinatorialObjectType, obj)
        for rule in reversed(self.rules):
            res = cast(CombinatorialObjectType, rule.forward_map(res)[0])
        return (res,)

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and [r.strategy for r in self.rules] == [
            r.strategy for r in other.rules
        ]

    def __str__(self) -> str:
        def frontpad(res, height):
            n = max(len(s) for s in res)
            for _ in range(height - len(res)):
                res.append(" " * n)

        def backpad(res):
            n = max(len(s) for s in res)
            for i, s in enumerate(res):
                res[i] = s + " " * (n - len(s))

        def join(res, new):
            backpad(new)
            backpad(res)
            frontpad(res, len(new))
            for i, s in enumerate(new):
                res[i] += s

        res = str(self.comb_class).split("\n")
        backpad(res)
        comb_classes = [str(rule.children[0]).split("\n") for rule in self.rules]
        symbol_height = min(1, len(res) - 1)
        eq_symbol = (
            ["     " for i in range(symbol_height)]
            + ["  {}  ".format("=")]
            + ["     " for i in range(symbol_height)]
        )
        for comb_class in comb_classes:
            join(res, eq_symbol)
            join(res, comb_class)
        return "{}\n".format(self.formal_step) + "\n".join(x for x in res)


class ReverseRule(Rule[CombinatorialClassType, CombinatorialObjectType]):
    """
    A class for creating the reverse of an equivalence rule.
    """

    def __init__(self, rule: Rule):
        assert (
            rule.is_equivalence()
        ), "reversing a rule only works for equivalence rules"
        super().__init__(rule.strategy, rule.children[0], (rule.comb_class,))
        self.original_rule = rule
        self._constructor: Optional[DisjointUnion] = None

    @property
    def constructor(self) -> DisjointUnion:
        if self._constructor is None:
            original_constructor = self.original_rule.constructor
            assert isinstance(original_constructor, DisjointUnion), (
                "reverse rule coming from non disjoint union strategy - "
                "you'll need to update the ReverseRule constructor!"
            )
            flipped_extra_params = {
                b: a for a, b in original_constructor.extra_parameters[0].items()
            }
            fixed_values = {
                k: 0
                for k in self.children[0].extra_parameters
                if k not in flipped_extra_params.values()
            }
            self._constructor = DisjointUnion(
                self.comb_class, self.children, (flipped_extra_params,), (fixed_values,)
            )
        return self._constructor

    @staticmethod
    def is_equivalence() -> bool:
        return True

    @property
    def formal_step(self) -> str:
        return "reverse of '{}'".format(self.strategy.formal_step())

    def backward_map(
        self, objs: Tuple[Optional[CombinatorialObjectType], ...]
    ) -> Iterator[CombinatorialObjectType]:
        yield cast(CombinatorialObjectType, self.original_rule.forward_map(objs[0])[0])

    def forward_map(
        self, obj: CombinatorialObjectType
    ) -> Tuple[Optional[CombinatorialObjectType], ...]:
        return (next(self.original_rule.backward_map((obj,))),)


class VerificationRule(AbstractRule[CombinatorialClassType, CombinatorialObjectType]):
    """
    A class for verification rules. In particular, the children will be an
    empty tuple if it applies, else None.
    """

    def __init__(
        self,
        strat: "VerificationStrategy[CombinatorialClassType,CombinatorialObjectType]",
        comb_class: CombinatorialClassType,
        children: Optional[Tuple[CombinatorialClassType, ...]] = None,
    ):
        assert not children
        super().__init__(strat, comb_class, children)

    @property
    def strategy(
        self,
    ) -> "VerificationStrategy[CombinatorialClassType, CombinatorialObjectType]":
        return cast(
            "VerificationStrategy[CombinatorialClassType, CombinatorialObjectType]",
            super().strategy,
        )

    @staticmethod
    def is_equivalence() -> bool:
        return False

    def _ensure_level(self, n: int) -> None:
        while n >= len(self.terms_cache):
            terms = self.strategy.get_terms(self.comb_class, len(self.terms_cache))
            self.terms_cache.append(terms)

    def _ensure_level_objects(self, n: int) -> None:
        while n >= len(self.objects_cache):
            objects = self.strategy.get_objects(
                self.comb_class, len(self.objects_cache)
            )
            self.objects_cache.append(objects)

    def pack(self) -> "StrategyPack":
        return self.strategy.pack(self.comb_class)

    def get_equation(
        self,
        get_function: Callable[[CombinatorialClassType], Function],
        funcs: Optional[Dict[CombinatorialClassType, Function]] = None,
    ) -> Eq:
        lhs_func = get_function(self.comb_class)
        return Eq(lhs_func, self.strategy.get_genf(self.comb_class, funcs))

    def random_sample_object_of_size(
        self, n: int, **parameters: int
    ) -> CombinatorialObjectType:
        return self.strategy.random_sample_object_of_size(
            self.comb_class, n, **parameters
        )

    def sanity_check(self, n: int) -> bool:
        return self.get_terms(n) == self.comb_class.get_terms(n)
