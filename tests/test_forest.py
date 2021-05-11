import itertools
from typing import Dict, List, Union

import pytest

from comb_spec_searcher.rule_db.forest import RuleDBForest, Function
from comb_spec_searcher.typing import ForestRuleKey, RuleBucket


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
    ruledb = RuleDBForest()
    rules = [
        ForestRuleKey(0, (1, 2), (0, 0), RuleBucket.NORMAL),
        ForestRuleKey(1, (), (), RuleBucket.VERIFICATION),  # Empty verif
        ForestRuleKey(2, (3,), (0,), RuleBucket.NORMAL),  # point placement
        ForestRuleKey(3, (4,), (0,), RuleBucket.NORMAL),  # row col sep
        ForestRuleKey(4, (5, 0, 0), (0, 1, 1), RuleBucket.NORMAL),  # factor
        ForestRuleKey(5, (), (), RuleBucket.VERIFICATION),  # point verif
        ForestRuleKey(2, (6,), (2,), RuleBucket.UNDEFINED),  # dumb rule
    ]
    for rule in rules:
        ruledb.add_rule(rule)
    assert ruledb.function == {i: None for i in range(6)}
    assert all(ruledb.is_pumping(c) for c in range(6))
    assert not ruledb.is_pumping(6)
    assert sorted(fk.key for fk in ruledb.pumping_subuniverse()) == [
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
    ruledb = RuleDBForest()

    # Point insertion
    ruledb.add_rule(ForestRuleKey(0, (1, 2), (0, 0), RuleBucket.NORMAL))
    assert ruledb.function == {}

    # Empty verif
    ruledb.add_rule(ForestRuleKey(1, (), (), RuleBucket.VERIFICATION))
    assert ruledb.function == {1: None}

    # Point placement
    ruledb.add_rule(ForestRuleKey(2, (3,), (0,), RuleBucket.NORMAL))
    assert ruledb.function == {1: None}

    # Row col sep
    ruledb.add_rule(ForestRuleKey(3, (4,), (0,), RuleBucket.NORMAL))
    assert ruledb.function == {1: None}

    # Point verif
    ruledb.add_rule(ForestRuleKey(5, (), (), RuleBucket.VERIFICATION))
    assert ruledb.function == {1: None, 5: None}

    # Dumb rule
    ruledb.add_rule(ForestRuleKey(2, (6,), (-2,), RuleBucket.UNDEFINED))
    assert ruledb.function == {1: None, 5: None}

    # Dumb rule. This will pump 2 and 0 a little bit
    ruledb.add_rule(ForestRuleKey(2, (7,), (2,), RuleBucket.UNDEFINED))
    assert ruledb.function == {0: 2, 1: None, 2: 2, 5: None}

    # Factor
    ruledb.add_rule(ForestRuleKey(4, (5, 0, 0), (0, 1, 1), RuleBucket.NORMAL))
    assert ruledb.function == {i: None for i in range(6)}


def test_universe_not_pumping():
    ruledb = RuleDBForest()
    rules = [
        ForestRuleKey(0, (1, 2), (0, 0), RuleBucket.NORMAL),  # point insertion
        ForestRuleKey(5, (), (), RuleBucket.VERIFICATION),  # point verif
        ForestRuleKey(2, (3,), (0,), RuleBucket.NORMAL),  # point placement
        ForestRuleKey(3, (4,), (0,), RuleBucket.NORMAL),  # row col sep
        ForestRuleKey(4, (5, 0, 0), (0, 1, 1), RuleBucket.NORMAL),  # factor
    ]
    for rule in rules:
        ruledb.add_rule(rule)
    assert ruledb.function == {2: 1, 3: 1, 4: 1, 5: None}


def test_segmented():
    """The segemented forest."""
    ruledb = RuleDBForest()
    ruledb.add_rule(ForestRuleKey(0, (1, 2), (0, 0), RuleBucket.UNDEFINED))
    ruledb.add_rule(ForestRuleKey(1, (4, 14), (0, 0), RuleBucket.UNDEFINED))
    ruledb.add_rule(ForestRuleKey(2, tuple(), tuple(), RuleBucket.UNDEFINED))
    assert ruledb.function == {2: None}

    ruledb.add_rule(ForestRuleKey(3, (16, 5), (1, 0), RuleBucket.UNDEFINED))
    ruledb.add_rule(ForestRuleKey(4, tuple(), tuple(), RuleBucket.UNDEFINED))
    ruledb.add_rule(ForestRuleKey(5, tuple(), tuple(), RuleBucket.UNDEFINED))
    assert ruledb.function == {2: None, 3: 1, 4: None, 5: None}

    # Induced a gap size change
    ruledb.add_rule(ForestRuleKey(6, (7, 5, 17), (2, 1, 1), RuleBucket.UNDEFINED))
    assert ruledb.function == {2: None, 3: 1, 4: None, 5: None, 6: 1}

    ruledb.add_rule(ForestRuleKey(16, (6,), (0,), RuleBucket.UNDEFINED))
    assert ruledb.function == {2: None, 3: 2, 4: None, 5: None, 6: 1, 16: 1}

    ruledb.add_rule(ForestRuleKey(7, tuple(), tuple(), RuleBucket.UNDEFINED))
    ruledb.add_rule(ForestRuleKey(8, (9, 5), (1, 0), RuleBucket.UNDEFINED))
    assert ruledb.function == {
        2: None,
        3: 2,
        4: None,
        5: None,
        6: 1,
        7: None,
        8: 1,
        16: 1,
    }

    ruledb.add_rule(ForestRuleKey(12, (20, 5), (-1, 0), RuleBucket.UNDEFINED))
    ruledb.add_rule(ForestRuleKey(20, (13,), (0,), RuleBucket.UNDEFINED))
    ruledb.add_rule(ForestRuleKey(13, (15, 2, 5), (-1, 1, 0), RuleBucket.UNDEFINED))
    ruledb.add_rule(ForestRuleKey(15, (1,), (0,), RuleBucket.UNDEFINED))
    ruledb.add_rule(ForestRuleKey(14, (3,), (0,), RuleBucket.UNDEFINED))
    assert ruledb.function == {
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
    }

    ruledb.add_rule(ForestRuleKey(18, (8,), (0,), RuleBucket.UNDEFINED))
    ruledb.add_rule(ForestRuleKey(11, (12, 18), (0, 0), RuleBucket.UNDEFINED))
    assert ruledb.function == {
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
    }

    ruledb.add_rule(ForestRuleKey(17, (8,), (0,), RuleBucket.UNDEFINED))
    assert ruledb.function == {
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
    }

    ruledb.add_rule(ForestRuleKey(9, (0, 19), (0, 0), RuleBucket.UNDEFINED))
    ruledb.add_rule(ForestRuleKey(10, (5, 11), (0, 1), RuleBucket.UNDEFINED))
    assert ruledb.function == {
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
    }

    ruledb.add_rule(ForestRuleKey(19, (10,), (0,), RuleBucket.UNDEFINED))
    assert ruledb.function == {i: None for i in range(21)}
    assert all(ruledb.is_pumping(c) for c in range(21))
