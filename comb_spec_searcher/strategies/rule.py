from typing import Callable, Iterator, Optional, Tuple, TYPE_CHECKING
from sympy import Eq, Function
from .constructor import Constructor
from ..combinatorial_class import CombinatorialClass, CombinatorialObject

__all__ = ("EmptyRule", "Rule", "VerificationRule")

if TYPE_CHECKING:
    from .strategy import Strategy


class Rule:
    def __init__(
        self,
        strategy: "Strategy",
        comb_class: CombinatorialClass,
        children: Optional[Tuple[CombinatorialClass, ...]] = None,
    ):
        self.comb_class = comb_class
        self.strategy = strategy
        self.count_cache = {}
        self.obj_cache = {}
        self.subrecs = None
        self._children = children

    @property
    def ignore_parent(self) -> bool:
        return self.strategy.ignore_parent

    @property
    def inferrable(self) -> bool:
        return self.strategy.inferrable

    @property
    def possibly_empty(self) -> bool:
        return self.strategy.possibly_empty

    @property
    def workable(self) -> bool:
        return self.strategy.workable

    def set_subrecs(self, get_subrule: Callable[[CombinatorialClass], "SpecificRule"]):
        self.subrecs = tuple(
            get_subrule(child).count_objects_of_size for child in self.children
        )
        self.subgenerators = tuple(
            get_subrule(child).generate_objects_of_size for child in self.children
        )

    @property
    def children(self) -> Tuple[CombinatorialClass, ...]:
        if self._children is None:
            self._children = self.strategy.decomposition_function(self.comb_class)
        return self._children

    @property
    def constructor(self) -> Constructor:
        return self.strategy.constructor(self.comb_class, self.children)

    @property
    def formal_step(self) -> str:
        return self.strategy.formal_step()

    def backward_map(
        self, objs: Tuple[CombinatorialObject, ...]
    ) -> CombinatorialObject:
        return self.strategy.backward_map(self.comb_class, objs, self.children)

    def to_reverse_rule(self) -> "ReverseRule":
        return ReverseRule(self)

    def forward_map(
        self, obj: CombinatorialObject
    ) -> Tuple[Tuple[CombinatorialObject, CombinatorialClass], ...]:
        return self.strategy.forward_map(self.comb_class, obj, self.children)

    def count_objects_of_size(self, **parameters):
        key = tuple(parameters.items())
        res = self.count_cache.get(key)
        if res is None:
            assert self.set_subrecs is not None
            res = self.constructor.get_recurrence(self.subrecs, **parameters)
            self.count_cache[key] = res
        return res

    def get_equation(
        self, get_function: Callable[[CombinatorialClass], Function]
    ) -> Eq:
        lhs_func = get_function(self.comb_class)
        rhs_funcs = [get_function(comb_class) for comb_class in self.children]
        return self.constructor.get_equation(lhs_func, rhs_funcs)

    def generate_objects_of_size(
        self, **parameters
    ) -> Iterator[Tuple[Tuple[CombinatorialObject, CombinatorialClass], ...]]:
        key = tuple(parameters.items())
        res = self.obj_cache.get(key)
        if res is not None:
            yield from res
            return
        res = []
        for subobjs in self.constructor.get_sub_objects(
            self.subgenerators, **parameters
        ):
            obj = self.backward_map(subobjs)
            yield obj
            res.append(obj)
        self.obj_cache[key] = tuple(res)

    def __eq__(self, other):
        return (
            type(self) == type(other)
            and self.comb_class == other.comb_class
            and self.strategy == other.strategy
        )

    def __str__(self):
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


class EquivalencePathRule(Rule):
    def __init__(self, rules):
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

    def eqv_path_rules(self):
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

    def forward_map(
        self, obj: CombinatorialObject
    ) -> Tuple[Tuple[CombinatorialObject, CombinatorialClass], ...]:
        res = obj
        for rule in reversed(self.rules):
            res = rule.backward_map(res)[0]
        return res

    def __eq__(self, other):
        return super().__eq__(other) and [r.strategy for r in self.rules] == [
            r.strategy for r in other.rules
        ]

    def __str__(self):
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
    def __init__(self, rule):
        assert (
            len(rule.children) == 1
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
        return self.strategy.forward_map(self.children[0], objs[0], (self.comb_class,))

    def forward_map(self, obj: CombinatorialObject) -> Tuple[CombinatorialObject, ...]:
        return self.strategy.backward_map(self.children[0], (obj,), (self.comb_class,))


class VerificationRule(Rule):
    def count_objects_of_size(self, **parameters):
        key = tuple(parameters.items())
        res = self.count_cache.get(key)
        if res is None:
            res = self.strategy.count_objects_of_size(self.comb_class, **parameters)
            self.count_cache[key] = res
        return res

    def get_equation(
        self, get_function: Callable[[CombinatorialClass], Function]
    ) -> Eq:
        lhs_func = get_function(self.comb_class)
        return self.strategy.get_equation(self.comb_class, lhs_func)

    def generate_objects_of_size(self, **parameters):
        key = tuple(parameters.items())
        res = self.obj_cache.get(key)
        if res is not None:
            yield from res
            return
        res = []
        for obj in self.strategy.generate_objects_of_size(
            self.comb_class, **parameters
        ):
            yield obj
            res.append(obj)
        self.obj_cache[key] = tuple(res)
