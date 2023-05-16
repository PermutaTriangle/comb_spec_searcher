import gc
import itertools
import platform
import time
from datetime import timedelta
from typing import (
    Dict,
    Iterable,
    Iterator,
    List,
    Set,
    Tuple,
    Union,
)

from comb_spec_searcher_rs import ForestRuleKey, RuleBucket, TableMethod
from logzero import logger

from comb_spec_searcher.class_db import ClassDB
from comb_spec_searcher.exception import StrategyDoesNotApply
from comb_spec_searcher.rule_db.abstract import RuleDBAbstract, ensure_specification
from comb_spec_searcher.strategies.rule import (
    AbstractRule,
    EquivalencePathRule,
    EquivalenceRule,
    Rule,
)
from comb_spec_searcher.strategies.strategy import (
    AbstractStrategy,
    EmptyStrategy,
    StrategyFactory,
)
from comb_spec_searcher.strategies.strategy_pack import StrategyPack
from comb_spec_searcher.typing import CSSstrategy

SortedRWS = Dict[RuleBucket, List[ForestRuleKey]]
empty_strategy: EmptyStrategy = EmptyStrategy()


class ForestRuleExtractor:
    MINIMIZE_ORDER = (
        RuleBucket.REVERSE,
        RuleBucket.NORMAL,
        RuleBucket.EQUIV,
        RuleBucket.VERIFICATION,
    )

    def __init__(
        self,
        root_label: int,
        ruledb: "RuleDBForest",
        classdb: ClassDB,
        pack: StrategyPack,
    ):
        self.pack = pack
        self.classdb = classdb
        self.root_label = root_label
        self.rule_by_bucket = self._sorted_stable_rules(ruledb.table_method)
        assert set(ForestRuleExtractor.MINIMIZE_ORDER) == set(self.rule_by_bucket)
        self.needed_rules: List[ForestRuleKey] = []
        self._minimize()

    def check(self) -> None:
        """
        Make a sanity check of the status of the extractor.
        """
        lhs = set(rk.parent for rk in self.needed_rules)
        assert len(lhs) == len(self.needed_rules)
        assert self._is_productive(self.needed_rules)

    def rules(self, cache: Tuple[AbstractRule, ...]) -> Iterator[AbstractRule]:
        """
        Return all the rules of the specification.

        It will first try to use a rule in the cache and otherwise will try to
        recompute it from the pack.

        The empty rule are ignored as they be produced as needed by the specification.
        """
        cache_dict = {
            rule.forest_key(self.classdb.get_label, self.classdb.is_empty): rule
            for rule in cache
        }
        for rk in self.needed_rules:
            if rk in cache_dict:
                rule = cache_dict[rk]
            else:
                rule = self._find_rule(rk)
            if isinstance(rule.strategy, EmptyStrategy):
                continue
            if (
                rule.is_equivalence()
                and not isinstance(rule, (EquivalencePathRule, EquivalenceRule))
                and len(rule.children) > 1
            ):
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
        logger.info("Minimizing %s", key.name)
        maybe_useful: List[ForestRuleKey] = []
        not_minimizing: List[List[ForestRuleKey]] = [self.needed_rules, maybe_useful]
        not_minimizing.extend(
            rules for k, rules in self.rule_by_bucket.items() if k != key
        )
        minimizing = self.rule_by_bucket[key]
        while minimizing:
            tb = TableMethod()
            # Add the rule we are not trying to minimize
            for rk in itertools.chain.from_iterable(not_minimizing):
                tb.add_rule_key(rk)
            if tb.is_pumping(self.root_label):
                minimizing.clear()
                break
            # Add rule until it gets productive
            for i, rk in enumerate(minimizing):
                tb.add_rule_key(rk)
                if tb.is_pumping(self.root_label):
                    break
            else:
                raise RuntimeError("Not pumping after adding all rules")
            maybe_useful.append(rk)
            assert minimizing, "variable i won't be set"
            # pylint: disable=undefined-loop-variable
            for _ in range(i, len(minimizing)):
                minimizing.pop()
            # added to avoid doubling in memory when minimizing with pypy
            if platform.python_implementation() == "PyPy":
                gc.collect_step()  # type: ignore
        counter = 0
        while maybe_useful:
            rk = maybe_useful.pop()
            if not self._is_productive(itertools.chain.from_iterable(not_minimizing)):
                self.needed_rules.append(rk)
                counter += 1
            # added to avoid doubling in memory when minimizing with pypy
            if platform.python_implementation() == "PyPy":
                gc.collect_step()  # type: ignore
        logger.info("Using %s rule for %s", counter, key.name)

    def _is_productive(self, rule_keys: Iterable[ForestRuleKey]) -> bool:
        """
        Check if the given set of rules is productive.
        """
        ruledb = TableMethod()
        for rk in rule_keys:
            ruledb.add_rule_key(rk)
        return ruledb.is_pumping(self.root_label)

    def _sorted_stable_rules(self, ruledb: TableMethod) -> SortedRWS:
        """
        Extract all the rule from the stable subuniverse and return all of them in a
        dict sorted by type.
        """
        res: SortedRWS = {bucket: [] for bucket in self.MINIMIZE_ORDER}
        for forest_key in ruledb.pumping_subuniverse():
            try:
                res[forest_key.bucket].append(forest_key)
            except KeyError as e:
                msg = (
                    f"{forest_key.bucket} type is not currently supported "
                    "by the extractor"
                )
                raise RuntimeError(msg) from e
        return res

    def _find_rule(self, rule_key: ForestRuleKey) -> AbstractRule:
        """
        Find a rule that have the given rule key.
        """
        all_classes = (rule_key.parent,) + rule_key.children
        all_normal_rules = itertools.chain.from_iterable(
            self._rules_for_class(c) for c in all_classes
        )
        for normal_rule in all_normal_rules:
            potential_rules = [normal_rule]
            if normal_rule.is_reversible():
                assert isinstance(normal_rule, Rule)
                potential_rules.extend(
                    normal_rule.to_reverse_rule(i)
                    for i in range(len(normal_rule.children))
                )
            for rule in potential_rules:
                if (
                    rule.forest_key(self.classdb.get_label, self.classdb.is_empty)
                    == rule_key
                ):
                    return rule
        err = f"Can't find a rule for {rule_key}\n"
        err += f"Parent:\n{self.classdb.get_class(rule_key.parent)}\n"
        for i, l in enumerate(rule_key.children):
            err += f"Child {i}:\n{self.classdb.get_class(l)}\n"
        raise RuntimeError(err)

    def _rules_for_class(self, label: int) -> Iterator[AbstractRule]:
        """
        Return all the rule created for that class with the pack.
        """
        comb_class = self.classdb.get_class(label)
        strats: Iterator[CSSstrategy] = itertools.chain([EmptyStrategy()], self.pack)
        for strat in strats:
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


class RuleDBForest(RuleDBAbstract):
    """
    The rule database that provides live information on which class are pumping with the
    current rule in the database.

    Set `reverse` to prevent the reverse of the added rules to be added to the database.
    """

    def __init__(
        self, *, reverse: bool = True, rule_cache: Iterable[AbstractRule] = tuple()
    ) -> None:
        super().__init__()
        self.reverse = reverse
        self._num_rules = 0
        self._time_table_method = 0.0
        self._time_key = 0.0
        self.table_method = TableMethod()
        self._already_empty: Set[int] = set()
        self._rule_cache = tuple(rule_cache)

    # Implementation of RuleDBAbstract

    def status(self, elaborate: bool) -> str:
        s = "RuleDB status:\n"
        s += f"\tAdded from {self._num_rules} normal rules\n"
        key_time = timedelta(seconds=int(self._time_key))
        tm_time = timedelta(seconds=int(self._time_table_method))
        s += f"\tTime spent computing forest keys: {key_time}\n"
        s += f"\tTime spent running the table method: {tm_time}\n"
        s += self.table_method.status()
        return s

    def is_verified(self, label: int) -> bool:
        """
        Determine if the comb_class is pumping in the current universe.
        """
        return self.table_method.is_pumping(label)

    def has_specification(self) -> bool:
        return self.is_verified(self.root_label)

    def add(self, start: int, ends: Tuple[int, ...], rule: AbstractRule) -> None:
        self._add_empty_rule(ends, rule)
        self._num_rules += 1
        start_time = time.time()
        new_rule_keys = [rule.forest_key(self.classdb.get_label, self.classdb.is_empty)]

        if self.reverse and rule.is_reversible():
            assert isinstance(rule, Rule)
            new_rule_keys.extend(
                rule.to_reverse_rule(i).forest_key(
                    self.classdb.get_label, self.classdb.is_empty
                )
                for i in range(len(rule.children))
            )
        self._time_key += time.time() - start_time
        start_time = time.time()
        for new_key in new_rule_keys:
            self.table_method.add_rule_key(new_key)
        self._time_table_method += time.time() - start_time

    @ensure_specification
    def get_specification_rules(self, **kwargs) -> Iterator[AbstractRule]:
        extractor = ForestRuleExtractor(
            self.root_label, self, self.classdb, self.strategy_pack
        )
        extractor.check()
        return extractor.rules(self._rule_cache)

    # Other methods

    def _add_empty_rule(self, ends: Iterable[int], rule: AbstractRule) -> None:
        """
        Add empty rule for the children of the rule if needed.
        """
        if not rule.possibly_empty:
            return
        for label, comb_class in zip(ends, rule.children):
            if label not in self._already_empty and self.classdb.is_empty(
                comb_class, label
            ):
                rule = empty_strategy(comb_class)
                self._already_empty.add(label)
                self.searcher.add_rule(label, (), rule)
