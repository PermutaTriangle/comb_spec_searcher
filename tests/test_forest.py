from comb_spec_searcher_rs import ForestRuleKey, RuleBucket

from comb_spec_searcher import CombinatorialSpecificationSearcher
from comb_spec_searcher.rule_db.forest import RuleDBForest, TableMethod
from comb_spec_searcher.strategies.strategy import EmptyStrategy
from example import AvoidingWithPrefix, pack


# Test of the table method
def test_rule_key_eq():
    key1 = ForestRuleKey(0, (1, 2), (0, 0), RuleBucket.NORMAL)
    key2 = ForestRuleKey(0, (1, 2), (0, 0), RuleBucket.NORMAL)
    key3 = ForestRuleKey(1, (), (), RuleBucket.VERIFICATION)
    assert key1 == key2
    assert key1 != key3
    assert key2 != key3


def test_132_universe_pumping():
    """
    The universe consist of the rule of the usual 132 tree plus a dummy rule that is
    useless.
    """
    tb = TableMethod()
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
        tb.add_rule_key(rule)
    assert tb.function == {i: None for i in range(6)}
    assert all(tb.is_pumping(c) for c in range(6))
    assert not tb.is_pumping(6)
    assert sorted(fk.key for fk in tb.pumping_subuniverse()) == [
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
    tb = TableMethod()

    # Point insertion
    tb.add_rule_key(ForestRuleKey(0, (1, 2), (0, 0), RuleBucket.NORMAL))
    assert tb.function == {}

    # Empty verif
    tb.add_rule_key(ForestRuleKey(1, (), (), RuleBucket.VERIFICATION))
    assert tb.function == {1: None}

    # Point placement
    tb.add_rule_key(ForestRuleKey(2, (3,), (0,), RuleBucket.NORMAL))
    assert tb.function == {1: None}

    # Row col sep
    tb.add_rule_key(ForestRuleKey(3, (4,), (0,), RuleBucket.NORMAL))
    assert tb.function == {1: None}

    # Point verif
    tb.add_rule_key(ForestRuleKey(5, (), (), RuleBucket.VERIFICATION))
    assert tb.function == {1: None, 5: None}

    # Dumb rule
    tb.add_rule_key(ForestRuleKey(2, (6,), (-2,), RuleBucket.UNDEFINED))
    assert tb.function == {1: None, 5: None}

    # Dumb rule. This will pump 2 and 0 a little bit
    tb.add_rule_key(ForestRuleKey(2, (7,), (2,), RuleBucket.UNDEFINED))
    assert tb.function == {0: 2, 1: None, 2: 2, 5: None}

    # Factor
    tb.add_rule_key(ForestRuleKey(4, (5, 0, 0), (0, 1, 1), RuleBucket.NORMAL))
    assert tb.function == {i: None for i in range(6)}


def test_universe_not_pumping():
    tb = TableMethod()
    rules = [
        ForestRuleKey(0, (1, 2), (0, 0), RuleBucket.NORMAL),  # point insertion
        ForestRuleKey(5, (), (), RuleBucket.VERIFICATION),  # point verif
        ForestRuleKey(2, (3,), (0,), RuleBucket.NORMAL),  # point placement
        ForestRuleKey(3, (4,), (0,), RuleBucket.NORMAL),  # row col sep
        ForestRuleKey(4, (5, 0, 0), (0, 1, 1), RuleBucket.NORMAL),  # factor
    ]
    for rule in rules:
        tb.add_rule_key(rule)
    assert tb.function == {2: 1, 3: 1, 4: 1, 5: None}


def test_segmented():
    """The segemented forest."""
    tb = TableMethod()
    tb.add_rule_key(ForestRuleKey(0, (1, 2), (0, 0), RuleBucket.UNDEFINED))
    tb.add_rule_key(ForestRuleKey(1, (4, 14), (0, 0), RuleBucket.UNDEFINED))
    tb.add_rule_key(ForestRuleKey(2, tuple(), tuple(), RuleBucket.UNDEFINED))
    assert tb.function == {2: None}

    tb.add_rule_key(ForestRuleKey(3, (16, 5), (1, 0), RuleBucket.UNDEFINED))
    tb.add_rule_key(ForestRuleKey(4, tuple(), tuple(), RuleBucket.UNDEFINED))
    tb.add_rule_key(ForestRuleKey(5, tuple(), tuple(), RuleBucket.UNDEFINED))
    assert tb.function == {2: None, 3: 1, 4: None, 5: None}

    # Induced a gap size change
    tb.add_rule_key(ForestRuleKey(6, (7, 5, 17), (2, 1, 1), RuleBucket.UNDEFINED))
    assert tb.function == {2: None, 3: 1, 4: None, 5: None, 6: 1}

    tb.add_rule_key(ForestRuleKey(16, (6,), (0,), RuleBucket.UNDEFINED))
    assert tb.function == {2: None, 3: 2, 4: None, 5: None, 6: 1, 16: 1}

    tb.add_rule_key(ForestRuleKey(7, tuple(), tuple(), RuleBucket.UNDEFINED))
    tb.add_rule_key(ForestRuleKey(8, (9, 5), (1, 0), RuleBucket.UNDEFINED))
    assert tb.function == {2: None, 3: 2, 4: None, 5: None, 6: 1, 7: None, 8: 1, 16: 1}

    tb.add_rule_key(ForestRuleKey(12, (20, 5), (-1, 0), RuleBucket.UNDEFINED))
    tb.add_rule_key(ForestRuleKey(20, (13,), (0,), RuleBucket.UNDEFINED))
    tb.add_rule_key(ForestRuleKey(13, (15, 2, 5), (-1, 1, 0), RuleBucket.UNDEFINED))
    tb.add_rule_key(ForestRuleKey(15, (1,), (0,), RuleBucket.UNDEFINED))
    tb.add_rule_key(ForestRuleKey(14, (3,), (0,), RuleBucket.UNDEFINED))
    assert tb.function == {
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

    tb.add_rule_key(ForestRuleKey(18, (8,), (0,), RuleBucket.UNDEFINED))
    tb.add_rule_key(ForestRuleKey(11, (12, 18), (0, 0), RuleBucket.UNDEFINED))
    assert tb.function == {
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

    tb.add_rule_key(ForestRuleKey(17, (8,), (0,), RuleBucket.UNDEFINED))
    assert tb.function == {
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

    tb.add_rule_key(ForestRuleKey(9, (0, 19), (0, 0), RuleBucket.UNDEFINED))
    tb.add_rule_key(ForestRuleKey(10, (5, 11), (0, 1), RuleBucket.UNDEFINED))
    assert tb.function == {
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

    tb.add_rule_key(ForestRuleKey(19, (10,), (0,), RuleBucket.UNDEFINED))
    assert tb.function == {i: None for i in range(21)}
    assert all(tb.is_pumping(c) for c in range(21))


# Test of the extractor


def test_emtpy_rule_first():
    """
    When recomputing the rules. The forest extractor should favor the empty rule.
    """
    empty_class = AvoidingWithPrefix("ab", ["ab"], ["a", "b"])
    assert empty_class.is_empty()
    css = CombinatorialSpecificationSearcher(empty_class, pack, ruledb=RuleDBForest())
    spec = css.auto_search()
    assert isinstance(spec.rules_dict[empty_class].strategy, EmptyStrategy)
