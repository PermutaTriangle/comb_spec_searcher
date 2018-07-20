"""A function for inferral strategies."""
from comb_spec_searcher.strategies import Strategy


def InferralStrategy(formal_step, comb_class):
    """A function for inferral strategies."""
    return Strategy(formal_step, [comb_class], [True], [True],
                    ignore_parent=True, constructor='equiv')
