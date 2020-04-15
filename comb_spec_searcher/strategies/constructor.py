from functools import reduce
from operator import add, mul
from typing import Any, Callable, Tuple

from sympy import Eq, Function
import sympy

from comb_spec_searcher.utils import compositions

import abc


__all__ = ["Constructor", "Cartesian", "DisjointUnion", "Empty", "Point"]


# TODO: remove the get_subrule quirk from the constructor class


class Constructor(abc.ABC):
    """The constructor is akin to the 'counting function' in the comb exp paper."""

    @abc.abstractmethod
    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        pass

    @abc.abstractmethod
    def get_recurrence(
        self,
        subrecs: Callable[[Any], int],
        get_subrule: Callable,
        **lhs_parameters: Any
    ) -> int:
        pass


class CartesianProduct(Constructor):
    def __init__(self, children):
        # Number of children that are just the atom
        self.index_of_atoms = set()
        for i, child in enumerate(children):
            if child.is_atom():
                self.index_of_atoms.add(i)
        non_point_children = [
            child for i, child in enumerate(children) if i not in self.index_of_atoms
        ]
        # index of positive children after removing atoms
        self.indices_pos_children = set(
            i for i, child in enumerate(non_point_children) if child.is_positive()
        )

    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        return Eq(lhs_func, reduce(mul, rhs_funcs, 1))

    def get_recurrence(self, subrecs: Callable[[Any], int], get_subrule, n: int) -> int:
        atoms = len(self.index_of_atoms)
        subrecs = [rec for i, rec in enumerate(subrecs) if i not in self.index_of_atoms]
        res = 0
        for comp in compositions(n - atoms, len(subrecs)):
            # A composition is only valid if all positive children
            # get more than 0 atoms.
            if any(
                c == 0 for i, c in enumerate(comp) if i in self.indices_pos_children
            ):
                continue
            tmp = 1
            for i, rec in enumerate(subrecs):
                tmp *= rec(get_subrule, n=comp[i])
                if tmp == 0:
                    break
            res += tmp
        return res


class DisjointUnion(Constructor):
    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        return Eq(lhs_func, reduce(add, rhs_funcs, 0))

    def get_recurrence(
        self, subrecs: Callable[[Any], int], get_subrule, **lhs_parameters: Any
    ) -> int:
        return sum(rec(get_subrule, **lhs_parameters) for rec in subrecs)


class Empty(Constructor):
    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        return Eq(lhs_func, 1)

    def get_recurrence(self, subrecs: Callable[[Any], int], get_subrule, n: int) -> Any:
        if n == 0:
            return 1
        return 0


class Point(Constructor):
    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        return Eq(lhs_func, sympy.abc.x)

    def get_recurrence(self, subrecs: Callable[[Any], int], get_subrule, n: int) -> Any:
        if n == 1:
            return 1
        return 0
