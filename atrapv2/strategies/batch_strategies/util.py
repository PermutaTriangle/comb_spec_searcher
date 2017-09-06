from permuta import *
from grids import Tiling, Block

def tiling_from_mesh_pattern(mpatt, perm_class):
    """Given a mesh pattern and perm_class, generate a tiling where
    the mesh pattern has been placed within the perm class."""
    tiling = {(2*i, 2*j): perm_class
            for i in range(len(mpatt) + 1) for j in range(len(mpatt) + 1) if (i,j) not in mpatt.shading}
    for i in range(len(mpatt)):
        tiling[(2*i + 1, 2*mpatt.pattern[i] + 1)] = Block.point

    return Tiling(tiling)

def is_binary(patt, basis):
    """Checks if a given pattern is binary with respect to the basis"""
    permset = PermSet.avoiding(basis)
    for l in range(len(patt) + 1, 2 * len(patt) + 1):
        for p in permset.of_length(l):
            if patt.count_occurrences_in(p) > 1:
                return False
    return True
