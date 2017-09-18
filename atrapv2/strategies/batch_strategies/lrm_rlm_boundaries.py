from permuta import Perm, Av
from grids import Tiling, Block, Cell
from .batch_class import BatchStrategy

def left_to_right_maxima(perm):
    """Return the indices of left to right maxima."""
    lrm = []
    mx = -1
    for i in range(len(perm)):
        if perm[i] > mx:
            lrm.append(i)
            mx = perm[i]
    return lrm


def right_to_left_minima(perm):
    """Return the indices of right to left minima."""
    rlm = []
    mn = len(perm)
    for i in range(len(perm)-1,-1,-1):
        if perm[i] < mn:
            rlm.append(i)
            mn = perm[i]
    return rlm


def get_boundary_tiling(perm, permclass):
    """Return the boundary tiling for a 321-avoiding permutation."""
    lrm = left_to_right_maxima(perm)
    rlm = right_to_left_minima(perm)[::-1]
    tiling = {}
    for k in range(len(perm)):
        tiling[Cell(i=2*k, j=2*perm[k])] = Block.point
    lrm_ind = 0
    rlm_ind = 0
    for x in range(1, 2*len(perm)-1, 2):
        if lrm_ind+1 < len(lrm) and x > 2*lrm[lrm_ind+1]:
            lrm_ind += 1
        if rlm_ind < len(rlm) and x > 2*rlm[rlm_ind]:
            rlm_ind += 1
        start = 2*perm[rlm[rlm_ind]] + 1 if rlm_ind < len(rlm) else 1
        end = 2*perm[lrm[lrm_ind]] + 1 if lrm_ind < len(lrm) else 2*len(perm)-1
        for y in range(start, end, 2):
            tiling[Cell(i=x,j=y)] = permclass
    return Tiling(tiling)


def all_321_boundaries(tiling, basis, **kwargs):
    """All 321 boundaries."""
    if tiling.dimensions.i != 1 or tiling.dimensions.j != 1:
        return
    if tiling[(0,0)] != Av(basis):
        return
    boundary_basis = list(basis) + [Perm((2, 1, 0))]
    if not any(perm.is_increasing() for perm in boundary_basis):
        return
    boundary_list = [get_boundary_tiling(perm, Av(basis)) for perm in Av(boundary_basis)]
    yield BatchStrategy("All 321 boundaries", boundary_list)
