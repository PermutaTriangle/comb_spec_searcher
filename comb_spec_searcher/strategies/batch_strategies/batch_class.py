from comb_spec_searcher.strategies import Strategy

def BatchStrategy(formal_step, tilings):
    return Strategy(formal_step, tilings, [True for _ in tilings])
