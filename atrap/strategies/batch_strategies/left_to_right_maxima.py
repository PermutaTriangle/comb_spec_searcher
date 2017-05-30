"""A strategy for placing left to right maxima at the start of search into classes with 123."""


from permuta import Perm
from grids import Tiling, PositiveClass, Block
from .batch_class import BatchStrategy


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
