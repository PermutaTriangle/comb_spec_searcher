from itertools import product
from typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Set,
    Tuple,
    TypeVar,
)

from .combinatorial_class import CombinatorialClass
from .strategies.rule import AbstractRule, Rule

if TYPE_CHECKING:
    from .combinatorial_class import CombinatorialObject
    from .specification import CombinatorialSpecification


ClassType1 = TypeVar("ClassType1", bound="CombinatorialClass")
ObjType1 = TypeVar("ObjType1", bound="CombinatorialObject")
ClassType2 = TypeVar("ClassType2", bound="CombinatorialClass")
ObjType2 = TypeVar("ObjType2", bound="CombinatorialObject")
OrderMap = Dict[Tuple[ClassType1, ClassType2], List[int]]


class Isomorphism(Generic[ClassType1, ObjType1, ClassType2, ObjType2]):
    """Isomorphism checker."""

    _INVALID, _UNKNOWN, _VALID = range(-1, 2)

    @classmethod
    def check(
        cls,
        spec1: "CombinatorialSpecification[ClassType1, ObjType1]",
        spec2: "CombinatorialSpecification[ClassType2, ObjType2]",
    ) -> bool:
        """Check if two specs are isomorphic."""
        return cls(spec1, spec2).are_isomorphic()

    def __init__(
        self,
        spec1: "CombinatorialSpecification[ClassType1, ObjType1]",
        spec2: "CombinatorialSpecification[ClassType2, ObjType2]",
    ) -> None:
        self._rules1: Dict[
            ClassType1, AbstractRule[ClassType1, ObjType1]
        ] = spec1.rules_dict
        self._rules2: Dict[
            ClassType2, AbstractRule[ClassType2, ObjType2]
        ] = spec2.rules_dict
        self._ancestors: Set[Tuple[ClassType1, ClassType2]] = set()
        self._order_map: Dict[Tuple[ClassType1, ClassType2], List[int]] = {}
        self._failed: Set[Tuple[ClassType1, ClassType2]] = set()
        self._index_data: Dict[Tuple[ClassType1, ClassType2], object] = {}
        self._isomorphic = self._are_isomorphic(spec1.root, spec2.root)

    def get_order_data(
        self,
    ) -> Dict[Tuple[ClassType1, ClassType2], object]:
        """Return any index data for nonbijective matches."""
        return self._index_data

    def are_isomorphic(self) -> bool:
        """Check if the two specs are isomorphic."""
        return self._isomorphic

    def get_order(
        self,
    ) -> OrderMap:
        """Get order map of corresponding nodes."""
        return self._order_map

    def _are_isomorphic(self, node1: ClassType1, node2: ClassType2) -> bool:
        # If there are equivilances, we use the 'latest' one
        # but we check for recursion for any possible pairing
        eq_path1, eq_path2 = Isomorphism._get_eq_descendant(
            node1, self._rules1, node2, self._rules2
        )
        curr1, curr2 = eq_path1[-1], eq_path2[-1]
        rule1, rule2 = self._rules1[curr1], self._rules2[curr2]

        non_empty_ind1, non_empty_ind2 = (
            tuple(i for i, c in enumerate(rule1.children) if not c.is_empty()),
            tuple(i for i, c in enumerate(rule2.children) if not c.is_empty()),
        )

        is_base_case = self._base_cases(
            eq_path1, rule1, non_empty_ind1, eq_path2, rule2, non_empty_ind2
        )
        if is_base_case:
            return bool(is_base_case + 1)

        self._ancestors.update(product(eq_path1, eq_path2))

        # Check all matches of children, if any are valid then trees are isomorphic
        n = len(non_empty_ind1)
        child_order: List[int] = [-1] * n
        stack = [(0, i, {i}) for i in range(n - 1, -1, -1)]
        blacklist: Set[Tuple[int, int]] = set()
        while stack:
            i1, i2, in_use = stack.pop()
            if (i1, i2) in blacklist:
                continue
            if not self._are_isomorphic(
                rule1.children[non_empty_ind1[i1]], rule2.children[non_empty_ind2[i2]]
            ):
                blacklist.add((i1, i2))
                continue
            child_order[i2] = i1
            if i1 == n - 1:
                self._order_map[(curr1, curr2)] = child_order
                self._ancestors.difference_update(product(eq_path1, eq_path2))
                return True
            Isomorphism._extend_stack(i1, n, in_use, stack)
        self._ancestors.difference_update(product(eq_path1, eq_path2))
        self._failed.add((curr1, curr2))
        self._index_data.pop((curr1, curr2), None)
        return False

    @staticmethod
    def _get_eq_descendant(
        node1: ClassType1,
        rules1: Dict[ClassType1, AbstractRule[ClassType1, ObjType1]],
        node2: ClassType2,
        rules2: Dict[ClassType2, AbstractRule[ClassType2, ObjType2]],
    ) -> Tuple[List[ClassType1], List[ClassType2]]:
        rule1, rule2 = rules1[node1], rules2[node2]
        nodes1, nodes2 = [node1], [node2]
        if rule1.is_equivalence():
            nodes1.append(rule1.children[0])
        if rule2.is_equivalence():
            nodes2.append(rule2.children[0])
        return nodes1, nodes2

    def _base_cases(
        self,
        eq_nodes1: List[ClassType1],
        rule1: AbstractRule[ClassType1, ObjType1],
        non_empty_children1: Tuple[int, ...],
        eq_nodes2: List[ClassType2],
        rule2: AbstractRule[ClassType2, ObjType2],
        non_empty_children2: Tuple[int, ...],
    ) -> int:
        curr1, curr2 = eq_nodes1[-1], eq_nodes2[-1]

        # Already matched
        if (curr1, curr2) in self._order_map:
            return Isomorphism._VALID

        # Already failed
        if (curr1, curr2) in self._failed:
            return Isomorphism._INVALID

        # If different number of non-empty children
        if len(non_empty_children1) != len(non_empty_children2):
            return Isomorphism._INVALID

        # Atoms
        if not rule1.children and not rule2.children:
            if curr1.is_atom() and curr2.is_atom():
                sz1 = next(curr1.objects_of_size(curr1.minimum_size_of_object())).size()
                sz2 = next(curr2.objects_of_size(curr2.minimum_size_of_object())).size()
                if sz1 == sz2 and rule1.get_terms(sz1) == rule2.get_terms(sz2):
                    return Isomorphism._VALID
            return Isomorphism._INVALID

        # If different type of rules are applied, the trees are not isomorphic
        assert isinstance(rule1, Rule) and isinstance(rule2, Rule)
        are_eq, data = rule1.constructor.equiv(rule2.constructor)
        if not are_eq:
            return Isomorphism._INVALID
        if data is not None:
            self._index_data[(curr1, curr2)] = data

        # Check for recursive match
        if any((n1, n2) in self._ancestors for n1, n2 in product(eq_nodes1, eq_nodes2)):
            return Isomorphism._VALID

        return Isomorphism._UNKNOWN

    @staticmethod
    def _extend_stack(
        i1: int, n: int, in_use: Set[int], stack: List[Tuple[int, int, Set[int]]]
    ) -> None:
        for i in range(n - 1, -1, -1):
            if i in in_use:
                continue
            stack.append((i1 + 1, i, in_use.union({i})))


class Node(Generic[ClassType1, ObjType1, ClassType2, ObjType2]):
    """Parse tree node."""

    def __init__(
        self,
        rule: AbstractRule[ClassType1, ObjType1],
        obj: ObjType1,
        get_rule: Callable[[ClassType1], AbstractRule[ClassType1, ObjType1]],
    ):
        self.obj = obj
        self._rule = rule
        if not rule.children:
            self._children: Tuple[
                Optional["Node[ClassType1, ObjType1, ClassType2, ObjType2]"], ...
            ] = tuple()
        else:
            assert isinstance(rule, Rule)
            children, self.idx = rule.indexed_forward_map(obj)
            self._children = tuple(
                type(self)(get_rule(child), child_obj, get_rule)
                if child_obj is not None
                else None
                for child, child_obj in zip(rule.children, children)
                if not child.is_empty()
            )

    def build_obj(
        self,
        rule: AbstractRule[ClassType2, ObjType2],
        get_order: OrderMap,
        get_rule: Callable[[ClassType2], AbstractRule[ClassType2, ObjType2]],
        index_data: Dict[Tuple[ClassType1, ClassType2], object],
    ) -> ObjType2:
        """Parse tree's recursive build object function."""

        if not self._children:
            # TODO: stop special casing verification rules!
            obj: ObjType2 = next(
                rule.comb_class.objects_of_size(
                    rule.comb_class.minimum_size_of_object()
                )
            )
            return obj
        if rule.is_equivalence():
            if not self._rule.is_equivalence():
                assert isinstance(rule, Rule)
                val: ObjType2 = rule.indexed_backward_map(
                    (
                        self.build_obj(
                            get_rule(rule.children[0]), get_order, get_rule, index_data
                        ),
                    ),
                    self.idx,
                )
                return val
            order = [0]
        elif self._rule.is_equivalence():
            assert self._children[0] is not None
            return self._children[0].build_obj(rule, get_order, get_rule, index_data)
        else:
            order = get_order[(self._rule.comb_class, rule.comb_class)]
        children = (self._children[idx] for idx in order)
        assert isinstance(rule, Rule)
        val = rule.indexed_backward_map(
            tuple(
                c[0].build_obj(get_rule(c[1]), get_order, get_rule, index_data)
                if c is not None and c[0] is not None
                else None
                for c in (
                    None if child.is_empty() else (next(children), child)
                    for child in rule.children
                )
            ),
            self.idx,
            index_data.get((self._rule.comb_class, rule.comb_class)),
        )
        return val


class ParseTree(Generic[ClassType1, ObjType1, ClassType2, ObjType2]):
    """Parse tree that parses an object and can reconstruct it for the other
    specification."""

    def __init__(
        self, obj: ObjType1, spec: "CombinatorialSpecification[ClassType1, ObjType1]"
    ):
        self._root = Node[ClassType1, ObjType1, ClassType2, ObjType2](
            spec.root_rule, obj, spec.get_rule
        )

    def build_obj(
        self,
        root: AbstractRule[ClassType2, ObjType2],
        get_order: OrderMap,
        get_rule: Callable[[ClassType2], AbstractRule[ClassType2, ObjType2]],
        index_data: Dict[Tuple[ClassType1, ClassType2], object],
    ) -> ObjType2:
        """Build object from the other specification."""
        return self._root.build_obj(root, get_order, get_rule, index_data)


class Bijection(Generic[ClassType1, ObjType1, ClassType2, ObjType2]):
    """A bijection object that contains a map between two specifications."""

    @classmethod
    def construct(
        cls,
        spec: "CombinatorialSpecification[ClassType1, ObjType1]",
        other: "CombinatorialSpecification[ClassType2, ObjType2]",
    ) -> Optional["Bijection[ClassType1, ObjType1, ClassType2, ObjType2]"]:
        """Create a bijection object between two specifications if possible."""
        iso = Isomorphism[ClassType1, ObjType1, ClassType2, ObjType2](spec, other)
        if not iso.are_isomorphic():
            return None
        return cls(spec, other, iso.get_order(), iso.get_order_data())

    def __init__(
        self,
        spec: "CombinatorialSpecification[ClassType1, ObjType1]",
        other: "CombinatorialSpecification[ClassType2, ObjType2]",
        get_order: OrderMap,
        index_data: Optional[Dict[Tuple[ClassType1, ClassType2], object]] = None,
    ):
        self._index_data = {} if index_data is None else index_data
        self._inv_index_data = {
            (t2, t1): data for (t1, t2), data in self._index_data.items()
        }
        self._spec = spec
        self._other = other
        self._get_order = get_order
        self._get_inverse_order = {
            (c2, c1): Bijection._perm_inv(lis) for ((c1, c2), lis) in get_order.items()
        }

    @property
    def domain(self) -> "CombinatorialSpecification[ClassType1, ObjType1]":
        return self._spec

    @property
    def codomain(self) -> "CombinatorialSpecification[ClassType2, ObjType2]":
        return self._other

    @staticmethod
    def _perm_inv(perm: List[int]) -> List[int]:
        inv = [0] * len(perm)
        for i, v in enumerate(perm):
            inv[v] = i
        return inv

    def map(self, obj: ObjType1) -> ObjType2:
        """Map an object of the root of one specification to the root of the other."""
        parse_tree = ParseTree[ClassType1, ObjType1, ClassType2, ObjType2](
            obj, self._spec
        )
        return parse_tree.build_obj(
            self._other.root_rule,
            self._get_order,
            self._other.get_rule,
            self._index_data,
        )

    def inverse_map(self, obj: ObjType2) -> ObjType1:
        parse_tree = ParseTree[ClassType2, ObjType2, ClassType1, ObjType1](
            obj, self._other
        )
        return parse_tree.build_obj(
            self._spec.root_rule,
            self._get_inverse_order,
            self._spec.get_rule,
            self._inv_index_data,
        )

    def to_jsonable(self) -> dict:
        """Return a JSON serializable dictionary for the bijection."""
        id_map: Dict[CombinatorialClass, str] = {}
        classes: List[dict] = []
        for c1, c2 in self._get_order.keys():
            if c1 not in id_map:
                id_map[c1] = f"{len(classes)}"
                classes.append(c1.to_jsonable())
            if c2 not in id_map:
                id_map[c2] = f"{len(classes)}"
                classes.append(c2.to_jsonable())

        reconstructed_map: Dict[str, Dict[str, List[int]]] = {}
        for (c1, c2), lis in self._get_order.items():
            i1, i2 = id_map[c1], id_map[c2]
            if i1 not in reconstructed_map:
                reconstructed_map[i1] = {i2: lis}
            else:
                reconstructed_map[i1][i2] = lis
        # TODO: index order data
        return {
            "spec": self._spec.to_jsonable(),
            "other": self._other.to_jsonable(),
            "order": reconstructed_map,
            "classes": classes,
        }

    @classmethod
    def from_dict(cls, d) -> "Bijection":
        """Return the bijection with the dictionary outputter by
        the 'to_jsonable' method.
        """
        # pylint: disable=import-outside-toplevel
        from comb_spec_searcher import CombinatorialSpecification

        spec1 = CombinatorialSpecification.from_dict(d["spec"])
        spec2 = CombinatorialSpecification.from_dict(d["other"])
        order = [CombinatorialClass.from_dict(c) for c in d["classes"]]
        get_order = {
            (order[int(idx1)], order[int(idx2)]): lis
            for idx1, sub_map in d["order"].items()
            for idx2, lis in sub_map.items()
        }
        # TODO: index order data
        return cls(spec1, spec2, get_order)
