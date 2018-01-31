"""The point insertion strategy places either a point obstruction or the
point requirement into a cell"""

from grids_two import Tiling
from comb_spec_searcher import BatchStrategy

from permuta import Perm

def all_point_insertions(tiling, **kwargs):
    for cell in tiling._possibly_empty:
        yield BatchStrategy(formal_step="Insert point requirement into cell {}.".format(cell),
                            tilings=[tiling.add_single_cell_obstruction(cell, Perm((0,))),
                                     tiling.add_single_cell_requirement(cell, Perm((0,)))])
