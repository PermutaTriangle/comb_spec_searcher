from grids import *
from permuta import *
from copy import copy


def cell_insertion(parent_tiling, cell):
    tiling = parent_tiling
    d = {}
    for (i, j), perm_set in tiling.items():
        if perm_set is not Tile.P:
            perm_set = None
        if i < cell[0]:
            if j < cell[1]:
                d[(i, j)] = perm_set
            elif j == cell[1]:
                d[(i, j)] = perm_set
                d[(i, j + 2)] = perm_set
            else:
                d[(i, j + 2)] = perm_set
        elif i == cell[0]:
            if j < cell[1]:
                d[(i, j)] = perm_set
                d[(i + 2, j)] = perm_set
            elif j == cell[1]:
                d[(i, j)] = perm_set
                d[(i + 2, j)] = perm_set
                d[(i, j + 2)] = perm_set
                d[(i + 2, j + 2)] = perm_set
                d[(i + 1, j + 1)] = Tile.P
            else:
                d[(i, j + 2)] = perm_set
                d[(i + 2, j + 2)] = perm_set
        else:  # i > cell[0]:
            if j < cell[1]:
                d[(i + 2, j)] = perm_set
            elif j == cell[1]:
                d[(i + 2, j)] = perm_set
                d[(i + 2, j + 2)] = perm_set
            else:
                d[(i + 2, j + 2)] = perm_set
    left_tiling = copy(parent_tiling)
    left_tiling.pop(cell)
    return left_tiling, Tiling(d)


def cell_inferral(tiling, the_cell, input_set):
    point_cells = {}
    for cell, block in tiling.items():
        if block is Tile.P:
            point_cells[cell] = block

    max_length = len(input_set.basis[-1])

    inferred_basis = list(input_set.basis)
    for length in range(1, max_length):
        perm_set = PermSet.avoiding(inferred_basis)
        for patt in perm_set.of_length(length):
            point_cells[the_cell] = PermSet([patt])
            T = Tiling(point_cells)
            TD = TilingPermSetDescriptor(T)
            TPS = TilingPermSet(TD)
            for perm in TPS.of_length(len(point_cells) - 1 + length):
                if perm not in input_set:
                    inferred_basis.append(patt)

    return PermSet.avoiding(inferred_basis)

def tiling_inferral(tiling, input_set):
    inferred_tiling = copy(tiling)
    for cell, block in tiling.items():
        if block is None:
            inferred_block = cell_inferral(tiling, cell, input_set)
            if inferred_block == PermSet.avoiding(Perm((0,))):
                inferred_tiling.pop(cell)
            else:
                inferred_tiling[cell] = inferred_block
    return Tiling(inferred_tiling)
