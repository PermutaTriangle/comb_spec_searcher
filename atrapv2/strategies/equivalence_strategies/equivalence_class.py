from atrapv2.strategies import Strategy
from grids import Tiling

def EquivalenceStrategy(formal_step, tiling):
    if not isinstance(tiling, Tiling):
        raise TypeError("An equivalence strategy should return a single tiling")
    return Strategy(formal_step, [tiling], [True])
