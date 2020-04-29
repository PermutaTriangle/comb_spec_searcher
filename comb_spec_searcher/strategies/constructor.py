"""
The constructor class contains all the method, and logic, needed to get the
enumeration, generate objects, and sample objects.

The default constructors implemented are:
- Atom
- CartesianProduct
- DisjointUnion
- Empty

Currently the constructors are implemented in one variable, namely 'n' which is
used throughout to denote size.
"""
from functools import reduce
from itertools import product
from operator import add, mul
from typing import Any, Callable, Iterable, Iterator, Tuple
import abc

from sympy import Eq, Function
import sympy

from ..combinatorial_class import CombinatorialClass, CombinatorialObject


__all__ = ("Constructor", "CartesianProduct", "DisjointUnion", "Empty")


RelianceProfile = Tuple[Tuple[int, ...], ...]


class Constructor(abc.ABC):
    """The constructor is akin to the 'counting function' in the comb exp paper."""

    @abc.abstractmethod
    def is_equivalence(self) -> bool:
        """
        Return true if the constructor is the same as "=" when there is only
        one child.
        """

    @abc.abstractmethod
    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        """
        Return the sympy.Eq in the form lhs_func = f(rhs_funcs).
        """

    @abc.abstractmethod
    def reliance_profile(self, **parameters: int) -> RelianceProfile:
        """
        Return the reliance profile. That is for the parameters given,
        which parameters of each individual subclass are required.
        """

    @abc.abstractmethod
    def get_recurrence(self, subrecs: Callable[[Any], int], **parameters: int) -> int:
        """
        Return the count for the given parameters, assuming the children are
        counted by the subrecs given.
        """

    @abc.abstractmethod
    def get_sub_objects(
        self, subgens: Callable[[int], CombinatorialObject], **parameters: int
    ) -> Iterator[Tuple[CombinatorialObject, ...]]:
        """Return the subobjs/image of the bijection implied by the constructor."""

    def get_eq_symbol(self) -> str:
        """
        Return a choice for '=' in the pretty print a '=' b '+' c of rules.
        Your choice should be a single charachter.
        """
        return "="

    def get_op_symbol(self) -> str:
        """
        Return a choice for '+' in the pretty print a '=' b '+' c of rules.
        Your choice should be a single charachter.
        """
        return "+"


class Atom(Constructor):
    """
    The Atom constructor is used for counting a combinatorial class that
    consists of exactly one object. The parameters the Atom is initialised with
    are the parameters satisfied by the single object.
    """

    def __init__(self, **parameters):
        self.parameters = dict(**parameters)

    def is_equivalence(self) -> bool:
        return False

    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        # TODO: implement in multiple variable
        return Eq(lhs_func, sympy.abc.x ** self.parameters["n"])

    def get_recurrence(self, subrecs: Callable[[Any], int], **parameters: int) -> int:
        if parameters == self.parameters:
            return 1
        return 0

    def get_sub_objects(
        self, subgens: Callable[[int], CombinatorialObject], **parameters: int
    ) -> Iterator[Tuple[CombinatorialObject, ...]]:
        if parameters == self.parameters:
            yield tuple()
        return

    def reliance_profile(self, **parameters) -> RelianceProfile:
        return tuple()


class CartesianProduct(Constructor):
    """
    The CartesianProduct is initialised with the children of the rule that is
    being counted. These are needed in the reliance profile. In particular,
    the CombinatorialClass that you are counting must have implemented the
    methods 'is_positive', and 'is_atom', which are needed to ensure that the
    recursions are productive.
    """

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

    def is_equivalence(self) -> bool:
        return True

    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        return Eq(lhs_func, reduce(mul, rhs_funcs, 1))

    # pylint: disable=arguments-differ
    def reliance_profile(self, n: int) -> RelianceProfile:
        # TODO: implement in multiple variables
        return tuple(f(n) for f in self._reliance_profile_functions)

    def _valid_compositions(self, n: int) -> Iterator[Tuple[int, ...]]:
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

    def get_eq_symbol(self) -> str:
        return "="

    def get_op_symbol(self) -> str:
        return "x"


class DisjointUnion(Constructor):
    """
    The DisjointUnion constructor takes as input the children. Each constructor
    is unique up to the length of the children being used to count.
    """

    def __init__(self, children: Tuple[CombinatorialClass, ...]):
        self.number_of_children = len(children)

    def is_equivalence(self) -> bool:
        return True

    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        return Eq(lhs_func, reduce(add, rhs_funcs, 0))

    # pylint: disable=arguments-differ
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
        for i, subgen in enumerate(subgens):
            for gp in subgen(n=n):
                yield tuple(None for _ in range(i)) + (gp,) + tuple(
                    None for _ in range(len(subgens) - i - 1)
                )

    def get_eq_symbol(self) -> str:
        return "="

    def get_op_symbol(self) -> str:
        return "+"


class Empty(Constructor):
    """
    The Empty constructor is used for counting CombinatorialClass that are
    empty.
    """

    def is_equivalence(self) -> bool:
        return False

    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        return Eq(lhs_func, 0)

    # pylint: disable=arguments-differ
    def reliance_profile(self, n: int) -> RelianceProfile:
        # TODO: implement in multiple variables
        return tuple()

    def get_recurrence(
        self, subrecs: Callable[[Any], int], **lhs_parameters: Any
    ) -> int:
        return 0

    def get_sub_objects(
        self, subgens: Callable[[int], CombinatorialObject], n: int
    ) -> Iterator[Tuple[CombinatorialObject, ...]]:
        return []
