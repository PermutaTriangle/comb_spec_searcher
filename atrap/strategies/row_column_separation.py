from collections import defaultdict
from grids import Tiling, Block, PositiveClass
from atrap.tools import basis_partitioning
from permuta import Perm, PermSet


def row_inequalities_of_tiling(tiling, basis, row):
    # The containing/avoiding perms_of_cells dictionary
    smaller_than_dicts = (defaultdict(set), defaultdict(set))

    # We only need to check permutations up to this length because any longer
    # perm can be reduced to a perm of this length and still contain the patt
    # if it already did
    verification_length = tiling.total_points + 2
    verification_length += sum(1 for _, block in tiling.non_points if isinstance(block, PositiveClass))

    for length in range(verification_length + 1):
        # Get the partitioning into containing/avoiding perms
        partitions = basis_partitioning(tiling, length, basis)

        # For containing and avoiding
        for partition, cells_smaller_than in zip(partitions, smaller_than_dicts):
            # For each perm and its associated info
            for cell_infos in partition.values():
                # Store for each cell its contribution to the perm
                for cell_info in cell_infos:

                    all_single_cells_values = []
                    for cell, info in cell_info.items():
                        if cell.j == row:
                            _, cell_values, _ = info
                            if len(cell_values) > 1:
                                continue
                            all_single_cells_values.append( (cell, cell_values[0]) )
                    print(all_single_cells_values)
                    if len(all_single_cells_values) > 1:
                        all_single_cells_values.sort( key=lambda x: x[1])
                        smallest_cell = all_single_cells_values[0][0]
                        cells_smaller_than[smallest_cell].update( x[0] for x in all_single_cells_values[1:] )

    containing_smaller_than, avoiding_smaller_than = smaller_than_dicts
    print()
    print(containing_smaller_than)
    print(avoiding_smaller_than)
    smaller_than = {}

    for cell, _ in tiling.get_row(row):
        smaller_than[cell] = containing_smaller_than[cell] - avoiding_smaller_than[cell]

    return smaller_than
