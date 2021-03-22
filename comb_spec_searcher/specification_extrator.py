import itertools
from typing import Dict, Iterable, Iterator, List, Tuple, Union

from comb_spec_searcher import rule_and_flip
from comb_spec_searcher.class_db import ClassDB
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.rule_db.base import RuleDBBase
from comb_spec_searcher.rule_db.forest import ForestRuleDB
from comb_spec_searcher.strategies.rule import AbstractRule, Rule
from comb_spec_searcher.strategies.strategy import AbstractStrategy, StrategyFactory
from comb_spec_searcher.strategies.strategy_pack import StrategyPack
from comb_spec_searcher.tree_searcher import Node
from comb_spec_searcher.typing import RuleKey


class SpecificationRuleExtractor:
    def __init__(
        self, root_label: int, root_node: Node, ruledb: RuleDBBase, classdb: ClassDB
    ):
        self.ruledb = ruledb
        self.classdb = classdb
        self.root_label = root_label
        self.eqv_rulekeys: List[RuleKey] = [
            (node.label, tuple(sorted(child.label for child in node.children)))
            for node in root_node.nodes()
        ]
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
            try:
                parent, children = eqvrule_to_rule[eqvrule]
            except KeyError:
                continue
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


RuleWithShifts = Tuple[RuleKey, Tuple[int, ...]]


class ForestRuleExtractor:
    def __init__(
        self,
        root_label: int,
        ruledb: ForestRuleDB,
        classdb: ClassDB,
        pack: StrategyPack,
    ):
        self.pack = pack
        self.classdb = classdb
        self.root_label = root_label
        self.all_rule_with_shifts = list(self._rule_with_shifts_for_zero(ruledb))
        self.needed_rule_with_shifts: List[RuleWithShifts] = list()
        self._minimize()
        lhs = set(rk[0] for rk, _ in self.needed_rule_with_shifts)
        assert len(lhs) == len(self.needed_rule_with_shifts)

    def rules(self) -> Iterator[AbstractRule]:
        for rk, _ in self.needed_rule_with_shifts:
            rule = self._find_rule(rk)
            if rule.is_equivalence():
                assert isinstance(rule, Rule)
                yield rule.to_equivalence_rule()
            else:
                yield rule

    def _minimize(self) -> List[RuleKey]:
        while self.all_rule_with_shifts:
            print(len(self.all_rule_with_shifts), len(self.needed_rule_with_shifts))
            rws = self.all_rule_with_shifts.pop()
            if not self._is_productive(
                itertools.chain(self.needed_rule_with_shifts, self.all_rule_with_shifts)
            ):
                self.needed_rule_with_shifts.append(rws)

    def _is_productive(self, rules_and_shifts: Iterator[RuleWithShifts]) -> bool:
        ruledb = ForestRuleDB()
        for rws in rules_and_shifts:
            ruledb.add_rule(*rws)
        return ruledb.is_pumping(self.root_label)

    def _rule_with_shifts_for_zero(
        self, ruledb: ForestRuleDB
    ) -> Iterator[RuleWithShifts]:
        """
        Extract all the rule rom the stable subuniverse and return all the rule it
        contains with there shifts.
        """
        rule_to_find = set(ruledb.pumping_subuniverse())
        for rule in itertools.chain.from_iterable(
            map(self._rules_for_class, ruledb.stable_subset())
        ):
            for rk, shifts in rule_and_flip.all_flips(rule, self.classdb.get_label):
                if rk in rule_to_find:
                    rule_to_find.remove(rk)
                    yield rk, shifts
        if rule_to_find:
            rk = next(iter(rule_to_find))
            err_message = (
                f"Could not recompute all the rules."
                f"Still missing {len(rule_to_find)}.\n"
                f"One of them is {rk}\n"
            )
            for label in itertools.chain([rk[0]], rk[1]):
                err_message += f"Label: {label}\n"
                err_message += str(self.classdb.get_class(label)) + "\n"
            raise RuntimeError(err_message)

    def _find_rule(self, rule_key: RuleKey) -> AbstractRule:
        """
        Find a rule that have the given rule key.
        """

        def rule_to_key(rule: AbstractRule) -> RuleKey:
            parent = self.classdb.get_label(rule.comb_class)
            children = tuple(map(self.classdb.get_label, rule.children))
            return parent, children

        parent = self.classdb.get_class(rule_key[0])
        for rule in self._rules_for_class(rule_key[0]):
            if rule_to_key(rule) == rule_key:
                return rule
        for child_idx, child_label in enumerate(rule_key[1]):
            for rule in self._rules_for_class(child_label):
                assert isinstance(rule, Rule)
                try:
                    pindex = rule.children.index(parent)
                    if rule.is_two_way():
                        reverse_rule = rule.to_reverse_rule(pindex)
                        if rule_to_key(reverse_rule) == rule_key:
                            return reverse_rule
                except ValueError:
                    pass

        raise RuntimeError(f"Can't find a rule for {rule_key}")

    def _rules_for_class(self, label: int) -> Iterator[AbstractRule]:
        """
        Return all the rule created for that class with the pack.
        """
        for strat in self.pack:
            comb_class = self.classdb.get_class(label)
            if isinstance(strat, StrategyFactory):
                strats_or_rules: Iterable[
                    Union[AbstractRule, AbstractStrategy]
                ] = strat(comb_class)
            else:
                strats_or_rules = [strat]
            for x in strats_or_rules:
                if isinstance(x, AbstractStrategy):
                    try:
                        yield x(comb_class)
                    except StrategyDoesNotApply:
                        continue
                else:
                    yield x
