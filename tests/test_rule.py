from itertools import product

import sympy

from comb_spec_searcher import CombinatorialClass
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


class LetterWords(CombinatorialClass[Word]):
    """
    The words over the letters a and b: all of them, or those with or without a
    b, as has_b is None, True or False. Every parameter counts the letter a,
    but one named in only_without_b is 0 on a word with a b.
    """

    def __init__(self, has_b, parameters, only_without_b=()):
        self.has_b = has_b
        self._parameters = tuple(parameters)
        self.only_without_b = tuple(only_without_b)
        super().__init__()

    @property
    def extra_parameters(self):
        return self._parameters

    def get_parameters(self, obj):
        return tuple(
            0 if "b" in obj and parameter in self.only_without_b else obj.count("a")
            for parameter in self._parameters
        )

    def objects_of_size(self, n, **parameters):
        for letters in product("ab", repeat=n):
            word = Word("".join(letters))
            if self.has_b is not None and ("b" in word) != self.has_b:
                continue
            values = dict(zip(self._parameters, self.get_parameters(word)))
            if all(values[name] == value for name, value in parameters.items()):
                yield word

    def get_minimum_value(self, parameter):
        return 0

    def is_atom(self):
        return False

    def minimum_size_of_object(self):
        return 1 if self.has_b else 0

    def is_empty(self):
        return False

    @classmethod
    def from_dict(cls, d):
        raise NotImplementedError

    def _key(self):
        return (self.has_b, self._parameters, self.only_without_b)

    def __eq__(self, other):
        return isinstance(other, LetterWords) and self._key() == other._key()

    def __hash__(self):
        return hash(self._key())

    def __repr__(self):
        return f"LetterWords{self._key()!r}"

    def __str__(self):
        return repr(self)


class SplitOnLetterB(DisjointUnionStrategy[LetterWords, Word]):
    """
    All words, as those without a b and those with one. Both of the parent's
    parameters go to the first child's one parameter, and only the first goes
    to the second child's, as the second is 0 on a word with a b.
    """

    def decomposition_function(self, comb_class):
        return (LetterWords(False, ("u",)), LetterWords(True, ("w",)))

    def extra_parameters(self, comb_class, children=None):
        return ({"p": "u", "q": "u"}, {"p": "w"})

    def formal_step(self):
        return "split on the letter b"

    def forward_map(self, comb_class, obj, children=None):
        return (None, obj) if "b" in obj else (obj, None)

    @classmethod
    def from_dict(cls, d):
        return cls()

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def __str__(self):
        return self.formal_step()


def test_reverse_union_with_two_parent_parameters_on_one_child_parameter():
    parent = LetterWords(None, ("p", "q"), only_without_b=("q",))
    rule = SplitOnLetterB()(parent)
    reverse_rules = [rule.to_reverse_rule(idx) for idx in range(2)]
    for n in range(5):
        assert rule.sanity_check(n)
        for reverse_rule in reverse_rules:
            assert reverse_rule.sanity_check(n)


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
