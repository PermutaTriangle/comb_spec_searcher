import sympy

from comb_spec_searcher.strategies.rule import EquivalenceRule
from example import AvoidingWithPrefix, ExpansionStrategy, RemoveFrontOfPrefix


def test_reverse_equivalence():
    comb_class = AvoidingWithPrefix("aaa", ["aaaa"], "a", False)
    rule = ExpansionStrategy()(comb_class)
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
