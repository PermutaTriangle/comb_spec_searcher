from grids import Block, PermSetTiled
from permuta import *


def verify_tiling(tiling, input_set):
    longest_basis_length = len(input_set.basis[-1])
    number_of_points = sum(1 for cell in tiling if tiling[cell] is Block.point)
    perm_set_tiled = PermSetTiled(tiling)
    for length in range(number_of_points, number_of_points + longest_basis_length + 1):
        # print("TILING SET OF LENGTH", length)
        # print(list(perm_set_tiled.of_length(length)))
        # print("INPUT SET OF LENGTH", length)
        # print(list(input_set.of_length(length)))
        if not set(perm_set_tiled.of_length(length)).issubset(input_set.of_length(length)):
            return False
    return True
