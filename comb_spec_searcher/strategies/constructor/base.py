"""
The constructor class contains all the method, and logic, needed to get the
enumeration, generate objects, and sample objects.
"""
import abc
from functools import partial
from typing import Callable, Generic, Iterator, List, Optional, Tuple

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
            Constructor.param_map, child_pos_to_parent_pos, num_parent_params
        )
