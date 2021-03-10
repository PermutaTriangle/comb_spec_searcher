from typing import Callable, Deque, Generic, Iterator, List, Set, Tuple, TypeVar

from comb_spec_searcher.typing import RuleKey

T = TypeVar("T")


class DefaultList(Generic[T]):
    def __init__(self, default_factory: Callable[[], T]):
        self._default_factory = default_factory
        self._list: List[T] = []

    def _increase_list_len(self, key: int) -> None:
        """
        Increase the length of the list to the give key.
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
        return repr(self._list)


class Function:
    """
    A python representation of a function.
    The function maps natural number to n to a natural number.
    The default value of the function is 0.
    """

    def __init__(self) -> None:
        self._value: List[int] = []
        self._preimage_count: DefaultList[int] = DefaultList(int)

    def __getitem__(self, key: int) -> int:
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
        except IndexError:
            self._increase_list_len(key)
            old_value = 0
        self._value[key] += 1
        self._preimage_count[old_value] -= 1
        self._preimage_count[old_value + 1] += 1

    def preimage_gap(self, length: int) -> int:
        """
        Return the smallest k such that the preimage of [k, k+length-1]
        is empty.
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

    def __str__(self) -> str:
        parts = [f"{i} -> {v}" for i, v in enumerate(self._value)]
        return "\n".join(parts)


class ForestRuleDB:
    def __init__(self) -> None:
        self._rules: List[RuleKey] = []
        self._rules_using_class: DefaultList[List[Tuple[int, int]]] = DefaultList(list)
        self._rules_pumping_class: DefaultList[List[int]] = DefaultList(list)
        self._function: Function = Function()
        self._shifts: List[List[int]] = []
        self._gap_size: int = 1
        self._processing_queue: Deque[int] = Deque()
        self._rule_holding_extra_terms: Set[int] = set()
        self._current_gap: Tuple[int, int] = (1, 1)

    def _add_rule(self, rule_key: RuleKey, shifts_for_zero: Tuple[int, ...]):
        """
        Add the rule key and update all the attributes accordingly.

        INPUTS:
          - `rule_key`
          - `shifts_for_zero`: The values of the shifts if all the classes of
            the rule where at 0.
        """
        self._rules.append(rule_key)
        rule_idx = len(self._rules) - 1
        self._rules_pumping_class[rule_key[0]].append(rule_idx)
        for child_idx, child in enumerate(rule_key[1]):
            self._rules_using_class[child].append((rule_idx, child_idx))
        parent_current_value = self._function[rule_key[0]]
        self._shifts.append(
            [
                self._function[child]
                + shifts_for_zero[child_idx]
                - parent_current_value
                for child_idx, child in enumerate(rule_key[1])
            ]
        )
        max_gap = max((abs(s) for s in shifts_for_zero), default=0)
        self._processing_queue.append(rule_idx)
        if max_gap > self._gap_size:
            self._gap_size = max_gap
            self._correct_gap()

    @staticmethod
    def _can_give_terms(shifts: List[int]) -> bool:
        """
        Return True if the shifts indicate that a new terms can be computed.
        """
        return all(s > 0 for s in shifts)

    def _process_queue(self) -> None:
        """
        Try to make improvement with all the class in the processing queue.
        """
        while self._processing_queue:
            rule_idx = self._processing_queue.popleft()
            shifts = self._shifts[rule_idx]
            if self._can_give_terms(shifts):
                parent = self._rules[rule_idx][0]
                self._increase_value(parent, rule_idx)
        # TODO: When the queue is empty we can infer that things are in the stable
        # subset. That can then be used to make a better gap correction.

    def _correct_gap(self) -> None:
        k = self._function.preimage_gap(self._gap_size)
        new_gap = (k, k + self._gap_size - 1)
        if new_gap[1] > self._current_gap[1]:
            self._processing_queue.extend(self._rule_holding_extra_terms)
            self._rule_holding_extra_terms.clear()
        self._current_gap = new_gap

    def _increase_value(self, comb_class: int, rule_idx: int) -> None:
        """
        Increase the value of the comb_class and put on the processing stack any rule
        that can now give a new term.

        The rule_idx must indicate the rule used to justify the increase.
        """
        if self._function[comb_class] > self._current_gap[0]:
            self._rule_holding_extra_terms.add(rule_idx)
            return
        self._function.increase_value(comb_class)
        # Correction of the gap
        gap_start = self._function.preimage_gap(self._gap_size)
        if self._current_gap[0] != gap_start:
            self._correct_gap()
        # Correction of the shifts for rule pumping comb_class
        for rule_idx in self._rules_pumping_class[comb_class]:
            shifts = self._shifts[rule_idx]
            for i in range(len(shifts)):
                shifts[i] -= 1
            if self._can_give_terms(shifts):
                self._processing_queue.append(rule_idx)
        # Correction of the shifts for rules using comb_class to pump
        for rule_idx, class_idx in self._rules_using_class[comb_class]:
            shifts = self._shifts[rule_idx]
            shifts[class_idx] += 1
            if self._can_give_terms(shifts):
                self._processing_queue.append(rule_idx)

    def rule_info(self, rule_idx: int) -> str:
        """
        Return a string with information about a particular rule.
        Mostly intended for debugging.
        """
        rule_key = self._rules[rule_idx]
        return str(rule_key)
