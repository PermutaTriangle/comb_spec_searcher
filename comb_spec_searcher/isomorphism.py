from itertools import product
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generic,
    Iterator,
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


ObjType1 = TypeVar("ObjType1", bound="CombinatorialObject")
ClassType1 = TypeVar("ClassType1", bound="CombinatorialClass")
ClassType2 = TypeVar("ClassType2", bound="CombinatorialClass")
ObjType2 = TypeVar("ObjType2", bound="CombinatorialObject")
OrderMap = Dict[Tuple[ClassType1, ClassType2], List[int]]
IndexDataMap = Optional[Dict[Tuple[ClassType1, ClassType2], object]]


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
        # The specs
        self._rules1: Dict[
            ClassType1, AbstractRule[ClassType1, ObjType1]
        ] = spec1.rules_dict
        self._rules2: Dict[
            ClassType2, AbstractRule[ClassType2, ObjType2]
        ] = spec2.rules_dict
        self.root1 = spec1.root
        self.root2 = spec2.root

        # Tracking recursion
        self._ancestors: Set[Tuple[ClassType1, ClassType2]] = set()

        # Tracking matchin permutations
        self._order_map: Dict[Tuple[ClassType1, ClassType2], List[int]] = {}

        # Tracking failed matchings
        self._failed: Set[Tuple[ClassType1, ClassType2]] = set()

        # Tracking additional data
        self._index_data: Dict[Tuple[ClassType1, ClassType2], object] = {}

        # Tracking paths in terms of child indices
        self._path_tracker: List[Tuple[Tuple[int, ...], Tuple[int, ...]]] = []

        # Store results
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
    ) -> OrderMap[ClassType1, ClassType2]:
        """Get order map of corresponding nodes."""
        return self._order_map

    def _are_isomorphic(self, node1: ClassType1, node2: ClassType2) -> bool:
        # Both ends of equivilance paths (len = 1 if none)
        eq_path1, eq_path2 = self._get_eq_descendant(node1, node2)

        # The ones that are not on the LHS of equivalence rules
        curr1, curr2 = eq_path1[-1], eq_path2[-1]

        # Rules from curr1 and curr2 to their respective children
        rule1, rule2 = self._rules1[curr1], self._rules2[curr2]

        # Any empty children are ignored
        non_empty_ind1, non_empty_ind2 = (
            tuple(i for i, c in enumerate(rule1.children) if not c.is_empty()),
            tuple(i for i, c in enumerate(rule2.children) if not c.is_empty()),
        )

        # Check for base cases (invalid = -1, valid = 1)
        is_base_case = self._base_cases(
            eq_path1, rule1, non_empty_ind1, eq_path2, rule2, non_empty_ind2
        )
        if is_base_case:
            return bool(is_base_case + 1)

        # Update ancestors for recursion
        self._ancestors.update(product(eq_path1, eq_path2))

        # The number of nonempty children
        n = len(non_empty_ind1)

        # The permutation of matched children indices
        child_order: List[int] = [-1] * n

        # To avoid repeated index pairs, since outside choices have no effect.
        blacklist: Set[Tuple[int, int]] = set()

        # Iterative stack with elements:
        # (index1, index2, indices of the second rule's children already matched)
        stack = [(0, i, {i}) for i in range(n - 1, -1, -1)]

        # Check all pairings of children. Any pairing hat exhaust all nonempty children,
        # such that all are valid will result in current nodes being matched. This is
        # done with backtracking.
        while stack:
            i1, i2, in_use = stack.pop()

            # Already failed
            if (i1, i2) in blacklist:
                continue

            # Track path
            self._path_tracker_push(
                non_empty_ind1[i1],
                non_empty_ind2[i2],
                len(eq_path1) > 1,
                len(eq_path2) > 1,
            )

            # Call _are_isomorphic recursively for current pair
            # and add to blacklist and try again if we fail.
            if not self._are_isomorphic(
                rule1.children[non_empty_ind1[i1]], rule2.children[non_empty_ind2[i2]]
            ):
                blacklist.add((i1, i2))
                self._path_tracker_pop()
                continue
            self._path_tracker_pop()

            # Update permutation
            child_order[i2] = i1

            # If we reach the last index we have succeeded
            if i1 == n - 1:
                self._order_map[(curr1, curr2)] = child_order
                # Since we did not conclude this match by recursion we can remove our
                # current ids from the ancestor set since the next ones we check are
                # not descendants of the current ids (or their equivalences).
                self._ancestors.difference_update(product(eq_path1, eq_path2))
                return True

            # If we have indices to expand, that is done here
            Isomorphism._extend_stack(i1, n, in_use, stack)

        # If stack has been exhausted we have failed to match the ids. We remove them
        # from the ancestors set, memorize the failure and remove any data gathered.
        self._ancestors.difference_update(product(eq_path1, eq_path2))
        self._failed.add((curr1, curr2))
        self._index_data.pop((curr1, curr2), None)
        return False

    def _get_eq_descendant(
        self, node1: ClassType1, node2: ClassType2
    ) -> Tuple[List[ClassType1], List[ClassType2]]:
        """Get path to nodes that are not on the LHS of equivalence rules."""
        rule1, rule2 = self._rules1[node1], self._rules2[node2]
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
        # The ones that are not on the LHS of equivalence rules
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
                if self._atom_match(curr1, curr2, rule1, rule2):
                    return Isomorphism._VALID
            return Isomorphism._INVALID

        # If different type of rules are applied, the trees are not isomorphic
        assert isinstance(rule1, Rule) and isinstance(rule2, Rule)
        if not self._constructor_match(rule1, rule2, curr1, curr2):
            return Isomorphism._INVALID

        # Check for recursive match
        if any((n1, n2) in self._ancestors for n1, n2 in product(eq_nodes1, eq_nodes2)):
            return Isomorphism._VALID

        return Isomorphism._UNKNOWN

    def _path_tracker_push(
        self, c1: int, c2: int, eq_path1: bool, eq_path2: bool
    ) -> None:
        """Store the path being taken."""
        t1 = (0, c1) if eq_path1 else (c1,)
        t2 = (0, c2) if eq_path2 else (c2,)
        self._path_tracker.append((t1, t2))

    def _path_tracker_pop(self) -> None:
        """Remove last stored step in path."""
        self._path_tracker.pop()

    def _atom_match(
        self,
        atom1: ClassType1,
        atom2: ClassType2,
        rule1: AbstractRule[ClassType1, ObjType1],
        rule2: AbstractRule[ClassType2, ObjType2],
    ) -> bool:
        """Returns true if atoms match, false otherwise."""
        # pylint: disable=no-self-use
        sz1 = next(atom1.objects_of_size(atom1.minimum_size_of_object())).size()
        sz2 = next(atom2.objects_of_size(atom2.minimum_size_of_object())).size()
        return sz1 == sz2 and rule1.get_terms(sz1) == rule2.get_terms(sz2)

    def _constructor_match(
        self,
        rule1: Rule[ClassType1, ObjType1],
        rule2: Rule[ClassType2, ObjType2],
        curr1: ClassType1,
        curr2: ClassType2,
    ) -> bool:
        are_eq, data = rule1.constructor.equiv(rule2.constructor)
        if not are_eq:
            return False
        if data is not None:
            self._index_data[(curr1, curr2)] = data
        return True

    @staticmethod
    def _extend_stack(
        i1: int, n: int, in_use: Set[int], stack: List[Tuple[int, int, Set[int]]]
    ) -> None:
        for i in range(n - 1, -1, -1):
            if i in in_use:
                continue
            stack.append((i1 + 1, i, in_use.union({i})))


class ParseTreeMap(Generic[ClassType1, ObjType1, ClassType2, ObjType2]):
    """
    Map the object by creating parse tree for it while mimicking the steps
    in the other specification. Then backward maps are applied in the other
    parse tree to get the object the original will map to.
    """

    @classmethod
    def map(
        cls,
        domain: "CombinatorialSpecification[ClassType1, ObjType1]",
        codomain: "CombinatorialSpecification[ClassType2, ObjType2]",
        get_order: OrderMap[ClassType1, ClassType2],
        index_data: Dict[Tuple[ClassType1, ClassType2], object],
        obj: ObjType1,
    ) -> ObjType2:
        return cls(domain, codomain, get_order, index_data).map_rec(
            obj, domain.root_rule, codomain.root_rule
        )

    def __init__(
        self,
        domain: "CombinatorialSpecification[ClassType1, ObjType1]",
        codomain: "CombinatorialSpecification[ClassType2, ObjType2]",
        get_order: OrderMap[ClassType1, ClassType2],
        index_data: Dict[Tuple[ClassType1, ClassType2], object],
    ) -> None:
        self.domain = domain
        self.codomain = codomain
        self.get_order = get_order
        self.index_data = index_data

    @staticmethod
    def _min_object(rule: AbstractRule[ClassType2, ObjType2]) -> ObjType2:
        """Get min object from rule's parent."""
        obj: ObjType2 = next(
            rule.comb_class.objects_of_size(rule.comb_class.minimum_size_of_object())
        )
        return obj

    def _get_nonempty(
        self, rule: Rule[ClassType1, ObjType1], children: Tuple[Optional[ObjType1], ...]
    ) -> Tuple[Optional[Tuple[ObjType1, AbstractRule[ClassType1, ObjType1]]], ...]:
        """Get the nonempty children for the domain's rule. We gather both the part
        of the mapped object and the class it belongs to."""
        return tuple(
            (child_obj, self.domain.rules_dict[child])
            if child_obj is not None
            else None
            for child, child_obj in zip(rule.children, children)
            if not child.is_empty()
        )

    def map_rec(
        self,
        obj: Optional[ObjType1],
        rule1: AbstractRule[ClassType1, ObjType1],
        rule2: AbstractRule[ClassType2, ObjType2],
    ) -> ObjType2:
        # If atom, we return the minimum object of the corresponding rule.
        if not rule1.children:
            return ParseTreeMap._min_object(rule2)

        assert isinstance(rule1, Rule) and isinstance(rule2, Rule)
        mapped_obj, idx = rule1.indexed_forward_map(obj)

        if rule2.is_equivalence():
            if not rule1.is_equivalence():
                # Backward map the outcome of a recursion when
                # we move one rule further in spec2 only.
                val: ObjType2 = rule2.indexed_backward_map(
                    (
                        self.map_rec(
                            obj, rule1, self.codomain.rules_dict[rule2.children[0]]
                        ),
                    ),
                    idx,
                )
                return val
            # When both are eq-rules, we treat them normally and set matching order
            order: List[int] = [0]
        elif rule1.is_equivalence():
            # If only domain's rule is eq-rule then we don't backward map for the
            # spec2's rule here but move along with the mapped object and next rule
            # and return the outcome directly.
            return self.map_rec(
                mapped_obj[0], self.domain.rules_dict[rule1.children[0]], rule2
            )
        else:
            # Fetch the matching order to know what parts to recurse together.
            order = self.get_order[(rule1.comb_class, rule2.comb_class)]

        # Sort rule1's children to match those of rule 2
        _children = self._get_nonempty(rule1, mapped_obj)
        child_it: Iterator[
            Optional[Tuple[ObjType1, AbstractRule[ClassType1, ObjType1]]]
        ] = (_children[idx] for idx in order)

        # Recurse, when rule2's is not empty and the mapped object corresponding to
        # the rule1's nonempty class is not None and gather the result into a tuple
        # to backward map with rule2.
        val = rule2.indexed_backward_map(
            tuple(
                self.map_rec(c[0][0], c[0][1], c[1])
                if c is not None and c[0] is not None
                else None
                for c in (
                    None
                    if child.is_empty()
                    else (next(child_it), self.codomain.rules_dict[child])
                    for child in rule2.children
                )
            ),
            idx,
            self.index_data.get((rule1.comb_class, rule2.comb_class)),
        )
        return val


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
        get_order: OrderMap[ClassType1, ClassType2],
        index_data: IndexDataMap = None,
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
        """The root class of the first specification."""
        return self._spec

    @property
    def codomain(self) -> "CombinatorialSpecification[ClassType2, ObjType2]":
        """The root class of the second specification."""
        return self._other

    @staticmethod
    def _perm_inv(perm: List[int]) -> List[int]:
        inv = [0] * len(perm)
        for i, v in enumerate(perm):
            inv[v] = i
        return inv

    def map(self, obj: ObjType1) -> ObjType2:
        """Map an object of the domain to an object of the codomain."""
        return ParseTreeMap[ClassType1, ObjType1, ClassType2, ObjType2].map(
            self._spec, self._other, self._get_order, self._index_data, obj
        )

    def inverse_map(self, obj: ObjType2) -> ObjType1:
        """Map an object of the codomain to an object of the domain."""
        # Swap types and use inverse versions of tuple maps
        return ParseTreeMap[ClassType2, ObjType2, ClassType1, ObjType1].map(
            self._other, self._spec, self._get_inverse_order, self._inv_index_data, obj
        )

    def to_jsonable(self) -> dict:
        """Return a JSON serializable dictionary for the bijection."""
        id_map, classes = self._classes_to_array()
        reconstructed_order: Dict[str, Dict[str, List[int]]] = {}
        reconstructed_data: Dict[str, Dict[str, object]] = {}
        Bijection._populate_json_map(self._get_order, reconstructed_order, id_map)
        Bijection._populate_json_map(self._index_data, reconstructed_data, id_map)
        return {
            "spec": self._spec.to_jsonable(),
            "other": self._other.to_jsonable(),
            "order": reconstructed_order,
            "index_data": reconstructed_data,
            "classes": classes,
        }

    def _classes_to_array(self) -> Tuple[Dict[CombinatorialClass, str], List[dict]]:
        """Dump classes into an array with indices as keys to simplify maps."""
        id_map: Dict[CombinatorialClass, str] = {}
        classes: List[dict] = []
        for c1, c2 in self._get_order.keys():
            if c1 not in id_map:
                id_map[c1] = f"{len(classes)}"
                classes.append(c1.to_jsonable())
            if c2 not in id_map:
                id_map[c2] = f"{len(classes)}"
                classes.append(c2.to_jsonable())
        return id_map, classes

    @staticmethod
    def _populate_json_map(
        tuple_map: Dict[Tuple[ClassType1, ClassType2], Any],
        json_map: Dict[str, Dict[str, Any]],
        id_map: Dict[CombinatorialClass, str],
    ) -> None:
        """Convert tuple maps into valid json maps."""
        for (c1, c2), value in tuple_map.items():
            i1, i2 = id_map[c1], id_map[c2]
            if i1 not in json_map:
                json_map[i1] = {i2: value}
            else:
                json_map[i1][i2] = value

    @classmethod
    def from_dict(cls, d) -> "Bijection":
        """Return the bijection with the dictionary outputter by
        the 'to_jsonable' method.
        """
        # pylint: disable=import-outside-toplevel
        from comb_spec_searcher import CombinatorialSpecification

        spec1 = CombinatorialSpecification[ClassType1, ObjType1].from_dict(d["spec"])
        spec2 = CombinatorialSpecification[ClassType2, ObjType2].from_dict(d["other"])
        order = [CombinatorialClass.from_dict(c) for c in d["classes"]]
        get_order = {
            (order[int(idx1)], order[int(idx2)]): lis
            for idx1, sub_map in d["order"].items()
            for idx2, lis in sub_map.items()
        }
        index_data = {
            (order[int(idx1)], order[int(idx2)]): data
            for idx1, sub_map in d["index_data"].items()
            for idx2, data in sub_map.items()
        }
        return cls(spec1, spec2, get_order, index_data)  # type: ignore
