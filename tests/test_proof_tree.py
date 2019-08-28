import pytest
from example import AvoidingWithPrefix, pack

from comb_spec_searcher import CombinatorialSpecificationSearcher


@pytest.fixture
def tree():
    alphabet = ['a', 'b']
    start_class = AvoidingWithPrefix('', ['ababa', 'babb'], alphabet)
    searcher = CombinatorialSpecificationSearcher(start_class, pack)
    tree = searcher.auto_search()
    return tree


@pytest.mark.repeat(100)
def test_count_object_of_length_single_value(tree):
    assert tree.count_objects_of_length(15) == 9798


@pytest.mark.repeat(100)
def test_count_object_of_length_all_values(tree):
    assert ([tree.count_objects_of_length(i) for i in range(11)] ==
            [1, 2, 4, 8, 15, 27, 48, 87, 157, 283, 511])
