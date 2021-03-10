import itertools
from typing import Dict, List, Tuple, Union

import pytest

from comb_spec_searcher.rule_db.forest import ForestRuleDB, Function


def assert_function_values(
    function: Function, values: Union[Dict[int, int], List[int]], gap: Tuple[int, int]
):
    """
    Check that the function values matches the given values.
    """
    if isinstance(values, dict):
        values = [values[i] if i in values else 0 for i in range(max(values) + 1)]
    gap_size = gap[1] - gap[0] + 1
    gap_start = function.preimage_gap(gap_size)
    gap_end = function.preimage_gap(gap_size) + gap_size - 1
    if gap != (gap_start, gap_end):
        m = "The gap doesn't match:\n"
        m += f"The expected gap was {gap}, but the gap found is {(gap_start, gap_end)}.\n"
        m += f"The function values are:\n{function._value}\n"
        m += f"The expected values are:\n{values}"
        raise AssertionError(m)
    failing_index = []
    for n, (fv, gv) in enumerate(
        itertools.zip_longest(function._value, values, fillvalue=0)
    ):
        if not (fv == gv or fv > gv > gap_end):
            failing_index.append(n)

    if failing_index:
        m = f"Function differs on index {failing_index}\n"
        m += f"The function values are {function._value}\n"
        m += f"The expected values are {values}"
        raise AssertionError(m)


class TestFunction:
    def test_add_value(self):
        f = Function()
        assert f[0] == 0
        assert f[4] == 0
        f.increase_value(0)
        assert f[0] == 1
        f.increase_value(3)
        assert f[4] == 0
        f.increase_value(4)
        assert f[0] == 1
        assert f[1] == 0
        assert f[2] == 0
        assert f[3] == 1
        assert f[4] == 1
        assert f[5] == 0
        assert f[6] == 0

    def test_find_gap(self):
        f = Function()
        f.increase_value(0)
        f.increase_value(0)
        f.increase_value(0)
        f.increase_value(0)
        f.increase_value(1)
        f.increase_value(2)
        assert f[0] == 4
        assert f[1] == 1
        assert f[2] == 1
        assert f[3] == 0
        assert f[4] == 0
        assert f[5] == 0
        assert f[6] == 0
        assert f.preimage_gap(1) == 2
        assert f.preimage_gap(2) == 2
        assert f.preimage_gap(3) == 5
        with pytest.raises(ValueError):
            f.preimage_gap(0)
        with pytest.raises(ValueError):
            f.preimage_gap(-1)

    def test_find_gap2(self):
        f = Function()
        f.increase_value(2)
        f.increase_value(3)
        f.increase_value(4)
        f.increase_value(5)
        f.increase_value(5)
        f.increase_value(5)
        print(f)
        print(f._preimage_count)
        assert f[0] == 0
        assert f[1] == 0
        assert f[2] == 1
        assert f[3] == 1
        assert f[4] == 1
        assert f[5] == 3
        assert f.preimage_gap(1) == 2
        assert f.preimage_gap(2) == 4
        assert f.preimage_gap(3) == 4


def test_132_universe_pumping():
    """
    The universe consist of the rule of the usual 132 tree plus a dummy rule that is
    useless.
    """
    ruledb = ForestRuleDB()
    ruledb._add_rule((0, (1, 2)), (0, 0))  # Point insertion
    ruledb._add_rule((1, tuple()), tuple())  # Empty verif
    ruledb._add_rule((2, (3,)), (0,))  # point placement
    ruledb._add_rule((3, (4,)), (0,))  # row col sep
    ruledb._add_rule((4, (5, 0, 0)), (0, 1, 1))  # factor
    ruledb._add_rule((5, tuple()), tuple())  # point verif
    ruledb._add_rule((2, (6,)), (2,))  # dumb rule
    ruledb._process_queue()
    assert_function_values(ruledb._function, [3, 5, 3, 3, 3, 5], (1, 2))


def test_132_universe_pumping_progressive():
    """
    The universe consist of the rule of the usual 132 tree plus a dummy rule that is
    useless.

    We add rule progressively and make sure the function is always up to date.
    """
    ruledb = ForestRuleDB()
    ruledb._add_rule((0, (1, 2)), (0, 0))  # Point insertion
    ruledb._process_queue()
    assert_function_values(ruledb._function, [], (1, 1))

    ruledb._add_rule((1, tuple()), tuple())  # Empty verif
    ruledb._process_queue()
    assert_function_values(ruledb._function, [0, 2], (1, 1))

    ruledb._add_rule((2, (3,)), (0,))  # point placement
    ruledb._process_queue()
    assert_function_values(ruledb._function, [0, 2], (1, 1))

    ruledb._add_rule((3, (4,)), (0,))  # row col sep
    ruledb._process_queue()
    assert_function_values(ruledb._function, [0, 2], (1, 1))

    ruledb._add_rule((5, tuple()), tuple())  # point verif
    ruledb._process_queue()
    assert_function_values(ruledb._function, [0, 2, 0, 0, 0, 2], (1, 1))

    # The rule increase the size of the gap needed. The verified things should bump.
    ruledb._add_rule((2, (6,)), (-2,))  # dumb rule
    ruledb._process_queue()
    assert_function_values(ruledb._function, [0, 3, 0, 0, 0, 3], (1, 2))

    # This will pump to and 0 a little bit
    ruledb._add_rule((2, (7,)), (2,))  # dumb rule
    ruledb._process_queue()
    assert_function_values(ruledb._function, [2, 5, 2, 0, 0, 5], (3, 4))

    ruledb._add_rule((4, (5, 0, 0)), (0, 1, 1))  # factor
    ruledb._process_queue()
    assert_function_values(ruledb._function, [3, 5, 3, 3, 3, 5], (1, 2))


def test_universe_not_pumping():
    ruledb = ForestRuleDB()
    ruledb._add_rule((0, (1, 2)), (0, 0))  # Point insertion
    ruledb._add_rule((5, tuple()), tuple())  # point verif
    ruledb._add_rule((2, (3,)), (0,))  # point placement
    ruledb._add_rule((3, (4,)), (0,))  # row col sep
    ruledb._add_rule((4, (5, 0, 0)), (0, 1, 1))  # factor
    ruledb._process_queue()
    assert_function_values(ruledb._function, [0, 0, 1, 1, 1, 3], (2, 2))


def test_segmented():
    """The segemented forest."""
    ruledb = ForestRuleDB()
    ruledb._add_rule((0, (1, 2)), (0, 0))
    ruledb._add_rule((1, (4, 14)), (0, 0))
    ruledb._add_rule((2, tuple()), tuple())
    ruledb._process_queue()
    assert_function_values(ruledb._function, {2: 2}, (1, 1))

    ruledb._add_rule((3, (16, 5)), (1, 0))
    ruledb._add_rule((4, tuple()), tuple())
    ruledb._add_rule((5, tuple()), tuple())
    ruledb._process_queue()
    assert_function_values(ruledb._function, {2: 3, 3: 1, 4: 3, 5: 3}, (2, 2))

    # Induced a gap size change
    ruledb._add_rule((6, (7, 5, 17)), (2, 1, 1))
    ruledb._process_queue()
    assert_function_values(ruledb._function, {2: 4, 3: 1, 4: 4, 5: 4, 6: 1}, (2, 3))

    ruledb._add_rule((16, (6,)), (0,))
    ruledb._process_queue()
    assert_function_values(
        ruledb._function, {2: 5, 3: 2, 4: 5, 5: 5, 6: 1, 16: 1}, (3, 4)
    )

    ruledb._add_rule((7, tuple()), tuple())
    ruledb._add_rule((8, (9, 5)), (1, 0))
    ruledb._process_queue()
    assert_function_values(
        ruledb._function, {2: 5, 3: 2, 4: 5, 5: 5, 6: 1, 7: 5, 8: 1, 16: 1}, (3, 4)
    )

    ruledb._add_rule((12, (20, 5)), (-1, 0))
    ruledb._add_rule((20, (13,)), (0,))
    ruledb._add_rule((13, (15, 2, 5)), (-1, 1, 0))
    ruledb._add_rule((15, (1,)), (0,))
    ruledb._add_rule((14, (3,)), (0,))
    ruledb._process_queue()
    assert_function_values(
        ruledb._function,
        {
            0: 2,
            1: 2,
            2: 5,
            3: 2,
            4: 5,
            5: 5,
            6: 1,
            7: 5,
            8: 1,
            13: 1,
            14: 2,
            15: 2,
            16: 1,
            20: 1,
        },
        (3, 4),
    )

    ruledb._add_rule((18, (8,)), (0,))
    ruledb._add_rule((11, (12, 18)), (0, 0))
    ruledb._process_queue()
    assert_function_values(
        ruledb._function,
        {
            0: 2,
            1: 2,
            2: 5,
            3: 2,
            4: 5,
            5: 5,
            6: 1,
            7: 5,
            8: 1,
            13: 1,
            14: 2,
            15: 2,
            16: 1,
            18: 1,
            20: 1,
        },
        (3, 4),
    )

    ruledb._add_rule((17, (8,)), (0,))
    ruledb._process_queue()
    assert_function_values(
        ruledb._function,
        {
            0: 3,
            1: 3,
            2: 6,
            3: 3,
            4: 6,
            5: 6,
            6: 2,
            7: 6,
            8: 1,
            11: 1,
            12: 1,
            13: 2,
            14: 3,
            15: 3,
            16: 2,
            17: 1,
            18: 1,
            20: 2,
        },
        (4, 5),
    )

    ruledb._add_rule((9, (0, 19)), (0, 0))
    ruledb._add_rule((10, (5, 11)), (0, 1))
    ruledb._process_queue()
    assert_function_values(
        ruledb._function,
        {
            0: 3,
            1: 3,
            2: 6,
            3: 3,
            4: 6,
            5: 6,
            6: 2,
            7: 6,
            8: 1,
            10: 2,
            11: 1,
            12: 1,
            13: 2,
            14: 3,
            15: 3,
            16: 2,
            17: 1,
            18: 1,
            20: 2,
        },
        (4, 5),
    )

    ruledb._add_rule((19, (10,)), (0,))
    ruledb._process_queue()
    assert_function_values(ruledb._function, {i: 2 for i in range(21)}, (0, 1))
