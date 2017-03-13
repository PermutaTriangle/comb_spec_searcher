

from grids import Block
from grids import Cell
from grids import PositiveClass
from grids import Tiling


def scale_cell(cell, i_factor, i_add, j_factor, j_add):
    return Cell(i_factor*cell.i + i_add, j_factor*cell.j + j_add)


def row_col_placement(tiling):
    pass


def row_placement(tiling):
    for row_number in range(tiling.dimensions.j):
        ineligible = False

        row = tiling.get_row(row_number)
        for cell, block in row:
            if not (isinstance(block, PositiveClass) or block is Block.point):
                ineligible = True
                break

        if ineligible or len(row) == 1 and row[0][1] is Block.point:
            # Row ineligible, don't try placing point:
            #   - either no cells found to place points; or,
            #   - a single point cell found (which is useless to place points on).
            continue

        for cell, _ in row:
            if sum(1 for _, col_block in tiling.get_col(cell.i) if isinstance(col_block, PositiveClass) or col_block is Block.point) != 1:
                ineligible = True
                break

        if ineligible:
            # Row ineligible because each cell is not the sole non-class cell
            # in its respective col
            continue

        new_tiling_dict = {}
        for cell, block in tiling:
            new_tiling_dict[(3*cell.i, 3*cell.j)] = block

        # There are two strategies: inserting a minimum or maximum
        minimum_strategy = []
        maximum_strategy = []

        for cell, block in row:
            extra_cells = []
            for col_cell, col_block in tiling.get_col(cell.i):
                if col_cell == cell:
                    if col_block is block.Point:
                        placed_block = col_block
                    placed_block = col_block.perm_class
                else:
                    placed_block = col_block
                new_cell = (3*col_cell.i + 2, 3*col_cell.j)
                new_tiling_dict[new_cell] = placed_block
                extra_cells.append(new_cell)
            new_tiling_dict[(3*cell.i, 3*cell.j)] = block.perm_class
            point_cell = (3*cell.i + 1, 3*cell.j - 1)
            new_tiling_dict[point_cell] = Block.point
            minimum_strategy.append(Tiling(new_tiling_dict))
            new_tiling_dict.pop(point_cell)
            point_cell = (3*cell.i + 1, 3*cell.j + 1)
            new_tiling_dict[point_cell] = Block.point
            maximum_strategy.append(Tiling(new_tiling_dict))
            new_tiling_dict.pop(point_cell)
            for extra_cell in extra_cells:
                new_tiling_dict.pop(extra_cell)
            new_tiling_dict[(3*cell.i, 3*cell.j)] = block

        yield minimum_strategy
        yield maximum_strategy
