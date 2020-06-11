import pytest

from comb_spec_searcher import CombinatorialSpecificationSearcher
from comb_spec_searcher.exception import NoMoreClassesToExpandError
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
