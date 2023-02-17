"""
The constructor class contains all the method, and logic, needed to get the
enumeration, generate objects, and sample objects.
"""
import abc
from collections import Counter
from functools import partial
from typing import Callable, Dict, Generic, Iterator, List, Optional, Set, Tuple

import sympy

from comb_spec_searcher.typing import (
    CombinatorialClassType,
    CombinatorialObjectType,
    Parameters,
    ParametersMap,
    RelianceProfile,
    SubObjects,
    SubRecs,
    SubSamplers,
    SubTerms,
    Terms,
)


class Constructor(abc.ABC, Generic[CombinatorialClassType, CombinatorialObjectType]):
    """The constructor is akin to the 'counting function' in the comb exp paper."""

    def can_be_equivalent(self) -> bool:  # pylint: disable=no-self-use
        """
        Return False if the constructor can NOT be an 'identity' map
        (i.e., up to rearranging params)
        """
        return True

    @abc.abstractmethod
    def get_equation(
        self, lhs_func: sympy.Function, rhs_funcs: Tuple[sympy.Function, ...]
    ) -> sympy.Eq:
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
    def get_terms(
        self, parent_terms: Callable[[int], Terms], subterms: SubTerms, n: int
    ) -> Terms:
        """
        Return the terms for n given the subterms of the children.
        """

    @abc.abstractmethod
    def get_sub_objects(
        self, subobjs: SubObjects, n: int
    ) -> Iterator[
        Tuple[Parameters, Tuple[List[Optional[CombinatorialObjectType]], ...]]
    ]:
        """
        Iterate over all the possibe subobjs/image of the bijection implied by
        the constructor together with the parameters.
        """

    @abc.abstractmethod
    def random_sample_sub_objects(
        self,
        parent_count: int,
        subsamplers: SubSamplers,
        subrecs: SubRecs,
        n: int,
        **parameters: int,
    ) -> Tuple[Optional[CombinatorialObjectType], ...]:
        """Return a randomly sampled subobjs/image of the bijection implied
        by the constructor."""

    @staticmethod
    def param_map(
        child_pos_to_parent_pos: Tuple[Tuple[int, ...], ...],
        num_parent_params: int,
        param: Parameters,
    ) -> Parameters:
        new_params = [0 for _ in range(num_parent_params)]
        for pos, value in enumerate(param):
            parent_pos = child_pos_to_parent_pos[pos]
            for p in parent_pos:
                new_params[p] += value
        return tuple(new_params)

    @staticmethod
    def build_param_map(
        child_pos_to_parent_pos: Tuple[Tuple[int, ...], ...], num_parent_params: int
    ) -> ParametersMap:
        """
        Return a parameters map according to the given pos map.
        """
        return partial(
            Constructor.param_map,
            child_pos_to_parent_pos,
            num_parent_params,
        )

    @abc.abstractmethod
    def equiv(
        self, other: "Constructor", data: Optional[object] = None
    ) -> Tuple[bool, Optional[object]]:
        """Two constructors are equiv if A <self> B and C <other> D are isomorphic for
        any combinatorial classes A, B, C and D where A and C are isomorphic and B and
        D. This must be implemented for bijections. The data argument is to optionally
        pass additional information to the equiv function. The second returned value is
        optional data for bijections. It is used to pass additional arguments to
        determine index ordering. It needs to be JSON compatible for bijection's
        `to_jsonable` and `from_dict` to work.
        """

    @staticmethod
    def extra_params_equiv(
        params1: Tuple[Dict[str, str], ...],
        params2: Tuple[Dict[str, str], ...],
    ) -> bool:
        """A base equiv for extra params that will suffice for most constructors."""
        non_empty1 = tuple(par for par in params1 if par)
        non_empty2 = tuple(par for par in params2 if par)
        n = len(non_empty1)
        if len(non_empty2) != n:
            return False
        if n == 0:
            return True
        return Constructor._extra_params_match_bijection(n, non_empty1, non_empty2)

    @staticmethod
    def _extra_params_match_single(par1: Dict[str, str], par2: Dict[str, str]) -> bool:
        """Two parameter dictionaries are equivalent if they have the same number
        of keys if there is a value with k keys mapping to it, then there is a
        corresponding value with k keys mapping to it in the other one.
        """
        return len(par1) == len(par2) and sorted(
            Counter(par1.values()).values()
        ) == sorted(Counter(par2.values()).values())

    @staticmethod
    def _extra_params_match_bijection(
        n: int, p1: Tuple[Dict[str, str], ...], p2: Tuple[Dict[str, str], ...]
    ) -> bool:
        """Check if there is a bijection between the two tuples of params
        such that they are pairwise equivalent."""

        # Shared variables in recursion
        bijection: List[int] = []
        in_use: Set[int] = set()
        cache: Dict[Tuple[int, int], bool] = {}

        def _backtracking() -> bool:
            for i in range(n):
                if i in in_use:
                    continue
                bijection.append(i)
                in_use.add(i)

                k = len(bijection)
                key = (k - 1, i)
                res = cache.get(key, None)
                if res is None:
                    res = Constructor._extra_params_match_single(p1[key[0]], p2[key[1]])
                    cache[key] = res

                # Check if consistent and either done or recursive success.
                res = res and (k == n or _backtracking())

                bijection.pop()
                in_use.remove(i)
                if res:
                    return True
            return False

        return _backtracking()
