from comb_spec_searcher.strategies import Strategy


def DecompositionStrategy(formal_step, tilings, back_maps):
    return Strategy(formal_step, tilings, [True for _ in tilings], back_maps=back_maps)
