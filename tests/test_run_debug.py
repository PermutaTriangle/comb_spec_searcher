from example import AvoidingWithPrefix, pack

from comb_spec_searcher import CombinatorialSpecificationSearcher


def test_run_with_debug():
    alphabet = ['a', 'b']
    start_class = AvoidingWithPrefix('', ['ababa', 'babb'], alphabet)
    searcher = CombinatorialSpecificationSearcher(start_class, pack,
                                                  debug=True)
    searcher.auto_search()
