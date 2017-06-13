from permuta import Perm, Av
from grids import Tiling, Block
from .batch_class import BatchStrategy

def get_boundary_tiling(perm, perm_class):
    tiling_dict = { (2*i, 2*perm[i]):Block.point for i in range(len(perm)) }
    for i in range(len(perm) - 1):
        for j in range(len(perm) - 1):
            tiling_dict[(2*i + 1, 2*j+1)] = perm_class
    return Tiling(tiling_dict)

def extreme_point_boundaries(tiling, basis, **kwargs):
    if tiling.dimensions.i != 1 or tiling.dimensions.j != 1:
        return
    if tiling[(0,0)] != Av(basis):
        return
    boundary_basis = list(basis) + [Perm((2, 1, 0)), Perm((0, 1, 2))]

    boundary_list = [get_boundary_tiling(perm, Av(basis)) for perm in Av(boundary_basis)]
    # for t in boundary_list:
    #     print(t)
    yield BatchStrategy("All boundaries", boundary_list)
