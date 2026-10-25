import itertools
import json
import sys

import pytest

from comb_spec_searcher import (
    CombinatorialSpecification,
    CombinatorialSpecificationSearcher,
)
from comb_spec_searcher.exception import InvalidOperationError
from comb_spec_searcher.rule_db import RuleDBForest, RuleDBForgetStrategy
from comb_spec_searcher.specification import Derivation
from comb_spec_searcher.strategies import AtomStrategy
from comb_spec_searcher.strategies.rule import ReverseRule, VerificationRule
from comb_spec_searcher.strategies.strategy import VerificationStrategy
from comb_spec_searcher.strategies.strategy_pack import StrategyPack
from comb_spec_searcher.utils import taylor_expand
from example import (
    AvoidingWithPrefix,
    ExpansionStrategy,
    RemoveFrontOfPrefix,
    Word,
    pack,
)


@pytest.fixture
def specification():
    alphabet = ["a", "b"]
    start_class = AvoidingWithPrefix("", ["ababa", "babb"], alphabet)
    searcher = CombinatorialSpecificationSearcher(start_class, pack)
    return searcher.auto_search()


@pytest.fixture
def finite_specification():
    alphabet = ["a", "b"]
    start_class = AvoidingWithPrefix("", ["aa", "bb", "ab", "ba"], alphabet)
    searcher = CombinatorialSpecificationSearcher(start_class, pack)
    return searcher.auto_search()


def test_specification_with_genf(specification):
    genf = specification.get_genf()
    assert taylor_expand(genf) == [1, 2, 4, 8, 15, 27, 48, 87, 157, 283, 511]


def test_specification_json(specification):
    new_spec = CombinatorialSpecification.from_dict(
        json.loads(json.dumps(specification.to_jsonable()))
    )
    assert isinstance(new_spec, CombinatorialSpecification)
    assert specification.root == new_spec.root
    assert specification.get_genf() == new_spec.get_genf()
    assert specification.count_objects_of_size(20) == new_spec.count_objects_of_size(20)
    assert list(specification.generate_objects_of_size(8)) == list(
        new_spec.generate_objects_of_size(8)
    )


@pytest.mark.repeat(50)
def test_count_object_of_length_single_value(specification):
    assert specification.count_objects_of_size(n=15) == 9798


@pytest.mark.repeat(50)
def test_count_object_of_length_all_values(specification):
    assert [specification.count_objects_of_size(n=i) for i in range(11)] == [
        1,
        2,
        4,
        8,
        15,
        27,
        48,
        87,
        157,
        283,
        511,
    ]


def test_generate_objects_of_length(specification):
    assert len(list(specification.generate_objects_of_size(0))) == 1
    assert len(list(specification.generate_objects_of_size(1))) == 2
    assert len(list(specification.generate_objects_of_size(2))) == 4
    assert len(list(specification.generate_objects_of_size(3))) == 8
    assert len(list(specification.generate_objects_of_size(4))) == 15
    assert Word("babb") not in specification.generate_objects_of_size(4)
    assert Word("aaaa") in specification.generate_objects_of_size(4)


def test_comb_classes(specification):
    assert len(specification.comb_classes()) >= len(specification.rules_dict)


def test_count_object_of_length_big_value(specification):
    for i in range(1001):
        specification.count_objects_of_size(i)


def test_random_sample(specification):
    """
    Just test that it works and don't hit the maximum recursion depth.
    """
    assert specification.random_sample_object_of_size(0) == ""
    assert len(specification.random_sample_object_of_size(100)) == 100


def test_random_sample_from_finite(finite_specification):
    """
    Testing that the finite spec behaves properly.
    """
    assert finite_specification.random_sample_object_of_size(0) == ""
    assert finite_specification.random_sample_object_of_size(1) in set(
        [Word("a"), Word("b")]
    )
    with pytest.raises(InvalidOperationError):
        finite_specification.random_sample_object_of_size(2)
    with pytest.raises(InvalidOperationError):
        finite_specification.random_sample_object_of_size(100)


def test_forget_ruledb():
    alphabet = ["a", "b"]
    start_class = AvoidingWithPrefix("", ["ababa", "babb"], alphabet)
    ruledb = RuleDBForgetStrategy()
    searcher = CombinatorialSpecificationSearcher(start_class, pack, ruledb=ruledb)
    spec = searcher.auto_search()
    expected_count = [1, 2, 4, 8, 15, 27, 48, 87, 157, 283]
    count = [spec.count_objects_of_size(n) for n in range(10)]
    assert count == expected_count


def test_forest_ruledb():
    alphabet = ["a", "b"]
    start_class = AvoidingWithPrefix("", ["ababa", "babb"], alphabet)
    ruledb = RuleDBForest()
    searcher = CombinatorialSpecificationSearcher(start_class, pack, ruledb=ruledb)
    spec = searcher.auto_search()
    expected_count = [1, 2, 4, 8, 15, 27, 48, 87, 157, 283]
    count = [spec.count_objects_of_size(n) for n in range(10)]
    assert count == expected_count


def test_sancheck(specification):
    assert specification.sanity_check(6)


def test_expand_size1_spec():
    """
    Test that the expansion of spec with only one verification rule works.
    """
    alphabet = ["a", "b"]
    start_class = AvoidingWithPrefix("", ["ababa", "babb"], alphabet)

    class RootVerificationStrategy(VerificationStrategy):
        """
        Verify the specific root for this run so that we get a specification
        with only one rule.
        """

        def verified(self, comb_class):
            return comb_class == start_class

        def formal_step(self):
            return f"Verify {start_class}"

        def from_dict(self, d):
            raise NotImplementedError

        def pack(self, comb_class):
            if comb_class == start_class:
                return pack
            else:
                raise NotImplementedError

    verif_root_pack = StrategyPack(
        [], [], [], [RootVerificationStrategy()], "root_verif"
    )

    searcher = CombinatorialSpecificationSearcher(start_class, verif_root_pack)
    spec = searcher.auto_search()
    assert spec.number_of_rules() == 1
    new_spec = spec.expand_verified()
    assert new_spec.number_of_rules() > 1
    assert new_spec.count_objects_of_size(10) == 511


def test_cant_count_unexpanded():
    """
    Test that the expanded spec is not using the same rule object as the original spec.
    """
    alphabet = ["a", "b"]
    start_class = AvoidingWithPrefix("", ["aa"], alphabet)

    class SomeVerification(VerificationStrategy):
        """
        Verify the specific root for this run so that we get a specification
        with only one rule.
        """

        comb_class = AvoidingWithPrefix("a", ["aa"], alphabet)

        def verified(self, comb_class):
            return comb_class == SomeVerification.comb_class

        def formal_step(self):
            return f"Verify {SomeVerification.comb_class}"

        def from_dict(self, d):
            raise NotImplementedError

        def get_terms(self, comb_class, n):
            raise NotImplementedError

        def pack(self, comb_class):
            if comb_class == SomeVerification.comb_class:
                return pack
            else:
                raise NotImplementedError

    extra_pack = pack.add_verification(SomeVerification())

    searcher = CombinatorialSpecificationSearcher(start_class, extra_pack)
    spec = searcher.auto_search()
    with pytest.raises(NotImplementedError):
        spec.count_objects_of_size(10)
    new_spec = spec.expand_verified()
    with pytest.raises(NotImplementedError):
        spec.count_objects_of_size(10)
    assert new_spec.count_objects_of_size(10) == 144
    for rule1, rule2 in itertools.product(spec, new_spec):
        assert not (rule1 is rule2)


def nodes(derivation):
    """Yield each node of a derivation once, a node shared by branches too."""
    seen = set()
    stack = [derivation]
    while stack:
        node = stack.pop()
        if id(node) in seen:
            continue
        seen.add(id(node))
        yield node
        stack.extend(child for child in node.children if child is not None)


def check_derivation(spec, derivation, choose_images=None):
    """
    Check every node of the derivation against the specification: its rule is
    the class's, its children are the images of the forward map, or those of
    choose_images where there is none, each an object of its class, a
    verification's children are None, and the backward map, where there is
    one, gives the object back.
    """
    for node in nodes(derivation):
        assert node.rule is spec.get_rule(node.comb_class)
        assert len(node.children) == len(node.rule.children)
        if isinstance(node.rule, VerificationRule):
            assert node.children == tuple(None for _ in node.rule.children)
            continue
        try:
            images = node.rule.forward_map(node.obj)
        except NotImplementedError:
            images = choose_images(node.rule, node.obj)
        for child_class, image, child in zip(node.rule.children, images, node.children):
            if image is None:
                assert child is None
            else:
                assert child.comb_class == child_class
                assert child.obj == image
                assert image in child_class.objects_of_size(len(image))
        objs = tuple(None if child is None else child.obj for child in node.children)
        try:
            assert list(node.rule.backward_map(objs)) == [node.obj]
        except NotImplementedError:
            pass


def test_derivation(specification):
    word_count = 0
    for size in range(9):
        for word in specification.root.objects_of_size(size):
            derivation = specification.derivation(word)
            assert isinstance(derivation, Derivation)
            assert derivation.comb_class == specification.root
            assert derivation.obj == word
            check_derivation(specification, derivation)
            word_count += 1
    assert word_count == sum(specification.count_objects_of_size(n) for n in range(9))


def test_derivation_in_a_class_other_than_the_root(specification):
    child = specification.root_rule.children[1]
    for word in child.objects_of_size(5):
        derivation = specification.derivation(word, child)
        assert derivation.comb_class == child
        assert derivation.obj == word
        check_derivation(specification, derivation)


def test_derivation_from_a_verified_class(specification):
    atom, atom_rule = next(
        (comb_class, rule)
        for comb_class, rule in specification.rules_dict.items()
        if isinstance(rule.strategy, AtomStrategy)
    )
    word = next(atom.objects_of_size(atom.minimum_size_of_object()))
    assert specification.derivation(word, atom) == Derivation(atom, atom_rule, word, ())


def test_derivation_from_a_class_with_no_rule(specification):
    not_in_the_specification = AvoidingWithPrefix("bbbbbbbb", ["ababa", "babb"], "ab")
    with pytest.raises(InvalidOperationError, match="has no rule for the class"):
        specification.derivation(Word("bbbbbbbb"), not_in_the_specification)


@pytest.fixture
def reverse_rule_specification():
    """
    The words over a and b that avoid aa and start with bb, counted by the
    reverse of the expansion of those that start with b: they are those that
    start with b, less the word b and those that start with ba.
    """
    patterns, alphabet = ["aa"], ["a", "b"]
    start_with_b = AvoidingWithPrefix("b", patterns, alphabet)
    expansion = ExpansionStrategy()(start_with_b)
    _, start_with_ba, start_with_bb = expansion.children
    rules = [expansion.to_reverse_rule(2)]
    for comb_class in (start_with_b, start_with_ba):
        rules.extend(CombinatorialSpecificationSearcher(comb_class, pack).auto_search())
    return CombinatorialSpecification(start_with_bb, rules)


def test_derivation_through_a_reverse_rule(reverse_rule_specification):
    spec = reverse_rule_specification
    reverse = spec.get_rule(spec.root)
    assert isinstance(reverse, ReverseRule)
    start_with_b = reverse.children[0]
    for size in range(9):
        words = list(spec.root.objects_of_size(size))
        assert spec.count_objects_of_size(size) == len(words)
        for word in words:
            derivation = spec.derivation(word)
            assert derivation.rule is reverse
            assert derivation.children[0].comb_class == start_with_b
            assert derivation.children[0].obj == word
            assert derivation.children[1:] == (None, None)
            check_derivation(spec, derivation)


def test_derivation_chooses_images_where_a_rule_cannot_map(
    reverse_rule_specification, monkeypatch
):
    spec = reverse_rule_specification
    reverse = spec.get_rule(spec.root)
    word = Word("bbab")
    expected = spec.derivation(word)

    def cannot_map(obj):
        raise NotImplementedError

    monkeypatch.setattr(reverse, "forward_map", cannot_map)
    with pytest.raises(NotImplementedError):
        spec.derivation(word)
    chosen = []

    def choose_images(rule, obj):
        chosen.append((rule, obj))
        return (obj, None, None)

    assert spec.derivation(word, choose_images=choose_images) == expected
    assert chosen == [(reverse, word)]


@pytest.fixture
def division_specification():
    """
    The words over b, counted by division: those that start with b, divided by
    the word b. Those that start with b are the word b and those that start
    with bb, which are the word bb times all the words.
    """
    all_words = AvoidingWithPrefix("", [], ["b"])
    start_with_b = AvoidingWithPrefix("b", [], ["b"])
    remove_b = RemoveFrontOfPrefix()(start_with_b)
    just_b, rest = remove_b.children
    assert rest == all_words
    expansion = ExpansionStrategy()(start_with_b)
    remove_bb = RemoveFrontOfPrefix()(expansion.children[1])
    rules = [
        remove_b.to_reverse_rule(1),
        expansion,
        remove_bb,
        AtomStrategy()(just_b),
        AtomStrategy()(remove_bb.children[0]),
    ]
    return CombinatorialSpecification(all_words, rules)


def prepend_b(rule, word):
    """The images of a word under the division: b in front of it, and b."""
    return (Word("b" + word), Word("b"))


def test_derivation_that_reaches_the_same_object_by_two_branches(
    division_specification,
):
    spec = division_specification
    divide, expand = spec.root_rule, spec.get_rule(spec.root_rule.children[0])
    just_b = divide.children[1]
    remove_bb = spec.get_rule(expand.children[1])
    just_bb = remove_bb.children[0]

    def expected(comb_class, size):
        """The derivation of the word of b's of the size, from the equations."""
        word = Word("b" * size)
        rule = spec.get_rule(comb_class)
        if comb_class == spec.root:
            children = (expected(divide.children[0], size + 1), expected(just_b, 1))
        elif rule is expand:
            children = (
                (expected(just_b, 1), None)
                if size == 1
                else (None, expected(expand.children[1], size))
            )
        elif rule is remove_bb:
            children = (expected(just_bb, 2), expected(spec.root, size - 2))
        else:
            children = ()
        return Derivation(comb_class, rule, word, children)

    for size in range(6):
        word = Word("b" * size)
        derivation = spec.derivation(word, choose_images=prepend_b)
        assert derivation == expected(spec.root, size)
        check_derivation(spec, derivation, prepend_b)
        by_key = {}
        for node in nodes(derivation):
            assert (node.comb_class, node.obj) not in by_key
            by_key[(node.comb_class, node.obj)] = node
    derivation = spec.derivation(Word(""), choose_images=prepend_b)
    assert derivation.children[0].children[0] is derivation.children[1]


def test_derivation_with_too_few_images(division_specification):
    def only_one(rule, word):
        return prepend_b(rule, word)[:1]

    with pytest.raises(InvalidOperationError, match="1 images for the 2 children"):
        division_specification.derivation(Word("bb"), choose_images=only_one)


def test_derivation_with_images_past_the_children(division_specification):
    spec = division_specification
    expected = spec.derivation(Word("bb"), choose_images=prepend_b)

    def with_none_past(rule, word):
        return prepend_b(rule, word) + (None,)

    def with_a_word_past(rule, word):
        return prepend_b(rule, word) + (Word("b"),)

    def generated(rule, word):
        yield from prepend_b(rule, word)

    assert spec.derivation(Word("bb"), choose_images=with_none_past) == expected
    assert spec.derivation(Word("bb"), choose_images=generated) == expected
    with pytest.raises(InvalidOperationError, match="3 images for the 2 children"):
        spec.derivation(Word("bb"), choose_images=with_a_word_past)


def test_derivation_in_a_circular_specification():
    patterns, alphabet = ["aa"], ["a", "b"]
    all_words = AvoidingWithPrefix("", patterns, alphabet)
    expansion = ExpansionStrategy()(all_words)
    empty_word, _, start_with_b = expansion.children
    remove_b = RemoveFrontOfPrefix()(start_with_b)
    # the words that start with a, counted as all words less the empty word
    # and those that start with b, which the expansion of all words needs
    rules = [
        expansion,
        expansion.to_reverse_rule(1),
        remove_b,
        AtomStrategy()(empty_word),
        AtomStrategy()(remove_b.children[0]),
    ]
    spec = CombinatorialSpecification(all_words, rules)
    check_derivation(spec, spec.derivation(Word("bb")))
    cache = {}
    with pytest.raises(
        InvalidOperationError, match="The derivation comes back to the object ab"
    ):
        spec.derivation(Word("ab"), cache=cache)
    for derivation in cache.values():  # only those it finished
        for node in nodes(derivation):
            assert cache[(node.comb_class, node.obj)] is node


def test_derivation_cache(specification):
    word = Word("abba")
    cache = {}
    derivation = specification.derivation(word, cache=cache)
    assert specification.derivation(word, cache=cache) is derivation
    for node in nodes(derivation):
        assert cache[(node.comb_class, node.obj)] is node
    assert specification.derivation(word) == derivation
    cache = {(specification.root, word): "known"}
    assert specification.derivation(word, cache=cache) == "known"


def test_a_derivation_deeper_than_the_recursion_limit():
    spec = CombinatorialSpecificationSearcher(
        AvoidingWithPrefix("", [], ["b"]), pack
    ).auto_search()
    derivation = spec.derivation(Word("b" * sys.getrecursionlimit()))
    depth = 0
    node = derivation
    while node.children:
        node = max(
            (child for child in node.children if child is not None),
            key=lambda child: len(child.obj),
        )
        depth += 1
    assert depth > sys.getrecursionlimit()


class AtomStrategyNamingAClass(AtomStrategy):
    """
    Verifies atoms, as AtomStrategy does, and names a class among the rule's
    children, as a verification relying on another class's specification does
    (Tilings' locally factorable verification names its root).
    """

    def __init__(self, named_class):
        super().__init__()
        self.named_class = named_class

    def decomposition_function(self, comb_class):
        if self.verified(comb_class):
            return (self.named_class,)
        return None


def test_derivation_ends_at_a_verification_that_names_a_class(specification):
    naming_strategy = AtomStrategyNamingAClass(specification.root)
    rules = [
        (
            naming_strategy(rule.comb_class)
            if isinstance(rule.strategy, AtomStrategy)
            else rule
        )
        for rule in specification
    ]
    spec = CombinatorialSpecification(specification.root, rules)
    verifications = 0
    for size in range(7):
        for word in spec.root.objects_of_size(size):
            derivation = spec.derivation(word)
            check_derivation(spec, derivation)
            for node in nodes(derivation):
                if isinstance(node.rule, VerificationRule):
                    assert node.rule.children == (specification.root,)
                    assert node.children == (None,)
                    verifications += 1
    assert verifications > 0
