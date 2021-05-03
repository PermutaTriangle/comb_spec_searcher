import itertools
from typing import Dict, Iterable, Iterator, List, Tuple, Union

from logzero import logger

from comb_spec_searcher.class_db import ClassDB
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.rule_and_flip import all_flips
from comb_spec_searcher.rule_db.base import RuleDBBase
from comb_spec_searcher.rule_db.forest import ForestRuleDB
from comb_spec_searcher.strategies.rule import AbstractRule, ReverseRule, Rule
from comb_spec_searcher.strategies.strategy import AbstractStrategy, StrategyFactory
from comb_spec_searcher.strategies.strategy_pack import StrategyPack
from comb_spec_searcher.tree_searcher import Node
from comb_spec_searcher.typing import ForestRuleKey, RuleBucket, RuleKey


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


RuleWithShifts = Tuple[RuleKey, Tuple[int, ...]]
SortedRWS = Dict[RuleBucket, List[ForestRuleKey]]


class ForestRuleExtractor:
    MINIMIZE_ORDER = [RuleBucket.REVERSE, RuleBucket.NORMAL, RuleBucket.VERIFICATION]

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
        self.rule_by_bucket = self._sorted_stable_rules(ruledb)
        assert set(ForestRuleExtractor.MINIMIZE_ORDER) == set(self.rule_by_bucket)
        self.needed_rules: List[ForestRuleKey] = list()
        self._minimize()

    def check(self) -> bool:
        """
        Make a sanity check of the status of the extractor.
        """
        lhs = set(rk.parent for rk in self.needed_rules)
        assert len(lhs) == len(self.needed_rules)
        assert self._is_productive(self.needed_rules)
        for rk in sorted(self.needed_rules):
            rule = self._find_rule(rk)
            if isinstance(rule, ReverseRule):
                af = list(all_flips(rule.original_rule, self.classdb.get_label))
                assert af[rule.idx + 1], rule
            else:
                af = list(all_flips(rule, self.classdb.get_label))
                assert af[0], rule

    def rules(self) -> Iterator[AbstractRule]:
        """
        Return all the rules of the specification.
        """
        for rk in self.needed_rules:
            rule = self._find_rule(rk)
            if rule.is_equivalence():
                assert isinstance(rule, Rule)
                yield rule.to_equivalence_rule()
            else:
                yield rule

    def _minimize(self):
        """
        Perform the complete minimization of the forest.
        """
        for key in ForestRuleExtractor.MINIMIZE_ORDER:
            self._minimize_key(key)

    def _minimize_key(self, key: RuleBucket) -> None:
        """
        Minimize the number of rules used for the type of rule given by key.

        The list of rule in `self.rule_by_bucket[key]` is cleared and a
        minimal set from theses is added to `self.needed_rules`.
        """
        logger.info(f"Minimizing {key}")
        maybe_useful: List[ForestRuleKey] = []
        not_minimizing: List[List[ForestRuleKey]] = [
            self.needed_rules,
            maybe_useful,
        ]
        not_minimizing.extend(
            rules for k, rules in self.rule_by_bucket.items() if k != key
        )
        minimizing = self.rule_by_bucket[key]
        while minimizing:
            ruledb = ForestRuleDB()
            # Add the rule we are not trying to minimize
            for rk in itertools.chain.from_iterable(not_minimizing):
                ruledb.add_rule(rk)
            if ruledb.is_pumping(self.root_label):
                self.rule_by_bucket[key].clear()
                break
            # Add rule until it gets productive
            for i, rk in enumerate(minimizing):
                ruledb.add_rule(rk)
                if ruledb.is_pumping(self.root_label):
                    break
            else:
                raise RuntimeError("Not pumping after adding all rules")
            maybe_useful.append(rk)
            for _ in range(i, len(minimizing)):
                minimizing.pop()
        counter = 0
        while maybe_useful:
            rk = maybe_useful.pop()
            if not self._is_productive(itertools.chain.from_iterable(not_minimizing)):
                self.needed_rules.append(rk)
                counter += 1
        logger.info(f"Using {counter} rule for {key}")

    def _is_productive(self, rule_keys: Iterable[ForestRuleKey]) -> bool:
        """
        Check if the given set of rules is productive.
        """
        ruledb = ForestRuleDB()
        for rk in rule_keys:
            ruledb.add_rule(rk)
        return ruledb.is_pumping(self.root_label)

    def _sorted_stable_rules(self, ruledb: ForestRuleDB) -> SortedRWS:
        """
        Extract all the rule from the stable subuniverse and return all of them in a
        dict sorted by type.
        """
        res: SortedRWS = {bucket: [] for bucket in ForestRuleExtractor.MINIMIZE_ORDER}
        for forest_key in ruledb.pumping_subuniverse():
            try:
                res[forest_key.bucket].append(forest_key)
            except KeyError as e:
                raise RuntimeError(
                    f"{forest_key.bucket} type is not currently supported by the extractor"
                ) from e
        return res

    def _find_rule(self, rule_key: ForestRuleKey) -> AbstractRule:
        """
        Find a rule that have the given rule key.
        """

        def rule_to_key(rule: AbstractRule) -> RuleKey:
            parent = self.classdb.get_label(rule.comb_class)
            children = tuple(map(self.classdb.get_label, rule.children))
            return parent, children

        all_classes = (rule_key.parent,) + rule_key.children
        all_normal_rules = itertools.chain.from_iterable(
            self._rules_for_class(c) for c in all_classes
        )
        for rule in all_normal_rules:
            if rule_to_key(rule) == rule_key.key:
                return rule
            # TODO: Make this is_reversible when implemented
            if not rule.is_two_way():
                continue
            assert isinstance(rule, Rule)
            for i in range(len(rule.children)):
                reverse_rule = rule.to_reverse_rule(i)
                if rule_to_key(reverse_rule) == rule_key.key:
                    return reverse_rule

        err = f"Can't find a rule for {rule_key}\n"
        err += f"Parent:\n{self.classdb.get_class(rule_key.parent)}\n"
        for i, l in enumerate(rule_key.children):
            err += f"Child {i}:\n{self.classdb.get_class(l)}\n"
        raise RuntimeError(err)

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
