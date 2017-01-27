from grids import *
from .tools import tiling_inferral
from copy import copy


__all__ = ["all_row_and_column_insertions"]


# this returns the tiling with row left empty, plus a list of all the coordinates of the cells in row.
def row_insertion_helper(parent_tiling, row):
    tiling = parent_tiling
    empty_d = {}
    row_cells = []
    for (i, j), perm_set in tiling.items():
        if i == row:
            row_cells.append( (i,j) )
        elif  i < row:
            empty_d[(i,j)] = perm_set
        else: # i > row
            empty_d[(i+1,j)] = perm_set
    return Tiling(empty_d), row_cells


# This returns the strategies achieved by inserting into a row. It assumes this can be done.
def row_insertion(parent_tiling, row, input_set):
    empty_row, row_cells = row_insertion_helper(parent_tiling, row)
    # bottom_strategy will insert points in to the bottom of the row, each cell at a time.
    bottom_strategy = [empty_row]
    # top_strategy will insert points in to the top of the row, each cell at a time.
    top_strategy = [empty_row]
    for (n,m) in row_cells:
        # we will now insert min or max into cell (n,m)
        bottom_d = {}
        bottom_d[(n,m+1)] = Tile.P
        top_d = {}
        top_d[(n+1,m+1)] = Tile.P

        for (i,j), perm_set in empty_row.items():
            # we go through the remaining items. If not a point, we insert None, as it need to be inferred.
            if perm_set is not Tile.P:
                perm_set = None
            if j < m:
                bottom_d[(i,j)] = perm_set
                top_d[(i,j)] = perm_set
            elif j > m:
                bottom_d[(i,j+2)] = perm_set
                top_d[(i,j+2)] = perm_set
            else:
                bottom_d[(i,j)] = perm_set
                bottom_d[(i,j+2)] = perm_set
                top_d[(i,j)] = perm_set
                top_d[(i,j+2)] = perm_set

        for (i,j) in row_cells:
            # we now go through the cells in the row, and add None to all perm_sets as they will need to be inferred.
            if (i,j) == (n,m):
                bottom_d[(i+1, j)] = None
                bottom_d[(i+1, j+2)] = None
                top_d[(i, j)] = None
                top_d[(i, j+2)] = None
            elif j < m:
                bottom_d[(i+1,j)] = None
                top_d[(i,j)] = None
            else:
                bottom_d[(i+1,j+2)] = None
                top_d[(i,j+2)] = None

        # we then infer the tillings and add them to the strategies.
        inferred_bottom = tiling_inferral(Tiling(bottom_d), input_set)
        inferred_top = tiling_inferral(Tiling(top_d), input_set)

        bottom_strategy.append(inferred_bottom)
        top_strategy.append(inferred_top)

    # I got top and bottom mixed up, need to go through and change these around!
    yield "Inserting the top most point into row " + str(row), tuple( bottom_strategy )
    yield "Inserting the bottom most point into row " + str(row), tuple( top_strategy )

# this returns the tiling with column left empty, plus a list of all the coordinates of the cells in column.
def column_insertion_helper(parent_tiling, column):
    tiling = parent_tiling
    empty_d = {}
    column_cells = []
    # TODO Add check that no points in column trying to insert into. All sets must contain empty.
    # TODO Check that if adding point to each box, then this kills rest of column every time.
    for (i, j), perm_set in tiling.items():
        if j == column:
            column_cells.append( (i,j) )
        elif  j < column:
            empty_d[(i,j)] = perm_set
        else: # j > column
            empty_d[(i,j+1)] = perm_set
    return Tiling(empty_d), column_cells

# This returns the strategies achieved by inserting into a column. It assumes this can be done.
def column_insertion(parent_tiling, column, input_set):
    empty_column, column_cells = column_insertion_helper(parent_tiling, column)
    # left_strategy will insert points in to the leftmost of the column, each cell at a time.
    left_strategy = [empty_column]
    # right_strategy will insert points in to the rightmost of the column, each cell at a time.
    right_strategy = [empty_column]
    for (n,m) in column_cells:
        # we will now insert leftmost or rightmost into cell (n,m)
        left_d = {}
        left_d[(n+1,m)] = Tile.P
        right_d = {}
        right_d[(n+1,m+1)] = Tile.P

        for (i,j), perm_set in empty_column.items():
            # we go through the remaining items, not in column. If not a point, we insert None, as it need to be inferred.
            if perm_set is not Tile.P:
                perm_set = None
            if i < n:
                left_d[(i,j)] = perm_set
                right_d[(i,j)] = perm_set
            elif i > n:
                left_d[(i+2,j)] = perm_set
                right_d[(i+2,j)] = perm_set
            else:
                left_d[(i,j)] = perm_set
                left_d[(i+2,j)] = perm_set
                right_d[(i,j)] = perm_set
                right_d[(i+2,j)] = perm_set

        for (i,j) in column_cells:
            # we now go through the cells in the column, and add None to all perm_sets as they will need to be inferred.
            if (i,j) == (n,m):
                left_d[(i, j+1)] = None
                left_d[(i+2, j+1)] = None
                right_d[(i, j)] = None
                right_d[(i+2, j)] = None
            elif i < n:
                left_d[(i,j+1)] = None
                right_d[(i,j)] = None
            else:
                left_d[(i+2,j+1)] = None
                right_d[(i+2,j)] = None

        # we then infer the tillings and add them to the strategies.
        inferred_left = tiling_inferral(Tiling(left_d), input_set)
        inferred_right = tiling_inferral(Tiling(right_d), input_set)

        left_strategy.append(inferred_left)
        right_strategy.append(inferred_right)

    yield "Inserting the left most point into column " + str(column), tuple( left_strategy )
    yield "Inserting the right most point into column " + str(column), tuple( right_strategy )


def all_row_and_column_insertions(tiling, input_set):
    row_blocks = {}
    column_blocks = {}
    for (i,j), block in tiling.items():
        if block is Tile.P:
            # If row or column contains a point, we do not insert into this row or column.
            row_blocks[i] = None
            column_blocks[j] = None
        else:
            # We count how many cells are contained in each row and column as we do not do row or column insertion if only one.
            if i not in row_blocks:
                row_blocks[i] = 1
            else:
                row_blocks[i] += 1
            if j not in column_blocks:
                column_blocks[j] = 1
            else:
                column_blocks[j] += 1
    # if value is None, then row or column contains a point, so we ignore it.
    # if the count = 1 then exactly one in each row and column so equivalent to cell insertion so we ignore it.
    for i, value in row_blocks.items():
        if value is not None:
            if value > 0:
                for strategy in row_insertion(tiling, i, input_set):
                    yield strategy
    for j, value in column_blocks.items():
        if value is not None:
            if value > 0:
                for strategy in column_insertion(tiling, j, input_set):
                    yield strategy
