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
import functools
import operator
from collections import defaultdict
from itertools import product
from random import randint
from typing import (
    Callable,
    Counter,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    cast,
)

from sympy import Eq, Function

from comb_spec_searcher.combinatorial_class import (
    CombinatorialClassType,
    CombinatorialObjectType,
)

__all__ = ("Constructor", "CartesianProduct", "DisjointUnion")


Parameters = Tuple[int, ...]
ParametersMap = Callable[[Parameters], Parameters]
RelianceProfile = Tuple[Dict[str, Tuple[int, ...]], ...]
SubGens = Tuple[Callable[..., Iterator[CombinatorialObjectType]], ...]
SubRecs = Tuple[Callable[..., int], ...]
SubSamplers = Tuple[Callable[..., CombinatorialObjectType], ...]
Terms = Counter[Parameters]  # all terms for a fixed n
SubTerms = Tuple[Callable[[int], Terms], ...]


class Constructor(abc.ABC, Generic[CombinatorialClassType, CombinatorialObjectType]):
    """The constructor is akin to the 'counting function' in the comb exp paper."""

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
    def get_terms(self, subterms: SubTerms, n: int) -> Terms:
        """
        Return the terms for n given the subterms of the children.
        """

    @abc.abstractmethod
    def get_sub_objects(
        self, subgens: SubGens, n: int, **parameters: int
    ) -> Iterator[Tuple[Optional[CombinatorialObjectType], ...]]:
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


class CartesianProduct(Constructor[CombinatorialClassType, CombinatorialObjectType]):
    """
    The CartesianProduct is initialised with the children of the rule that is
    being counted. These are needed in the reliance profile. In particular,
    the CombinatorialClass that you are counting must have implemented the
    methods is_atom', 'minimum_size_of_object', 'get_minimum_values' which are
    needed to ensure that the recursions are productive.

    This CartesianProduct constructor considers compositions all of the
    parameters including n. then these should be passed to one other factor.
    The details of how the parameters map forward must be given using
    'extra_parameters'. This is a tuple, where the ith dictionary tells the
    constructor for each parent variable maps to on the child. If it does not
    map to the child it should not be a key in the dictionary.
    """

    def __init__(
        self,
        parent: CombinatorialClassType,
        children: Iterable[CombinatorialClassType],
        extra_parameters: Optional[Tuple[Dict[str, str], ...]] = None,
    ):

        children = tuple(children)

        if extra_parameters is not None:
            self.extra_parameters = tuple(extra_parameters)
        else:
            self.extra_parameters = tuple(dict() for _ in children)
        self._children_param_maps = self._build_children_param_map(parent, children)

        self.minimum_sizes = {"n": parent.minimum_size_of_object()}
        for k in parent.extra_parameters:
            self.minimum_sizes[k] = parent.get_minimum_value(k)

        self.min_child_sizes = tuple(
            {"n": child.minimum_size_of_object()} for child in children
        )
        self.max_child_sizes = tuple(
            {"n": child.minimum_size_of_object()} if child.is_atom() else {}
            for child in children
        )
        self.parent_parameters = ("n",) + parent.extra_parameters

        for (idx, child), parameters in zip(enumerate(children), self.extra_parameters):
            for k in parent.extra_parameters:
                self.min_child_sizes[idx][k] = (
                    child.get_minimum_value(parameters[k]) if k in parameters else 0
                )
                if k not in parameters:
                    self.max_child_sizes[idx][k] = 0
                elif child.is_atom():
                    self.max_child_sizes[idx][k] = child.get_minimum_value(
                        parameters[k]
                    )

    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        res = 1
        for extra_parameters, rhs_func in zip(self.extra_parameters, rhs_funcs):
            res *= rhs_func.subs(
                {child: parent for parent, child in extra_parameters.items()},
                simultaneous=True,
            )
        return Eq(lhs_func, res)

    def reliance_profile(self, n: int, **parameters: int) -> RelianceProfile:
        #  TODO: consider when parameters are subsets of each other etc
        # TODO: should this go back to only on n? i.e. RelianceProfile = Tuple[int, ...]
        assert all(
            set(["n", *parameters]) == set(min_child_sizes)
            for min_child_sizes in self.min_child_sizes
        )
        parameters["n"] = n
        return tuple(
            {
                k: tuple(
                    range(
                        min_child_sizes[k],
                        min(
                            [
                                parameters[k]
                                - self.minimum_sizes[k]
                                + min_child_sizes[k]
                                + 1
                            ]
                            + (
                                [max_child_sizes[k] + 1] if k in max_child_sizes else []
                            ),
                        ),
                    )
                )
                for k in min_child_sizes
            }
            for min_child_sizes, max_child_sizes in zip(
                self.min_child_sizes, self.max_child_sizes
            )
        )

    def _valid_compositions(
        self, n: int, **parameters: int
    ) -> Iterator[Tuple[Dict[str, int], ...]]:
        reliance_profile = self.reliance_profile(n, **parameters)

        def _helper(
            minmaxes: Tuple[Dict[str, Tuple[int, int]], ...], **parameters: int
        ):
            if len(minmaxes) == 1:
                minmax = minmaxes[0]
                if all(
                    minmax[k][0] <= parameters[k] <= minmax[k][1]
                    for k in self.parent_parameters
                ):
                    yield ({**parameters},)
                return

            still_to_come = {
                k: sum(minmax[k][0] for minmax in minmaxes[1:])
                for k in self.parent_parameters
            }
            max_available = {
                k: sum(minmax[k][1] for minmax in minmaxes[1:])
                for k in self.parent_parameters
            }
            minmax = minmaxes[0]
            for values in product(
                *[
                    range(
                        max(minmax[k][0], parameters[k] - max_available[k]),
                        min(minmax[k][1], parameters[k] - still_to_come[k]) + 1,
                    )
                    for k in self.parent_parameters
                ]
            ):
                params = dict(zip(self.parent_parameters, values))
                update_params = {
                    k: parameters[k] - params[k] for k in self.parent_parameters
                }
                for comp in _helper(minmaxes[1:], **update_params):
                    yield (params,) + comp

        if all(all(profile.values()) for profile in reliance_profile):
            minmaxes: Tuple[Dict[str, Tuple[int, int]], ...] = tuple(
                {k: (min(profile[k]), max(profile[k])) for k in self.parent_parameters}
                for profile in reliance_profile
            )
            parameters["n"] = n
            yield from _helper(minmaxes, **parameters)

    def get_extra_parameters(
        self, child_parameters: Tuple[Dict[str, int], ...]
    ) -> Optional[List[Dict[str, int]]]:
        """
        Will return the extra parameters dictionary based on the given child
        parameters given. If there is a contradiction, that is some child
        parameter is given two or more different values that do not match,
        then None will be returned indicating that there is a contradiction,
        and so there are no objects satisfying the child parameters.
        """
        res: List[Dict[str, int]] = []
        for params, map_params in zip(child_parameters, self.extra_parameters):
            assert all(
                params[k] == 0
                for k in self.parent_parameters
                if k not in map_params and k != "n"
            )
            extra_params: Dict[str, int] = {"n": params["n"]}
            for k in map_params:
                mapped_k = map_params[k]
                if mapped_k not in extra_params:
                    extra_params[mapped_k] = params[k]
                elif extra_params[mapped_k] != params[k]:
                    return None
            res.append(extra_params)
        return res

    def get_terms(self, subterms: SubTerms, n: int) -> Terms:
        min_sizes = tuple(d["n"] for d in self.min_child_sizes)
        max_sizes = tuple(d.get("n", None) for d in self.max_child_sizes)
        return self._cartesian_push(
            n, subterms, self._children_param_maps, min_sizes, max_sizes
        )

    @staticmethod
    def _cartesian_push(
        n: int,
        children_terms: SubTerms,
        children_param_maps: Tuple[ParametersMap, ...],
        min_sizes: Tuple[int, ...],
        max_sizes: Tuple[Optional[int], ...],
    ) -> Terms:
        new_terms: Terms = Counter()
        size_compositions = compositions(n, len(children_terms), min_sizes, max_sizes)
        for sizes in size_compositions:
            children_size_caches: Iterator[Terms] = (
                st(s) for st, s in zip(children_terms, sizes)
            )
            param_value_pairs_combinations = cast(
                Iterator[Tuple[Tuple[Parameters, int], ...]],
                product(*(c.items() for c in children_size_caches)),
            )
            for param_value_pairs in param_value_pairs_combinations:
                new_param = vector_add(
                    *(
                        pmap(p)
                        for pmap, (p, _) in zip(children_param_maps, param_value_pairs)
                    )
                )
                new_terms[new_param] += prod((v for _, v in param_value_pairs))
        return new_terms

    def _build_children_param_map(
        self,
        parent: CombinatorialClassType,
        children: Tuple[CombinatorialClassType, ...],
    ) -> Tuple[ParametersMap, ...]:
        map_list: List[ParametersMap] = []
        num_parent_params = len(parent.extra_parameters)
        parent_param_to_pos = {
            param: pos for pos, param in enumerate(parent.extra_parameters)
        }
        for child, extra_param in zip(children, self.extra_parameters):
            reversed_extra_param: Dict[str, List[str]] = defaultdict(list)
            for parent_var, child_var in extra_param.items():
                reversed_extra_param[child_var].append(parent_var)
            child_pos_to_parent_pos: Tuple[Tuple[int, ...], ...] = tuple(
                tuple(
                    map(
                        parent_param_to_pos.__getitem__,
                        reversed_extra_param[child_param],
                    )
                )
                for child_param in child.extra_parameters
            )
            map_list.append(
                self._build_param_map(child_pos_to_parent_pos, num_parent_params)
            )
        return tuple(map_list)

    @staticmethod
    def _build_param_map(
        child_pos_to_parent_pos: Tuple[Tuple[int, ...], ...], num_parent_params: int
    ) -> ParametersMap:
        """
        Build the ParametersMap that will map according to the given child pos to parent
        pos map given.
        """

        def param_map(param: Parameters) -> Parameters:
            new_params = [0 for _ in range(num_parent_params)]
            for pos, value in enumerate(param):
                parent_pos = child_pos_to_parent_pos[pos]
                for p in parent_pos:
                    new_params[p] += value
            return tuple(new_params)

        return param_map

    def get_sub_objects(
        self, subgens: SubGens, n: int, **parameters: int
    ) -> Iterator[Tuple[CombinatorialObjectType, ...]]:
        for child_parameters in self._valid_compositions(n, **parameters):
            extra_parameters = self.get_extra_parameters(child_parameters)
            if extra_parameters is None:
                continue
            for objs in product(
                *[
                    gen(n=extra_params.pop("n"), **extra_params)
                    for gen, extra_params in zip(subgens, extra_parameters)
                ]
            ):
                yield tuple(objs)

    def random_sample_sub_objects(
        self,
        parent_count: int,
        subsamplers: SubSamplers,
        subrecs: SubRecs,
        n: int,
        **parameters: int
    ):
        random_choice = randint(1, parent_count)
        total = 0
        for child_parameters in self._valid_compositions(n, **parameters):
            tmp = 1
            extra_parameters = self.get_extra_parameters(child_parameters)
            if extra_parameters is None:
                continue
            for rec, extra_params in zip(subrecs, extra_parameters):
                tmp *= rec(n=extra_params.pop("n"), **extra_params)
                if tmp == 0:
                    break
            total += tmp
            if random_choice <= total:
                extra_parameters = self.get_extra_parameters(child_parameters)
                assert extra_parameters is not None
                return tuple(
                    subsampler(n=extra_params.pop("n"), **extra_params)
                    for subsampler, extra_params in zip(subsamplers, extra_parameters)
                )

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

    The fixed value dictionaries passed will be used ensure that the parameter
    of a child must take on the given value.
    """

    def __init__(
        self,
        parent: CombinatorialClassType,
        children: Tuple[CombinatorialClassType, ...],
        extra_parameters: Optional[Tuple[Dict[str, str], ...]] = None,
        fixed_values: Optional[Tuple[Dict[str, int], ...]] = None,
    ):
        self.number_of_children = len(children)
        if extra_parameters is not None:
            self.extra_parameters = extra_parameters
            assert len(extra_parameters) == len(children)
        else:
            assert not parent.extra_parameters
            self.extra_parameters = tuple(
                dict() for _ in range(self.number_of_children)
            )
        self._children_param_maps = build_children_param_maps(
            parent, children, self.extra_parameters
        )
        self.zeroes = tuple(
            frozenset(parent.extra_parameters) - frozenset(parameter.keys())
            for parameter in self.extra_parameters
        )
        if fixed_values is not None:
            self.fixed_values = fixed_values
            assert len(fixed_values) == len(children)
        else:
            self.fixed_values = tuple({} for _ in children)

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
        return tuple({"n": (n,)} for _ in range(self.number_of_children))

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
        for i, extra_parameters in enumerate(self.extra_parameters):
            update_params: Dict[str, int] = {**self.fixed_values[i]}
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

    def get_terms(self, subterms: SubTerms, n: int) -> Terms:
        return self._union_push(n, subterms, self._children_param_maps)

    @staticmethod
    def _union_push(
        n: int,
        children_terms: SubTerms,
        children_param_maps: Tuple[ParametersMap, ...],
    ) -> Terms:
        """
        Uses the `children_terms` functions to and the `children_param_maps` to compute
        the terms of size `n`.
        """
        assert len(children_terms) == len(children_param_maps)
        new_terms: Terms = Counter()
        for child_terms, param_map in zip(children_terms, children_param_maps):
            for param, value in child_terms(n).items():
                new_terms[param_map(param)] += value
        return new_terms

    def get_sub_objects(
        self, subgens: SubGens, n: int, **parameters: int
    ) -> Iterator[Tuple[Optional[CombinatorialObjectType], ...]]:
        for (idx, subgen), extra_params in zip(
            enumerate(subgens), self.get_extra_parameters(n, **parameters)
        ):
            if extra_params is None or any(
                val != 0 and k in self.zeroes[idx] for k, val in parameters.items()
            ):
                continue
            for gp in subgen(n, **extra_params):
                yield tuple(None for _ in range(idx)) + (gp,) + tuple(
                    None for _ in range(len(subgens) - idx - 1)
                )

    def random_sample_sub_objects(
        self,
        parent_count: int,
        subsamplers: SubSamplers,
        subrecs: SubRecs,
        n: int,
        **parameters: int
    ):
        random_choice = randint(1, parent_count)
        total = 0
        for (idx, rec), subsampler, extra_params in zip(
            enumerate(subrecs), subsamplers, self.get_extra_parameters(n, **parameters)
        ):
            # if a parent parameter is not mapped to by some child parameter
            # then it is assumed that the value of the parent parameter must be 0
            if extra_params is None or any(
                val != 0 and k in self.zeroes[idx] for k, val in parameters.items()
            ):
                continue
            total += rec(n=n, **extra_params)
            if random_choice <= total:
                obj = subsampler(n=n, **extra_params)
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


##############################################
# Functions that need to be sorted somewhere #
##############################################


def build_param_map(
    child_pos_to_parent_pos: Tuple[Optional[int], ...], num_parent_params: int
) -> ParametersMap:
    """
    Build the ParametersMap that will map according to the given child pos to parent
    pos map given.

    If a child pos maps to None, then the value of the parameter must be 0 at all times.
    """

    def param_map(param: Parameters) -> Parameters:
        new_params = [0 for _ in range(num_parent_params)]
        for pos, value in enumerate(param):
            parent_pos = child_pos_to_parent_pos[pos]
            if parent_pos is None:
                assert value == 0
                continue
            assert new_params[parent_pos] == 0
            new_params[parent_pos] = value
        return tuple(new_params)

    return param_map


def build_children_param_maps(
    parent: CombinatorialClassType,
    children: Tuple[CombinatorialClassType, ...],
    parent_to_child_params: Tuple[Dict[str, str], ...],
) -> Tuple[ParametersMap, ...]:
    map_list: List[ParametersMap] = []
    num_parent_params = len(parent.extra_parameters)
    parent_param_to_pos = {
        param: pos for pos, param in enumerate(parent.extra_parameters)
    }
    for child, extra_param in zip(children, parent_to_child_params):
        reverse_extra_param = {b: a for a, b in extra_param.items()}
        child_pos_to_parent_pos = tuple(
            parent_param_to_pos[reverse_extra_param[child_param]]
            if child_param in reverse_extra_param
            else None
            for child_param in child.extra_parameters
        )
        map_list.append(build_param_map(child_pos_to_parent_pos, num_parent_params))
    return tuple(map_list)


def compositions(
    n: int, k: int, min_sizes: Tuple[int, ...], max_sizes: Tuple[Optional[int], ...]
) -> Iterator[Tuple[int, ...]]:
    """
    Iterator over all composition of n in k parts with the given max_sizes and
    min_sizes.
    """
    if (
        n < 0
        or k <= 0
        or n < sum(min_sizes)
        or (
            all(s is not None for s in max_sizes)
            and sum(cast(Tuple[int, ...], max_sizes)) < n
        )
    ):
        return
    if k == 1:
        assert (max_sizes[0] is None or max_sizes[0] >= n) and n >= min_sizes[0]
        yield (n,)
        return
    max_size = max_sizes[0] if max_sizes[0] is not None else n
    for i in range(min_sizes[0], max_size + 1):
        yield from map(
            (i,).__add__, compositions(n - i, k - 1, min_sizes[1:], max_sizes[1:])
        )


def vector_add(*args: Tuple[int, ...]) -> Tuple[int, ...]:
    """
    Perform vector addition on tuples.

    >>> vector_add((1,), (1,), (1,), (2,))
    (5,)
    >>> vector_add((1, 2), (1, 3))
    (2, 5)
    >>> vector_add((1, 2, 3))
    (1, 2, 3)
    """
    return tuple(sum(vals) for vals in zip(*args))


def prod(values: Iterable[int]) -> int:
    """Compute the product of the integers."""
    return functools.reduce(operator.mul, values)
