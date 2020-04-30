import pytest

from comb_spec_searcher import CombinatorialSpecificationSearcher
from comb_spec_searcher.utils import taylor_expand
from example import AvoidingWithPrefix, pack


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
