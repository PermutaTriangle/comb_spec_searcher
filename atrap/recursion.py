from grids import *
from permuta import *
from permuta.misc import UnionFind
from itertools import combinations

def components(tiling, basis):

    cell_to_int = {}

    for cell in tiling:
        # TODO: use integer mapping
        cell_to_int[cell] = len(cell_to_int)

    components = UnionFind(len(cell_to_int))

    tilingpermset = PermSetTiled(tiling)

    for patt in basis:
        max_length = tiling.total_points + len(patt)
        for perm_length in range(max_length + 1):
            for perm, where in tilingpermset.of_length_with_positions(perm_length):
                for occurence in perm.occurrences_of(patt):
                    cells_to_be_joined = set( where[perm[i]] for i in occurence )
                    for cell1, cell2 in combinations(list(cells_to_be_joined), 2):
                        components.unite(cell_to_int[cell1], cell_to_int[cell2])
    all_components = {}
    for cell in tiling:
        i = components.find( cell_to_int[cell] )
        if i in all_components:
            all_components[i].append(cell)
        else:
            all_components[i] = [cell]
    return list( all_components.values() )
