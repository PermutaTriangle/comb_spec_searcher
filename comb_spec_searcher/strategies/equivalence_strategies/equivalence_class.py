"""A function for equivalent strategies."""
from comb_spec_searcher.strategies import Strategy


def EquivalenceStrategy(formal_step, object):
    return Strategy(formal_step, [object], [True], [True],
                    constructor='equiv')
