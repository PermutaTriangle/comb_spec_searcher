from atrapv2.strategies import Strategy


def RecursiveStrategy(formal_step, tilings, back_maps):
    return Strategy(formal_step, tilings, [False for _ in tilings], back_maps=back_maps)
