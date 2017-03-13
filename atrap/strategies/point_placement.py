
from grids import Block
from grids import PositiveClass
from grids import Tiling


def point_placement(tiling):
    for cell, block in tiling.non_points:
        if not isinstance(block, PositiveClass):
            continue
