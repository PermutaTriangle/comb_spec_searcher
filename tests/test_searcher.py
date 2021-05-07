import pytest

from comb_spec_searcher import CombinatorialSpecificationSearcher
from comb_spec_searcher.exception import (
    NoMoreClassesToExpandError,
    SpecificationNotFound,
)
from example import AvoidingWithPrefix, pack


@pytest.mark.timeout(5)
def test_do_level():
    alphabet = ["a", "b"]
    start_class = AvoidingWithPrefix("", ["aabb", "bbbbab"], alphabet)
    searcher = CombinatorialSpecificationSearcher(start_class, pack)
    with pytest.raises(NoMoreClassesToExpandError):
        while True:
            searcher.do_level()
    assert all(searcher.classqueue.queue_sizes)


def test_no_spec_exception():
    alphabet = ["a", "b"]
    start_class = AvoidingWithPrefix("", ["aabb", "bbbbab"], alphabet)
    searcher = CombinatorialSpecificationSearcher(start_class, pack)
    for _ in range(2):
        searcher.do_level()
    assert not searcher.ruledb.has_specification()
    with pytest.raises(SpecificationNotFound):
        searcher.get_specification()
    with pytest.raises(SpecificationNotFound):
        searcher.ruledb.get_specification_rules()


def test_iterative():
    alphabet = ["a", "b"]
    start_class = AvoidingWithPrefix("", ["a"], alphabet)
    it_pack = pack.make_iterative("iterative")
    searcher = CombinatorialSpecificationSearcher(start_class, it_pack)
    searcher.auto_search()
