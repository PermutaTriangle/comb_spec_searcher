"""
The rule class is used for a specific application of a strategy on a combinatorial
class. This is not something the user should implement, as it is just a wrapper for
calling the Strategy class and storing its results.

A CombinatorialSpecification is (more or less) a set of Rule.
"""
import abc
import random
from collections import defaultdict
from importlib import import_module
from itertools import chain, product
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
    Type,
    Union,
    cast,
)

from sympy import Eq, Function

from comb_spec_searcher.combinatorial_class import CombinatorialClass
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
from .constructor import Complement, Constructor, DisjointUnion

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
        self.subsamplers: Optional[
            Tuple[Callable[..., CombinatorialObjectType], ...]
        ] = None
        self.subterms: Optional[SubTerms] = None
        self.subobjects: Optional[SubObjects] = None
        self._children = children
        self._non_empty_children: Optional[Tuple[CombinatorialClassType, ...]] = None

    def to_jsonable(self) -> dict:
        d = {
            "class_module": self.__class__.__module__,
            "rule_class": self.__class__.__name__,
        }
        return d

    @classmethod
    @abc.abstractmethod
    def from_dict(cls, d: dict) -> "AbstractRule":
        module = import_module(d.pop("class_module"))
        RuleClass: Type["AbstractRule"] = getattr(module, d.pop("rule_class"))
        if not issubclass(RuleClass, AbstractRule):
            raise ValueError("Not a valid rule class")
        return RuleClass.from_dict(d)

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

    def is_two_way(self) -> bool:
        """
        Returns True if it is a two way rule.
        """
        return self.strategy.is_two_way(self.comb_class)

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

    def get_eq_symbol(self):
        return self.strategy.get_eq_symbol()

    def get_op_symbol(self):
        return self.strategy.get_op_symbol()

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
                + ["  {}  ".format(self.get_eq_symbol())]
                + ["     " for i in range(symbol_height)]
            )
            join(res, eq_symbol)
            join(res, children[0])
            if len(children) > 1:
                op_symbol = (
                    ["     " for i in range(symbol_height)]
                    + ["  {}  ".format(self.get_op_symbol())]
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

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d["comb_class"] = self.comb_class.to_jsonable()
        d["children"] = [child.to_jsonable() for child in self.children]
        d["strategy"] = self.strategy.to_jsonable()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Rule":
        # pylint: disable=import-outside-toplevel
        from comb_spec_searcher.strategies.strategy import AbstractStrategy, Strategy

        strategy = AbstractStrategy.from_dict(d.pop("strategy"))
        assert isinstance(strategy, Strategy)
        comb_class = CombinatorialClass.from_dict(d.pop("comb_class"))
        comb_class = cast(CombinatorialClassType, comb_class)
        d.pop("children")
        assert not d
        return cls(strategy, comb_class)

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
        return (
            isinstance(self.constructor, (DisjointUnion, Complement))
            and len(self.non_empty_children()) == 1
        )

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

    def to_reverse_rule(self, idx: int) -> "Rule":
        """
        Return the reverse rule. At this stage, reverse rules can only be
        created for equivalence rules.
        """
        return ReverseRule(self, idx)

    def _ensure_level(self, n: int) -> None:
        if self.subterms is None:
            raise RuntimeError("set_subrecs must be set first")
        while n >= len(self.terms_cache):
            terms = self.constructor.get_terms(
                self.get_terms, self.subterms, len(self.terms_cache)
            )
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
        return random.choice(objs)

    def sanity_check(self, n: int) -> bool:
        try:
            return (
                self._sanity_check_count(n)
                and self._sanity_check_objects(n)
                and self._sanity_check_random_sample(n)
            )
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

    def _sanity_check_random_sample(self, n: int) -> bool:
        # pylint: disable=access-member-before-definition
        # pylint: disable=attribute-defined-outside-init
        actual_objects = self.comb_class.get_objects(n)
        possible_parameters = [
            (dict(zip(self.comb_class.extra_parameters, param)), param)
            for param in actual_objects
        ]
        if not possible_parameters:
            return True

        def fake_subsampler(
            comb_class: CombinatorialClassType,
        ) -> Callable[..., CombinatorialObjectType]:
            objs_cache: Dict[int, Objects] = {}

            def sampler(n: int, **parameters: int) -> CombinatorialObjectType:
                if n not in objs_cache:
                    objs_cache[n] = comb_class.get_objects(n)
                objs = objs_cache[n]
                param_tuple = tuple(parameters[p] for p in comb_class.extra_parameters)
                return cast(CombinatorialObjectType, random.choice(objs[param_tuple]))

            return sampler

        def fake_subrec(comb_class: CombinatorialClassType) -> Callable[..., int]:
            terms_cache: Dict[int, Terms] = {}

            def subrec(n: int, **parameters: int) -> int:
                if n not in terms_cache:
                    terms_cache[n] = comb_class.get_terms(n)
                terms = terms_cache[n]
                param_tuple = tuple(parameters[p] for p in comb_class.extra_parameters)
                return terms[param_tuple]

            return subrec

        tmpsamplers = self.subsamplers
        tmpsubrec = self.subrecs
        tmpsubterms = self.subterms
        self.subsamplers = tuple(fake_subsampler(child) for child in self.children)
        self.subrecs = tuple(fake_subrec(child) for child in self.children)
        self.subterms = tuple(child.get_terms for child in self.children)
        try:
            self.random_sample_object_of_size(n, **possible_parameters[0][0])
        except NotImplementedError:
            # Skipping testing rules that have not implemented random_sampling.
            self.subsamplers = tmpsamplers
            self.subrecs = tmpsubrec
            self.subterms = tmpsubterms
            return True

        for paramd, paramt in possible_parameters:
            obj = self.random_sample_object_of_size(n, **paramd)
            if obj not in actual_objects[paramt]:
                self.subsamplers = tmpsamplers
                self.subrecs = tmpsubrec
                self.subterms = tmpsubterms
                raise SanityCheckFailure(
                    f"The following rule failed sanity check:\n"
                    f"{self}\n"
                    f"Failed for size {n}:\n"
                    f"Sampled the object {obj} for the parameters {paramd}\n"
                )
        self.subsamplers = tmpsamplers
        self.subrecs = tmpsubrec
        self.subterms = tmpsubterms
        return True


class EquivalenceRule(Rule[CombinatorialClassType, CombinatorialObjectType]):
    def __init__(self, rule: Rule[CombinatorialClassType, CombinatorialObjectType]):
        non_empty_children = rule.non_empty_children()
        assert rule.is_equivalence(), "not an equivalence rule: {}".format(str(rule))
        child = non_empty_children[0]
        super().__init__(rule.strategy, rule.comb_class, (child,))
        self.child_idx = rule.children.index(child)
        self.actual_children = rule.children
        self.original_rule = rule
        self._constructor: Optional[Union[DisjointUnion, Complement]] = None

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d.pop("comb_class")
        d.pop("strategy")
        d.pop("children")
        d["original_rule"] = self.original_rule.to_jsonable()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "EquivalenceRule":
        rule = AbstractRule.from_dict(d.pop("original_rule"))
        assert isinstance(rule, Rule)
        assert not d, d.keys()
        return cls(rule)

    @property
    def constructor(self) -> Union[DisjointUnion, Complement]:
        """
        Return the constructor, that contains all the information about how to
        count/generate objects from the rule.
        """
        if self._constructor is None:
            original_constructor = self.original_rule.constructor
            if isinstance(original_constructor, DisjointUnion):
                self._constructor = DisjointUnion(
                    self.comb_class,
                    self.children,
                    (original_constructor.extra_parameters[self.child_idx],),
                )
            elif isinstance(original_constructor, Complement):
                assert isinstance(self.original_rule, ReverseRule)
                original_original_rule = self.original_rule.original_rule
                original_original_child_idx = (
                    original_original_rule.to_equivalence_rule().child_idx
                )
                original_original_constructor = original_original_rule.constructor
                assert isinstance(original_original_constructor, DisjointUnion)
                self._constructor = Complement(
                    self.children[0],
                    (self.comb_class,),
                    0,
                    (
                        original_original_constructor.extra_parameters[
                            original_original_child_idx
                        ],
                    ),
                )
            else:
                raise NotImplementedError
        return self._constructor

    @staticmethod
    def is_equivalence() -> bool:
        return True

    def to_reverse_rule(self, idx: int) -> "EquivalenceRule":
        assert idx == 0
        return self.original_rule.to_reverse_rule(self.child_idx).to_equivalence_rule()

    def to_equivalence_rule(self) -> "EquivalenceRule":
        raise NotImplementedError("You don't want to do that! I promise")

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
        yield from self.original_rule.backward_map(actual_objs)

    def forward_map(
        self, obj: CombinatorialObjectType
    ) -> Tuple[Optional[CombinatorialObjectType], ...]:
        return (self.original_rule.forward_map(obj)[self.child_idx],)


class EquivalencePathRule(Rule[CombinatorialClassType, CombinatorialObjectType]):
    """
    A class for shortening a chain of disjoint union  or complement unary rules into a
    single Rule.
    """

    def __init__(
        self, rules: Sequence[Rule[CombinatorialClassType, CombinatorialObjectType]]
    ):
        assert all(rule.is_equivalence() for rule in rules)
        assert all(len(rule.children) == 1 for rule in rules)
        super().__init__(rules[0].strategy, rules[0].comb_class, rules[-1].children)
        self.rules = tuple(rules)
        self._constructor: Optional[DisjointUnion] = None

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d.pop("comb_class")
        d.pop("strategy")
        d.pop("children")
        d["rules"] = [r.to_jsonable() for r in self.rules]
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "EquivalencePathRule":
        rules: List[Rule] = []
        for rule_dict in d.pop("rules"):
            rule = AbstractRule.from_dict(rule_dict)
            assert isinstance(rule, Rule)
            rules.append(rule)
        assert not d
        return cls(rules)

    @property
    def constructor(self) -> DisjointUnion:
        if self._constructor is None:
            extra_parameters: Dict[str, str] = {
                k: k for k in self.comb_class.extra_parameters
            }
            for rule in self.rules:
                original_constructor = rule.constructor
                assert isinstance(original_constructor, (DisjointUnion, Complement))
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

    def to_equivalence_rule(self) -> "EquivalenceRule":
        raise NotImplementedError("You don't want to do that! I promise")

    def to_reverse_rule(self, idx: int) -> "Rule":
        raise NotImplementedError("You don't want to do that! I promise")

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
        for rule in self.rules:
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
    A class for creating a reverse equivalence rule.
    """

    def __init__(
        self, rule: Rule[CombinatorialClassType, CombinatorialObjectType], idx: int
    ):
        assert rule.is_two_way()
        super().__init__(
            rule.strategy,
            rule.children[idx],
            (rule.comb_class, *rule.children[:idx], *rule.children[idx + 1 :]),
        )
        self.original_rule = rule
        self.idx = idx  # the idx of the child to be counted.
        self._constructor: Optional[Constructor] = None

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d.pop("comb_class")
        d.pop("strategy")
        d.pop("children")
        d["original_rule"] = self.original_rule.to_jsonable()
        d["idx"] = self.idx
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "ReverseRule":
        rule = AbstractRule.from_dict(d.pop("original_rule"))
        assert isinstance(rule, Rule)
        idx = d.pop("idx")
        assert not d
        return cls(rule, idx)

    def to_reverse_rule(self, idx: int) -> "Rule":
        raise NotImplementedError("You don't want to do that! I promise")

    def get_equation(
        self, get_function: Callable[[CombinatorialClassType], Function]
    ) -> Eq:
        try:
            return super().get_equation(get_function)
        except NotImplementedError:
            return self.original_rule.get_equation(get_function)

    @property
    def constructor(
        self,
    ) -> Constructor:
        if self._constructor is None:
            self._constructor = self.strategy.reverse_constructor(
                self.idx,
                self.original_rule.comb_class,
                self.original_rule.children,
            )
        return self._constructor

    @property
    def formal_step(self) -> str:
        if len(self.children) == 1:
            return "reverse of '{}'".format(self.strategy.formal_step())
        return f"reverse of '{self.strategy.formal_step()}', counting child {self.idx}"

    def backward_map(
        self, objs: Tuple[Optional[CombinatorialObjectType], ...]
    ) -> Iterator[CombinatorialObjectType]:
        if not len(self.original_rule.non_empty_children()) == 1:
            raise NotImplementedError("Cannot map forward for non equivalence rule.")
        assert all(obj is None for obj in objs[1:])
        assert objs[0] is not None
        res = self.original_rule.forward_map(objs[0])[self.idx]
        assert res is not None
        yield res

    def forward_map(
        self, obj: CombinatorialObjectType
    ) -> Tuple[Optional[CombinatorialObjectType], ...]:
        if not len(self.original_rule.non_empty_children()) == 1:
            raise NotImplementedError("Cannot map forward for non equivalence rule.")
        objs: List[Optional[CombinatorialObjectType]] = [
            None for _ in self.original_rule.children
        ]
        objs[self.idx] = obj
        orig_res = list(self.original_rule.backward_map(tuple(objs)))
        assert len(orig_res) == 1, "More than one results from back map"
        return tuple(orig_res) + tuple(None for _ in range(len(self.children) - 1))

    def get_op_symbol(self):
        return self.strategy.get_reverse_op_symbol()


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

    def to_jsonable(self) -> dict:
        d = super().to_jsonable()
        d["comb_class"] = self.comb_class.to_jsonable()
        d["strategy"] = self.strategy.to_jsonable()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "VerificationRule":
        # pylint: disable=import-outside-toplevel
        from comb_spec_searcher.strategies.strategy import (
            AbstractStrategy,
            VerificationStrategy,
        )

        strategy = AbstractStrategy.from_dict(d.pop("strategy"))
        assert isinstance(strategy, VerificationStrategy)
        comb_class = CombinatorialClass.from_dict(d.pop("comb_class"))
        comb_class = cast(CombinatorialClassType, comb_class)
        assert not d
        return cls(strategy, comb_class)

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

    # pylint: disable=arguments-differ
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
