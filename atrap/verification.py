from grids import *
from permuta import *


def verify_tiling(tiling, input_set):
    longest_basis_length = len(input_set.basis[-1])
    number_of_points = sum(1 for cell in tiling if tiling[cell] is Tile.P)
    tiling_perm_set = TilingPermSet(TilingPermSetDescriptor(tiling))
    for length in range(number_of_points, number_of_points + longest_basis_length + 1):
        # print("TILING SET OF LENGTH", length)
        # print(list(tiling_perm_set.of_length(length)))
        # print("INPUT SET OF LENGTH", length)
        # print(list(input_set.of_length(length)))
        if not set(tiling_perm_set.of_length(length)).issubset(input_set.of_length(length)):
            return False
    return True
