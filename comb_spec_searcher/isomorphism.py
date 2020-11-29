from typing import TYPE_CHECKING, Dict, List, Set, Tuple

from .combinatorial_class import CombinatorialClass
from .strategies.rule import AbstractRule

if TYPE_CHECKING:
    from .specification import CombinatorialSpecification


class Isomorphism:
    """Isomorphism checker."""

    _INVALID, _UNKNOWN, _VALID = range(-1, 2)

    def __init__(
        self, spec1: "CombinatorialSpecification", spec2: "CombinatorialSpecification"
    ) -> None:
        self._index = 0
        self._root1: CombinatorialClass = spec1.root
        self._rules1: Dict[CombinatorialClass, AbstractRule] = spec1.rules_dict
        self._ancestors1: Dict[CombinatorialClass, int] = {}
        self._root2: CombinatorialClass = spec2.root
        self._rules2: Dict[CombinatorialClass, AbstractRule] = spec2.rules_dict
        self._ancestors2: Dict[CombinatorialClass, int] = {}
        self.eq_map: Dict[CombinatorialClass, AbstractRule] = {}
        self._iso_label: int = 1
        self.iso_labels: Dict[CombinatorialClass, List[int]] = {}
        self.iso_labels_to_rules: Dict[int, Tuple[AbstractRule, List[int]]] = {}

    def are_isomorphic(self) -> bool:
        """Check if the two specs are isomorphic."""
        return self._are_isomorphic(self._root1, self._root2, 0)

    def _are_isomorphic(
        self, node1: CombinatorialClass, node2: CombinatorialClass, iso_label: int
    ) -> bool:
        # If there are equivilances, we use the 'latest' one
        node1, node2 = Isomorphism._get_eq_descendant(
            node1, self._rules1, node2, self._rules2, self.eq_map
        )
        rule1, rule2 = self._rules1[node1], self._rules2[node2]

        is_base_case = self._base_cases(node1, rule1, node2, rule2)
        if is_base_case:
            return bool(is_base_case + 1)

        self._index += 1
        self._ancestors1[node1], self._ancestors2[node2] = (self._index, self._index)

        # Check all matches of children, if any are valid then trees are isomorphic
        n = len(rule1.children)
        child_order: List[int] = [0] * n
        stack = [(0, i, {i}) for i in range(n - 1, -1, -1)]

        child_labels = self.iso_labels.get(node1, None)
        if child_labels is None:
            child_labels = [self._iso_label + i for i in range(n)]
            self.iso_labels[node1] = child_labels
            self._iso_label += n

        while stack:
            i1, i2, in_use = stack.pop()
            if not self._are_isomorphic(
                rule1.children[i1], rule2.children[i2], child_labels[i1]
            ):
                continue
            child_order[i1] = i2
            if i1 == n - 1:
                self.iso_labels_to_rules[iso_label] = (rule2, child_order)
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
        eq_map: Dict[CombinatorialClass, AbstractRule],
    ) -> Tuple[CombinatorialClass, CombinatorialClass]:
        rule1, rule2 = rules1[node1], rules2[node2]

        if rule2.is_equivalence():
            node2 = rule2.children[0]
            eq_map[node1] = rule2

        if rule1.is_equivalence():
            node1 = rule1.children[0]

        return node1, node2

    def _base_cases(
        self,
        node1: CombinatorialClass,
        rule1: AbstractRule,
        node2: CombinatorialClass,
        rule2: AbstractRule,
    ) -> int:
        # If different type of rules are applied, the trees are not isomorphic
        if rule1.strategy.get_op_symbol() != rule2.strategy.get_op_symbol():
            return Isomorphism._INVALID

        # If different number of children
        if len(rule1.children) != len(rule2.children):
            return Isomorphism._INVALID

        # If leaf that has no equal-ancestors
        if not rule1.children and not rule2.children:
            # If one is atom, both should be and should also be equal
            if node1.is_atom() and node2.is_atom() and node1 == node2:
                return Isomorphism._VALID
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
