from typing import Callable, Iterator, Optional, Tuple, TYPE_CHECKING
from .constructor import Constructor
from ..combinatorial_class import CombinatorialClass, CombinatorialObject

__all__ = "Rule"

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

    def forward_map(
        self, obj: CombinatorialObject
    ) -> Tuple[Tuple[CombinatorialObject, CombinatorialClass], ...]:
        return self.strategy.forward_map(self.comb_class, obj, self.children)

    def count_objects_of_size(self, **parameters):
        key = tuple(parameters.items())
        res = self.count_cache.get(key)
        if res is None:
            assert self.set_subrecs is not None
            res = self.constructor().get_recurrence(self.subrecs, **parameters)
            self.count_cache[key] = res
        return res

    def generate_objects_of_size(
        self, **parameters
    ) -> Iterator[Tuple[Tuple[CombinatorialObject, CombinatorialClass], ...]]:
        key = tuple(parameters.items())
        res = self.obj_cache.get(key)
        if res is not None:
            yield from res
            return
        res = []
        for subobjs in self.constructor().get_sub_objects(
            self.subgenerators, **parameters
        ):
            obj = self.backward_map(subobjs)
            yield obj
            res.append(obj)
        self.obj_cache[key] = tuple(res)
