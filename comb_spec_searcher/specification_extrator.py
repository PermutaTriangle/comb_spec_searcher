import itertools
from typing import Dict, Iterator, Tuple

from comb_spec_searcher.class_db import ClassDB
from comb_spec_searcher.rule_db.base import RuleDBBase
from comb_spec_searcher.strategies.rule import AbstractRule, Rule
from comb_spec_searcher.tree_searcher import Node


class SpecificationRuleExtractor:
    def __init__(
        self, root_label: int, root_node: Node, ruledb: RuleDBBase, classdb: ClassDB
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
        all_rhs = itertools.chain.from_iterable(self.rules_dict.values())
        no_lhs_labels = set(
            itertools.filterfalse(self.rules_dict.__contains__, all_rhs)
        )
        if self.root_label not in self.rules_dict:
            no_lhs_labels.add(self.root_label)
        for label in no_lhs_labels:
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
