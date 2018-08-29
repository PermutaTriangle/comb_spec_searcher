"""A function for decomposition strategies."""
from comb_spec_searcher.strategies import Strategy


def DecompositionStrategy(formal_step, comb_classes, back_maps,
                          ignore_parent=True):
    return Strategy(formal_step, comb_classes, 
                    [False for _ in comb_classes],
                    [False for _ in comb_classes], 
                    [False for _ in comb_classes], 
                    ignore_parent=ignore_parent, constructor='cartesian') 
