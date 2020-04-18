from functools import reduce
from itertools import chain, product
from operator import add, mul
from typing import Any, Callable, Iterable, Iterator, Tuple

from sympy import Eq, Function

from .combinatorial_class import CombinatorialClass, CombinatorialObject
from .utils import compositions

import abc


__all__ = ["Constructor", "Cartesian", "DisjointUnion", "Empty", "Point"]


RelianceProfile = Tuple[Tuple[int, ...], ...]

class Constructor(abc.ABC):
    """The constructor is akin to the 'counting function' in the comb exp paper."""

    @abc.abstractmethod
    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        pass

    @abc.abstractmethod
    def reliance_profile(self, **parameters: int) -> RelianceProfile:
        pass

    @abc.abstractmethod
    def get_recurrence(
        self, subrecs: Callable[[Any], int], **lhs_parameters: int
    ) -> int:
        pass

    @abc.abstractmethod
    def get_sub_objects(
        self, subgens: Callable[[int], CombinatorialObject], size: int
    ) -> Iterator[Tuple[CombinatorialObject, ...]]:
        pass


class CartesianProduct(Constructor):
    def __init__(self, children: Iterable[CombinatorialClass]):
        number_of_positive = sum(1 for comb_class in children if comb_class.is_positive())
        self._reliance_profile_functions = tuple(
            (lambda n: tuple(range(1, min(2, n - number_of_positive + 2))))
            if child.is_atom() else (lambda n: tuple(range(1, n - number_of_positive + 2)))
            if child.is_positive() else (lambda n: tuple(range(0, n - number_of_positive + 1)))
            for child in children)


    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        return Eq(lhs_func, reduce(mul, rhs_funcs, 1))

    def reliance_profile(self, n: int):
        # TODO: implement in multiple variables
        return tuple(f(n) for f in self._reliance_profile_functions)

    def _valid_compositions(self, n: int):
        # TODO: be smarter!
        return [comp for comp in product(*self.reliance_profile(n)) if sum(comp) == n]

    def get_recurrence(self, subrecs: Tuple[Callable[[Any], int]], n: int) -> int:
        res = 0
        for comp in self._valid_compositions(n):
            print(comp)
            tmp = 1
            for i, rec in enumerate(subrecs):
                tmp *= rec(n=comp[i])
                if tmp == 0:
                    break
            res += tmp
        return res

    def get_sub_objects(
        self, subgens: Callable[[int], CombinatorialObject], size: int
    ) -> Iterator[Tuple[CombinatorialObject, ...]]:
        for comp in self._valid_compositions(size):
            yield from map(
                tuple,
                product(
                    *tuple(
                        subgen(i) for i, subgen in zip(comp, subgens)
                    )
                ),
            )


class DisjointUnion(Constructor):
    def __init__(self, children: CombinatorialClass):
        self.number_of_children = len(children)

    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        return Eq(lhs_func, reduce(add, rhs_funcs, 0))

    def reliance_profile(self, n: int) -> RelianceProfile:
        # TODO: implement in multiple variables
        return tuple((n,) for _ in range(self.number_of_children))

    def get_recurrence(
        self, subrecs: Callable[[Any], int], **lhs_parameters: Any
    ) -> int:
        return sum(rec(**lhs_parameters) for rec in subrecs)

    def get_sub_objects(
        self, subgens: Callable[[int], CombinatorialObject], size: int
    ) -> Iterator[Tuple[CombinatorialObject, ...]]:
        for gp in chain.from_iterable(subgen(size) for subgen in subgens):
            yield (gp,)
