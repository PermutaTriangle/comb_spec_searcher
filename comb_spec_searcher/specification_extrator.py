import itertools
from collections import deque
from operator import itemgetter
from typing import TYPE_CHECKING, Deque, Dict, Iterable, Iterator, List, Set, Tuple

from comb_spec_searcher.class_db import ClassDB
from comb_spec_searcher.strategies.rule import AbstractRule, Rule
from comb_spec_searcher.tree_searcher import Node
from comb_spec_searcher.typing import RuleKey

if TYPE_CHECKING:
    from comb_spec_searcher.rule_db.base import RuleDBBase


class SpecificationRuleExtractor:
    def __init__(
        self, root_label: int, root_node: Node, ruledb: "RuleDBBase", classdb: ClassDB
    ):
        self.ruledb = ruledb
        self.classdb = classdb
        self.root_label = root_label
        self.eqv_rulekeys = root_node.rule_keys()
        self.rules_dict: Dict[int, Tuple[int, ...]] = {}
        # A map from equiv label to an equivalent label actually in the tree.
        self.eqvparent_to_parent: Dict[int, int] = {}
        self._populate_decompositions()
        self._populate_equivalences()
        self._check()

    def _populate_decompositions(self) -> None:
        """
        Populate the rules dict with the labels of decomposition rules.
        """
        eqvrule_to_rule = self.ruledb.rule_from_equivalence_rule_dict(self.eqv_rulekeys)
        for eqvrule in self.eqv_rulekeys:
            parent, children = eqvrule_to_rule[eqvrule]
            self.rules_dict[parent] = children
            self.eqvparent_to_parent[eqvrule[0]] = parent

    def _populate_equivalences(self) -> None:
        """
        Populate the rules dict with the labels of equivalences rules needed to make
        every class be on a right hand side.
        """
        for label in self._no_lhs_labels():
            eqv_label = self.ruledb.equivdb[label]
            path = self.ruledb.equivdb.find_path(
                label, self.eqvparent_to_parent[eqv_label]
            )
            for parent, child in zip(path[:-1], path[1:]):
                if parent in self.rules_dict:
                    # No need to keep adding the path since the class already connects
                    # with something in the specification
                    break
                self.rules_dict[parent] = (child,)

    def _no_lhs_labels(self) -> Set[int]:
        """
        Find labels that are not a lhs of any rule.
        """
        all_rhs = itertools.chain.from_iterable(self.rules_dict.values())
        no_lhs_labels = set(
            itertools.filterfalse(self.rules_dict.__contains__, all_rhs)
        )
        if self.root_label not in self.rules_dict:
            no_lhs_labels.add(self.root_label)
        return no_lhs_labels

    def _check(self):
        """
        Perform a check to make sure that the spec make sense.
        """
        all_rhs = set(
            itertools.chain.from_iterable(
                children for children in self.rules_dict.values()
            )
        )
        assert all_rhs.issubset(self.rules_dict), "Something is not on the lhs"
        extra_lhs = {c for c in self.rules_dict if c not in all_rhs}
        assert extra_lhs.issubset({self.root_label})

    def _find_rule(self, parent: int, children: Tuple[int, ...]) -> AbstractRule:
        try:
            strategy = self.ruledb.rule_to_strategy[(parent, children)]
        except KeyError as e:
            if len(children) != 1:
                raise self._missing_rule_error(parent, children) from e
        else:
            return strategy(self.classdb.get_class(parent))
        # From now on we are looking for a two way strategy
        assert len(children) == 1
        try:
            strategy = self.ruledb.eqv_rule_to_strategy[(parent, children)]
        except KeyError:
            pass
        else:
            rule = strategy(self.classdb.get_class(parent))
            assert isinstance(rule, Rule)
            return rule if len(rule.children) == 1 else rule.to_equivalence_rule()
        # Now trying a reverse rule
        try:
            strategy = self.ruledb.eqv_rule_to_strategy[(children[0], (parent,))]
        except KeyError:
            pass
        else:
            rule = strategy(self.classdb.get_class(children[0]))
            assert isinstance(rule, Rule)
            rule = rule if len(rule.children) == 1 else rule.to_equivalence_rule()
            return rule.to_reverse_rule(0)
        raise self._missing_rule_error(parent, children)

    def _missing_rule_error(self, parent: int, children: Tuple[int, ...]) -> ValueError:
        """
        Return a ValueError saying the rule was not found.
        """
        msg = f"Unable to retrieve rule for {(parent, children)}\n"
        msg += f"Class {parent} is:\n{self.classdb.get_class(parent)}\n"
        for child in children:
            msg += f"Class {child} is:\n{self.classdb.get_class(child)}\n"
        return ValueError(msg)

    def rules(self) -> Iterator[AbstractRule]:
        for parent, children in self.rules_dict.items():
            yield self._find_rule(parent, children)


class EquivalenceRuleExtractor(SpecificationRuleExtractor):
    """
    This class extracts the actual rules that would be created for an equivalence
    label given a partial spec that is traversable from root. Suppose we want the
    rules for the parent in `grandparent-parent-children` than what rules are used
    will depend on the grandparent and children and we are looking for the rules
    that have the same equivalance label on both the LHS and RHS and in the order they
    would be traversed from the root.
    """

    def __init__(
        self,
        root_eq_label: int,
        root_class_label: int,
        root_node: Node,
        ruledb: "RuleDBBase",
        classdb: ClassDB,
        target: int,
        parent_of_target: int,
        idx: int,
    ):
        # parent
        self.target = target
        # grandparent
        self.parent_of_target = parent_of_target
        # grandparent.children[idx] is parent
        self.idx = idx
        # class label of the LHS of the first rule for the eq path, updated later
        self.start = root_class_label
        # class label of the RHS of the last rule for the eq path, updated later
        self.end = -1
        # Maps our children index order to that of the actual rules
        self.index_order_map: Dict[RuleKey, Tuple[int, ...]] = {}
        # Children are included in the tree
        super().__init__(root_eq_label, root_node, ruledb, classdb)

    def _populate_decompositions(self) -> None:
        # Altered rule_from_equivalence_rule_dict
        eqv_rules = set(self.eqv_rulekeys)
        eqvrule_to_rule: Dict[RuleKey, RuleKey] = {}
        for start, ends in self.ruledb.rule_to_strategy:
            eqv_start = self.ruledb.equivdb[start]
            # Sort but keep knowledge of original order
            index_order, eqv_ends = (
                zip(
                    *sorted(
                        enumerate(map(self.ruledb.equivdb.__getitem__, ends)),
                        key=itemgetter(1),
                    )
                )
                if ends
                else ((), ())
            )

            eqv_key = (eqv_start, eqv_ends)
            self.index_order_map[eqv_key] = index_order
            if eqv_key in eqv_rules:
                eqvrule_to_rule[eqv_key] = (start, ends)

        for eqvrule in self.eqv_rulekeys:
            # Might not exist because spec is incomplete.
            try:
                parent, children = eqvrule_to_rule[eqvrule]
            except KeyError:
                continue
            self.rules_dict[parent] = children
            self.eqvparent_to_parent[eqvrule[0]] = parent
            # If grandparent, then we can find our starting point
            # If no grandparent exists, this will always be the root.
            if eqvrule[0] == self.parent_of_target:
                self.start = children[self.index_order_map[eqvrule][self.idx]]
            # If parent, we have our end point
            if eqvrule[0] == self.target:
                self.end = parent

    def _populate_equivalences(self) -> None:
        # SpecificationRuleExtractor's with a try-catch do deal with incomplete spec

        for label in self._no_lhs_labels():
            eqv_label = self.ruledb.equivdb[label]
            try:
                path = self.ruledb.equivdb.find_path(
                    label, self.eqvparent_to_parent[eqv_label]
                )
            except KeyError:
                assert eqv_label != self.target
                continue
            for parent, child in zip(path[:-1], path[1:]):
                if parent in self.rules_dict:
                    break
                self.rules_dict[parent] = (child,)

    def _check(self):
        pass

    def nonequivalent_rules_in_equiv_path(self) -> List[Rule]:
        return list(self._nonequivalent_rules_in_equiv_path())

    def _nonequivalent_rules_in_equiv_path(self) -> Iterator[Rule]:
        path = self.ruledb.equivdb.find_path(self.start, self.end)
        for p, c in zip(path, path[1:]):
            rule = self._find_rule(p, (c,))
            # If rule is an actual equivalence rule, we don't care and ignore it.
            if not rule.is_equivalence():
                assert isinstance(rule, Rule)
                yield rule


class RulePathToAtomExtractor(SpecificationRuleExtractor):
    def __init__(
        self,
        root_label: int,
        root_node: Node,
        ruledb: "RuleDBBase",
        classdb: ClassDB,
        path: Iterable[Tuple[int, int]],
        atom: int,
    ):
        super().__init__(root_label, root_node, ruledb, classdb)

    def _populate_decompositions(self) -> None:
        pass

    def _populate_equivalences(self) -> None:
        pass

    def _check(self):
        pass

    def rule_path(self) -> Deque[Tuple[AbstractRule, int]]:
        return deque([])
