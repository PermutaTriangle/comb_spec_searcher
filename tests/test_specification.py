import json
import itertools

import pytest

from comb_spec_searcher import (
    CombinatorialSpecification,
    CombinatorialSpecificationSearcher,
)
from comb_spec_searcher.rule_db import RuleDBForest, RuleDBForgetStrategy
from comb_spec_searcher.strategies.strategy import VerificationStrategy
from comb_spec_searcher.strategies.strategy_pack import StrategyPack
from comb_spec_searcher.utils import taylor_expand
from example import AvoidingWithPrefix, Word, pack


@pytest.fixture
def specification():
    alphabet = ["a", "b"]
    start_class = AvoidingWithPrefix("", ["ababa", "babb"], alphabet)
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
