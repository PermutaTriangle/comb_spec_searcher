from example import AvoidingWithPrefix, ExpansionStrategy


def test_reverse_equivalence():
    comb_class = AvoidingWithPrefix("aaa", ["aaaa"], "a", False)
    rule = ExpansionStrategy()(comb_class)
    assert len(rule.non_empty_children()) == 1
    equiv_then_reverse = rule.to_equivalence_rule().to_reverse_rule(0)
    assert equiv_then_reverse.is_equivalence()
    assert equiv_then_reverse.children == (comb_class,)
    assert equiv_then_reverse.comb_class == rule.non_empty_children()[0]
    reverse_then_equiv = rule.to_reverse_rule(0).to_equivalence_rule()
    assert reverse_then_equiv.is_equivalence()
    assert reverse_then_equiv.children == (comb_class,)
    assert reverse_then_equiv.comb_class == rule.non_empty_children()[0]
