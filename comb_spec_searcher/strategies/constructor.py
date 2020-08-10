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
from itertools import product
from random import randint
from typing import Callable, Dict, Generic, Iterable, Iterator, List, Optional, Tuple

from sympy import Eq, Function

from ..combinatorial_class import CombinatorialClassType, CombinatorialObjectType

__all__ = ("Constructor", "CartesianProduct", "DisjointUnion")


RelianceProfile = Tuple[Dict[str, Tuple[int, ...]], ...]
SubGens = Tuple[Callable[..., Iterator[CombinatorialObjectType]], ...]
SubRecs = Tuple[Callable[..., int], ...]
SubSamplers = Tuple[Callable[..., CombinatorialObjectType], ...]


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

    def get_recurrence(self, subrecs: SubRecs, n: int, **parameters: int) -> int:
        # The extra parameters variable maps each of the parent parameter to
        # the unique child that it was mapped to.
        res = 0
        for child_parameters in self._valid_compositions(n, **parameters):
            tmp = 1
            extra_parameters = self.get_extra_parameters(child_parameters)
            if extra_parameters is None:
                continue
            for rec, extra_params in zip(subrecs, extra_parameters):
                tmp *= rec(n=extra_params.pop("n"), **extra_params)
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
                *tuple(subgen(n=d["n"]) for d, subgen in zip(comp, subgens))
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
                tmp *= rec(n=comp[i]["n"])
                if tmp == 0:
                    break
            total += tmp
            if random_choice <= total:
                return tuple(
                    subsampler(d["n"]) for d, subsampler in zip(comp, subsamplers)
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

    def get_recurrence(self, subrecs: SubRecs, n: int, **parameters: int) -> int:
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
