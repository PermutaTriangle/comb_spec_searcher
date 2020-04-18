import pytest
import sympy

from comb_spec_searcher import CombinatorialSpecificationSearcher
from comb_spec_searcher.utils import taylor_expand
from example import AvoidingWithPrefix, pack


@pytest.fixture
def tree():
    alphabet = ["a", "b"]
    start_class = AvoidingWithPrefix("", ["ababa", "babb"], alphabet)
    searcher = CombinatorialSpecificationSearcher(start_class, pack)
    tree = searcher.auto_search()
    return tree


def test_tree_with_genf():
    alphabet = ["a", "b"]
    start_class = AvoidingWithPrefix("", ["ababa", "babb"], alphabet)
    searcher = CombinatorialSpecificationSearcher(start_class, pack)
    tree = searcher.auto_search()
    min_poly = tree.get_min_poly()
    genf = tree.get_genf()
    assert taylor_expand(genf) == [1, 2, 4, 8, 15, 27, 48, 87, 157, 283, 511]
    F = sympy.Symbol("F")
    assert min_poly.subs(F, genf).simplify() == 0


@pytest.mark.repeat(50)
def test_count_object_of_length_single_value(tree):
    assert tree.count_objects_of_length(15) == 9798


@pytest.mark.repeat(50)
def test_count_object_of_length_all_values(tree):
    assert [tree.count_objects_of_length(i) for i in range(11)] == [
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
