"""A function for decomposition strategies."""
from ..strategy import Strategy


def DecompositionStrategy(formal_step, comb_classes,
                          ignore_parent=True):
    return Strategy(formal_step, comb_classes,
                    [False for _ in comb_classes],
                    [False for _ in comb_classes],
                    [False for _ in comb_classes],
                    ignore_parent=ignore_parent, constructor='cartesian')
