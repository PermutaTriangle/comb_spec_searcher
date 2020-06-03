import json

import pytest

from comb_spec_searcher import (
    CombinatorialSpecification,
    CombinatorialSpecificationSearcher,
)
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


def test_count_object_of_length_big_value(specification):
    specification.count_objects_of_size(1000)


def test_random_sample(specification):
    """
    Just test that it works and don't hit the maximum recursion depth.
    """
    assert len(specification.random_sample_object_of_size(1000)) == 1000


def test_forget_ruledb():
    alphabet = ["a", "b"]
    start_class = AvoidingWithPrefix("", ["ababa", "babb"], alphabet)
    searcher = CombinatorialSpecificationSearcher(start_class, pack, ruledb="forget")
    return searcher.auto_search()


def test_sancheck(specification):
    assert specification.sanity_check(6)
