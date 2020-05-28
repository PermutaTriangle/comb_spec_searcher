import pickle

import pytest

from comb_spec_searcher import CombinatorialSpecificationSearcher
from example import AvoidingWithPrefix, pack


def test_pickle_queue_exhausted():
    alphabet = ["a", "b"]
    start_class = AvoidingWithPrefix("", ["ababa", "babb"], alphabet)
    searcher = CombinatorialSpecificationSearcher[AvoidingWithPrefix](start_class, pack)
    searcher.auto_search()
    queue = searcher.classqueue
    new_queue = pickle.loads(pickle.dumps(queue))
    print(queue.status())
    with pytest.raises(StopIteration):
        next(queue)
    with pytest.raises(StopIteration):
        next(new_queue)


def test_pickle_queue_not_exhausted():
    alphabet = ["a", "b"]
    start_class = AvoidingWithPrefix("", ["ababa", "babb"], alphabet)
    searcher = CombinatorialSpecificationSearcher[AvoidingWithPrefix](start_class, pack)
    searcher.do_level()
    searcher.do_level()
    queue = searcher.classqueue
    new_queue = pickle.loads(pickle.dumps(queue))
    assert new_queue == queue
    assert list(queue) == list(new_queue)
