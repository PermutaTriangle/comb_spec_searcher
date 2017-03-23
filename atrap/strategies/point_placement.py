
from grids import Block
from grids import PositiveClass
from grids import Tiling


def all_point_placements(tiling, **kwargs):
    for cell, block in tiling.non_points:
        if not isinstance(block, PositiveClass):
            continue

        if sum(1 for _, col_block in tiling.get_col(cell.i)
               if isinstance(col_block, PositiveClass)
               or col_block is Block.point) != 1:
            # Cell ineligible because cell is not the sole non-class cell
            # in its respective col
            return

        if sum(1 for _, row_block in tiling.get_row(cell.j)
               if isinstance(row_block, PositiveClass)
               or row_block is Block.point) != 1:
             # Cell ineligible because cell is not the sole non-class cell
             # in its respective row
            return

        topmost_tiling_dict = {}
        bottommost_tiling_dict = {}
        leftmost_tiling_dict = {}
        rightmost_tiling_dict = {}

        for new_cell, new_block in tiling:
            if new_cell.i == cell.i:
                # same cell
                if new_cell.j == cell.j:
                    perm_class = new_block.perm_class
                    topmost_tiling_dict[cell.i + 0.5, cell.j - 0.5] = perm_class
                    topmost_tiling_dict[cell.i - 0.5, cell.j - 0.5] = perm_class
                    topmost_tiling_dict[cell] = Block.point

                    bottommost_tiling_dict[cell.i + 0.5, cell.j + 0.5] = perm_class
                    bottommost_tiling_dict[cell.i - 0.5, cell.j + 0.5] = perm_class
                    bottommost_tiling_dict[cell] = Block.point


                    leftmost_tiling_dict[cell.i + 0.5, cell.j + 0.5] = perm_class
                    leftmost_tiling_dict[cell.i + 0.5, cell.j - 0.5] = perm_class
                    leftmost_tiling_dict[new_cell] = Block.point

                    rightmost_tiling_dict[cell.i - 0.5, cell.j + 0.5] = perm_class
                    rightmost_tiling_dict[cell.i - 0.5, cell.j - 0.5] = perm_class
                    rightmost_tiling_dict[new_cell] = Block.point

                # same column, but different row
                else:
                    topmost_tiling_dict[(new_cell.i + 0.5, new_cell.j)] = new_block
                    topmost_tiling_dict[(new_cell.i - 0.5, new_cell.j)] = new_block

                    bottommost_tiling_dict[(new_cell.i + 0.5, new_cell.j)] = new_block
                    bottommost_tiling_dict[(cell.i - 0.5, new_cell.j)] = new_block

                    leftmost_tiling_dict[(new_cell.i + 0.5, new_cell.j)] = new_block
                    leftmost_tiling_dict[(new_cell.i - 0.5, new_cell.j)] = new_block

                    rightmost_tiling_dict[(new_cell.i - 0.5, new_cell.j)] = new_block
                    rightmost_tiling_dict[(new_cell.i - 0.5, new_cell.j)] = new_block

            # same row, but different column
            elif new_cell.j == cell.j:
                topmost_tiling_dict[(new_cell.i, new_cell.j + 0.5)] = new_block
                topmost_tiling_dict[(new_cell.i, new_cell.j - 0.5)] = new_block

                bottommost_tiling_dict[(new_cell.i, new_cell.j + 0.5)] = new_block
                bottommost_tiling_dict[(new_cell.i, new_cell.j - 0.5)] = new_block

                leftmost_tiling_dict[(new_cell.i, new_cell.j + 0.5)] = new_block
                leftmost_tiling_dict[(new_cell.i, new_cell.j - 0.5)] = new_block

                rightmost_tiling_dict[(new_cell.i, new_cell.j + 0.5)] = new_block
                rightmost_tiling_dict[(new_cell.i, new_cell.j - 0.5)] = new_block

            # different row and column
            else:
                topmost_tiling_dict[new_cell] = new_block
                bottommost_tiling_dict[new_cell] = new_block
                leftmost_tiling_dict[new_cell] = new_block
                rightmost_tiling_dict[new_cell] = new_block

        topmost_tiling = Tiling(topmost_tiling_dict)
        bottommost_tiling = Tiling(bottommost_tiling_dict)
        leftmost_tiling = Tiling(leftmost_tiling_dict)
        rightmost_tiling = Tiling(rightmost_tiling_dict)

        yield "Inserting the top most point in to the cell " + str(cell), topmost_tiling
        yield "Inserting the left most point in to the cell " + str(cell), leftmost_tiling
        yield "Inserting the bottom most point in to the cell " + str(cell), bottommost_tiling
        yield "Inserting the right most point in to the cell " + str(cell),  rightmost_tiling
