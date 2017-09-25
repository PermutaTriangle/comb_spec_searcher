from tilescopetwo.strategies import Strategy
from grids_two import Tiling

def EquivalenceStrategy(formal_step, tiling):
    if not isinstance(tiling, Tiling):
        raise TypeError("An equivalence strategy should return a single tiling")
    return Strategy(formal_step, [tiling], [True])
