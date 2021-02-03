from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Set, Tuple

from .combinatorial_class import CombinatorialClass, CombinatorialObject
from .strategies.rule import AbstractRule, Rule

if TYPE_CHECKING:
    from .specification import CombinatorialSpecification


AtomEquals = Callable[["CombinatorialClass", "CombinatorialClass"], bool]


def _default_equals(c1: CombinatorialClass, c2: CombinatorialClass) -> bool:
    return c1 == c2


class Isomorphism:
    """Isomorphism checker."""

    _INVALID, _UNKNOWN, _VALID = range(-1, 2)

    @classmethod
    def check(
        cls,
        spec1: "CombinatorialSpecification",
        spec2: "CombinatorialSpecification",
        eq: AtomEquals = _default_equals,
    ) -> bool:
        """Check if two specs are isomorphic."""
        return cls(spec1, spec2, eq).are_isomorphic()

    def __init__(
        self,
        spec1: "CombinatorialSpecification",
        spec2: "CombinatorialSpecification",
        eq: AtomEquals = _default_equals,
    ) -> None:
        self._eq = eq
        self._index = 0
        self._root1: CombinatorialClass = spec1.root
        self._rules1: Dict[CombinatorialClass, AbstractRule] = spec1.rules_dict
        self._ancestors1: Dict[CombinatorialClass, int] = {}
        self._root2: CombinatorialClass = spec2.root
        self._rules2: Dict[CombinatorialClass, AbstractRule] = spec2.rules_dict
        self._ancestors2: Dict[CombinatorialClass, int] = {}
        self._order_map: Dict[
            Tuple[CombinatorialClass, CombinatorialClass], List[int]
        ] = {}
        self._isomorphic = self._are_isomorphic(self._root1, self._root2)

    def are_isomorphic(self) -> bool:
        """Check if the two specs are isomorphic."""
        return self._isomorphic

    def get_order(
        self,
    ) -> Dict[Tuple[CombinatorialClass, CombinatorialClass], List[int]]:
        """Get order map of corresponding nodes."""
        return self._order_map

    def _are_isomorphic(
        self, node1: CombinatorialClass, node2: CombinatorialClass
    ) -> bool:
        # If there are equivilances, we use the 'latest' one
        node1, node2 = Isomorphism._get_eq_descendant(
            node1, self._rules1, node2, self._rules2
        )
        rule1, rule2 = self._rules1[node1], self._rules2[node2]

        non_empty_ind1, non_empty_ind2 = (
            tuple(i for i, c in enumerate(rule1.children) if not c.is_empty()),
            tuple(i for i, c in enumerate(rule2.children) if not c.is_empty()),
        )

        is_base_case = self._base_cases(
            node1, rule1, non_empty_ind1, node2, rule2, non_empty_ind2
        )
        if is_base_case:
            return bool(is_base_case + 1)

        self._index += 1
        self._ancestors1[node1], self._ancestors2[node2] = (self._index, self._index)

        # Check all matches of children, if any are valid then trees are isomorphic
        n = len(non_empty_ind1)
        child_order: List[int] = [-1] * n
        stack = [(0, i, {i}) for i in range(n - 1, -1, -1)]
        while stack:
            i1, i2, in_use = stack.pop()
            if not self._are_isomorphic(
                rule1.children[non_empty_ind1[i1]], rule2.children[non_empty_ind2[i2]]
            ):
                continue
            child_order[i1] = i2
            if i1 == n - 1:
                self._order_map[(node1, node2)] = child_order
                self._cleanup(node1, node2)
                return True
            Isomorphism._extend_stack(i1, n, in_use, stack)

        self._cleanup(node1, node2)
        return False

    @staticmethod
    def _get_eq_descendant(
        node1: CombinatorialClass,
        rules1: Dict[CombinatorialClass, AbstractRule],
        node2: CombinatorialClass,
        rules2: Dict[CombinatorialClass, AbstractRule],
    ) -> Tuple[CombinatorialClass, CombinatorialClass]:
        rule1, rule2 = rules1[node1], rules2[node2]

        if rule2.is_equivalence():
            node2 = rule2.children[0]

        if rule1.is_equivalence():
            node1 = rule1.children[0]

        return node1, node2

    def _base_cases(
        self,
        node1: CombinatorialClass,
        rule1: AbstractRule,
        nec1: Tuple[int, ...],
        node2: CombinatorialClass,
        rule2: AbstractRule,
        nec2: Tuple[int, ...],
    ) -> int:
        # If different number of children
        if len(nec1) != len(nec2):
            return Isomorphism._INVALID

        # If leaf that has no equal-ancestors
        if not rule1.children and not rule2.children:
            # If one is atom, both should be and should also be equal
            if node1.is_atom() and node2.is_atom() and self._eq(node1, node2):
                return Isomorphism._VALID
            return Isomorphism._INVALID

        # If different type of rules are applied, the trees are not isomorphic
        # TODO: Use == when implemented
        assert isinstance(rule1, Rule) and isinstance(rule2, Rule)
        if rule1.constructor.__class__ != rule2.constructor.__class__:
            return Isomorphism._INVALID

        # Check if we have seen this node before
        ind1, ind2 = self._ancestors1.get(node1, -1), self._ancestors2.get(node2, -1)

        # If one is found and the other not or if
        # they occured in different places before
        if ind1 != ind2:
            return Isomorphism._INVALID

        # If they have occured before and that occurrence matches in both trees
        if ind1 == ind2 != -1:
            return Isomorphism._VALID

        return Isomorphism._UNKNOWN

    def _cleanup(self, node1: CombinatorialClass, node2: CombinatorialClass) -> None:
        self._index -= 1
        del self._ancestors1[node1]
        del self._ancestors2[node2]

    @staticmethod
    def _extend_stack(
        i1: int, n: int, in_use: Set[int], stack: List[Tuple[int, int, Set[int]]]
    ) -> None:
        for i in range(n - 1, -1, -1):
            if i in in_use:
                continue
            stack.append((i1 + 1, i, in_use.union({i})))


class Node:
    """Parse tree node."""

    def __init__(
        self,
        rule: AbstractRule,
        obj: CombinatorialObject,
        get_rule: Callable[[CombinatorialClass], AbstractRule],
    ):
        self.rule = rule
        self.obj = obj
        if not rule.children:
            self.children: Tuple[Optional["Node"], ...] = tuple()
        else:
            assert isinstance(rule, Rule)
            self.children = (
                tuple(
                    type(self)(get_rule(child), child_obj, get_rule)
                    if child_obj is not None
                    else None
                    for child, child_obj in zip(rule.children, rule.forward_map(obj))
                    if not child.is_empty()
                )
                if rule.children
                else tuple()
            )

    def build_obj(
        self,
        rule: AbstractRule,
        get_order: Dict[Tuple[CombinatorialClass, CombinatorialClass], List[int]],
        get_rule: Callable[[CombinatorialClass], AbstractRule],
    ) -> CombinatorialObject:
        """Parse tree's recursive build object function."""
        if not self.children:
            # TODO: stop special casing verification rules!
            obj: CombinatorialObject = next(
                rule.comb_class.objects_of_size(
                    rule.comb_class.minimum_size_of_object()
                )
            )
            return obj
        if rule.is_equivalence():
            if not self.rule.is_equivalence():
                return self.build_obj(get_rule(rule.children[0]), get_order, get_rule)
            order = [0]
        elif self.rule.is_equivalence():
            assert self.children[0] is not None
            return self.children[0].build_obj(rule, get_order, get_rule)
        else:
            order = get_order[(self.rule.comb_class, rule.comb_class)]
        children = tuple(self.children[idx] for idx in order)
        child_objs = tuple(
            None
            if child is None
            else child.build_obj(get_rule(child_class), get_order, get_rule)
            for child, child_class in zip(
                children, (c for c in rule.children if not c.is_empty())
            )
        )
        assert isinstance(rule, Rule)
        val: CombinatorialObject = next(rule.backward_map(child_objs))
        return val


class ParseTree:
    """Parse tree that parses an object and can reconstruct it for the other
    specification."""

    def __init__(self, obj: CombinatorialObject, spec: "CombinatorialSpecification"):
        self.root = Node(spec.root_rule, obj, spec.get_rule)

    def build_obj(
        self,
        root: AbstractRule,
        get_order: Dict[Tuple[CombinatorialClass, CombinatorialClass], List[int]],
        get_rule: Callable[[CombinatorialClass], AbstractRule],
    ) -> CombinatorialObject:
        """Build object from the other specification."""
        return self.root.build_obj(root, get_order, get_rule)


class Bijection:
    """A bijection object that contains a map between two specifications."""

    @classmethod
    def construct(
        cls,
        spec: "CombinatorialSpecification",
        other: "CombinatorialSpecification",
        eq: AtomEquals = _default_equals,
    ) -> Optional["Bijection"]:
        """Create a bijection object between two specifications if possible.

        raises: ValueError if specifications are not isomorphic.
        """
        iso = Isomorphism(spec, other, eq)
        if not iso.are_isomorphic():
            return None
        return cls(spec, other, iso.get_order())

    def __init__(
        self,
        spec: "CombinatorialSpecification",
        other: "CombinatorialSpecification",
        get_order: Dict[Tuple[CombinatorialClass, CombinatorialClass], List[int]],
    ):
        self.spec = spec
        self.other = other
        self.get_order = get_order
        self.get_inverse_order = {
            (c2, c1): Bijection._perm_inv(lis)
            for ((c1, c2), lis) in self.get_order.items()
        }

    @staticmethod
    def _perm_inv(perm: List[int]) -> List[int]:
        inv = [0] * len(perm)
        for i, v in enumerate(perm):
            inv[v] = i
        return inv

    def map(self, obj: CombinatorialObject) -> CombinatorialObject:
        """Map an object of the root of one specification to the root of the other."""
        parse_tree = ParseTree(obj, self.spec)
        return parse_tree.build_obj(
            self.other.root_rule, self.get_order, self.other.get_rule
        )

    def inverse_map(self, obj: CombinatorialObject) -> CombinatorialObject:
        parse_tree = ParseTree(obj, self.other)
        return parse_tree.build_obj(
            self.spec.root_rule, self.get_inverse_order, self.spec.get_rule
        )

    def to_jsonable(self) -> dict:
        """Return a JSON serializable dictionary for the bijection."""
        id_map: Dict[CombinatorialClass, str] = {}
        classes: List[dict] = []
        for c1, c2 in self.get_order.keys():
            if c1 not in id_map:
                id_map[c1] = f"{len(classes)}"
                classes.append(c1.to_jsonable())
            if c2 not in id_map:
                id_map[c2] = f"{len(classes)}"
                classes.append(c2.to_jsonable())

        reconstructed_map: Dict[str, Dict[str, List[int]]] = {}
        for (c1, c2), lis in self.get_order.items():
            i1, i2 = id_map[c1], id_map[c2]
            if i1 not in reconstructed_map:
                reconstructed_map[i1] = {i2: lis}
            else:
                reconstructed_map[i1][i2] = lis
        return {
            "spec": self.spec.to_jsonable(),
            "other": self.other.to_jsonable(),
            "order": reconstructed_map,
            "classes": classes,
        }

    @classmethod
    def from_dict(cls, d):
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
        return cls(spec1, spec2, get_order)
