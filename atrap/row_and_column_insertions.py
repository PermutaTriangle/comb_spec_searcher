from grids import *
from permuta import *
from atrap.proof_strategies import tiling_inferral
from copy import copy

def row_insertion_helper(parent_tiling, row):
    tiling = parent_tiling
    empty_d = {}
    row_cells = []
    # TODO Add check that no points in row trying to insert into. All sets must contain empty.
    # TODO Check that if adding point to each box, then this kills rest of row every time.
    for (i, j), perm_set in tiling.items():
        if i == row:
            row_cells.append( (i,j) )
        elif  i < row:
            empty_d[(i,j)] = perm_set
        else: # i > row
            empty_d[(i+1,j)] = perm_set
    return Tiling(empty_d), row_cells

def row_insertion(parent_tiling, row, input_set):
    empty_row, row_cells = row_insertion_helper(parent_tiling, row)
    bottom_strategy = [empty_row]
    top_strategy = [empty_row]
    for (n,m) in row_cells:

        bottom_d = {}
        bottom_d[(n,m+1)] = Tile.P
        top_d = {}
        top_d[(n+1,m+1)] = Tile.P

        for (i,j), perm_set in empty_row.items():
            if perm_set is not Tile.P:
                perm_set = None
            if j < m:
                bottom_d[(i,j)] = perm_set
                top_d[(i,j)] = perm_set
            else:
                bottom_d[(i,j+2)] = perm_set
                top_d[(i,j+2)] = perm_set

        for (i,j) in row_cells:
            if (i,j) == (n,m):
                bottom_d[(i+1, j)] = None
                bottom_d[(i+1, j+2)] = None
                top_d[(i, j)] = None
                top_d[(i, j+2)] = None
            elif j < m:
                bottom_d[(i+1,j)] = None
                top_d[(i,j)] = None
            else:
                bottom_d[(i+1,j+2)] = None
                top_d[(i,j+2)] = None

        inferred_bottom = tiling_inferral(Tiling(bottom_d), input_set)
        inferred_top = tiling_inferral(Tiling(top_d), input_set)

        bottom_strategy.append(inferred_bottom)
        top_strategy.append(inferred_top)

    yield 'T', tuple( bottom_strategy )
    yield 'B', tuple( top_strategy )
