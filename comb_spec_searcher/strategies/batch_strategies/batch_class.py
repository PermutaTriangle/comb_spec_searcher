"""A function for batch strategies."""
from ..strategy import Strategy


def BatchStrategy(formal_step, comb_classes):
    return Strategy(formal_step, comb_classes,
                    [True for _ in comb_classes],
                    [True for _ in comb_classes],
                    [True for _ in comb_classes],
                    constructor='disjoint')
