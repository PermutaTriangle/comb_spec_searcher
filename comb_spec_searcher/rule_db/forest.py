import gc
import itertools
import multiprocessing
import os
import time
from datetime import timedelta
from typing import (
    Callable,
    Deque,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
)

from logzero import logger

from comb_spec_searcher.class_db import AbstractClassDB
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
from comb_spec_searcher.typing import CSSstrategy, ForestRuleKey, RuleBucket, RuleKey

T = TypeVar("T")
RuleWithShifts = Tuple[RuleKey, Tuple[int, ...]]
SortedRWS = Dict[RuleBucket, List[ForestRuleKey]]
empty_strategy: EmptyStrategy = EmptyStrategy()


class DefaultList(Generic[T]):
    """
    A list data structure get automatically gets longer if an index not existing is
    requested.

    When getting longer the list is filled by calling the provied `default_factory`.
    This is similar to the `collections.defaultdict` data structure.
    """

    def __init__(self, default_factory: Callable[[], T]):
        self._default_factory = default_factory
        self._list: List[T] = []

    def _increase_list_len(self, key: int) -> None:
        """
        Increase the length of the list so that the given is valid.
        """
        num_new_entry = key - len(self._list) + 1
        self._list.extend((self._default_factory() for _ in range(num_new_entry)))

    def __getitem__(self, key: int) -> T:
        try:
            return self._list[key]
        except IndexError:
            self._increase_list_len(key)
            return self._list[key]

    def __setitem__(self, key: int, value: T) -> None:
        self._list[key] = value

    def __iter__(self) -> Iterator[T]:
        return iter(self._list)

    def __str__(self) -> str:
        return str(self._list)


class Function:
    """
    A python representation of a function.

    The function maps natural number to a natural number or infinity (represented
    by the use of None)

    The default value of the function is 0.
    """

    def __init__(self) -> None:
        self._value: List[Optional[int]] = []
        self._preimage_count: DefaultList[int] = DefaultList(int)
        self._infinity_count: int = 0

    @property
    def preimage_count(self) -> List[int]:
        """
        Return the number of classes for each value of the function.
        """
        count = list(self._preimage_count)
        while count and count[-1] == 0:
            count.pop()
        return count

    @property
    def infinity_count(self) -> int:
        return self._infinity_count

    def __getitem__(self, key: int) -> Optional[int]:
        """
        Return the value of the function for the given key.
        """
        try:
            return self._value[key]
        except IndexError:
            self._increase_list_len(key)
            return 0

    def _increase_list_len(self, key: int) -> None:
        num_new_entry = key - len(self._value) + 1
        self._value.extend((0 for _ in range(num_new_entry)))
        self._preimage_count[0] += num_new_entry

    def increase_value(self, key: int) -> None:
        """
        Increase by one the value of the function for the given key.
        """
        try:
            old_value = self._value[key]
            if old_value is None:
                raise ValueError(f"The function is already infinity for {key}")
        except IndexError:
            self._increase_list_len(key)
            old_value = 0
        self._value[key] = old_value + 1
        self._preimage_count[old_value] -= 1
        self._preimage_count[old_value + 1] += 1

    def set_infinite(self, key: int) -> None:
        """
        Set the value of function for the given key to infinity.
        """
        try:
            old_value = self._value[key]
            if old_value is None:
                raise ValueError(f"The function is already infinity for {key}")
        except IndexError:
            self._increase_list_len(key)
            old_value = 0
        self._value[key] = None
        self._preimage_count[old_value] -= 1
        self._infinity_count += 1

    def preimage_gap(self, length: int) -> int:
        """
        Return the smallest k such that the preimage of the interval
        [k, k+length-1] is empty.
        """
        if length <= 0:
            raise ValueError("length argument must be positive")
        last_non_zero = -1
        for i, v in enumerate(self._preimage_count):
            if v != 0:
                last_non_zero = i
            elif i - last_non_zero >= length:
                return last_non_zero + 1
        return last_non_zero + 1

    def preimage(self, value: Optional[int]) -> Iterator[int]:
        """
        Return the preimage of the function for the given value.
        """
        if value == 0:
            raise ValueError("The preimage of 0 is infinite.")
        return (k for k, v in enumerate(self._value) if v == value)

    def to_dict(self) -> Dict[int, Optional[int]]:
        """
        Return a dictionary view of the function with only the non-zero value.
        """
        return {i: v for i, v in enumerate(self._value) if v != 0}

    def __str__(self) -> str:
        parts = (
            f"{i} -> {v if v is not None else '∞'}" for i, v in enumerate(self._value)
        )
        return "\n".join(parts)


class TableMethod:
    def __init__(self) -> None:
        self._rules: List[ForestRuleKey] = []
        self._shifts: List[List[Optional[int]]] = []
        self._function: Function = Function()
        self._gap_size: int = 1
        self._rules_using_class: DefaultList[List[Tuple[int, int]]] = DefaultList(list)
        self._rules_pumping_class: DefaultList[List[int]] = DefaultList(list)
        self._processing_queue: Deque[int] = Deque()
        self._current_gap: Tuple[int, int] = (1, 1)
        self._rule_holding_extra_terms: Set[int] = set()

    @property
    def function(self) -> Dict[int, Optional[int]]:
        """
        Return a dict representing the number of term that are computable for each
        class.
        Only the class where it can get at least a term are included. If a class is map
        to None, then all the terms of the enumeration are computable.
        """
        return self._function.to_dict()

    def add_rule_key(
        self,
        rule_key: ForestRuleKey,
    ):
        """
        Add the rule to the database.

        INPUTS:
          - `rule_key`
          - `shifts_for_zero`: The values of the shifts if no information was known
          about any of the classes.
          - `rule_bucket` the type of rule
        """
        self._rules.append(rule_key)
        self._shifts.append(self._compute_shift(rule_key.key, rule_key.shifts))
        max_gap = max((abs(s) for s in rule_key.shifts), default=0)
        if max_gap > self._gap_size:
            self._gap_size = max_gap
            self._correct_gap()
        if self._function[rule_key.parent] is not None:
            rule_idx = len(self._rules) - 1
            self._rules_pumping_class[rule_key.parent].append(rule_idx)
            for child_idx, child in enumerate(rule_key.children):
                if self._function[child] is not None:
                    self._rules_using_class[child].append((rule_idx, child_idx))
            self._processing_queue.append(rule_idx)
        self._process_queue()

    def is_pumping(self, label: int) -> bool:
        """
        Determine if the comb_class is pumping in the current universe.
        """
        return self._function[label] is None

    def status(self) -> str:
        s = f"\tSize of the gap: {self._gap_size}\n"
        s += f"\tSize of the stable subset: {self._function.infinity_count}\n"
        s += f"\tSizes of the pre-images: {self._function.preimage_count}\n"
        return s

    def stable_subset(self) -> Iterator[int]:
        return self._function.preimage(None)

    def pumping_subuniverse(
        self,
    ) -> Iterator[ForestRuleKey]:
        """
        Iterator over all the forest rule keys that contain only pumping
        combinatorial classes.
        """
        stable_subset = set(self.stable_subset())
        for forest_key in self._rules:
            if forest_key.parent in stable_subset and stable_subset.issuperset(
                forest_key.children
            ):
                yield forest_key

    def _compute_shift(
        self,
        rule_key: RuleKey,
        shifts_for_zero: Tuple[int, ...],
    ) -> List[Optional[int]]:
        """
        Compute the initial value for the shifts a rule based on the current state of
        the function.
        """
        parent_current_value = self._function[rule_key[0]]
        if parent_current_value is None:
            return [None for _ in shifts_for_zero]
        chidlren_function_value = map(self._function.__getitem__, rule_key[1])
        return [
            fvalue + sfz - parent_current_value if fvalue is not None else None
            for fvalue, sfz in zip(chidlren_function_value, shifts_for_zero)
        ]

    def _correct_gap(self) -> None:
        """
        Correct the gap and if needed queue rules for the classes that were previously
        on the right hand  side of the gap.

        This should be toggled every time the gap changes whether the size changes or
        the some value changes of the function caused the gap to change.
        """
        k = self._function.preimage_gap(self._gap_size)
        new_gap = (k, k + self._gap_size - 1)
        if new_gap[1] > self._current_gap[1]:
            self._processing_queue.extend(self._rule_holding_extra_terms)
            self._rule_holding_extra_terms.clear()
        self._current_gap = new_gap

    def _process_queue(self) -> None:
        """
        Try to make improvement with all the class in the processing queue.
        """
        while self._processing_queue or self._rule_holding_extra_terms:
            while self._processing_queue:
                rule_idx = self._processing_queue.popleft()
                shifts = self._shifts[rule_idx]
                if self._can_give_terms(shifts):
                    parent = self._rules[rule_idx].parent
                    self._increase_value(parent, rule_idx)
            if self._rule_holding_extra_terms:
                rule_idx = self._rule_holding_extra_terms.pop()
                parent = self._rules[rule_idx].parent
                self._set_infinite(parent)

    @staticmethod
    def _can_give_terms(shifts: List[Optional[int]]) -> bool:
        """
        Return True if the shifts indicate that a new terms can be computed.
        """
        return all(s is None or s > 0 for s in shifts)

    def _increase_value(self, comb_class: int, rule_idx: int) -> None:
        """
        Increase the value of the comb_class and put on the processing stack any rule
        that can now give a new term.

        The rule_idx must indicate the rule used to justify the increase.
        """
        current_value = self._function[comb_class]
        if current_value is None:
            return
        if current_value > self._current_gap[1]:
            self._rule_holding_extra_terms.add(rule_idx)
            return
        self._function.increase_value(comb_class)
        # Correction of the gap
        gap_start = self._function.preimage_gap(self._gap_size)
        if self._current_gap[0] != gap_start:
            self._correct_gap()
        # Correction of the shifts for rule pumping comb_class
        for r_idx in self._rules_pumping_class[comb_class]:
            shifts = self._shifts[r_idx]
            for i, v in enumerate(shifts):
                shifts[i] = v - 1 if v is not None else None
            if self._can_give_terms(shifts):
                self._processing_queue.append(r_idx)
        # Correction of the shifts for rules using comb_class to pump
        for r_idx, class_idx in self._rules_using_class[comb_class]:
            shifts = self._shifts[r_idx]
            current_shift = shifts[class_idx]
            assert current_shift is not None
            shifts[class_idx] = current_shift + 1
            if self._can_give_terms(shifts):
                self._processing_queue.append(r_idx)

    def _set_infinite(self, comb_class: int) -> None:
        """
        Set the value if the class to infinity.

        This should happen when we know that we cannot pump anything on the left side
        of the gap.
        """
        current_value = self._function[comb_class]
        if current_value is None:
            return
        assert current_value > self._current_gap[1]
        assert not self._processing_queue
        self._function.set_infinite(comb_class)
        # This class will never be increased again so we remove any occurrence
        # of the rule of any rule for that class from _rules_using_class and
        # _rules_pumping_class
        for rule_idx in self._rules_pumping_class[comb_class]:
            for child in self._rules[rule_idx].children:
                self._rules_using_class[child] = [
                    (ri, ci)
                    for ri, ci in self._rules_using_class[child]
                    if ri != rule_idx
                ]
        self._rules_pumping_class[comb_class].clear()
        # Correction of the shifts for rules using comb_class to pump
        for rule_idx, class_idx in self._rules_using_class[comb_class]:
            shifts = self._shifts[rule_idx]
            shifts[class_idx] = None
            if self._can_give_terms(shifts):
                self._processing_queue.append(rule_idx)
        self._rules_using_class[comb_class].clear()

    def rule_info(self, rule_idx: int) -> str:
        """
        Return a string with information about a particular rule.
        Mostly intended for debugging.
        """

        def v_to_str(v: Optional[int]) -> str:
            """Return a string for the integer and infinity if None"""
            if v is None:
                return "∞"
            return str(v)

        rule_key = self._rules[rule_idx]
        current_value = f"{v_to_str(self._function[rule_key.parent])} -> " + ", ".join(
            map(v_to_str, (self._function[c] for c in rule_key.children))
        )
        shifts = map(v_to_str, self._shifts[rule_idx])
        child_with_shift = ", ".join(
            f"({c}, {s})" for c, s in zip(rule_key.children, shifts)
        )
        return f"{rule_key.parent} -> {child_with_shift} || {current_value}"


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
        classdb: AbstractClassDB,
        pack: StrategyPack,
    ):
        self.pack = pack
        self.classdb = classdb
        self.root_label = root_label
        self.rule_by_bucket = self._sorted_stable_rules(ruledb.table_method)
        assert set(ForestRuleExtractor.MINIMIZE_ORDER) == set(self.rule_by_bucket)
        self.needed_rules: List[ForestRuleKey] = []
        self._minimize()

    def check(self) -> bool:
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
        cache_dict = {rule.forest_key(self.classdb.get_label): rule for rule in cache}
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
        not_minimizing: List[List[ForestRuleKey]] = [
            self.needed_rules,
            maybe_useful,
        ]
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
            gc.collect()
        counter = 0
        while maybe_useful:
            rk = maybe_useful.pop()
            if not self._is_productive(itertools.chain.from_iterable(not_minimizing)):
                self.needed_rules.append(rk)
                counter += 1
            # added to avoid doubling in memory when minimizing with pypy
            gc.collect()
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
                if rule.forest_key(self.classdb.get_label) == rule_key:
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
        self,
        *,
        reverse: bool = True,
        rule_cache: Iterable[AbstractRule] = tuple(),
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
        labels = dict(zip(rule.children, ends))
        labels[rule.comb_class] = start
        self._add_empty_rule(ends, rule)
        start_time = time.time()
        new_rule_keys = [rule.forest_key(labels.__getitem__)]
        if self.reverse and rule.is_reversible():
            assert isinstance(rule, Rule)
            new_rule_keys.extend(
                rule.to_reverse_rule(i).forest_key(labels.__getitem__)
                for i in range(len(rule.children))
            )
        self._time_key += time.time() - start_time
        self._add_keys_to_table(new_rule_keys)

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
                self.add(label, (), rule)

    def _add_keys_to_table(self, keys: List[ForestRuleKey]) -> None:
        self._num_rules += 1
        start_time = time.time()
        for new_key in keys:
            self.table_method.add_rule_key(new_key)
        self._time_table_method += time.time() - start_time


class WorkerRuleDBForest(RuleDBForest):
    def __init__(
        self, conn: "multiprocessing.connection.Connection", *, reverse: bool = True
    ) -> None:
        super().__init__(reverse=reverse)
        self.conn = conn

    def _add_keys_to_table(self, keys: List[ForestRuleKey]) -> None:
        self._num_rules += 1
        self.conn.send(keys)


class PrimaryRuleDBForest(RuleDBForest):
    def __init__(self, *, reverse: bool = True) -> None:
        super().__init__(reverse=reverse)
        self.connections: List["multiprocessing.connection.Connection"] = []

    def spawn_workerdb(self) -> WorkerRuleDBForest:
        primary_conn, worker_conn = multiprocessing.Pipe(duplex=False)
        self.connections.append(primary_conn)
        return WorkerRuleDBForest(conn=worker_conn, reverse=self.reverse)

    def monitor_connection_until_spec(self, status_update) -> None:
        print("ruledb", os.getpid())
        start = time.time()
        while not self.has_specification():
            # TODO: send verified labels to classqueue
            # self.searcher.queue.set_verified(...)
            ready_connections = multiprocessing.connection.wait(self.connections)
            for conn in ready_connections:
                assert isinstance(conn, multiprocessing.connection.Connection)
                message = conn.recv()
                self._add_keys_to_table(message)
            if time.time() - start > status_update:
                logger.info(self.searcher.status())
                start = time.time()
