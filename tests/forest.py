import itertools
from typing import Dict, List, Union

import pytest

from comb_spec_searcher.rule_db.forest import ForestRuleDB, Function


def assert_function_values(
    function: Function, values: Union[Dict[int, int], List[int]]
):
    """
    Check that the function values matches the given values.
    """
    if isinstance(values, dict):
        values = [values[i] if i in values else 0 for i in range(max(values) + 1)]
    failing_index = []
    for n, (fv, gv) in enumerate(
        itertools.zip_longest(function._value, values, fillvalue=0)
    ):
        if not (fv == gv):
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
        with pytest.raises(ValueError):
            assert sorted(f.preimage(0)) == []
        assert sorted(f.preimage(1)) == [0, 3, 4]
        assert sorted(f.preimage(2)) == []

    def test_infinity(self):
        f = Function()
        f.increase_value(0)
        f.increase_value(3)
        f.increase_value(4)
        f.set_infinite(3)
        assert f[0] == 1
        assert f[1] == 0
        assert f[2] == 0
        assert f[3] is None
        assert f[4] == 1
        assert f.preimage_gap(100) == 2
        assert sorted(f.preimage(None)) == [3]
        assert sorted(f.preimage(1)) == [0, 4]

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
    ruledb.add_rule((0, (1, 2)), (0, 0))  # Point insertion
    ruledb.add_rule((1, tuple()), tuple())  # Empty verif
    ruledb.add_rule((2, (3,)), (0,))  # point placement
    ruledb.add_rule((3, (4,)), (0,))  # row col sep
    ruledb.add_rule((4, (5, 0, 0)), (0, 1, 1))  # factor
    ruledb.add_rule((5, tuple()), tuple())  # point verif
    ruledb.add_rule((2, (6,)), (2,))  # dumb rule
    assert_function_values(ruledb._function, {i: None for i in range(6)})
    assert all(ruledb.is_pumping(c) for c in range(6))
    assert not ruledb.is_pumping(6)
    assert sorted(ruledb.pumping_subuniverse()) == [
        (0, (1, 2)),
        (1, tuple()),
        (2, (3,)),
        (3, (4,)),
        (4, (5, 0, 0)),
        (5, tuple()),
    ]


def test_132_universe_pumping_progressive():
    """
    The universe consist of the rule of the usual 132 tree plus a dummy rule that is
    useless.

    We add rule progressively and make sure the function is always up to date.
    """
    ruledb = ForestRuleDB()
    ruledb.add_rule((0, (1, 2)), (0, 0))  # Point insertion
    assert_function_values(ruledb._function, [])

    ruledb.add_rule((1, tuple()), tuple())  # Empty verif
    assert_function_values(ruledb._function, [0, None])

    ruledb.add_rule((2, (3,)), (0,))  # point placement
    assert_function_values(ruledb._function, [0, None])

    ruledb.add_rule((3, (4,)), (0,))  # row col sep
    assert_function_values(ruledb._function, [0, None])

    ruledb.add_rule((5, tuple()), tuple())  # point verif
    assert_function_values(ruledb._function, [0, None, 0, 0, 0, None])

    # The rule increase the size of the gap needed. The verified things should bump.
    ruledb.add_rule((2, (6,)), (-2,))  # dumb rule
    assert_function_values(ruledb._function, [0, None, 0, 0, 0, None])

    # This will pump to and 0 a little bit
    ruledb.add_rule((2, (7,)), (2,))  # dumb rule
    assert_function_values(ruledb._function, [2, None, 2, 0, 0, None])

    ruledb.add_rule((4, (5, 0, 0)), (0, 1, 1))  # factor
    assert_function_values(ruledb._function, {i: None for i in range(6)})


def test_universe_not_pumping():
    ruledb = ForestRuleDB()
    ruledb.add_rule((0, (1, 2)), (0, 0))  # Point insertion
    ruledb.add_rule((5, tuple()), tuple())  # point verif
    ruledb.add_rule((2, (3,)), (0,))  # point placement
    ruledb.add_rule((3, (4,)), (0,))  # row col sep
    ruledb.add_rule((4, (5, 0, 0)), (0, 1, 1))  # factor
    assert_function_values(ruledb._function, [0, 0, 1, 1, 1, None])


def test_segmented():
    """The segemented forest."""
    ruledb = ForestRuleDB()
    ruledb.add_rule((0, (1, 2)), (0, 0))
    ruledb.add_rule((1, (4, 14)), (0, 0))
    ruledb.add_rule((2, tuple()), tuple())
    assert_function_values(ruledb._function, {2: None})

    ruledb.add_rule((3, (16, 5)), (1, 0))
    ruledb.add_rule((4, tuple()), tuple())
    ruledb.add_rule((5, tuple()), tuple())
    assert_function_values(ruledb._function, {2: None, 3: 1, 4: None, 5: None})

    # Induced a gap size change
    ruledb.add_rule((6, (7, 5, 17)), (2, 1, 1))
    assert_function_values(ruledb._function, {2: None, 3: 1, 4: None, 5: None, 6: 1})

    ruledb.add_rule((16, (6,)), (0,))
    assert_function_values(
        ruledb._function, {2: None, 3: 2, 4: None, 5: None, 6: 1, 16: 1}
    )

    ruledb.add_rule((7, tuple()), tuple())
    ruledb.add_rule((8, (9, 5)), (1, 0))
    assert_function_values(
        ruledb._function, {2: None, 3: 2, 4: None, 5: None, 6: 1, 7: None, 8: 1, 16: 1}
    )

    ruledb.add_rule((12, (20, 5)), (-1, 0))
    ruledb.add_rule((20, (13,)), (0,))
    ruledb.add_rule((13, (15, 2, 5)), (-1, 1, 0))
    ruledb.add_rule((15, (1,)), (0,))
    ruledb.add_rule((14, (3,)), (0,))
    assert_function_values(
        ruledb._function,
        {
            0: 2,
            1: 2,
            2: None,
            3: 2,
            4: None,
            5: None,
            6: 1,
            7: None,
            8: 1,
            13: 1,
            14: 2,
            15: 2,
            16: 1,
            20: 1,
        },
    )

    ruledb.add_rule((18, (8,)), (0,))
    ruledb.add_rule((11, (12, 18)), (0, 0))
    assert_function_values(
        ruledb._function,
        {
            0: 2,
            1: 2,
            2: None,
            3: 2,
            4: None,
            5: None,
            6: 1,
            7: None,
            8: 1,
            13: 1,
            14: 2,
            15: 2,
            16: 1,
            18: 1,
            20: 1,
        },
    )

    ruledb.add_rule((17, (8,)), (0,))
    assert_function_values(
        ruledb._function,
        {
            0: 3,
            1: 3,
            2: None,
            3: 3,
            4: None,
            5: None,
            6: 2,
            7: None,
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
    )

    ruledb.add_rule((9, (0, 19)), (0, 0))
    ruledb.add_rule((10, (5, 11)), (0, 1))
    assert_function_values(
        ruledb._function,
        {
            0: 3,
            1: 3,
            2: None,
            3: 3,
            4: None,
            5: None,
            6: 2,
            7: None,
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
    )

    ruledb.add_rule((19, (10,)), (0,))
    assert_function_values(ruledb._function, {i: None for i in range(21)})
    assert all(ruledb.is_pumping(c) for c in range(21))
