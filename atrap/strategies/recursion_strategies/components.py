from grids import *
from permuta import *
from permuta.misc import UnionFind
from itertools import combinations
from atrap.tools import basis_partitioning

from .recursive_class import RecursiveStrategy

# Overly strict version, should we just remove it?
def components(tiling, basis):

    cell_to_int = {}

    for cell,_ in tiling:
        # TODO: use integer mapping
        cell_to_int[cell] = len(cell_to_int)

    components = UnionFind(len(cell_to_int))

    # TODO: work through permset first rather than regeneate for each pattern.
    for patt in basis:
        verification_length = tiling.total_points + len(patt)
        verification_length += sum(1 for _, block in tiling.non_points if isinstance(block, PositiveClass))
        for perm_length in range(verification_length + 1):
            containing_perms, _ = basis_partitioning(tiling, perm_length, basis)

            for perm, cell_infos in containing_perms.items():
                assert len(cell_infos) == 1
                for cell_info in cell_infos:
                    cell_perm = [ 0 for i in range(len(perm))]
                    for cell in cell_info.keys():
                        _, _, cell_indices = cell_info[cell]
                        for index in cell_indices:
                            cell_perm[index] = cell

                for occurrence in perm.occurrences_of(patt):
                    cells_to_be_joined = set( cell_perm[i] for i in occurrence )
                    for cell1, cell2 in combinations(list(cells_to_be_joined), 2):
                        components.unite(cell_to_int[cell1], cell_to_int[cell2])

    all_components = {}
    for cell, _ in tiling:
        i = components.find( cell_to_int[cell] )
        if i in all_components:
            all_components[i].append(cell)
        else:
            all_components[i] = [cell]
    cells_of_new_tilings = list( all_components.values() )

    if len(cells_of_new_tilings) == 1:
        return
    strategy = []
    for new_cells in cells_of_new_tilings:
        new_tiling_dict = {}
        for cell in new_cells:
            new_tiling_dict[cell] = tiling[cell]
        strategy.append(Tiling(new_tiling_dict))
    if len(strategy) <= 1:
        return

    yield RecursiveStrategy( "The components of the tiling", strategy  )
# Consider the union of components?
