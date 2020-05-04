"""
The rule class is used for a specific application of a strategy on a tiling.
This is not something the user should implement, as it is just a wrapper for
calling the Strategy class and storing its results.

A CombinatorialSpecification is (more or less) a set of Rule.
"""
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)

from sympy import Eq, Function

from ..combinatorial_class import CombinatorialClass, CombinatorialObject
from ..exception import StrategyDoesNotApply
from .constructor import Constructor

if TYPE_CHECKING:
    from .strategy import Strategy, VerificationStrategy


__all__ = ("Rule", "VerificationRule")


class Rule:
    """
    An instance of Rule is created by the __call__ method of strategy.
    """

    def __init__(
        self,
        strategy: "Strategy",
        comb_class: CombinatorialClass,
        children: Optional[Tuple[CombinatorialClass, ...]] = None,
    ):
        self.comb_class = comb_class
        self.strategy = strategy
        self.count_cache: Dict[Any, int] = {}
        self.obj_cache: Dict[Any, List[CombinatorialObject]] = {}
        self.subrecs: Union[None, Tuple[Callable[..., int], ...]] = None
        self.subgenerators: Union[
            None, Tuple[Callable[..., Iterator[CombinatorialObject]], ...]
        ] = (None)
        self._children = children

    @property
    def ignore_parent(self) -> bool:
        """
        Return True if it is not worth expanding the parent/comb_class if
        this rule is found.
        """
        return self.strategy.ignore_parent

    @property
    def inferrable(self) -> bool:
        """
        Return True if the children could change using inferral strategies.
        """
        return self.strategy.inferrable

    @property
    def possibly_empty(self) -> bool:
        """
        Return True if it is possible that a child is empty.
        """
        return self.strategy.possibly_empty

    @property
    def workable(self) -> bool:
        """
        Return True if the children can expanded using other strategies.
        """
        return self.strategy.workable

    def set_subrecs(self, get_subrule: Callable[[CombinatorialClass], "Rule"]) -> None:
        """
        In general a rule comes in the context of a set of rules, e.g. in a
        CombinatorialSpecification. In order to count, generate, etc using the
        rule we must set the subfunctions that the children refer to.
        """
        self.subrecs = tuple(
            get_subrule(child).count_objects_of_size for child in self.children
        )
        self.subgenerators = tuple(
            get_subrule(child).generate_objects_of_size for child in self.children
        )

    @property
    def children(self) -> Tuple[CombinatorialClass, ...]:
        """
        Return the tuple of CombinatorialClass that are found by applying the
        decomposition function of the strategy to the parent.
        """
        if self._children is None:
            self._children = self.strategy.decomposition_function(self.comb_class)
            if self._children is None:
                raise StrategyDoesNotApply("{} does not apply".format(self.strategy))
        return self._children

    @property
    def constructor(self) -> Constructor:
        """
        Return the constructor, that contains all the information about how to
        count/generate objects from the rule.
        """
        return self.strategy.constructor(self.comb_class, self.children)

    @property
    def formal_step(self) -> str:
        """
        Return a string with a short explanation about the rule.
        """
        return self.strategy.formal_step()

    def non_empty_children(self) -> Tuple[CombinatorialClass, ...]:
        """
        Return the tuple of non-empty combinatorial classes that are found
        by applying the decomposition function.
        """
        return tuple(child for child in self.children if not child.is_empty())

    def backward_map(
        self, objs: Tuple[CombinatorialObject, ...]
    ) -> CombinatorialObject:
        """
        This encodes the backward map of the underlying bijection that the
        strategy implies.
        """
        return self.strategy.backward_map(self.comb_class, objs, self.children)

    def forward_map(self, obj: CombinatorialObject) -> Tuple[CombinatorialObject, ...]:
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
            self.constructor.is_equivalence()
        ), "EquivalenceRule can only be created for equivalence rules"
        return EquivalenceRule(self)

    def to_reverse_rule(self) -> "ReverseRule":
        """
        Return the reverse rule. At this stage, reverse rules can only be
        created for equivalence rules.
        """
        assert (
            len(self.children) == 1 and self.constructor.is_equivalence()
        ), "reverse rule can only be created for equivalence rules"
        return ReverseRule(self)

    def count_objects_of_size(self, n: int, **parameters: int) -> int:
        """
        The function count the objects with respect to the parameters. The
        result is cached.
        """
        key = (("n", n),) + tuple(parameters.items())
        res = self.count_cache.get(key)
        if res is None:
            assert (
                self.subrecs is not None
            ), "you must call the set_subrecs function first"
            res = self.constructor.get_recurrence(self.subrecs, n, **parameters)
            self.count_cache[key] = res
        return res

    def get_equation(
        self, get_function: Callable[[CombinatorialClass], Function]
    ) -> Eq:
        """
        Return the equation for the (ordinary) generating function.
        """
        lhs_func = get_function(self.comb_class)
        rhs_funcs = tuple(get_function(comb_class) for comb_class in self.children)
        return self.constructor.get_equation(lhs_func, rhs_funcs)

    def generate_objects_of_size(
        self, n: int, **parameters: int
    ) -> Iterator[CombinatorialObject]:
        """
        Generate the objects by using the underlying bijection between the
        parent and children.
        """
        key = (("n", n),) + tuple(parameters.items())
        res = self.obj_cache.get(key)
        if res is not None:
            yield from res
            return
        assert (
            self.subgenerators is not None
        ), "you must call the set_subrecs function first"
        res = []
        for subobjs in self.constructor.get_sub_objects(
            self.subgenerators, n, **parameters
        ):
            obj = self.backward_map(subobjs)
            yield obj
            res.append(obj)
        self.obj_cache[key] = res

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.comb_class == other.comb_class
            and self.strategy == other.strategy
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
        if self.children:
            children = [str(child).split("\n") for child in self.children]
            symbol_height = 1
            eq_symbol = (
                ["     " for i in range(symbol_height)]
                + ["  {}  ".format(self.constructor.get_eq_symbol())]
                + ["     " for i in range(symbol_height)]
            )
            join(res, eq_symbol)
            join(res, children[0])
            if len(children) > 1:
                op_symbol = (
                    ["     " for i in range(symbol_height)]
                    + ["  {}  ".format(self.constructor.get_op_symbol())]
                    + ["     " for i in range(symbol_height)]
                )
                for child in children[1:]:
                    join(res, op_symbol)
                    join(res, child)
        return "Explanation: {}\n".format(self.formal_step) + "\n".join(x for x in res)


class EquivalenceRule(Rule):
    def __init__(self, rule: Rule):
        non_empty_children = rule.non_empty_children()
        assert (
            len(non_empty_children) == 1 and rule.constructor.is_equivalence
        ), "not an equivalence rule"
        child = non_empty_children[0]
        super().__init__(rule.strategy, rule.comb_class, (child,))
        self.child_idx = rule.children.index(child)
        self.actual_children = rule.children

    @property
    def constructor(self) -> Constructor:
        return self.strategy.constructor(self.comb_class, self.actual_children)

    @property
    def formal_step(self) -> str:
        return "{} but only the child at index {} is non-empty".format(
            self.strategy.formal_step(), self.child_idx
        )

    def forward_map(self, obj: CombinatorialObject) -> Tuple[CombinatorialObject, ...]:
        return (
            self.strategy.forward_map(self.comb_class, obj, self.actual_children)[
                self.child_idx
            ],
        )


class EquivalencePathRule(Rule):
    """
    A class for shortening a chain of equivalence rules into a single Rule.
    """

    def __init__(self, rules: Sequence[Rule]):
        assert all(
            len(rule.children) == 1 and rule.constructor.is_equivalence()
            for rule in rules
        )
        super().__init__(rules[0].strategy, rules[0].comb_class, rules[-1].children)
        self.rules = rules

    @property
    def constructor(self) -> Constructor:
        return self.strategy.constructor(self.comb_class, self.children)

    @property
    def formal_step(self) -> str:
        return ", then ".join(rule.formal_step for rule in self.rules)

    def eqv_path_rules(self) -> List[Tuple[CombinatorialClass, Rule]]:
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
        self, objs: Tuple[CombinatorialObject, ...]
    ) -> CombinatorialObject:
        res = objs
        for rule in reversed(self.rules):
            res = (rule.backward_map(res),)
        return res[0]

    def forward_map(self, obj: CombinatorialObject) -> Tuple[CombinatorialObject, ...]:
        res = obj
        for rule in reversed(self.rules):
            res = rule.forward_map(res)[0]
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
        symbol_height = 1
        eq_symbol = (
            ["     " for i in range(symbol_height)]
            + ["  {}  ".format("=")]
            + ["     " for i in range(symbol_height)]
        )
        for comb_class in comb_classes:
            join(res, eq_symbol)
            join(res, comb_class)
        return "Explanation: {}\n".format(self.formal_step) + "\n".join(x for x in res)


class ReverseRule(Rule):
    """
    A class for creating the reverse of an equivalence rule.
    """

    def __init__(self, rule: Rule):
        assert (
            len(rule.children) == 1 and rule.constructor.is_equivalence
        ), "reversing a rule only works for equivalence rules"
        super().__init__(rule.strategy, rule.children[0], (rule.comb_class,))

    @property
    def constructor(self) -> Constructor:
        return self.strategy.constructor(self.comb_class, self.children)

    @property
    def formal_step(self) -> str:
        return "reverse of '{}'".format(self.strategy.formal_step())

    def backward_map(
        self, objs: Tuple[CombinatorialObject, ...]
    ) -> CombinatorialObject:
        return self.strategy.forward_map(self.children[0], objs[0], (self.comb_class,))[
            0
        ]

    def forward_map(self, obj: CombinatorialObject) -> Tuple[CombinatorialObject, ...]:
        return (
            self.strategy.backward_map(self.children[0], (obj,), (self.comb_class,)),
        )


class VerificationRule(Rule):
    """
    A class for verification rules. In particular, the children will be an
    empty tuple if it applies, else None.
    """

    def __init__(
        self,
        strategy: "VerificationStrategy",
        comb_class: CombinatorialClass,
        children: Optional[Tuple[CombinatorialClass, ...]] = None,
    ):
        super().__init__(strategy, comb_class, children)  # type: ignore
        self.strategy: "VerificationStrategy"  # type: ignore

    def count_objects_of_size(self, n: int, **parameters: int) -> int:
        key = (("n", n),) + tuple(parameters.items())
        res = self.count_cache.get(key)
        if res is None:
            res = self.strategy.count_objects_of_size(self.comb_class, n, **parameters)
            self.count_cache[key] = res
        return res

    def get_equation(
        self, get_function: Callable[[CombinatorialClass], Function]
    ) -> Eq:
        lhs_func = get_function(self.comb_class)
        return Eq(lhs_func, self.strategy.get_genf(self.comb_class))

    def generate_objects_of_size(
        self, n: int, **parameters: int
    ) -> Iterator[CombinatorialObject]:
        key = (("n", n),) + tuple(parameters.items())
        res = self.obj_cache.get(key)
        if res is not None:
            yield from res
            return
        res = []
        for obj in self.strategy.generate_objects_of_size(
            self.comb_class, n, **parameters
        ):
            yield obj
            res.append(obj)
        self.obj_cache[key] = res
