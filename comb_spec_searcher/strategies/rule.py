from typing import Callable, Dict, Iterable, Tuple
from ..combinatorial_class import CombinatorialClass, CombinatorialObject
from .constructor import Constructor
import abc


__all__ = "Rule"


class Rule(abc.ABC):
    """
    The rule method is essentially following the mantra of 'strategy' from the
    combinatorial explanation paper.
    (https://permutatriangle.github.io/papers/2019-02-27-combex.html)

    Having it as a class will give us more flexibility making it easier to
    implement sampling, object generation and future projects we've not
    thought of yet. It will also allow us to port over the code from Unnar's
    thesis in a more user-friendly manner.
    """

    def __call__(self, comb_class: CombinatorialClass) -> "SpecificRule":
        return SpecificRule(self, comb_class)

    def ignore_parent(self) -> bool:
        return True

    def inferable(self) -> bool:
        return True

    def possibly_empty(self) -> bool:
        return True

    def workable(self) -> bool:
        return True

    @abc.abstractmethod
    def children(self, comb_class: CombinatorialClass):
        """This is the 'decomposition function'."""

    @abc.abstractmethod
    def constructor(self, comb_class: CombinatorialClass) -> Constructor:
        """This is where the details of the 'reliance profile' and 'counting' functions are hidden."""

    @abc.abstractmethod
    def formal_step(self) -> str:
        pass

    # The maps that follow are the show the underlying bijections, and need to
    # be implemented for every strategy individually.

    @abc.abstractmethod
    def backward_map(
        self,
        comb_class: CombinatorialClass,
        *objs: Tuple[Tuple[CombinatorialObject, CombinatorialClass], ...]
    ) -> CombinatorialObject:
        """This method will enable us to generate objects, and sample. """

    @abc.abstractmethod
    def forward_map(
        self, comb_class: CombinatorialClass, obj: CombinatorialObject
    ) -> Tuple[Tuple[CombinatorialObject, CombinatorialClass], ...]:
        """This function will enable us to have a quick membership test."""


class SpecificRule:
    def __init__(self, rule: Rule, comb_class: CombinatorialClass):
        self.comb_class = comb_class
        self.rule = rule
        self.count_cache = {}
        self.subrecs = None

    def ignore_parent(self) -> bool:
        return self.rule.ignore_parent()

    def inferable(self) -> bool:
        return self.rule.inferable()

    def possibly_empty(self) -> bool:
        return self.rule.possibly_empty()

    def workable(self) -> bool:
        return self.rule.workable()

    def set_subrecs(self, get_subrule: Callable[[CombinatorialClass], "SpecificRule"]):
        self.subrecs = tuple(
            get_subrule(child).count_objects_of_size for child in self.children()
        )

    def children(self) -> Tuple[CombinatorialClass, ...]:
        return self.rule.children(self.comb_class)

    def constructor(self) -> Constructor:
        return self.rule.constructor(self.comb_class)

    def formal_step(self) -> str:
        return self.rule.formal_step()

    def backward_map(
        self, *objs: Tuple[Tuple[CombinatorialObject, CombinatorialClass], ...]
    ) -> CombinatorialObject:
        return self.rule.backward_map(self.comb_class, *objs)

    def forward_map(
        self, obj: CombinatorialObject
    ) -> Tuple[Tuple[CombinatorialObject, CombinatorialClass], ...]:
        return self.rule.forward_map(self.comb_class, obj)

    def count_objects_of_size(self, **parameters):
        key = tuple(parameters.items())
        res = self.count_cache.get(key)
        if res is None:
            assert self.set_subrecs is not None
            res = self.constructor().get_recurrence(self.subrecs, **parameters)
            self.count_cache[key] = res
        return res
