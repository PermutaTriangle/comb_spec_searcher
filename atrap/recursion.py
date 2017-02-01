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

def is_reversibly_deletable(tiling, cell, basis):

    tilingpermset = PermSetTiled(tiling)

    perms_to_consider = {}

    for patt in basis:
        max_length = tiling.total_points + len(patt)
        for perm_length in range(max_length + 1):
            # where tells you which cell a point belongs to.
            for perm, where in tilingpermset.of_length_with_positions(perm_length):
                occurences = [ [ perm[i] for i in occurence ] for occurence in perm.occurrences_of(patt) ]
                if len(occurences) > 0:
                    perms_to_consider[perm] = (occurences, where)


    for perm, (occurences, where) in perms_to_consider.items():
        new_occurences = []
        for occurence in occurences:
            if any( where[i] == cell for i in occurence ):
                continue
            new_occurences.append(occurence)
        if len(new_occurences) > 0:
            continue
            # for continuing on in future tiling without the cell, we would go into new_perm, new_occurences and check.
            # new_perm = [ i for i in perm if not where[i] == cell ]
        else:
            return False
    return True
