"""
The constructor class contains all the method, and logic, needed to get the
enumeration, generate objects, and sample objects.

The default constructors implemented are:
- CartesianProduct
- DisjointUnion
- Empty

Currently the constructors are implemented in one variable, namely 'n' which is
used throughout to denote size.
"""
import abc
from functools import partial
from itertools import product
from random import randint
from typing import Callable, Dict, Generic, Iterable, Iterator, List, Optional, Tuple

from sympy import Eq, Function

from ..combinatorial_class import CombinatorialClassType, CombinatorialObjectType

__all__ = ("Constructor", "CartesianProduct", "DisjointUnion")


RelianceProfile = Tuple[Tuple[int, ...], ...]
SubGens = Tuple[Callable[..., Iterator[CombinatorialObjectType]], ...]
SubRecs = Tuple[Callable[..., int], ...]
SubSamplers = Tuple[Callable[..., CombinatorialObjectType], ...]


class Constructor(abc.ABC, Generic[CombinatorialClassType, CombinatorialObjectType]):
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
    def reliance_profile(self, n: int, **parameters: int) -> RelianceProfile:
        """
        Return the reliance profile. That is for the parameters given,
        which parameters of each individual subclass are required.
        """

    @abc.abstractmethod
    def get_recurrence(self, subrecs: SubRecs, n: int, **parameters: int) -> int:
        """
        Return the count for the given parameters, assuming the children are
        counted by the subrecs given.
        """

    @abc.abstractmethod
    def get_sub_objects(
        self, subgens: SubGens, n: int, **parameters: int
    ) -> Iterator[Tuple[CombinatorialObjectType, ...]]:
        """Return the subobjs/image of the bijection implied by the constructor."""

    @abc.abstractmethod
    def random_sample_sub_objects(
        self,
        parent_count: int,
        subsamplers: SubSamplers,
        subrecs: SubRecs,
        n: int,
        **parameters: int
    ):
        """Return a randomly sampled subobjs/image of the bijection implied
        by the constructor."""

    @staticmethod
    def get_eq_symbol() -> str:
        """
        Return a choice for '=' in the pretty print a '=' b '+' c of rules.
        Your choice should be a single charachter.
        """
        return "="

    @staticmethod
    def get_op_symbol() -> str:
        """
        Return a choice for '+' in the pretty print a '=' b '+' c of rules.
        Your choice should be a single charachter.
        """
        return "+"


class CartesianProduct(Constructor[CombinatorialClassType, CombinatorialObjectType]):
    """
    The CartesianProduct is initialised with the children of the rule that is
    being counted. These are needed in the reliance profile. In particular,
    the CombinatorialClass that you are counting must have implemented the
    methods is_atom' and 'minimum_size_of_object', which are needed to ensure that the
    recursions are productive.

    This CartesianProduct constructor only considers compositions of n. If
    other parameters are given, then these should be passed to one other factor.
    The details of this must be given using 'parameters'. This is a tuple, where
    the ith dictionary tells the constructor for each variable on the child which
    variable it came from.
    (In particular, each extra variable on the child must be a key in the dictionary,
    and each extra variable in the parent must appear as a value in exactly one
    dictionary.)
    """

    def __init__(
        self,
        children: Iterable[CombinatorialClassType],
        extra_parameters: Optional[Tuple[Dict[str, str], ...]] = None,
    ):

        children = tuple(children)

        if extra_parameters is not None:
            self.extra_parameters = tuple(extra_parameters)
        else:
            self.extra_parameters = tuple(dict() for _ in children)

        self.minimum_size = sum(
            comb_class.minimum_size_of_object() for comb_class in children
        )

        reliance_profile_functions = []
        for child in children:
            min_child_size = child.minimum_size_of_object()
            if child.is_atom():
                func = partial(self.child_reliance_profile, min_child_size, atom=True)
            else:
                func = partial(self.child_reliance_profile, min_child_size)
            reliance_profile_functions.append(func)

        self._reliance_profile_functions = tuple(reliance_profile_functions)

    def child_reliance_profile(
        self, min_child_size: int, n: int, atom: bool = False
    ) -> Tuple[int, ...]:
        if atom:
            return tuple(
                range(
                    min_child_size,
                    min(n - self.minimum_size + min_child_size + 1, min_child_size + 1),
                )
            )
        return tuple(range(min_child_size, n - self.minimum_size + min_child_size + 1))

    @staticmethod
    def is_equivalence() -> bool:
        return True

    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        res = 1
        for extra_parameters, rhs_func in zip(self.extra_parameters, rhs_funcs):
            res *= rhs_func.subs(
                {child: parent for parent, child in extra_parameters.items()},
                simultaneous=True,
            )
        return Eq(lhs_func, res)

    def reliance_profile(self, n: int, **parameters: int) -> RelianceProfile:
        # TODO: implement in multiple variables
        assert not parameters, "only implemented in one variable, namely 'n'"
        return tuple(f(n) for f in self._reliance_profile_functions)

    def _valid_compositions(
        self, n: int, **parameters: int
    ) -> Iterator[Tuple[int, ...]]:
        assert not parameters, "only implemented in one variable, namely 'n'"
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

    def get_recurrence(self, subrecs: SubRecs, n: int, **parameters: int) -> int:
        # The extra parameters variable maps each of the parent parameter to
        # the unique child that it was mapped to.
        extra_params = tuple(
            {
                child_var: parameters[parent_var]
                for parent_var, child_var in param.items()
            }
            for param in self.extra_parameters
        )
        res = 0
        for comp in self._valid_compositions(n):
            tmp = 1
            for (i, rec), extra_param in zip(enumerate(subrecs), extra_params):
                tmp *= rec(n=comp[i], **extra_param)
                if tmp == 0:
                    break
            res += tmp
        return res

    def get_sub_objects(
        self, subgens: SubGens, n: int, **parameters: int
    ) -> Iterator[Tuple[CombinatorialObjectType, ...]]:
        assert len(parameters) == 0, "only implemented in one variable, namely 'n'"
        for comp in self._valid_compositions(n):
            for sub_objs in product(
                *tuple(subgen(n=i) for i, subgen in zip(comp, subgens))
            ):
                yield tuple(sub_objs)

    def random_sample_sub_objects(
        self,
        parent_count: int,
        subsamplers: SubSamplers,
        subrecs: SubRecs,
        n: int,
        **parameters: int
    ):
        assert not parameters, "only implemented in one variable"
        random_choice = randint(1, parent_count)
        total = 0
        for comp in self._valid_compositions(n):
            tmp = 1
            for i, rec in enumerate(subrecs):
                tmp *= rec(n=comp[i])
                if tmp == 0:
                    break
            total += tmp
            if random_choice <= total:
                return tuple(subsampler(i) for i, subsampler in zip(comp, subsamplers))

    @staticmethod
    def get_eq_symbol() -> str:
        return "="

    @staticmethod
    def get_op_symbol() -> str:
        return "x"

    def __str__(self) -> str:
        return "Cartesian product"


class DisjointUnion(Constructor[CombinatorialClassType, CombinatorialObjectType]):
    """
    The DisjointUnion constructor takes as input the children. Each constructor
    is unique up to the length of the children being used to count.

    Extra parameters are passed on using the parameters dictionaries. Each
    dictionary's keys should be the extra variable of the child pointing the
    variable on the parent it came from.
    If a parents variable does not map to a child, then this variable must be 0
    as the child contains no occurences.
    """

    def __init__(
        self,
        parent: CombinatorialClassType,
        children: Tuple[CombinatorialClassType, ...],
        extra_parameters: Optional[Tuple[Dict[str, str], ...]] = None,
    ):
        self.number_of_children = len(children)
        if extra_parameters is not None:
            self.extra_parameters = extra_parameters
        else:
            assert not parent.extra_parameters
            self.extra_parameters = tuple(
                dict() for _ in range(self.number_of_children)
            )

        self.zeroes = tuple(
            frozenset(parent.extra_parameters) - frozenset(parameter.keys())
            for parameter in self.extra_parameters
        )

    @staticmethod
    def is_equivalence() -> bool:
        return True

    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        res = 0
        for rhs_func, extra_parameters in zip(rhs_funcs, self.extra_parameters):
            res += rhs_func.subs(
                {child: parent for parent, child in extra_parameters.items()},
                simultaneous=True,
            )
        return Eq(lhs_func, res)

    def reliance_profile(self, n: int, **parameters: int) -> RelianceProfile:
        # TODO: implement in multiple variables and use in get_recurrence
        assert not parameters, "only implemented in one variable, namely 'n'"
        return tuple((n,) for _ in range(self.number_of_children))

    def get_extra_parameters(
        self, n: int, **parameters: int
    ) -> List[Optional[Dict[str, int]]]:
        """
        Will return the extra parameters dictionary based on the parent's
        parameters. If there is a contradiction, that is some child parameter
        is given two or more different values that do not match, then None
        will be returned for that child, indicating that 0 objects on the
        child match the parents parameters.
        """
        res: List[Optional[Dict[str, int]]] = []
        for extra_parameters in self.extra_parameters:
            update_params: Dict[str, int] = {}
            for parent_var, child_var in extra_parameters.items():
                updated_value = parameters[parent_var]
                if child_var not in update_params:
                    update_params[child_var] = updated_value
                elif update_params[child_var] != updated_value:
                    break
            else:
                res.append(update_params)
                continue
            res.append(None)
        return res

    def get_recurrence(self, subrecs: SubRecs, n: int, **parameters: int) -> int:
        if not parameters:
            return sum(rec(n) for rec in subrecs)
        res = 0
        for (idx, rec), extra_params in zip(
            enumerate(subrecs), self.get_extra_parameters(n, **parameters)
        ):
            # if a parent parameter is not mapped to by some child parameter
            # then it is assumed that the value of the parent parameter must be 0
            if extra_params is None or any(
                val != 0 and k in self.zeroes[idx] for k, val in parameters.items()
            ):
                continue
            res += rec(n=n, **extra_params)
        return res

    @staticmethod
    def get_sub_objects(
        subgens: SubGens, n: int, **parameters: int
    ) -> Iterator[Tuple[CombinatorialObjectType, ...]]:
        assert len(parameters) == 0, "only implemented in one variable, namely 'n'"
        for i, subgen in enumerate(subgens):
            for gp in subgen(n, **parameters):
                yield tuple(None for _ in range(i)) + (gp,) + tuple(
                    None for _ in range(len(subgens) - i - 1)
                )

    @staticmethod
    def random_sample_sub_objects(
        parent_count: int,
        subsamplers: SubSamplers,
        subrecs: SubRecs,
        n: int,
        **parameters: int
    ):
        random_choice = randint(1, parent_count)
        total = 0
        for idx, (subrec, subsampler) in enumerate(zip(subrecs, subsamplers)):
            total += subrec(n=n, **parameters)
            if random_choice <= total:
                obj = subsampler(n=n, **parameters)
                return (
                    tuple(None for _ in range(idx))
                    + (obj,)
                    + tuple(None for _ in range(len(subrecs) - idx - 1))
                )

    @staticmethod
    def get_eq_symbol() -> str:
        return "="

    @staticmethod
    def get_op_symbol() -> str:
        return "+"

    def __str__(self):
        return "disjoint union"
