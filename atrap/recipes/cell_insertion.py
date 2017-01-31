from grids import Tiling, Block
from copy import copy
from .tools import tiling_inferral


__all__ = ["all_cell_insertions"]


def cell_insertion_helper(parent_tiling, cell):
    tiling = parent_tiling
    d = {}
    for (i, j), perm_set in tiling.items():
        if perm_set is not Block.point:
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
                d[(i + 1, j + 1)] = Block.point
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


def cell_insertion(tiling, cell, input_set):
    left, temp_right = cell_insertion_helper(tiling, cell)
    right = dict(tiling_inferral(temp_right, input_set))
    NW_cell = cell
    NE_cell = cell[0], cell[1] + 2
    SW_cell = cell[0] + 2, cell[1]
    SE_cell = cell[0] + 2, cell[1] + 2
    if NW_cell in right:
        if NE_cell in right:
            NE_block = right.pop(NE_cell)
            NW_block = right.pop(NW_cell)
            yield "Inserting the top most point in to the cell " + str(cell), (left, Tiling(right))
            right[NE_cell] = NE_block
            SW_block = right.pop(SW_cell)
            yield "Inserting the left most point in to the cell " + str(cell), (left, Tiling(right))
            right[NW_cell] = NW_block
            SE_block = right.pop(SE_cell)
            yield "Inserting the bottom most point in to the cell " + str(cell), (left, Tiling(right))
            right[SW_cell] = SW_block
            NE_block = right.pop(NE_cell)
            yield "Inserting the right most point in to the cell " + str(cell),  (left, Tiling(right))
        else:
            NW_block = right.pop(NW_cell)
            yield "Inserting the top most point in to the cell " + str(cell), (left, Tiling(right))
            right[NW_cell] = NW_block
            SE_block = right.pop(SE_cell)
            yield "Inserting the bottom most point in to the cell " + str(cell), (left, Tiling(right))
    else:
        if NE_cell in right:
            NE_block = right.pop(NE_cell)
            yield "Inserting the top most point in to the cell " + str(cell), (left, Tiling(right))
            right[NE_cell] = NE_block
            SW_block = right.pop(SW_cell)
            yield "Inserting the top most point in to the cell " + str(cell), (left, Tiling(right))
        else:
            yield "Inserting the unique point in to the cell " + str(cell), (left, Tiling(right))


def all_cell_insertions(tiling, input_set):
    for cell, block in tiling.items():
        if block is not Block.point:
            for strategy in cell_insertion(tiling, cell, input_set):
                yield strategy
