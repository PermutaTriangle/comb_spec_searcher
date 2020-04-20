from functools import reduce
from itertools import chain, product
from operator import add, mul
from typing import Any, Callable, Iterable, Iterator, Tuple
import abc

from sympy import Eq, Function

from ..combinatorial_class import CombinatorialClass, CombinatorialObject


__all__ = ("Constructor", "CartesianProduct", "DisjointUnion")


RelianceProfile = Tuple[Tuple[int, ...], ...]


class Constructor(abc.ABC):
    """The constructor is akin to the 'counting function' in the comb exp paper."""

    @abc.abstractmethod
    def is_equivalence(self):
        """Return true if the constructor is the same as "=". This should only
        happen if there is 1 child."""

    @abc.abstractmethod
    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        """Return the sympy.Eq in the form lhs_func = f(rhs_funcs).
        TODO: remove lhs_func dependency"""

    @abc.abstractmethod
    def reliance_profile(self, **parameters: int) -> RelianceProfile:
        """Return the reliance profile. That is for the parameters given,
        which parameters of each individual subclass are required."""

    @abc.abstractmethod
    def get_recurrence(
        self, subrecs: Callable[[Any], int], **lhs_parameters: int
    ) -> int:
        """Return the count for the given parameters, assuming the children are
        counted by the subrecs given."""

    @abc.abstractmethod
    def get_sub_objects(
        self, subgens: Callable[[int], CombinatorialObject], size: int
    ) -> Iterator[Tuple[CombinatorialObject, ...]]:
        """Return the subobjs/image of the bijection implied by the constructor."""


class CartesianProduct(Constructor):
    def __init__(self, children: Iterable[CombinatorialClass]):
        number_of_positive = sum(
            1 for comb_class in children if comb_class.is_positive()
        )
        self._reliance_profile_functions = tuple(
            (lambda n: tuple(range(1, min(2, n - number_of_positive + 2))))
            if child.is_atom()
            else (lambda n: tuple(range(1, n - number_of_positive + 2)))
            if child.is_positive()
            else (lambda n: tuple(range(0, n - number_of_positive + 1)))
            for child in children
        )

    def is_equivalence(self):
        return len(self._reliance_profile_functions) == 1

    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        return Eq(lhs_func, reduce(mul, rhs_funcs, 1))

    def reliance_profile(self, n: int):
        # TODO: implement in multiple variables
        return tuple(f(n) for f in self._reliance_profile_functions)

    def _valid_compositions(self, n: int):
        # TODO: be smarter!
        reliance_profile = self.reliance_profile(n)
        if all(reliance_profile):
            minmax = tuple((min(p), max(p)) for p in reliance_profile)

            def _helper(n, minmax):
                if len(minmax) == 1:
                    minval, maxval = minmax[0]
                    if minval <= n <= maxval:
                        yield (n,)
                    return
                still_to_come = sum(x for x, _ in minmax[1:])
                max_available = sum(y for _, y in minmax[1:])
                minval, maxval = minmax[0]
                minval = max(minval, n - max_available)
                maxval = min(maxval, n - still_to_come)
                for val in range(minval, maxval + 1):
                    for comp in _helper(n - val, minmax[1:]):
                        yield (val,) + comp

            yield from _helper(n, minmax)

    def get_recurrence(self, subrecs: Tuple[Callable[[Any], int]], n: int) -> int:
        res = 0
        for comp in self._valid_compositions(n):
            tmp = 1
            for i, rec in enumerate(subrecs):
                tmp *= rec(n=comp[i])
                if tmp == 0:
                    break
            res += tmp
        return res

    def get_sub_objects(
        self, subgens: Callable[[int], CombinatorialObject], n: int
    ) -> Iterator[Tuple[CombinatorialObject, ...]]:
        for comp in self._valid_compositions(n):
            yield from map(
                tuple, product(*tuple(subgen(n=i) for i, subgen in zip(comp, subgens))),
            )


class DisjointUnion(Constructor):
    def __init__(self, children: Tuple[CombinatorialClass, ...]):
        self.number_of_children = len(children)

    def is_equivalence(self):
        return self.number_of_children == 1

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
        self, subgens: Callable[[int], CombinatorialObject], n: int
    ) -> Iterator[Tuple[CombinatorialObject, ...]]:
        for gp in chain.from_iterable(subgen(n=n) for subgen in subgens):
            yield (gp,)
