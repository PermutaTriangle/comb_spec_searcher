from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple

from .combinatorial_class import CombinatorialClass
from .strategies.rule import AbstractRule

if TYPE_CHECKING:
    from .specification import CombinatorialSpecification


class Isomorphism:
    """Isomorphism checker."""

    _INVALID, _UNKNOWN, _VALID = range(-1, 2)

    @classmethod
    def children_order(
        cls, spec1: "CombinatorialSpecification", spec2: "CombinatorialSpecification"
    ) -> Optional[Dict[CombinatorialClass, List[int]]]:
        """If the two specs are isomorphic, returns the order of children in the second
        spec that matches the first. If not, None is returned."""
        iso = cls(spec1, spec2)
        if iso.are_isomorphic():
            return iso.child_order

    def __init__(
        self, spec1: "CombinatorialSpecification", spec2: "CombinatorialSpecification"
    ) -> None:
        self.index: List[int] = [0]
        self.root1: CombinatorialClass = spec1.root
        self.rules1: Dict[CombinatorialClass, AbstractRule] = spec1.rules_dict
        self.ancestors1: Dict[CombinatorialClass, int] = {}
        self.root2: CombinatorialClass = spec2.root
        self.rules2: Dict[CombinatorialClass, AbstractRule] = spec2.rules_dict
        self.ancestors2: Dict[CombinatorialClass, int] = {}
        self.child_order: Dict[CombinatorialClass, List[int]] = {}

    def are_isomorphic(self) -> bool:
        """Check if the two specs are isomorphic."""
        return self._are_isomorphic(self.root1, self.root2)

    def _are_isomorphic(
        self, node1: CombinatorialClass, node2: CombinatorialClass
    ) -> bool:
        # If there are equivilances, we use the 'latest' one
        node1 = Isomorphism._get_eq_descendant(node1, self.rules1)
        node2 = Isomorphism._get_eq_descendant(node2, self.rules2)
        rule1, rule2 = self.rules1[node1], self.rules2[node2]

        is_base_case = self._base_cases(node1, rule1, node2, rule2)
        if is_base_case:
            return bool(is_base_case + 1)

        self.index[0] += 1
        self.ancestors1[node1], self.ancestors2[node2] = self.index[0], self.index[0]

        # Check all matches of children, if any are valid then trees are isomorphic
        n = len(rule1.children)
        if n > 1:
            if node2 not in self.child_order:
                self.child_order[node2] = [0] * n
            child_order: List[int] = self.child_order[node2]
        stack = [(0, i, {i}) for i in range(n - 1, -1, -1)]
        while stack:
            i1, i2, in_use = stack.pop()
            if not self._are_isomorphic(rule1.children[i1], rule2.children[i2]):
                continue
            if n > 1:
                child_order[i1] = i2
            if i1 == n - 1:
                self._cleanup(node1, node2)
                return True
            Isomorphism._extend_stack(i1, n, in_use, stack)

        self._cleanup(node1, node2)
        return False

    @staticmethod
    def _get_eq_descendant(
        node: CombinatorialClass,
        rules: Dict[CombinatorialClass, AbstractRule],
    ) -> CombinatorialClass:
        rule = rules[node]
        while rule.is_equivalence():
            node = rule.children[0]
            rule = rules[node]
        return node

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
        ind1, ind2 = self.ancestors1.get(node1, -1), self.ancestors2.get(node2, -1)

        # If one is found and the other not or if
        # they occured in different places before
        if ind1 != ind2:
            return Isomorphism._INVALID

        # If they have occured before and that occurrence matches in both trees
        if ind1 == ind2 != -1:
            return Isomorphism._VALID

        return Isomorphism._UNKNOWN

    def _cleanup(self, node1: CombinatorialClass, node2: CombinatorialClass) -> None:
        self.index[0] -= 1
        del self.ancestors1[node1]
        del self.ancestors2[node2]

    @staticmethod
    def _extend_stack(
        i1: int, n: int, in_use: Set[int], stack: List[Tuple[int, int, Set[int]]]
    ) -> None:
        for i in range(n - 1, -1, -1):
            if i in in_use:
                continue
            stack.append((i1 + 1, i, in_use.union({i})))
