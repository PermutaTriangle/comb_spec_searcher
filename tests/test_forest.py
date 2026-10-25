import itertools
import random
from types import SimpleNamespace
from typing import Dict, List, Union

import pytest

import comb_spec_searcher.rule_db.forest as forest_module
from comb_spec_searcher import CombinatorialSpecificationSearcher
from comb_spec_searcher.rule_db.forest import (
    DefaultList,
    ForestRuleExtractor,
    Function,
    RuleDBForest,
    TableMethod,
)
from comb_spec_searcher.strategies.strategy import EmptyStrategy
from comb_spec_searcher.typing import ForestRuleKey, RuleBucket
from example import AvoidingWithPrefix, pack


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

    def test_increase_value_tells_whether_the_values_taken_changed(self):
        """
        increase_value returns True exactly when a value stops being taken or
        starts being taken.
        """
        f = Function()
        f[3]  # four classes with value 0
        assert f.increase_value(0)  # 1 is taken for the first time
        assert not f.increase_value(1)  # 0 and 1 stay taken
        assert not f.increase_value(2)
        assert f.increase_value(3)  # 0 is no longer taken
        assert f.increase_value(3)  # 2 is taken for the first time
        assert not f.increase_value(2)  # 1 and 2 stay taken
        assert not f.increase_value(1)
        assert f.increase_value(0)  # 1 is no longer taken


# Test of the table method


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
    assert tb.function == {
        2: None,
        3: 2,
        4: None,
        5: None,
        6: 1,
        7: None,
        8: 1,
        16: 1,
    }

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


def test_default_list_copy():
    """
    A copy of a default list shares its items with the list copied until one of
    the two changes them.
    """
    default_list = DefaultList(list)
    default_list.mutable(0).append(1)
    default_list.mutable(2).append(2)
    copy = default_list.copy()
    copy.mutable(0).append(3)
    # an item is copied once, then changed in place
    assert copy.mutable(0) is copy.mutable(0)
    default_list.mutable(2).append(4)
    copy[1] = [5]
    copy.append([6])
    default_list.mutable(4).append(7)
    assert list(default_list) == [[1], [], [2, 4], [], [7]]
    assert list(copy) == [[1, 3], [5], [2], [6]]
    again = copy.copy()
    again.mutable(0).append(8)
    copy.mutable(3).append(9)
    assert list(copy) == [[1, 3], [5], [2], [6, 9]]
    assert list(again) == [[1, 3, 8], [5], [2], [6]]


def test_default_list_copy_of_a_changed_copy():
    """
    A copy of a list that changed an item since it was itself copied shares that
    item again, which a change in place must then not reach.
    """
    original = DefaultList(list)
    original.mutable(0).append(1)
    first = original.copy()
    first.mutable(0).append(2)
    second = first.copy()
    first.mutable(0).append(3)
    assert list(second) == [[1, 2]]
    assert list(first) == [[1, 2, 3]]
    assert list(original) == [[1]]


def test_table_copy():
    """
    A copy of a table and the table copied take rules of their own without
    changing each other, and each ends as a table built with its rules.
    """
    base = [
        ForestRuleKey(0, (1, 2), (0, 0), RuleBucket.NORMAL),
        ForestRuleKey(1, (), (), RuleBucket.VERIFICATION),
        ForestRuleKey(2, (3,), (0,), RuleBucket.NORMAL),
    ]
    more = [
        ForestRuleKey(3, (4,), (0,), RuleBucket.NORMAL),
        ForestRuleKey(4, (5, 0, 0), (0, 1, 1), RuleBucket.NORMAL),
        ForestRuleKey(5, (), (), RuleBucket.VERIFICATION),
    ]
    other = [ForestRuleKey(3, (), (), RuleBucket.VERIFICATION)]

    def table(rules):
        new_table = TableMethod()
        for rule in rules:
            new_table.add_rule_key(rule)
        return new_table

    original = table(base)
    before = original.function
    copy = original.copy()
    for rule in more:
        copy.add_rule_key(rule)
    assert original.function == before
    after = copy.function
    for rule in other:
        original.add_rule_key(rule)
    assert copy.function == after
    assert copy.function == table(base + more).function == {i: None for i in range(6)}
    assert (
        original.function == table(base + other).function == {i: None for i in range(4)}
    )


def table_state(table):
    """
    Everything a table holds, its lists of shifts and of rules included.
    """
    # pylint: disable=protected-access
    return (
        list(table._rules),
        [list(shifts) for shifts in table._shifts],
        [list(rules) for rules in table._rules_using_class],
        [list(rules) for rules in table._rules_pumping_class],
        list(table._function._value),
        table._gap_size,
        table._current_gap,
    )


def table_values(table):
    """
    What a table means: the values of its classes (None for one that pumps) and
    its gap. Its lists of shifts can hold different stale entries for the rules
    of a class that pumps, as the rules held for extra terms come out of a set,
    in an order that depends on the set's history.
    """
    # pylint: disable=protected-access
    return (list(table._function._value), table._gap_size, table._current_gap)


def random_rule_keys(random_generator):
    """
    The rules of a random forest: verifications, and rules of one to three
    children with shifts from -2 to 3, each once.
    """
    labels = list(range(random_generator.randint(3, 10)))
    rule_keys = []
    for _ in range(random_generator.randint(len(labels), 4 * len(labels))):
        parent = random_generator.choice(labels)
        if random_generator.random() < 0.2:
            rule_keys.append(ForestRuleKey(parent, (), (), RuleBucket.VERIFICATION))
        else:
            children = tuple(
                random_generator.choice(labels)
                for _ in range(random_generator.randint(1, 3))
            )
            shifts = tuple(
                random_generator.choice([-2, -1, 0, 0, 1, 1, 2, 3]) for _ in children
            )
            rule_keys.append(ForestRuleKey(parent, children, shifts, RuleBucket.NORMAL))
    return list(dict.fromkeys(rule_keys))


def test_table_copies_on_random_forests():
    """
    On 300 seeded random forests, a table copied partway, and the copy extended
    with the remaining rules: the original keeps the state of a table built from
    its own rules, its lists included, and the copy gets the values of a table
    built from all of them. Then the original is extended too, with the copy
    alive, and both have the full table's values.
    """

    def built(rule_keys):
        table = TableMethod()
        for rule_key in rule_keys:
            table.add_rule_key(rule_key)
        return table

    for seed in range(300):
        random_generator = random.Random(seed)
        rule_keys = random_rule_keys(random_generator)
        split = random_generator.randrange(len(rule_keys) + 1)
        original = built(rule_keys[:split])
        copy = original.copy()
        for rule_key in rule_keys[split:]:
            copy.add_rule_key(rule_key)
        full = table_values(built(rule_keys))
        assert table_state(original) == table_state(built(rule_keys[:split])), seed
        assert table_values(copy) == full, seed
        for rule_key in rule_keys[split:]:
            original.add_rule_key(rule_key)
        assert table_values(original) == full, seed
        assert table_values(copy) == full, seed


# The values of the tables built from the first ten random forests, as develop
# (826a16c) gives them: the classes' values (None for a class that pumps), the
# gap's size and the current gap.
TABLE_VALUES_BEFORE = {
    0: ([None, None, None, None, None, None, None, None, None], 3, (0, 2)),
    1: ([None, None, None, None, None], 3, (0, 2)),
    2: ([1, 1, 0], 2, (2, 3)),
    3: ([None, None, None, None, None, None], 3, (0, 2)),
    4: ([None, None, None, None, None, None], 3, (0, 2)),
    5: ([None, None, None, None, None, None, None], 3, (0, 2)),
    6: ([None, None, None, None], 3, (0, 2)),
    7: ([None, 0, None, None, 0, 0, None, 0], 3, (1, 3)),
    8: ([None, None, None, None, None, None], 3, (0, 2)),
    9: ([None, None, 0, None, None, None, None, None, None, None], 2, (1, 2)),
}


def test_table_values_on_random_forests_as_before():
    """
    The tables built from the first ten random forests have the values they had
    before tables were copied. Unlike those test_table_copies_on_random_forests
    compares, these values do not come from TableMethod.
    """
    for seed, values in TABLE_VALUES_BEFORE.items():
        table = TableMethod()
        for rule_key in random_rule_keys(random.Random(seed)):
            table.add_rule_key(rule_key)
        assert table_values(table) == values, seed


def minimize_as_before(root, rule_by_bucket):
    """
    The extractor's minimization as it was before it copied tables.
    """

    def is_productive(rule_keys):
        table = TableMethod()
        for rule_key in rule_keys:
            table.add_rule_key(rule_key)
        return table.is_pumping(root)

    needed_rules = []
    for bucket in ForestRuleExtractor.MINIMIZE_ORDER:
        maybe_useful = []
        not_minimizing = [needed_rules, maybe_useful]
        not_minimizing.extend(
            rules for other, rules in rule_by_bucket.items() if other != bucket
        )
        minimizing = rule_by_bucket[bucket]
        while minimizing:
            table = TableMethod()
            for rule_key in itertools.chain.from_iterable(not_minimizing):
                table.add_rule_key(rule_key)
            if table.is_pumping(root):
                minimizing.clear()
                break
            for i, rule_key in enumerate(minimizing):
                table.add_rule_key(rule_key)
                if table.is_pumping(root):
                    break
            else:
                raise RuntimeError("Not pumping after adding all rules")
            maybe_useful.append(rule_key)
            del minimizing[i:]
        while maybe_useful:
            rule_key = maybe_useful.pop()
            if not is_productive(itertools.chain.from_iterable(not_minimizing)):
                needed_rules.append(rule_key)
    return needed_rules


@pytest.mark.parametrize(
    "patterns",
    [["ababa", "babb"], ["abaab", "babb", "bbaa"], ["abba", "aaba", "babaa"]],
)
def test_minimization_keeps_the_same_rules(patterns):
    """
    The extractor keeps the rules it kept before it copied tables, in the same
    order.
    """
    start_class = AvoidingWithPrefix("", patterns, ["a", "b"])
    ruledb = RuleDBForest()
    searcher = CombinatorialSpecificationSearcher(start_class, pack, ruledb=ruledb)
    searcher.auto_search()
    extractor = ForestRuleExtractor(
        ruledb.root_label, ruledb, ruledb.classdb, ruledb.strategy_pack
    )
    extractor.check()
    stable_rules = extractor._sorted_stable_rules(ruledb.table_method)
    assert extractor.needed_rules == minimize_as_before(ruledb.root_label, stable_rules)


# The rules the extractor kept before it copied tables (develop at 826a16c), in
# their order, for three classes whose universes are expanded level by level.
RULES_KEPT_BEFORE = {
    ("ababa", "babb"): [
        (0, (1, 2, 3), (0, 0, 0), "NORMAL"),
        (2, (4, 5, 6), (0, 0, 0), "NORMAL"),
        (5, (4, 2), (1, 1), "NORMAL"),
        (3, (7, 8, 9), (0, 0, 0), "NORMAL"),
        (9, (7, 3), (1, 1), "NORMAL"),
        (6, (10, 11, 12), (0, 0, 0), "NORMAL"),
        (12, (10, 3), (1, 2), "NORMAL"),
        (8, (13, 14, 15), (0, 0, 0), "NORMAL"),
        (14, (13, 2), (1, 2), "NORMAL"),
        (11, (16, 17, 18), (0, 0, 0), "NORMAL"),
        (17, (16, 2), (1, 3), "NORMAL"),
        (15, (19, 20, 21), (0, 0, 0), "NORMAL"),
        (20, (7, 11), (3, 1), "NORMAL"),
        (18, (22, 23, 24), (0, 0, 0), "EQUIV"),
        (1, (), (), "VERIFICATION"),
        (4, (), (), "VERIFICATION"),
        (7, (), (), "VERIFICATION"),
        (10, (), (), "VERIFICATION"),
        (13, (), (), "VERIFICATION"),
        (16, (), (), "VERIFICATION"),
        (19, (), (), "VERIFICATION"),
        (21, (), (), "VERIFICATION"),
        (22, (), (), "VERIFICATION"),
        (23, (), (), "VERIFICATION"),
        (24, (), (), "VERIFICATION"),
    ],
    ("abaab", "babb", "bbaa"): [
        (0, (1, 2, 3), (0, 0, 0), "NORMAL"),
        (2, (4, 5, 6), (0, 0, 0), "NORMAL"),
        (5, (4, 2), (1, 1), "NORMAL"),
        (3, (7, 8, 9), (0, 0, 0), "NORMAL"),
        (6, (10, 11, 12), (0, 0, 0), "NORMAL"),
        (12, (4, 9), (2, 1), "NORMAL"),
        (8, (13, 14, 15), (0, 0, 0), "NORMAL"),
        (14, (13, 2), (1, 2), "NORMAL"),
        (9, (16, 17, 18), (0, 0, 0), "NORMAL"),
        (18, (7, 9), (2, 1), "NORMAL"),
        (11, (19, 20, 21), (0, 0, 0), "NORMAL"),
        (21, (4, 15), (3, 1), "NORMAL"),
        (15, (22, 23, 24), (0, 0, 0), "NORMAL"),
        (23, (7, 11), (3, 1), "NORMAL"),
        (17, (25, 26, 27), (0, 0, 0), "NORMAL"),
        (27, (7, 15), (3, 1), "NORMAL"),
        (20, (28, 29, 30), (0, 0, 0), "NORMAL"),
        (29, (28, 2), (1, 4), "NORMAL"),
        (1, (), (), "VERIFICATION"),
        (4, (), (), "VERIFICATION"),
        (7, (), (), "VERIFICATION"),
        (10, (), (), "VERIFICATION"),
        (13, (), (), "VERIFICATION"),
        (16, (), (), "VERIFICATION"),
        (19, (), (), "VERIFICATION"),
        (22, (), (), "VERIFICATION"),
        (24, (), (), "VERIFICATION"),
        (25, (), (), "VERIFICATION"),
        (26, (), (), "VERIFICATION"),
        (28, (), (), "VERIFICATION"),
        (30, (), (), "VERIFICATION"),
    ],
    ("abba", "aaba", "babaa"): [
        (0, (1, 2, 3), (0, 0, 0), "NORMAL"),
        (2, (4, 5, 6), (0, 0, 0), "NORMAL"),
        (3, (7, 8, 9), (0, 0, 0), "NORMAL"),
        (9, (7, 3), (1, 1), "NORMAL"),
        (5, (10, 11, 12), (0, 0, 0), "NORMAL"),
        (11, (4, 5), (2, 1), "NORMAL"),
        (6, (13, 14, 15), (0, 0, 0), "NORMAL"),
        (14, (4, 8), (2, 1), "NORMAL"),
        (8, (16, 17, 18), (0, 0, 0), "NORMAL"),
        (17, (7, 5), (2, 1), "NORMAL"),
        (12, (19, 20, 21), (0, 0, 0), "NORMAL"),
        (21, (4, 15), (3, 1), "NORMAL"),
        (15, (22, 23, 24), (0, 0, 0), "NORMAL"),
        (24, (22, 3), (1, 3), "NORMAL"),
        (18, (25, 26, 27), (0, 0, 0), "NORMAL"),
        (27, (7, 15), (3, 1), "NORMAL"),
        (26, (28, 29, 30), (0, 0, 0), "NORMAL"),
        (30, (16, 18), (3, 2), "NORMAL"),
        (1, (), (), "VERIFICATION"),
        (4, (), (), "VERIFICATION"),
        (7, (), (), "VERIFICATION"),
        (10, (), (), "VERIFICATION"),
        (13, (), (), "VERIFICATION"),
        (16, (), (), "VERIFICATION"),
        (19, (), (), "VERIFICATION"),
        (20, (), (), "VERIFICATION"),
        (22, (), (), "VERIFICATION"),
        (23, (), (), "VERIFICATION"),
        (25, (), (), "VERIFICATION"),
        (28, (), (), "VERIFICATION"),
        (29, (), (), "VERIFICATION"),
    ],
}


@pytest.mark.parametrize("patterns", list(RULES_KEPT_BEFORE))
def test_minimization_keeps_the_rules_kept_before(patterns):
    """
    The extractor keeps, in the same order, the rules it kept before it copied
    tables, on universes expanded level by level, which leave nothing to timing.
    Unlike test_minimization_keeps_the_same_rules, the rules to keep do not come
    from TableMethod, so that a fault in the table is seen.
    """
    ruledb = RuleDBForest()
    searcher = CombinatorialSpecificationSearcher(
        AvoidingWithPrefix("", list(patterns), ["a", "b"]), pack, ruledb=ruledb
    )
    while not ruledb.has_specification():
        searcher.do_level()
    extractor = ForestRuleExtractor(
        ruledb.root_label, ruledb, ruledb.classdb, ruledb.strategy_pack
    )
    extractor.check()
    assert [
        (rule_key.parent, rule_key.children, rule_key.shifts, rule_key.bucket.name)
        for rule_key in extractor.needed_rules
    ] == RULES_KEPT_BEFORE[patterns]


def test_justified_rules():
    """
    The rules that justify the root's value leave out the rules that do not help it,
    and make it pump on their own.
    """
    needed = [
        ForestRuleKey(0, (1, 2), (0, 0), RuleBucket.NORMAL),
        ForestRuleKey(1, (), (), RuleBucket.VERIFICATION),
        ForestRuleKey(2, (3,), (0,), RuleBucket.NORMAL),
        ForestRuleKey(3, (4,), (0,), RuleBucket.NORMAL),
        ForestRuleKey(4, (5, 0, 0), (0, 1, 1), RuleBucket.NORMAL),
        ForestRuleKey(5, (), (), RuleBucket.VERIFICATION),
    ]
    useless = [
        ForestRuleKey(2, (6,), (2,), RuleBucket.UNDEFINED),  # 6 has no rule
        ForestRuleKey(3, (4,), (1,), RuleBucket.NORMAL),  # added once 3 pumps
    ]
    table = TableMethod(record_justifications=True)
    for rule in needed + useless:
        table.add_rule_key(rule)
    justified = table.justified_rules(0)
    assert set(justified) == set(needed)
    alone = TableMethod()
    for rule in justified:
        alone.add_rule_key(rule)
    assert alone.is_pumping(0)
    with pytest.raises(ValueError):
        TableMethod().justified_rules(0)


def test_forest_justifying_rules_only():
    """
    Minimizing only the rules that justify the root still gives a specification.
    """
    alphabet = ["a", "b"]
    start_class = AvoidingWithPrefix("", ["ababa", "babb"], alphabet)
    ruledb = RuleDBForest(justifying_rules_only=True)
    searcher = CombinatorialSpecificationSearcher(start_class, pack, ruledb=ruledb)
    spec = searcher.auto_search()
    expected_count = [1, 2, 4, 8, 15, 27, 48, 87, 157, 283]
    assert [spec.count_objects_of_size(size) for size in range(10)] == expected_count


def test_justified_rules_on_random_forests():
    """
    On 300 seeded random forests, a table that records justifications has the
    values of one that does not. For every class, a table of the rules that
    justify it, alone, gives the class at least its value (and a class that
    pumps pumps), and the rules come in the order they were added.
    """
    for seed in range(300):
        rule_keys = random_rule_keys(random.Random(seed))
        recording = TableMethod(record_justifications=True)
        plain = TableMethod()
        for rule_key in rule_keys:
            recording.add_rule_key(rule_key)
            plain.add_rule_key(rule_key)
        assert table_values(recording) == table_values(plain), seed
        for label in range(len(table_values(plain)[0])):
            justified = recording.justified_rules(label)
            assert justified == [
                rule_key for rule_key in rule_keys if rule_key in justified
            ], (seed, label)
            alone = TableMethod()
            for rule_key in justified:
                alone.add_rule_key(rule_key)
            if plain.is_pumping(label):
                assert alone.is_pumping(label), (seed, label)
            else:
                assert alone.is_pumping(label) or alone.function.get(
                    label, 0
                ) >= plain.function.get(label, 0), (seed, label)


def test_copy_of_a_table_that_records_justifications():
    """
    A copy of a table that records justifications records them too, and the two
    are independent. On 300 seeded random forests, a table is copied partway and
    the copy extended with the remaining rules in reverse order, so that its new
    rules' indices are those of other rules in the original: the rules that
    justify each class in the copy give it its value on their own. Then the
    original is extended too, in order, with the copy alive: its justifications
    are those of a table built from all the rules, and the copy's do not change.
    """

    def built(rule_keys):
        table = TableMethod(record_justifications=True)
        for rule_key in rule_keys:
            table.add_rule_key(rule_key)
        return table

    for seed in range(300):
        random_generator = random.Random(seed)
        rule_keys = random_rule_keys(random_generator)
        split = random_generator.randrange(len(rule_keys) + 1)
        original = built(rule_keys[:split])
        copy = original.copy()
        for rule_key in reversed(rule_keys[split:]):
            copy.add_rule_key(rule_key)
        labels = range(len(table_values(copy)[0]))
        copy_justified = [copy.justified_rules(label) for label in labels]
        for label, justified in zip(labels, copy_justified):
            alone = TableMethod()
            for rule_key in justified:
                alone.add_rule_key(rule_key)
            assert alone.is_pumping(label) or not copy.is_pumping(label), seed
            assert alone.is_pumping(label) or alone.function.get(
                label, 0
            ) >= copy.function.get(label, 0), (seed, label)
        for rule_key in rule_keys[split:]:
            original.add_rule_key(rule_key)
        full = built(rule_keys)
        assert [original.justified_rules(label) for label in labels] == [
            full.justified_rules(label) for label in labels
        ], seed
        assert [copy.justified_rules(label) for label in labels] == copy_justified, seed


# The rules the extractor keeps from the random forest of seed 225, by default
# and with justifying_rules_only: the option keeps a different, larger minimal
# set.
RULES_KEPT_FROM_SEED_225 = {
    False: [
        (5, (5, 1, 1), (1, 0, -2), "NORMAL"),
        (0, (4, 1), (0, 1), "NORMAL"),
        (1, (5,), (3,), "NORMAL"),
        (4, (), (), "VERIFICATION"),
    ],
    True: [
        (0, (4, 1), (0, 1), "NORMAL"),
        (3, (4,), (-2,), "NORMAL"),
        (5, (3, 3), (-1, -2), "NORMAL"),
        (1, (5,), (3,), "NORMAL"),
        (4, (), (), "VERIFICATION"),
    ],
}


def test_justifying_rules_only_changes_the_rules_kept():
    """
    On the random forest of seed 225, the extractor keeps other rules with
    justifying_rules_only than without it, and the default is without it. Both
    sets make the root pump, and each of their rules is needed.
    """
    table = TableMethod()
    for rule_key in random_rule_keys(random.Random(225)):
        table.add_rule_key(rule_key)
    ruledb = SimpleNamespace(table_method=table)
    kept = {
        False: ForestRuleExtractor(0, ruledb, None, None).needed_rules,
        True: ForestRuleExtractor(
            0, ruledb, None, None, justifying_rules_only=True
        ).needed_rules,
    }
    for option, rule_keys in kept.items():
        assert [
            (rule_key.parent, rule_key.children, rule_key.shifts, rule_key.bucket.name)
            for rule_key in rule_keys
        ] == RULES_KEPT_FROM_SEED_225[option]
        for index in range(len(rule_keys) + 1):
            alone = TableMethod()
            for rule_key in rule_keys[:index] + rule_keys[index + 1 :]:
                alone.add_rule_key(rule_key)
            # without a rule the root does not pump; with all of them it does
            assert alone.is_pumping(0) == (index == len(rule_keys)), (option, index)


def test_forest_passes_justifying_rules_only_to_the_extractor(monkeypatch):
    """
    RuleDBForest gives the extractor its justifying_rules_only, which is False by
    default.
    """
    options_given = []

    class Extractor(ForestRuleExtractor):
        def __init__(self, *args, justifying_rules_only=False):
            options_given.append(justifying_rules_only)
            super().__init__(*args, justifying_rules_only=justifying_rules_only)

    monkeypatch.setattr(forest_module, "ForestRuleExtractor", Extractor)
    for option, ruledb in (
        (False, RuleDBForest()),
        (True, RuleDBForest(justifying_rules_only=True)),
    ):
        options_given.clear()
        start_class = AvoidingWithPrefix("", ["ababa", "babb"], ["a", "b"])
        CombinatorialSpecificationSearcher(
            start_class, pack, ruledb=ruledb
        ).auto_search()
        assert options_given and all(given is option for given in options_given)


@pytest.mark.parametrize("justifying_rules_only", [False, True])
def test_extractor_of_a_root_that_does_not_pump(justifying_rules_only):
    """
    With a root that does not pump, the extractor raises the same error with
    justifying_rules_only as without it, rather than keeping no rules.
    """
    table = TableMethod()
    table.add_rule_key(ForestRuleKey(1, (), (), RuleBucket.VERIFICATION))
    table.add_rule_key(ForestRuleKey(0, (2,), (0,), RuleBucket.NORMAL))
    assert not table.is_pumping(0)
    with pytest.raises(RuntimeError):
        ForestRuleExtractor(
            0,
            SimpleNamespace(table_method=table),
            None,
            None,
            justifying_rules_only=justifying_rules_only,
        )


def test_justified_rules_of_classes_apart():
    """
    The rules that justify a class leave out those of classes it does not use,
    and come in the order they were added. A class that no rule raised, or a
    label never seen, has none; a class a rule raised to a finite value has that
    rule.
    """
    rule_keys = [
        ForestRuleKey(0, (1,), (0,), RuleBucket.NORMAL),
        ForestRuleKey(1, (), (), RuleBucket.VERIFICATION),
        ForestRuleKey(7, (8,), (0,), RuleBucket.NORMAL),
        ForestRuleKey(8, (), (), RuleBucket.VERIFICATION),
        ForestRuleKey(2, (3,), (1,), RuleBucket.NORMAL),  # raises 2 to 1, no further
        ForestRuleKey(4, (5,), (0,), RuleBucket.NORMAL),  # 5 has no rule: 4 stays 0
    ]
    table = TableMethod(record_justifications=True)
    for rule_key in rule_keys:
        table.add_rule_key(rule_key)
    assert table.function == {0: None, 1: None, 2: 1, 7: None, 8: None}
    assert table.justified_rules(0) == rule_keys[:2]
    assert table.justified_rules(1) == [rule_keys[1]]
    assert table.justified_rules(7) == rule_keys[2:4]
    assert table.justified_rules(2) == [rule_keys[4]]
    assert table.justified_rules(4) == []
    assert table.justified_rules(5) == []
    assert table.justified_rules(99) == []


class LargestFirstSet(set):
    """
    A set that gives its largest element first, both when popped and when
    iterated over: another order than this Python's sets give, as CPython's and
    PyPy's sets of integers give different orders.
    """

    def pop(self):
        largest = max(self)
        self.remove(largest)
        return largest

    def __iter__(self):
        return iter(sorted(set.__iter__(self), reverse=True))


def test_justified_rules_whatever_order_a_set_gives():
    """
    In a table that records justifications, the rules held for extra terms
    leave in the order they were added to the table, and go back to the queue
    in that order, so the rules that justify a class do not depend on the order
    a set gives its elements in. On 1000 seeded random forests, a table whose
    set of held rules gives its largest element first records the same
    justifications (the order back to the queue matters on few of them, seed
    549 the first).
    """
    for seed in range(1000):
        rule_keys = random_rule_keys(random.Random(seed))
        table = TableMethod(record_justifications=True)
        other_order = TableMethod(record_justifications=True)
        # pylint: disable=protected-access
        other_order._rule_holding_extra_terms = LargestFirstSet()
        for rule_key in rule_keys:
            table.add_rule_key(rule_key)
            other_order.add_rule_key(rule_key)
        labels = range(len(table_values(table)[0]))
        assert [table.justified_rules(label) for label in labels] == [
            other_order.justified_rules(label) for label in labels
        ], seed


def test_justifying_rules_only_whatever_order_a_set_gives(monkeypatch):
    """
    With justifying_rules_only, the extractor keeps the same rules when the
    sets of rules held for extra terms give their largest element first, so the
    same on CPython as on PyPy: on 300 seeded random forests whose root pumps.
    """
    forests = []
    for seed in range(300):
        table = TableMethod()
        for rule_key in random_rule_keys(random.Random(seed)):
            table.add_rule_key(rule_key)
        if table.is_pumping(0):
            forests.append((seed, SimpleNamespace(table_method=table)))
    assert len(forests) > 100

    def rules_kept():
        return [
            ForestRuleExtractor(
                0, ruledb, None, None, justifying_rules_only=True
            ).needed_rules
            for _, ruledb in forests
        ]

    kept = rules_kept()
    original_init = TableMethod.__init__

    def init_with_largest_first(self, record_justifications=False):
        original_init(self, record_justifications=record_justifications)
        # pylint: disable=protected-access
        self._rule_holding_extra_terms = LargestFirstSet()

    monkeypatch.setattr(TableMethod, "__init__", init_with_largest_first)
    for (seed, _), rule_keys, other_order in zip(forests, kept, rules_kept()):
        assert rule_keys == other_order, seed


def test_justifying_rules_only_prunes_until_all_rules_left_justify_the_root(
    monkeypatch,
):
    """
    With justifying_rules_only, the extractor prunes the rules still to
    minimize before each bucket until all of them justify the root's value in a
    table of the rules kept and those left: on 300 seeded random forests whose
    root pumps, after each of the four prunings.
    """
    keep_justifying_rules = ForestRuleExtractor._keep_justifying_rules
    prunings = []

    def keep_and_check(extractor):
        keep_justifying_rules(extractor)
        table = TableMethod(record_justifications=True)
        for rule_key in extractor.needed_rules:
            table.add_rule_key(rule_key)
        for bucket in reversed(ForestRuleExtractor.MINIMIZE_ORDER):
            for rule_key in extractor.rule_by_bucket[bucket]:
                table.add_rule_key(rule_key)
        justifying = set(table.justified_rules(extractor.root_label))
        assert all(
            rule_key in justifying
            for rule_keys in extractor.rule_by_bucket.values()
            for rule_key in rule_keys
        )
        prunings.append(extractor)

    monkeypatch.setattr(ForestRuleExtractor, "_keep_justifying_rules", keep_and_check)
    for seed in range(300):
        table = TableMethod()
        for rule_key in random_rule_keys(random.Random(seed)):
            table.add_rule_key(rule_key)
        if table.is_pumping(0):
            ForestRuleExtractor(
                0,
                SimpleNamespace(table_method=table),
                None,
                None,
                justifying_rules_only=True,
            )
    assert len(prunings) > 400


def test_rule_added_first_justifies_a_class_set_infinite():
    """
    Class 0 has two rules, through 1 and through 2, and both are held for extra
    terms when the verification of 3 makes the classes pump, the one through 2
    first. The one added first, through 1, which also raised the values of 0,
    justifies 0 when it is set infinite, so the rules through 2 are not needed
    to justify it.
    """
    rule_keys = [
        ForestRuleKey(0, (1,), (0,), RuleBucket.NORMAL),
        ForestRuleKey(0, (2,), (0,), RuleBucket.NORMAL),
        ForestRuleKey(1, (3,), (0,), RuleBucket.NORMAL),
        ForestRuleKey(2, (3,), (0,), RuleBucket.NORMAL),
        ForestRuleKey(3, (), (), RuleBucket.VERIFICATION),
    ]
    table = TableMethod(record_justifications=True)
    for rule_key in rule_keys:
        table.add_rule_key(rule_key)
    assert table.function == {0: None, 1: None, 2: None, 3: None}
    assert table.justified_rules(0) == [rule_keys[0], rule_keys[2], rule_keys[4]]
    assert table.justified_rules(2) == [rule_keys[3], rule_keys[4]]
