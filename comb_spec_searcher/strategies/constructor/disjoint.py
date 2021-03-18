from collections import defaultdict
from random import randint
from typing import Callable, Counter, Dict, Iterator, List, Optional, Tuple

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

from .base import Constructor


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
        self._children_param_maps = self._build_children_param_maps(parent, children)
        self.zeroes = tuple(
            frozenset(parent.extra_parameters) - frozenset(parameter.keys())
            for parameter in self.extra_parameters
        )
        if fixed_values is not None:
            self.fixed_values = fixed_values
            assert len(fixed_values) == len(children)
        else:
            self.fixed_values = tuple({} for _ in children)

    def get_equation(
        self, lhs_func: sympy.Function, rhs_funcs: Tuple[sympy.Function, ...]
    ) -> sympy.Eq:
        res = 0
        for rhs_func, extra_parameters in zip(rhs_funcs, self.extra_parameters):
            res += rhs_func.subs(
                {child: parent for parent, child in extra_parameters.items()},
                simultaneous=True,
            )
        return sympy.Eq(lhs_func, res)

    def reliance_profile(self, n: int, **parameters: int) -> RelianceProfile:
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

    def get_terms(
        self, parent_terms: Callable[[int], Terms], subterms: SubTerms, n: int
    ) -> Terms:
        new_terms: Terms = Counter()
        for child_terms, param_map in zip(subterms, self._children_param_maps):
            for param, value in child_terms(n).items():
                new_terms[param_map(param)] += value
        return new_terms

    def _build_children_param_maps(
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
                if child_param in reversed_extra_param
                else tuple()
                for child_param in child.extra_parameters
            )
            map_list.append(
                self.build_param_map(child_pos_to_parent_pos, num_parent_params)
            )
        return tuple(map_list)

    def get_sub_objects(
        self, subobjs: SubObjects, n: int
    ) -> Iterator[
        Tuple[Parameters, Tuple[List[Optional[CombinatorialObjectType]], ...]]
    ]:
        res: List[List[Optional[CombinatorialObjectType]]]
        res = [[None] for _ in range(self.number_of_children)]
        for i, subobj in enumerate(subobjs):
            param_map = self._children_param_maps[i]
            for param, comb_objs in subobj(n).items():
                res[i] = comb_objs
                yield (param_map(param), tuple(res))
            res[i] = [None]

    def random_sample_sub_objects(
        self,
        parent_count: int,
        subsamplers: SubSamplers,
        subrecs: SubRecs,
        n: int,
        **parameters: int,
    ) -> Tuple[Optional[CombinatorialObjectType], ...]:
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


class Complement(Constructor[CombinatorialClassType, CombinatorialObjectType]):
    """
    This constructor implements the complement operation. A rule A -> (B, C, D)
    should be read as A = B - C - D.

    This comes from a disjoint union rule B = A + C + D

    The initialiser should be made using the original disjoint union rule.

    The parent is B, idx is the index of the child the rule is being rearranged
    for and the extra parameters maps from parent to children.
    """

    def __init__(
        self,
        parent: CombinatorialClassType,
        children: Tuple[CombinatorialClassType, ...],
        idx: int,
        extra_parameters: Optional[Tuple[Dict[str, str], ...]] = None,
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
        self.idx = idx
        self._children_param_maps = self._build_children_param_maps(parent, children)
        self._parent_param_map = self._build_parent_param_map(parent, children, idx)

    def _build_children_param_maps(
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
                if child_param in reversed_extra_param
                else tuple()
                for child_param in child.extra_parameters
            )
            map_list.append(
                self.build_param_map(child_pos_to_parent_pos, num_parent_params)
            )
        return tuple(map_list)

    def _build_parent_param_map(
        self,
        parent: CombinatorialClassType,
        children: Tuple[CombinatorialClassType, ...],
        idx: int,
    ):
        extra_param = self.extra_parameters[idx]
        child = children[self.idx]
        child_param_to_pos = {
            param: pos for pos, param in enumerate(child.extra_parameters)
        }
        parent_pos_to_child_pos: Tuple[Tuple[int, ...], ...] = tuple(
            (child_param_to_pos[extra_param[parent_var]],)
            if parent_var in extra_param
            else tuple()
            for parent_var in parent.extra_parameters
        )
        return self.build_param_map(
            parent_pos_to_child_pos, len(child.extra_parameters)
        )

    def get_equation(
        self, lhs_func: sympy.Function, rhs_funcs: Tuple[sympy.Function, ...]
    ) -> sympy.Eq:
        if any(self.extra_parameters):
            raise NotImplementedError(
                "Complement equation is not implemented with extra parameters. "
                "You can fall back on the union equations."
            )
        res = rhs_funcs[0]
        for rhs_func in rhs_funcs[1:]:
            res -= rhs_func
        return sympy.Eq(lhs_func, res)

    def reliance_profile(self, n: int, **parameters: int) -> RelianceProfile:
        raise NotImplementedError

    def get_terms(
        self, parent_terms: Callable[[int], Terms], subterms: SubTerms, n: int
    ) -> Terms:
        parent_terms_mapped: Terms = Counter()
        for param, value in subterms[0](n).items():
            if value:
                parent_terms_mapped[self._parent_param_map(param)] += value
        children_terms = subterms[1:]
        for (idx, child_terms), param_map in zip(
            enumerate(children_terms), self._children_param_maps
        ):
            # we subtract from total
            for param, value in child_terms(n).items():
                mapped_param = self._parent_param_map(param_map(param))
                parent_terms_mapped[mapped_param] -= value
                assert parent_terms_mapped[mapped_param] >= 0
                if parent_terms_mapped[mapped_param] == 0:
                    parent_terms_mapped.pop(mapped_param)

        return parent_terms_mapped

    def get_sub_objects(
        self, subobjs: SubObjects, n: int
    ) -> Iterator[
        Tuple[Parameters, Tuple[List[Optional[CombinatorialObjectType]], ...]]
    ]:
        raise NotImplementedError

    def random_sample_sub_objects(
        self,
        parent_count: int,
        subsamplers: SubSamplers,
        subrecs: SubRecs,
        n: int,
        **parameters: int,
    ) -> Tuple[Optional[CombinatorialObjectType], ...]:
        raise NotImplementedError

    def __str__(self):
        return "complement"
