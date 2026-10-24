import pytest
import sympy

from comb_spec_searcher.strategies import DisjointUnionStrategy
from comb_spec_searcher.strategies.rule import EquivalenceRule
from example import AvoidingWithPrefix, ExpansionStrategy, RemoveFrontOfPrefix, Word


def test_reverse_equivalence():
    comb_class = AvoidingWithPrefix("aaa", ["aaaa"], "a", False)
    rule = ExpansionStrategy()(comb_class)
    eqv_rule = rule.to_equivalence_rule()
    assert len(rule.non_empty_children()) == 1
    equiv_then_reverse = rule.to_equivalence_rule().to_reverse_rule(0)
    assert equiv_then_reverse.is_equivalence()
    assert equiv_then_reverse.children == (comb_class,)
    assert equiv_then_reverse.comb_class == rule.non_empty_children()[0]
    assert isinstance(equiv_then_reverse, EquivalenceRule)
    reverse_then_equiv = rule.to_reverse_rule(0).to_equivalence_rule()
    assert reverse_then_equiv.is_equivalence()
    assert reverse_then_equiv.children == (comb_class,)
    assert reverse_then_equiv.comb_class == rule.non_empty_children()[0]
    assert isinstance(reverse_then_equiv, EquivalenceRule)
    assert (
        eqv_rule.formal_step == "Either just the prefix, or append a"
        " letter from the alphabet but only child and index 0 is non-empty"
    )
    assert reverse_then_equiv.formal_step == f"reverse of '{eqv_rule.formal_step}'"
    assert equiv_then_reverse.formal_step == f"reverse of '{eqv_rule.formal_step}'"


def test_complement_rule():
    comb_class = AvoidingWithPrefix("aaa", ["aaaa"], "abc", False)
    rule = ExpansionStrategy()(comb_class)
    all_comb_classes = (rule.comb_class,) + rule.children
    x = sympy.var("x")

    def get_function(w):
        i = all_comb_classes.index(w)
        return sympy.Function(f"F_{i}")(x)

    reverse0 = rule.to_reverse_rule(0)
    reverse1 = rule.to_reverse_rule(1)
    reverse2 = rule.to_reverse_rule(2)
    reverse3 = rule.to_reverse_rule(3)
    for i in range(4):
        rule.sanity_check(i)
        reverse0.sanity_check(i)
        reverse1.sanity_check(i)
        reverse2.sanity_check(i)
        reverse3.sanity_check(i)
    assert rule.get_equation(get_function) == sympy.sympify(
        "Eq(F_0(x), F_1(x) + F_2(x) + F_3(x) + F_4(x))"
    )
    assert reverse0.get_equation(get_function) == sympy.sympify(
        "Eq(F_1(x), F_0(x) - F_2(x) - F_3(x) - F_4(x))"
    )
    assert reverse1.get_equation(get_function) == sympy.sympify(
        "Eq(F_2(x), F_0(x) - F_1(x) - F_3(x) - F_4(x))"
    )
    assert reverse2.get_equation(get_function) == sympy.sympify(
        "Eq(F_3(x), F_0(x) - F_1(x) - F_2(x) - F_4(x))"
    )
    assert reverse3.get_equation(get_function) == sympy.sympify(
        "Eq(F_4(x), F_0(x) - F_1(x) - F_2(x) - F_3(x))"
    )


def test_quotient_rule():
    comb_class = AvoidingWithPrefix("aaa", ["aa"], "a", False)
    rule = RemoveFrontOfPrefix()(comb_class)

    all_comb_classes = (rule.comb_class,) + rule.children
    x = sympy.var("x")

    def get_function(w):
        i = all_comb_classes.index(w)
        return sympy.Function(f"F_{i}")(x)

    reverse0 = rule.to_reverse_rule(0)
    reverse1 = rule.to_reverse_rule(1)
    assert rule.get_equation(get_function) == sympy.sympify(
        "Eq(F_0(x), F_1(x) * F_2(x))"
    )
    assert reverse0.get_equation(get_function) == sympy.sympify(
        "Eq(F_1(x), F_0(x) / F_2(x))"
    )
    assert reverse1.get_equation(get_function) == sympy.sympify(
        "Eq(F_2(x), F_0(x) / F_1(x))"
    )


class UpperCaseExpansionStrategy(ExpansionStrategy):
    """
    The expansion of a class of words, with every child's words in upper case,
    so that the rule's maps change the words they map.
    """

    @staticmethod
    def upper(avoiding_with_prefix):
        return AvoidingWithPrefix(
            avoiding_with_prefix.prefix.upper(),
            [pattern.upper() for pattern in avoiding_with_prefix.patterns],
            [letter.upper() for letter in avoiding_with_prefix.alphabet],
            avoiding_with_prefix.just_prefix,
        )

    def decomposition_function(self, avoiding_with_prefix):
        children = super().decomposition_function(avoiding_with_prefix)
        if children is None:
            return None
        return tuple(self.upper(child) for child in children)

    def forward_map(self, avoiding_with_prefix, word, children=None):
        lower_case_children = ExpansionStrategy.decomposition_function(
            self, avoiding_with_prefix
        )
        image = super().forward_map(avoiding_with_prefix, word, lower_case_children)
        return tuple(None if part is None else Word(part.upper()) for part in image)

    def backward_map(self, avoiding_with_prefix, words, children=None):
        if children is None:
            children = self.decomposition_function(avoiding_with_prefix)
        idx = DisjointUnionStrategy.backward_map_index(words)
        assert words[idx] in children[idx].objects_of_size(len(words[idx]))
        yield Word(words[idx].lower())


def test_complement_rule_object_maps():
    comb_class = AvoidingWithPrefix("aaa", ["aaaa"], "abc", False)
    rule = UpperCaseExpansionStrategy()(comb_class)
    for size in range(6):
        assert rule.sanity_check(size)
    parent_words_seen = []
    for idx, child in enumerate(rule.children):
        reverse = rule.to_reverse_rule(idx)
        others = tuple(None for _ in range(len(reverse.children) - 1))
        for size in range(7):
            child_words = set(child.objects_of_size(size))
            for word in child_words:
                assert word.isupper()
                image = reverse.forward_map(word)
                assert image == (Word(word.lower()),) + others
                assert list(reverse.backward_map(image)) == [word]
            for word in comb_class.objects_of_size(size):
                in_child = Word(word.upper()) in child_words
                preimages = list(reverse.backward_map((word,) + others))
                assert preimages == ([Word(word.upper())] if in_child else [])
                parent_words_seen.extend(word for _ in preimages)
    assert sorted(parent_words_seen) == sorted(
        word for size in range(7) for word in comb_class.objects_of_size(size)
    )


def test_reverse_equivalence_object_maps():
    comb_class = AvoidingWithPrefix("aaa", ["aaaa"], "a", False)
    rule = UpperCaseExpansionStrategy()(comb_class)
    assert len(rule.non_empty_children()) == 1
    reverse = rule.to_reverse_rule(0)
    assert reverse.forward_map(Word("AAA")) == (Word("aaa"), None)
    assert list(reverse.backward_map((Word("aaa"), None))) == [Word("AAA")]


def test_quotient_rule_has_no_object_maps():
    comb_class = AvoidingWithPrefix("ab", ["aa"], "ab", False)
    rule = RemoveFrontOfPrefix()(comb_class)
    reverse = rule.to_reverse_rule(1)
    with pytest.raises(NotImplementedError):
        reverse.forward_map(Word("ba"))
    with pytest.raises(NotImplementedError):
        next(reverse.backward_map((Word("abba"), None)))


class TwoWayUpperCaseExpansionStrategy(UpperCaseExpansionStrategy):
    """
    As UpperCaseExpansionStrategy, but every word of a child maps back to two
    words of the parent, as for a rule that is not bijective.
    """

    def backward_map(self, avoiding_with_prefix, words, children=None):
        word = next(super().backward_map(avoiding_with_prefix, words, children))
        yield word
        yield Word(word + "!")


def test_reverse_rule_of_a_map_that_is_not_bijective():
    comb_class = AvoidingWithPrefix("aaa", ["aaaa"], "a", False)
    rule = TwoWayUpperCaseExpansionStrategy()(comb_class)
    reverse = rule.to_reverse_rule(0)
    with pytest.raises(NotImplementedError):
        reverse.forward_map(Word("AAA"))
    assert list(reverse.backward_map((Word("aaa"), None))) == [Word("AAA")]
