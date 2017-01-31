from grids import Tiling, Block, PermSetTiled
from permuta import *
from copy import copy


__all__ = ["tiling_inferral"]


def cell_inferral(tiling, the_cell, input_set):
    point_cells = {}
    for cell, block in tiling.items():
        if block is Block.point:
            point_cells[cell] = block

    max_length = len(input_set.basis[-1])

    inferred_basis = list(input_set.basis)
    for length in range(1, max_length):
        perm_set = PermSet.avoiding(inferred_basis)
        for patt in perm_set.of_length(length):
            point_cells[the_cell] = PermSet([patt])
            T = Tiling(point_cells)
            TPS = PermSetTiled(T)
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
