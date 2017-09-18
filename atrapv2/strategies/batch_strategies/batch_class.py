from atrapv2.strategies import Strategy

def BatchStrategy(formal_step, tilings):
    return Strategy(formal_step, tilings, [True for _ in tilings])
