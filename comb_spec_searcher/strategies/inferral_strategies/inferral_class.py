"""A function for inferral strategies."""
from ..strategy import Strategy


def InferralStrategy(formal_step, comb_class):
    """A function for inferral strategies."""
    return Strategy(formal_step, [comb_class], [True], [False],
                    [True], ignore_parent=True, constructor='equiv')
