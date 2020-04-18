from comb_spec_searcher import CombinatorialSpecificationSearcher
from example import AvoidingWithPrefix, pack


def test_run_with_debug():
    alphabet = ["a", "b"]
    start_class = AvoidingWithPrefix("", ["ababa", "babb"], alphabet)
    searcher = CombinatorialSpecificationSearcher(start_class, pack, debug=True)
    searcher.auto_search()
