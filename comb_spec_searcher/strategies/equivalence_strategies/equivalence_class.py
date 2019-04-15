"""A function for equivalent strategies."""
from ..strategy import Strategy


def EquivalenceStrategy(formal_step, comb_class):
    return Strategy(formal_step, [comb_class], [True], [False],
                    [True], constructor='equiv')
