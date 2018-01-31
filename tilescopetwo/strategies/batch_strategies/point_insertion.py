"""The point insertion strategy places either a point obstruction or the
point requirement into a cell"""

from grids_two import Tiling
from comb_spec_searcher import BatchStrategy

def all_point_insertions(tiling, **kwargs):
    for cell in tiling._possibly_empty:
        yield BatchStrategy(formal_step="Insert point requirement into cell {}.".format(cell),
                            tilings=[tiling.add_point_obstruction(cell),
                                     tiling.add_point_requirement(cell)])
