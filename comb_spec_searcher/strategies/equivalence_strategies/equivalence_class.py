from comb_spec_searcher.strategies import Strategy
from collections import Iterable

def EquivalenceStrategy(formal_step, object):
    return Strategy(formal_step, [object], [True])
