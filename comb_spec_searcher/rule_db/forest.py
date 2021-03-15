from typing import (
    Callable,
    Deque,
    Dict,
    Generic,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    TypeVar,
)

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
    The function maps natural number to n to a natural number or infinity (represented
    by the use of None)

    The default value of the function is 0.
    """

    def __init__(self) -> None:
        self._value: List[Optional[int]] = []
        self._preimage_count: DefaultList[int] = DefaultList(int)
        self._infinity_count: int = 0

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
        Set the value of the given key to infinity.
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
        parts = [
            f"{i} -> {v if v is not None else '∞'}" for i, v in enumerate(self._value)
        ]
        return "\n".join(parts)


class ForestRuleDB:
    def __init__(self) -> None:
        self._rules: List[RuleKey] = []
        self._rules_using_class: DefaultList[List[Tuple[int, int]]] = DefaultList(list)
        self._rules_pumping_class: DefaultList[List[int]] = DefaultList(list)
        self._function: Function = Function()
        self._shifts: List[List[Optional[int]]] = []
        self._gap_size: int = 1
        self._processing_queue: Deque[int] = Deque()
        self._rule_holding_extra_terms: Set[int] = set()
        self._current_gap: Tuple[int, int] = (1, 1)

    @property
    def function(self) -> Dict[int, Optional[int]]:
        """
        Return a dict representing the function of the ruledb with only the non-zero
        values.
        """
        return self._function.to_dict()

    def add_rule(self, rule_key: RuleKey, shifts_for_zero: Tuple[int, ...]):
        """
        Add the rule key and update all the attributes accordingly.

        INPUTS:
          - `rule_key`
          - `shifts_for_zero`: The values of the shifts if all the classes of
            the rule where at 0.
        """
        self._rules.append(rule_key)
        self._shifts.append(self._compute_shift(rule_key, shifts_for_zero))
        max_gap = max((abs(s) for s in shifts_for_zero), default=0)
        if max_gap > self._gap_size:
            self._gap_size = max_gap
            self._correct_gap()
        if self._function[rule_key[0]] is not None:
            rule_idx = len(self._rules) - 1
            self._rules_pumping_class[rule_key[0]].append(rule_idx)
            for child_idx, child in enumerate(rule_key[1]):
                if self._function[child] is not None:
                    self._rules_using_class[child].append((rule_idx, child_idx))
            self._processing_queue.append(rule_idx)
        self._process_queue()

    def is_pumping(self, comb_class: int) -> bool:
        """
        Determine if the comb_class is pumping in the current universe.
        """
        assert not self._processing_queue and not self._rule_holding_extra_terms
        return self._function[comb_class] is None

    def pumping_subuniverse(self) -> Iterator[RuleKey]:
        """
        Iterator over all the rules that contain only pumping combinatorial classes.
        """
        stable_subset = set(self._function.preimage(None))
        for rule_key in self._rules:
            if rule_key[0] in stable_subset and stable_subset.issuperset(rule_key[1]):
                yield rule_key

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

    @staticmethod
    def _can_give_terms(shifts: List[Optional[int]]) -> bool:
        """
        Return True if the shifts indicate that a new terms can be computed.
        """
        return all(s is None or s > 0 for s in shifts)

    def _process_queue(self) -> None:
        """
        Try to make improvement with all the class in the processing queue.
        """
        while self._processing_queue or self._rule_holding_extra_terms:
            while self._processing_queue:
                rule_idx = self._processing_queue.popleft()
                shifts = self._shifts[rule_idx]
                if self._can_give_terms(shifts):
                    parent = self._rules[rule_idx][0]
                    self._increase_value(parent, rule_idx)
            if self._rule_holding_extra_terms:
                rule_idx = self._rule_holding_extra_terms.pop()
                self._set_infinite(self._rules[rule_idx][0])

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
        for rule_idx in self._rules_pumping_class[comb_class]:
            shifts = self._shifts[rule_idx]
            for i, v in enumerate(shifts):
                shifts[i] = v - 1 if v is not None else None
            if self._can_give_terms(shifts):
                self._processing_queue.append(rule_idx)
        # Correction of the shifts for rules using comb_class to pump
        for rule_idx, class_idx in self._rules_using_class[comb_class]:
            shifts = self._shifts[rule_idx]
            current_shift = shifts[class_idx]
            assert current_shift is not None
            shifts[class_idx] = current_shift + 1
            if self._can_give_terms(shifts):
                self._processing_queue.append(rule_idx)

    def _set_infinite(self, comb_class: int) -> None:
        """
        Set the value if the class to infinity.

        This should happen when we know that we can move anything on the left of the
        gap.
        """
        current_value = self._function[comb_class]
        assert current_value is not None
        assert current_value > self._current_gap[1]
        assert not self._processing_queue
        self._function.set_infinite(comb_class)
        # Cleaning the class pumping this comb_class
        for rule_idx in self._rules_pumping_class[comb_class]:
            for child in self._rules[rule_idx][1]:
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
            """Return a string for the in and inifinit if None"""
            if v is None:
                return "∞"
            return str(v)

        rule_key = self._rules[rule_idx]
        shifts = map(v_to_str, self._shifts[rule_idx])
        current_value = f"{v_to_str(self._function[rule_key[0]])} -> " + ", ".join(
            map(v_to_str, (self._function[c] for c in rule_key[1]))
        )
        child_with_shift = ", ".join(f"({c}, {s})" for c, s in zip(rule_key[1], shifts))
        s = f"{rule_key[0]} -> {child_with_shift} || {current_value}"
        return s

    def status(self):
        """
        Print the rule_info for tall the rules.
        Mostly intended for debugging.
        """
        for i in range(len(self._rules)):
            print(self.rule_info(i))
