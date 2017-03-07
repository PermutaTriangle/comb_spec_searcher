from collections import defaultdict
from grids import Tiling, Block, PositiveClass
from atrap.tools import basis_partitioning
from permuta import Perm, PermSet

def row_and_column_inequalities_of_tiling(tiling, basis):
    # This will create the containing/avoiding less than cells of the permutation by row
    smaller_than_dicts_by_row = (defaultdict(dict), defaultdict(dict))
    smaller_than_dicts_by_col = (defaultdict(dict), defaultdict(dict))

    # We only need to check permutations up to this length because we are trying to show
    # one cell is less than another, so only patterns using the two cells need be considered.
    verification_length = tiling.total_points + 2
    # Add to the length the number of positive classes.
    # Of course positive classes contribute one extra in length since they can't be empty.
    verification_length += sum(1 for _, block in tiling.non_points if isinstance(block, PositiveClass))

    for length in range(verification_length + 1):
        # Get the partitioning into containing/avoiding perms
        partitions = basis_partitioning(tiling, length, basis)

        # For containing and avoiding
        for partition, cells_smaller_than_by_row, cells_smaller_than_by_col in zip(partitions, smaller_than_dicts_by_row, smaller_than_dicts_by_col):
            # For each perm and its associated info
            # for cell_infos in partition.values():
            for perm, cell_infos in partition.items():
                print(perm, cell_infos)
                # Store for each cell its contribution to the perm
                for cell_info in cell_infos:

                    # we collect the cells and cell values, cell indices by row, column respectively
                    all_single_cells_indices_cols = defaultdict(list)
                    all_single_cells_values_rows = defaultdict(list)
                    for cell, info in cell_info.items():
                        _, cell_values, cell_indices = info
                        # we only consider the occurrences where there has been one point placed in the cells
                        if len(cell_values) == 1:
                            all_single_cells_indices_cols[cell.i].append( (cell, cell_indices[0]) )
                            all_single_cells_values_rows[cell.j].append( (cell, cell_values[0]) )

                    # for each row we now create the set of inequalities.
                    for row, all_single_cells_values in all_single_cells_values_rows.items():
                        # if there is only one cell in the row, there is no need, as we can't reorder the cells.
                        if len(all_single_cells_values) > 1:
                            # we sort by the values, thus the first element must be the smallest in value.
                            ordered_row = sorted(all_single_cells_values, key = lambda x: - x[1])
                            print(ordered_row)
                            while len(ordered_row) > 1:
                                smallest_cell = ordered_row.pop(0)[0]
                                # then store that the smallest cell is smaller than the rest.
                                if smallest_cell in cells_smaller_than_by_row[row]:
                                    cells_smaller_than_by_row[row][smallest_cell].update( x[0] for x in ordered_row )
                                else:
                                    cells_smaller_than_by_row[row][smallest_cell] = set( [x[0] for x in ordered_row] )

                    # for each column we now create the set of inequalities
                    for col, all_single_cells_indices in all_single_cells_indices_cols.items():
                        # if there is only one cell in the column, there is no need, as we can't reorder the cells.
                        if len(all_single_cells_indices) > 1:
                            # we sort by the indices, thus the first element must be the leftmost/smallest in index.
                            ordered_col = sorted(all_single_cells_indices, key = lambda x: - x[1])
                            print(ordered_col)
                            while len(ordered_col) > 1:
                                smallest_cell = ordered_col.pop(0)[0]
                                # then store that the smallest cell is smaller than the rest.
                                if smallest_cell in cells_smaller_than_by_col[col]:
                                    cells_smaller_than_by_col[col][smallest_cell].update( x[0] for x in ordered_col )
                                else:
                                    cells_smaller_than_by_col[col][smallest_cell] = set( [x[0] for x in ordered_col] )

    # we now have all the inequalities given by the perms, split by containing and avoiding.
    containing_smaller_than_row, avoiding_smaller_than_row = smaller_than_dicts_by_row
    containing_smaller_than_col, avoiding_smaller_than_col = smaller_than_dicts_by_col
    print("row")
    print(containing_smaller_than_row)
    print(avoiding_smaller_than_row)
    print("col")
    print(containing_smaller_than_col)
    print(avoiding_smaller_than_col)

    # we will create the actual inequalities, considering whether the perm avoids or contains
    # this dictionary points to a row that points to the cells.
    smaller_than_row = defaultdict(dict)
    smaller_than_col = defaultdict(dict)

    # for each row
    # TODO: this should be for all rows with two elements or more
    for row in range(tiling.dimensions.j):
        row_cells = tiling.get_row(row)
        if len(row_cells) > 1:
            # for each cell
            for cell, _ in row_cells:
                # pick out the inequalities for containing
                containing_cells_smaller_than = containing_smaller_than_row[row][cell] if cell in containing_smaller_than_row[row] else set()
                # pick out the inequalities for avoiding
                avoiding_cells_smaller_than = avoiding_smaller_than_row[row][cell] if cell in avoiding_smaller_than_row[row] else set()
                # then a cell is actually less than if and only if it is less than for only containing perms
                # hence we take the set minus.
                smaller_than_row[row][cell] = containing_cells_smaller_than - avoiding_cells_smaller_than

    # essentially repeat above for columns. for each column
    # TODO: this should be for all cols with two elements or more
    for col in range(tiling.dimensions.i):
        col_cells = tiling.get_col(col)
        if len(col_cells) > 1:
        # for each cell
            for cell, _ in col_cells:
                # pick out the inequalities for containing
                containing_cells_smaller_than = containing_smaller_than_col[col][cell] if cell in containing_smaller_than_col[col] else set()
                # pick out the inequalities for avoiding
                avoiding_cells_smaller_than = avoiding_smaller_than_col[col][cell] if cell in avoiding_smaller_than_col[col] else set()
                # then a cell is actually less than if and only if it is less than for only containing perms
                # hence we take the set minus.
                smaller_than_col[col][cell] = containing_cells_smaller_than - avoiding_cells_smaller_than

    # we then return these inequalities ready for parsing so as to determine how we can split rows and columns.
    return smaller_than_row, smaller_than_col
