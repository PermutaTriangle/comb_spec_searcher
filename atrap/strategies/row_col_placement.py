from grids import Block
from grids import Cell
from grids import PositiveClass
from grids import Tiling


__all__ = ["row_placement", "col_placement", "all_row_and_col_placements"]


def scale(cell, i_factor, i_add, j_factor, j_add):
    """Return a scale modified cell."""
    return Cell(i_factor*cell.i + i_add, j_factor*cell.j + j_add)


def all_row_and_col_placements(tiling, **kwargs):
    for row_number in range(tiling.dimensions.j):
        for strategy in row_placement(tiling, row_number):
            yield strategy
    for col_number in range(tiling.dimensions.i):
        for strategy in col_placement(tiling, col_number):
            yield strategy


def row_placement(tiling, row_number):
    """Yield the strategies that place the minimum and maximum of a row.

    TODO"""  # TODO: Doc
    row = tiling.get_row(row_number)

    if len(row) == 1 and row[0][1] is Block.point:
        # Row ineligible: a single point cell is useless to place points in.
        return

    for cell, block in row:
        if not (isinstance(block, PositiveClass) or block is Block.point):
            # Row ineligible: contains a cell that is not necessarily not empty
            return

    for cell, _ in row:
        if sum(1 for _, col_block in tiling.get_col(cell.i)
               if isinstance(col_block, PositiveClass)
               or col_block is Block.point) != 1:
            # Row ineligible because each cell is not the sole non-class cell
            # in its respective col
            return

    # Create a new tiling dict, but scale it up because we want to be able
    # to put some new blocks in between the old ones
    base_tiling_dict = {}
    for cell, block in tiling:
        base_tiling_dict[scale(cell, 3, 0, 3, 0)] = block

    # There are two strategies: inserting a minimum or maximum
    # We can place the minimum/maximum into any of the positive class
    # blocks of the row being looked at.
    minimum_strategy = []
    maximum_strategy = []

    for cell, block in row:
        new_tiling_dict = base_tiling_dict.copy()

        # Make a copy of the column to the right of it
        for col_cell, col_block in tiling.get_col(cell.i):
            new_tiling_dict[scale(col_cell, 3, 2, 3, 0)] = col_block

        # The cell we are placing into is treated differently
        if isinstance(block, PositiveClass):
            new_tiling_dict[scale(cell, 3, 0, 3, 0)] = block.perm_class
            new_tiling_dict[scale(cell, 3, 2, 3, 0)] = block.perm_class
        else:
            # It is a point, and we have concretely placed it
            # We need to clean up our mess
            new_tiling_dict.pop(scale(cell, 3, 0, 3, 0))
            new_tiling_dict.pop(scale(cell, 3, 2, 3, 0))

        # Point can be placed as a new minimum...
        point_cell = scale(cell, 3, 1, 3, -1)  # Slightly to the right and below
        new_tiling_dict[point_cell] = Block.point
        minimum_strategy.append(Tiling(new_tiling_dict))
        new_tiling_dict.pop(point_cell)

        # ... or as a new maximum
        point_cell = scale(cell, 3, 1, 3, 1)  # Slightly to the right and above
        new_tiling_dict[point_cell] = Block.point
        maximum_strategy.append(Tiling(new_tiling_dict))
        new_tiling_dict.pop(point_cell)

    # TODO: Formal step
    yield minimum_strategy
    yield maximum_strategy


def col_placement(tiling, col_number):
    col = tiling.get_col(col_number)

    if len(col) == 1 and col[0][1] is Block.point:
        return

    for cell, block in col:
        if not (isinstance(block, PositiveClass) or block is Block.point):
            return

    for cell, _ in col:
        if sum(1 for _, row_block in tiling.get_row(cell.j)
               if isinstance(row_block, PositiveClass)
               or row_block is Block.point) != 1:
            return

    base_tiling_dict = {}
    for cell, block in tiling:
        base_tiling_dict[scale(cell, 3, 0, 3, 0)] = block

    leftmost_strategy = []
    rightmost_strategy = []

    for cell, block in col:
        new_tiling_dict = base_tiling_dict.copy()

        for row_cell, row_block in tiling.get_row(cell.j):
            new_tiling_dict[scale(row_cell, 3, 0, 3, 2)] = row_block

        if isinstance(block, PositiveClass):
            new_tiling_dict[scale(cell, 3, 0, 3, 0)] = block.perm_class
            new_tiling_dict[scale(cell, 3, 0, 3, 2)] = block.perm_class
        else:
            new_tiling_dict.pop(scale(cell, 3, 0, 3, 0))
            new_tiling_dict.pop(scale(cell, 3, 0, 3, 2))

        point_cell = scale(cell, 3, -1, 3, 1)
        new_tiling_dict[point_cell] = Block.point
        leftmost_strategy.append(Tiling(new_tiling_dict))
        new_tiling_dict.pop(point_cell)

        point_cell = scale(cell, 3, 1, 3, 1)
        new_tiling_dict[point_cell] = Block.point
        rightmost_strategy.append(Tiling(new_tiling_dict))

    yield leftmost_strategy
    yield rightmost_strategy
