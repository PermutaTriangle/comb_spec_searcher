from atrapv2.strategies import Strategy

def EquivalenceStrategy(formal_step, tiling):
    return Strategy(formal_step, [tiling], [True])
