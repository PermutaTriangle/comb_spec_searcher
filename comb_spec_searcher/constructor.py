from functools import reduce
from itertools import chain, product
from operator import add, mul
from typing import Any, Callable, Iterator, Tuple

from sympy import Eq, Function
import sympy

from .combinatorial_class import CombinatorialClass, CombinatorialObject
from .utils import compositions

import abc


__all__ = ["Constructor", "Cartesian", "DisjointUnion", "Empty", "Point"]


class Constructor(abc.ABC):
    """The constructor is akin to the 'counting function' in the comb exp paper."""

    @abc.abstractmethod
    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        pass

    @abc.abstractmethod
    def get_recurrence(
        self, subrecs: Callable[[Any], int], **lhs_parameters: Any
    ) -> int:
        pass

    @abc.abstractmethod
    def get_sub_objects(
        self, subgens: Callable[[int], CombinatorialObject], size: int
    ) -> Iterator[Tuple[CombinatorialObject, ...]]:
        pass


class CartesianProduct(Constructor):
    def __init__(self, children):
        # Number of children that are just the atom
        indices_of_atoms = set()
        for i, child in enumerate(children):
            if child.is_atom():
                indices_of_atoms.add(i)
        self.indices_of_non_atoms = tuple(
            i for i in range(len(children)) if i not in indices_of_atoms
        )
        self.indices_of_atoms = tuple(sorted(indices_of_atoms))
        non_point_children = [
            child for i, child in enumerate(children) if i not in self.indices_of_atoms
        ]
        # index of positive children after removing atoms
        self.indices_pos_children = frozenset(
            i for i, child in enumerate(non_point_children) if child.is_positive()
        )

    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        return Eq(lhs_func, reduce(mul, rhs_funcs, 1))

    def get_recurrence(self, subrecs: Tuple[Callable[[Any], int]], n: int) -> int:
        subrecs = [subrecs[i] for i in self.indices_of_non_atoms]
        res = 0
        for comp in self._valid_composition(n):
            tmp = 1
            for i, rec in enumerate(subrecs):
                tmp *= rec(n=comp[i])
                if tmp == 0:
                    break
            res += tmp
        return res

    def _valid_composition(self, size: int):
        atoms = len(self.indices_of_atoms)
        for comp in compositions(size - atoms, len(self.indices_of_non_atoms)):
            # A composition is only valid if all positive children
            # get more than 0 atoms.
            if any(
                c == 0 for i, c in enumerate(comp) if i in self.indices_pos_children
            ):
                continue
            yield comp

    def get_sub_objects(
        self, subgens: Callable[[int], CombinatorialObject], size: int
    ) -> Iterator[Tuple[CombinatorialObject, ...]]:
        for comp in self._valid_composition(size):
            comp = [(i,) for i in comp]
            for idx in self.indices_of_atoms:
                comp.insert(idx, (1,))
            yield from map(
                tuple,
                product(
                    *tuple(
                        subgen(*parameters) for parameters, subgen in zip(comp, subgens)
                    )
                ),
            )


class DisjointUnion(Constructor):
    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        return Eq(lhs_func, reduce(add, rhs_funcs, 0))

    def get_recurrence(
        self, subrecs: Callable[[Any], int], **lhs_parameters: Any
    ) -> int:
        return sum(rec(**lhs_parameters) for rec in subrecs)

    def get_sub_objects(
        self, subgens: Callable[[int], CombinatorialObject], size: int
    ) -> Iterator[Tuple[CombinatorialObject, ...]]:
        for gp in chain.from_iterable(subgen(size) for subgen in subgens):
            yield (gp,)
