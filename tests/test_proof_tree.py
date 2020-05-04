import pytest

from comb_spec_searcher import CombinatorialSpecificationSearcher
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
