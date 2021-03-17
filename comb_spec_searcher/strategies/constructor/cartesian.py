import random
from collections import defaultdict
from itertools import product
from typing import (
    Callable,
    Counter,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
    cast,
)

import sympy

from comb_spec_searcher import utils
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

T = TypeVar("T")


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
        self._children_param_maps = self._build_children_param_map(
            parent, children, self.extra_parameters
        )

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

    @property
    def min_sizes(self) -> Tuple[int, ...]:
        """
        Lower bound on the sizes of combinatorial object on the children.
        """
        return tuple(d["n"] for d in self.min_child_sizes)

    @property
    def max_sizes(self) -> Tuple[Optional[int], ...]:
        """
        Upper bounds on the size of object on the children.

        None means no upper bound.
        """
        return tuple(d.get("n", None) for d in self.max_child_sizes)

    @staticmethod
    def _build_children_param_map(
        parent: CombinatorialClassType,
        children: Tuple[CombinatorialClassType, ...],
        extra_parameters: Tuple[Dict[str, str], ...],
    ) -> Tuple[ParametersMap, ...]:
        map_list: List[ParametersMap] = []
        num_parent_params = len(parent.extra_parameters)
        parent_param_to_pos = {
            param: pos for pos, param in enumerate(parent.extra_parameters)
        }
        for child, extra_param in zip(children, extra_parameters):
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
                Constructor.build_param_map(child_pos_to_parent_pos, num_parent_params)
            )
        return tuple(map_list)

    def get_equation(
        self, lhs_func: sympy.Function, rhs_funcs: Tuple[sympy.Function, ...]
    ) -> sympy.Eq:
        res = 1
        for extra_parameters, rhs_func in zip(self.extra_parameters, rhs_funcs):
            res *= rhs_func.subs(
                {child: parent for parent, child in extra_parameters.items()},
                simultaneous=True,
            )
        return sympy.Eq(lhs_func, res)

    def reliance_profile(self, n: int, **parameters: int) -> RelianceProfile:
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

    def get_terms(
        self, parent_terms: Callable[[int], Terms], subterms: SubTerms, n: int
    ) -> Terms:
        new_terms: Terms = Counter()
        size_compositions = utils.compositions(
            n, len(subterms), self.min_sizes, self.max_sizes
        )
        for sizes in size_compositions:
            for param_value_pairs in self.params_value_pairs_combinations(
                sizes, subterms
            ):
                new_param = self._new_param(*(p for p, _ in param_value_pairs))
                new_terms[new_param] += utils.prod((v for _, v in param_value_pairs))
        return new_terms

    def _new_param(self, *children_params: Parameters) -> Parameters:
        """
        Computes the parameter values on the parent that the given children parameters
        contribute to.
        """
        mapped_params = (
            pmap(p) for pmap, p in zip(self._children_param_maps, children_params)
        )
        return tuple(sum(vals) for vals in zip(*mapped_params))

    @staticmethod
    def params_value_pairs_combinations(
        sizes: Tuple[int, ...],
        sub_getters: Tuple[Callable[[int], Dict[Parameters, T]], ...],
    ) -> Iterator[Tuple[Tuple[Parameters, T], ...]]:
        assert len(sizes) == len(sub_getters), sub_getters
        children_values = (sg(s) for sg, s in zip(sub_getters, sizes))
        return product(*(c.items() for c in children_values))

    def get_sub_objects(
        self, subobjs: SubObjects, n: int
    ) -> Iterator[
        Tuple[Parameters, Tuple[List[Optional[CombinatorialObjectType]], ...]]
    ]:
        size_compositions = utils.compositions(
            n, len(subobjs), self.min_sizes, self.max_sizes
        )
        for sizes in size_compositions:
            for param_objs_pairs in self.params_value_pairs_combinations(
                sizes, subobjs
            ):
                new_param = self._new_param(*(p for p, _ in param_objs_pairs))
                children_objs = cast(
                    Iterator[List[Optional[CombinatorialObjectType]]],
                    (objs for _, objs in param_objs_pairs),
                )
                yield (new_param, tuple(children_objs))

    def random_sample_sub_objects(
        self,
        parent_count: int,
        subsamplers: SubSamplers,
        subrecs: SubRecs,
        n: int,
        **parameters: int,
    ) -> Tuple[Optional[CombinatorialObjectType], ...]:
        random_choice = random.randint(1, parent_count)
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

    def __eq__(self, obj: object) -> bool:
        return isinstance(obj, type(self))

    def __hash__(self) -> int:
        return hash(type(self))


class Quotient(Constructor[CombinatorialClassType, CombinatorialObjectType]):
    """
    This constructor implements the quotient operation. A rule A -> (B, C, D)
    should be read as A = B / (C * D).

    This comes from a cartesian product rule B = A * C * D

    The initialiser should be made using the original cartesian product rule.

    The parent is B, idx is the index of the child the rule is being rearranged
    for and the extra parameters maps from parent to children.

    To get terms we compute a polynomial equation for a fixed size a_n(x,...) =
    b_n(x,...) * c(x, ...) where b_n is the terms for the flipped child of length n and
    then make the division.
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
            self.extra_parameters = tuple(extra_parameters)
        else:
            self.extra_parameters = tuple(dict() for _ in children)
        self.idx = idx
        self._children_param_maps = CartesianProduct._build_children_param_map(
            parent, children, self.extra_parameters
        )
        self._min_sizes = tuple(child.minimum_size_of_object() for child in children)
        self._max_sizes = tuple(
            child.minimum_size_of_object() if child.is_atom() else None
            for child in children
        )
        self._parent_param_map = self._build_parent_param_map(parent, children)
        self._parent_shift = sum(self._min_sizes) - self._min_sizes[self.idx]
        self._num_parent_params = len(parent.extra_parameters)

    @staticmethod
    def build_param_map(
        child_pos_to_parent_pos: Tuple[Tuple[int, ...], ...], num_parent_params: int
    ) -> ParametersMap:
        def param_map(param: Parameters) -> Parameters:
            new_params: List[Optional[int]] = [None for _ in range(num_parent_params)]
            for pos, value in enumerate(param):
                parent_pos = child_pos_to_parent_pos[pos]
                for p in parent_pos:
                    assert new_params[p] is None or new_params[p] == value
                    new_params[p] = value
            assert all(p is not None for p in new_params)
            return cast(Parameters, tuple(new_params))

        return param_map

    def _build_parent_param_map(
        self,
        parent: CombinatorialClassType,
        children: Tuple[CombinatorialClassType, ...],
    ) -> ParametersMap:
        extra_param = self.extra_parameters[self.idx]
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

    def _new_param(self, *children_params: Parameters) -> Parameters:
        """
        Computes the parameter values on the parent that the given children parameters
        contribute to.
        """
        mapped_params = (
            pmap(p) for pmap, p in zip(self._children_param_maps, children_params)
        )
        return tuple(sum(vals) for vals in zip(*mapped_params))

    def _other_new_param(self, *children_params: Parameters) -> Parameters:
        """
        Computes the parameter values on the parent that the given children parameters
        contribute to.
        """
        mapped_params = (
            pmap(p)
            for pmap, p in zip(
                (m for i, m in enumerate(self._children_param_maps) if i != self.idx),
                children_params,
            )
        )
        return tuple(sum(vals) for vals in zip(*mapped_params))

    def _a(
        self,
        n: int,
        parent_subterm: Callable[[int], Terms],
        children_subterms: SubTerms,
    ) -> Terms:
        """
        A terms dict representing the polynomial for the rule parent terms minus the
        contribution of the childs when the size of the flipped child in the composition
        is smaller than n.
        """
        max_sizes = (
            self._max_sizes[: self.idx] + (n - 1,) + self._max_sizes[self.idx + 1 :]
        )
        possible_sizes = utils.compositions(
            n + self._parent_shift, self.number_of_children, self._min_sizes, max_sizes
        )
        res: Terms = Counter(parent_subterm(n + self._parent_shift))
        for sizes in possible_sizes:
            for param_value_pairs in CartesianProduct.params_value_pairs_combinations(
                sizes, children_subterms
            ):
                new_param = self._new_param(*(p for p, _ in param_value_pairs))
                res[new_param] -= utils.prod((v for _, v in param_value_pairs))
                assert res[new_param] >= 0
        return res

    def _c(
        self,
        children_subterms: SubTerms,
    ) -> Terms:
        """
        Dict representing the polynomial that multiply the polynomial of the
        flipped child for length n.
        """
        min_sizes = self._min_sizes[: self.idx] + self._min_sizes[self.idx + 1 :]
        max_sizes = self._max_sizes[: self.idx] + self._max_sizes[self.idx + 1 :]
        possible_sizes = utils.compositions(
            self._parent_shift, self.number_of_children - 1, min_sizes, max_sizes
        )
        other_children_subterms = (
            children_subterms[: self.idx] + children_subterms[self.idx + 1 :]
        )
        res: Terms = Counter()
        for sizes in possible_sizes:
            for param_value_pairs in CartesianProduct.params_value_pairs_combinations(
                sizes, other_children_subterms
            ):
                new_param = self._other_new_param(*(p for p, _ in param_value_pairs))
                res[new_param] += utils.prod((v for _, v in param_value_pairs))
                assert res[new_param] >= 0
        return res

    def _terms_to_poly(self, terms: Terms) -> Union[sympy.Poly, int]:
        variables = tuple(sympy.var(f"k_{i}") for i in range(self._num_parent_params))
        if variables:
            res = sympy.Poly(sympy.sympify("0"), *variables)
        else:
            res = 0
        for param, value in terms.items():
            if not variables:
                res += value
            else:
                res += value * utils.prod(
                    var ** power for var, power in zip(variables, param)
                )
        return res

    @staticmethod
    def _poly_to_terms(poly: Union[sympy.Poly, int]) -> Terms:
        if isinstance(poly, int):
            if poly == 0:
                return Counter()
            return Counter({tuple(): poly})
        return Counter(poly.as_dict())

    def _b(
        self,
        n: int,
        parent_subterm: Callable[[int], Terms],
        children_subterms: SubTerms,
    ) -> Terms:
        """
        The terms of length n for the flipped child.
        """
        a = self._a(n, parent_subterm, children_subterms)
        c = self._c(children_subterms)
        a_poly = self._terms_to_poly(a)
        c_poly = self._terms_to_poly(c)
        if self._num_parent_params > 0:
            b_poly, remainder = sympy.div(a_poly, c_poly, domain="ZZ")
            assert remainder == 0
        else:
            b_poly = a_poly // c_poly
            assert a_poly % c_poly == 0
        return self._poly_to_terms(b_poly)

    def get_terms(
        self, parent_terms: Callable[[int], Terms], subterms: SubTerms, n: int
    ) -> Terms:
        new_terms: Terms = Counter()
        children_subterms = (
            subterms[1 : self.idx + 1] + (parent_terms,) + subterms[self.idx + 1 :]
        )
        for param, value in self._b(n, subterms[0], children_subterms).items():
            mapped_params = self._parent_param_map(param)
            assert mapped_params not in new_terms or new_terms[mapped_params] == value
            new_terms[mapped_params] = value
        return new_terms

    def get_equation(
        self, lhs_func: sympy.Function, rhs_funcs: Tuple[sympy.Function, ...]
    ) -> sympy.Eq:
        res = lhs_func.subs(self.extra_parameters[self.idx])
        for (idx, rhs_func), extra_parameters in zip(
            enumerate(rhs_funcs), self.extra_parameters
        ):
            if self.idx != idx:
                res /= rhs_func.subs(
                    {child: parent for parent, child in extra_parameters.items()},
                    simultaneous=True,
                ).subs(self.extra_parameters[self.idx], simultaneous=True)
        return sympy.Eq(rhs_funcs[self.idx], res)

    def reliance_profile(self, n: int, **parameters: int) -> RelianceProfile:
        raise NotImplementedError

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
        return "quotient"

    def __eq__(self, obj: object) -> bool:
        return isinstance(obj, type(self))

    def __hash__(self) -> int:
        return hash(type(self))
