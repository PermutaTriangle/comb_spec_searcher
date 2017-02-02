from grids import *
from permuta import *
from permuta.misc import UnionFind
from itertools import combinations, chain
from copy import copy

# Overly strict version, should we just remove it?
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


# We never use this function. Probably should just delete it.
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
                    if perm in perms_to_consider:
                        perms_to_consider[perm] = (perms_to_consider[0] + occurences, perms_to_consider[1])
                    perms_to_consider[perm] = (occurences, where)


    for perm, (occurences, where) in perms_to_consider.items():
        new_occurences = []
        for occurence in occurences:
            if not any( where[i] == cell for i in occurence ):
                new_occurences.append(occurence)
        if len(new_occurences) > 0:
            continue
        else:
            return False
    return True

def reversibly_deletably_path_finder(tiling, basis):

    tilingpermset = PermSetTiled(tiling)

    perms_to_consider = {}
    max_patt_length = max(len(patt) for patt in basis)
    max_length = tiling.total_points + max_patt_length

    for perm_length in range(max_length + 1):
        # where tells you which cell a point belongs to.
        for perm, where in tilingpermset.of_length_with_positions(perm_length):
            for patt in basis:
                if max_length - tiling.total_points >= max_patt_length:
                    occurences = [ [ where[ perm[i] ] for i in occurence ] for occurence in perm.occurrences_of(patt) ]
                    if len(occurences) > 0:
                        if perm in perms_to_consider:
                            perms_to_consider[perm] += occurences
                        else:
                            perms_to_consider[perm] = occurences

    paths = set()
    for cell in tiling:
        for path in reversibly_deletably_path_finder_helper( cell, perms_to_consider, tiling ):
            yield path

def reversibly_deletably_path_finder_helper(cell, perms_to_consider, tiling):

    new_perms_to_consider = {}
    for perm, occurences in perms_to_consider.items():
        new_occurences = []
        for occurence in occurences:
            if not any( i == cell for i in occurence ):
                new_occurences.append(occurence)
        if len(new_occurences) > 0:
            new_perms_to_consider[perm] = new_occurences
        else:
            return
    yield [cell]
    for cell2 in tiling:
        if cell2 > cell:
            for path in reversibly_deletably_path_finder_helper(cell2, new_perms_to_consider, tiling):
                yield [cell] + path
