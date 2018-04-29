"""A function for batch strategies."""
from comb_spec_searcher.strategies import Strategy


def BatchStrategy(formal_step, objects):
    return Strategy(formal_step, objects, [True for _ in objects],
                    [True for _ in objects])
