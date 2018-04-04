from comb_spec_searcher.strategies import Strategy


def DecompositionStrategy(formal_step, objects, back_maps):
    return Strategy(formal_step, objects, [False for _ in objects], back_maps=back_maps)
