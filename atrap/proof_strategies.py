from grids import *
from permuta import *
from copy import copy


def cell_insertion_helper(parent_tiling, cell):
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


def cell_insertion(tiling, cell, input_set):
    temp_left, temp_right = cell_insertion_helper(tiling, cell)
    left = ("E", temp_left)
    right = dict(tiling_inferral(temp_right, input_set))
    NW_cell = cell
    NE_cell = cell[0], cell[1] + 2
    SW_cell = cell[0] + 2, cell[1]
    SE_cell = cell[0] + 2, cell[1] + 2
    if NW_cell in right:
        if NE_cell in right:
            NE_block = right.pop(NE_cell)
            NW_block = right.pop(NW_cell)
            yield left, ("T", Tiling(right))
            right[NE_cell] = NE_block
            SW_block = right.pop(SW_cell)
            yield left, ("L", Tiling(right))
            right[NW_cell] = NW_block
            SE_block = right.pop(SE_cell)
            yield left, ("B", Tiling(right))
            right[SW_cell] = SW_block
            NE_block = right.pop(NE_cell)
            yield left, ("R", Tiling(right))
        else:
            NW_block = right.pop(NW_cell)
            yield left, ("T", Tiling(right))
            right[NW_cell] = NW_block
            SE_block = right.pop(SE_cell)
            yield left, ("B", Tiling(right))
    else:
        if NE_cell in right:
            NE_block = right.pop(NE_cell)
            yield left, ("T", Tiling(right))
            right[NE_cell] = NE_block
            SW_block = right.pop(SW_cell)
            yield left, ("B", Tiling(right))
        else:
            yield left, ("U", Tiling(right))


def verify_tiling(tiling, input_set):
    longest_basis_length = len(input_set.basis[-1])
    number_of_points = sum(1 for cell in tiling if tiling[cell] is Tile.P)
    tiling_perm_set = TilingPermSet(TilingPermSetDescriptor(tiling))
    for length in range(number_of_points, number_of_points + longest_basis_length + 1):
        #print("TILING SET OF LENGTH", length)
        #print(list(tiling_perm_set.of_length(length)))
        #print("INPUT SET OF LENGTH", length)
        #print(list(input_set.of_length(length)))
        if not set(tiling_perm_set.of_length(length)).issubset(input_set.of_length(length)):
            return False
    return True
