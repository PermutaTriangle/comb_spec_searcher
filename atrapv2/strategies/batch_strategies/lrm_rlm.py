"""A strategy for placing left to right maxima at the start of search into classes with 123."""


from permuta import Perm
from grids import Tiling, PositiveClass, Block
from comb_spec_searcher import BatchStrategy


def left_to_right_maxima123(tiling, basis, **kwargs):
    """DocString."""
    if tiling.dimensions.i != 1 or tiling.dimensions.j != 1:
        return

    if Perm((0, 1, 2)) not in basis:
        return

    block = tiling[(0, 0)]
    if isinstance(block, PositiveClass):
        one_left_to_right_maxima = Tiling({(0, 1): Block.point,
                                           (1, 0): block.perm_class})
        two_left_to_right_maxima = Tiling({(0, 1): Block.point,
                                           (1, 0): block.perm_class,
                                           (2, 3): Block.point,
                                           (3, 0): block.perm_class,
                                           (3, 2): block.perm_class})

        tilings = [one_left_to_right_maxima, two_left_to_right_maxima]
        yield BatchStrategy("Placing the left-to-right maxima", tilings)


def left_to_right_maxima1234(tiling, basis, **kwargs):
    """DocString."""
    if tiling.dimensions.i != 1 or tiling.dimensions.j != 1:
        return

    if Perm((0, 1, 2, 3)) not in basis:
        return

    block = tiling[(0, 0)]
    if isinstance(block, PositiveClass):
        one_left_to_right_maxima = Tiling({(0, 1): Block.point,
                                           (1, 0): block.perm_class})
        two_left_to_right_maxima = Tiling({(0, 1): Block.point,
                                           (1, 0): block.perm_class,
                                           (2, 3): Block.point,
                                           (3, 0): block.perm_class,
                                           (3, 2): block.perm_class})
        three_left_to_right_maxima = Tiling({(0, 1): Block.point,
                                             (1, 0): block.perm_class,
                                             (2, 3): Block.point,
                                             (3, 0): block.perm_class,
                                             (3, 2): block.perm_class,
                                             (4, 5): Block.point,
                                             (5, 0): block.perm_class,
                                             (5, 2): block.perm_class,
                                             (5, 4): block.perm_class})

        tilings = [one_left_to_right_maxima, two_left_to_right_maxima, three_left_to_right_maxima]
        yield BatchStrategy("Placing the left-to-right maxima", tilings)


def right_to_left_minima123(tiling, basis, **kwargs):
    """DocString."""
    if tiling.dimensions.i != 1 or tiling.dimensions.j != 1:
        return

    if Perm((0, 1, 2)) not in basis:
        return

    block = tiling[(0, 0)]
    if isinstance(block, PositiveClass):
        one_right_to_left_minima = Tiling({(1, 0): Block.point,
                                           (0, 1): block.perm_class})
        two_right_to_left_minima = Tiling({(1, 0): Block.point,
                                           (3, 2): Block.point,
                                           (0, 1): block.perm_class,
                                           (0, 3): block.perm_class,
                                           (2, 3): block.perm_class})

        tilings = [one_right_to_left_minima, two_right_to_left_minima]
        yield BatchStrategy("Placing the right-to-left minima", tilings)


def right_to_left_minima1234(tiling, basis, **kwargs):
    """DocString."""
    if tiling.dimensions.i != 1 or tiling.dimensions.j != 1:
        return

    if Perm((0, 1, 2, 3)) not in basis:
        return

    block = tiling[(0, 0)]
    if isinstance(block, PositiveClass):
        one_right_to_left_minima = Tiling({(1, 0): Block.point,
                                           (0, 1): block.perm_class})
        two_right_to_left_minima = Tiling({(1, 0): Block.point,
                                           (3, 2): Block.point,
                                           (0, 1): block.perm_class,
                                           (0, 3): block.perm_class,
                                           (2, 3): block.perm_class})
        three_right_to_left_minima = Tiling({(1, 0): Block.point,
                                             (3, 2): Block.point,
                                             (5, 4): Block.point,
                                             (0, 1): block.perm_class,
                                             (0, 3): block.perm_class,
                                             (0, 5): block.perm_class,
                                             (2, 3): block.perm_class,
                                             (2, 5): block.perm_class,
                                             (4, 5): block.perm_class})

        tilings = [one_right_to_left_minima, two_right_to_left_minima, three_right_to_left_minima]
        yield BatchStrategy("Placing the right-to-left minima", tilings)


def left_to_right_minima321(tiling, basis, **kwargs):
    """DocString."""
    if tiling.dimensions.i != 1 or tiling.dimensions.j != 1:
        return

    if Perm((2, 1, 0)) not in basis:
        return

    block = tiling[(0, 0)]
    if isinstance(block, PositiveClass):
        one_left_to_right_minima = Tiling({(0, 0): Block.point,
                                           (1, 1): block.perm_class})
        two_left_to_right_minima = Tiling({(0, 2): Block.point,
                                           (2, 0): Block.point,
                                           (1, 3): block.perm_class,
                                           (3, 1): block.perm_class,
                                           (3, 3): block.perm_class})

        tilings = [one_left_to_right_minima, two_left_to_right_minima]
        yield BatchStrategy("Placing the left-to-right maxima", tilings)


def left_to_right_minima4321(tiling, basis, **kwargs):
    """DocString."""
    if tiling.dimensions.i != 1 or tiling.dimensions.j != 1:
        return

    if Perm((3, 2, 1, 0)) not in basis:
        return

    block = tiling[(0, 0)]
    if isinstance(block, PositiveClass):
        one_left_to_right_minima = Tiling({(0, 0): Block.point,
                                           (1, 1): block.perm_class})
        two_left_to_right_minima = Tiling({(0, 2): Block.point,
                                           (2, 0): Block.point,
                                           (1, 3): block.perm_class,
                                           (3, 1): block.perm_class,
                                           (3, 3): block.perm_class})
        three_left_to_right_minima = Tiling({(0, 4): Block.point,
                                             (2, 2): Block.point,
                                             (4, 0): Block.point,
                                             (1, 5): block.perm_class,
                                             (3, 3): block.perm_class,
                                             (3, 5): block.perm_class,
                                             (5, 1): block.perm_class,
                                             (5, 3): block.perm_class,
                                             (5, 5): block.perm_class})

        tilings = [one_left_to_right_minima, two_left_to_right_minima, three_left_to_right_minima]
        yield BatchStrategy("Placing the left-to-right minima", tilings)


def right_to_left_maxima321(tiling, basis, **kwargs):
    """DocString."""
    if tiling.dimensions.i != 1 or tiling.dimensions.j != 1:
        return

    if Perm((2, 1, 0)) not in basis:
        return

    block = tiling[(0, 0)]
    if isinstance(block, PositiveClass):
        one_right_to_left_maxima = Tiling({(1, 1): Block.point,
                                           (0, 0): block.perm_class})
        two_right_to_left_maxima = Tiling({(1, 3): Block.point,
                                           (3, 1): Block.point,
                                           (0, 0): block.perm_class,
                                           (0, 2): block.perm_class,
                                           (2, 0): block.perm_class})

        tilings = [one_right_to_left_maxima, two_right_to_left_maxima]
        yield BatchStrategy("Placing the right-to-left maxima", tilings)


def right_to_left_maxima4321(tiling, basis, **kwargs):
    """DocString."""
    if tiling.dimensions.i != 1 or tiling.dimensions.j != 1:
        return

    if Perm((3, 2, 1, 0)) not in basis:
        return

    block = tiling[(0, 0)]
    if isinstance(block, PositiveClass):
        one_right_to_left_maxima = Tiling({(1, 1): Block.point,
                                           (0, 0): block.perm_class})
        two_right_to_left_maxima = Tiling({(1, 3): Block.point,
                                           (3, 1): Block.point,
                                           (0, 0): block.perm_class,
                                           (0, 2): block.perm_class,
                                           (2, 0): block.perm_class})
        three_right_to_left_maxima = Tiling({(1, 5): Block.point,
                                             (3, 3): Block.point,
                                             (5, 1): Block.point,
                                             (0, 0): block.perm_class,
                                             (0, 2): block.perm_class,
                                             (0, 4): block.perm_class,
                                             (2, 0): block.perm_class,
                                             (2, 2): block.perm_class,
                                             (4, 0): block.perm_class})

        tilings = [one_right_to_left_maxima, two_right_to_left_maxima, three_right_to_left_maxima]
        yield BatchStrategy("Placing the right-to-left maxima", tilings)


def all_lrm_and_rlm_placements(tiling, basis, **kwargs):
    """Yield all BatchStrategies from placing lrm and rlm boundaries."""
    if tiling.dimensions.i != 1 or tiling.dimensions.j != 1:
        return

    block = tiling[(0, 0)]
    if isinstance(block, PositiveClass):
        if Perm((0, 1, 2)) in basis:
            for strategy in left_to_right_maxima123(tiling, basis):
                yield strategy
            for strategy in right_to_left_minima123(tiling, basis):
                yield strategy

        if Perm((0, 1, 2, 3)) in basis:
            for strategy in left_to_right_maxima1234(tiling, basis):
                yield strategy
            for strategy in right_to_left_minima1234(tiling, basis):
                yield strategy

        if Perm((2, 1, 0)) in basis:
            for strategy in right_to_left_maxima321(tiling, basis):
                yield strategy
            for strategy in left_to_right_minima321(tiling, basis):
                yield strategy

        if Perm((3, 2, 1, 0)) in basis:
            for strategy in left_to_right_minima4321(tiling, basis):
                yield strategy
            for strategy in right_to_left_maxima4321(tiling, basis):
                yield strategy
