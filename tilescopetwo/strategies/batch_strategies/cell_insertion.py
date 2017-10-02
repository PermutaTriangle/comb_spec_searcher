"""The cell insertion strategy checks whether a cell is empty or contains a
point"""

from grids_two import Tiling
from comb_spec_searcher import BatchStrategy

def all_cell_insertions(tiling, **kwargs):
    for cell in tiling._possibly_empty:
        yield BatchStrategy(formal_step="Insert into cell {}.".format(cell),
                            tilings=[tiling.delete_cell(cell),
                                     tiling.insert_cell(cell)])
