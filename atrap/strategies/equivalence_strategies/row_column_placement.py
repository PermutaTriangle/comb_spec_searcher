from grids import Tiling, Block, PositiveClass

from .equivalence_class import EquivalenceStrategy
from .point_placement import all_unique_point_or_empty, all_minimum_and_maximum_decreasing, all_minimum_and_maximum_increasing, all_minimum_decreasing, all_maximum_decreasing, all_minimum_increasing, all_maximum_increasing

def all_equivalent_row_placements(tiling, **kwargs):
    for row in range(tiling.dimensions.j):
        if len(tiling.get_row(row)) != 1:
            continue

        cell, block = tiling.get_row(row)[0]

        if not isinstance(block, PositiveClass) or block is Block.point:
            # Row inelegible as it is not a PositiveClass
            continue

        if any( sum(1 for _, col_block in tiling.get_col(cell.i)
               if isinstance(col_block, PositiveClass)
               or col_block is Block.point) != 1 for cell, _ in tiling.get_row(row) ):
            # Row ineligible because there is a cell that is not
            # the sole non-class cell in its respective col
            continue

        if block is PositiveClass(Block.decreasing):
            for strategy in all_minimum_and_maximum_decreasing( tiling, cell ):
                yield strategy
            continue

        if block is PositiveClass(Block.increasing):
            for strategy in all_minimum_and_maximum_increasing( tiling, cell ):
                yield strategy
            continue

        if block is PositiveClass(Block.point_or_empty):
            for strategy in all_unique_point_or_empty( tiling, cell ):
                yield strategy
            continue

        topmost_tiling_dict = {}
        bottommost_tiling_dict = {}

        for new_cell, new_block in tiling:
            if new_cell.i == cell.i:
                # same cell
                if new_cell.j == cell.j:
                    perm_class = new_block.perm_class
                    topmost_tiling_dict[(cell.i + 0.5, cell.j - 0.5)] = perm_class
                    topmost_tiling_dict[(cell.i - 0.5, cell.j - 0.5)] = perm_class
                    topmost_tiling_dict[cell] = Block.point

                    bottommost_tiling_dict[(cell.i + 0.5, cell.j + 0.5)] = perm_class
                    bottommost_tiling_dict[(cell.i - 0.5, cell.j + 0.5)] = perm_class
                    bottommost_tiling_dict[cell] = Block.point

                # same column, but different row
                else:
                    topmost_tiling_dict[(new_cell.i + 0.5, new_cell.j)] = new_block
                    topmost_tiling_dict[(new_cell.i - 0.5, new_cell.j)] = new_block

                    bottommost_tiling_dict[(new_cell.i + 0.5, new_cell.j)] = new_block
                    bottommost_tiling_dict[(new_cell.i - 0.5, new_cell.j)] = new_block

            # same row, but different column
            elif new_cell.j == cell.j:
                topmost_tiling_dict[(new_cell.i, new_cell.j + 0.5)] = new_block
                topmost_tiling_dict[(new_cell.i, new_cell.j - 0.5)] = new_block

                bottommost_tiling_dict[(new_cell.i, new_cell.j + 0.5)] = new_block
                bottommost_tiling_dict[(new_cell.i, new_cell.j - 0.5)] = new_block

            # different row and column
            else:
                topmost_tiling_dict[new_cell] = new_block
                bottommost_tiling_dict[new_cell] = new_block

        topmost_tiling = Tiling(topmost_tiling_dict)
        bottommost_tiling = Tiling(bottommost_tiling_dict)

        yield EquivalenceStrategy( "Inserting the top most point in to the cell " + str(cell), topmost_tiling )
        yield EquivalenceStrategy( "Inserting the bottom most point in to the cell " + str(cell), bottommost_tiling )


def all_equivalent_column_placements(tiling, **kwargs):
    for col in range(tiling.dimensions.i):
        if len(tiling.get_col(col)) != 1:
            continue

        cell, block = tiling.get_col(col)[0]

        if not isinstance(block, PositiveClass) or block is Block.point:
            # Row inelegible as it is not a PositiveClass
            continue

        if any( sum(1 for _, row_block in tiling.get_row(cell.j)
               if isinstance(row_block, PositiveClass)
               or row_block is Block.point) != 1 for cell, _ in tiling.get_col(col) ):
            # Col ineligible because there is a cell that is not
            # the sole non-class cell in its respective row
            continue

        if block is PositiveClass(Block.decreasing):
            for strategy in all_minimum_and_maximum_decreasing( tiling, cell ):
                yield strategy
            continue

        if block is PositiveClass(Block.increasing):
            for strategy in all_minimum_and_maximum_increasing( tiling, cell ):
                yield strategy
            continue

        if block is PositiveClass(Block.point_or_empty):
            for strategy in all_unique_point_or_empty( tiling, cell ):
                yield strategy
            continue

        leftmost_tiling_dict = {}
        rightmost_tiling_dict = {}

        for new_cell, new_block in tiling:
            if new_cell.i == cell.i:
                # same cell
                if new_cell.j == cell.j:
                    perm_class = new_block.perm_class
                    leftmost_tiling_dict[(cell.i + 0.5, cell.j + 0.5)] = perm_class
                    leftmost_tiling_dict[(cell.i + 0.5, cell.j - 0.5)] = perm_class
                    leftmost_tiling_dict[new_cell] = Block.point

                    rightmost_tiling_dict[(cell.i - 0.5, cell.j + 0.5)] = perm_class
                    rightmost_tiling_dict[(cell.i - 0.5, cell.j - 0.5)] = perm_class
                    rightmost_tiling_dict[new_cell] = Block.point

                # same column, but different row
                else:
                    leftmost_tiling_dict[(new_cell.i + 0.5, new_cell.j)] = new_block
                    leftmost_tiling_dict[(new_cell.i - 0.5, new_cell.j)] = new_block

                    rightmost_tiling_dict[(new_cell.i + 0.5, new_cell.j)] = new_block
                    rightmost_tiling_dict[(new_cell.i - 0.5, new_cell.j)] = new_block

            # same row, but different column
            elif new_cell.j == cell.j:
                leftmost_tiling_dict[(new_cell.i, new_cell.j + 0.5)] = new_block
                leftmost_tiling_dict[(new_cell.i, new_cell.j - 0.5)] = new_block

                rightmost_tiling_dict[(new_cell.i, new_cell.j + 0.5)] = new_block
                rightmost_tiling_dict[(new_cell.i, new_cell.j - 0.5)] = new_block

            # different row and column
            else:
                leftmost_tiling_dict[new_cell] = new_block
                rightmost_tiling_dict[new_cell] = new_block

        leftmost_tiling = Tiling(leftmost_tiling_dict)
        rightmost_tiling = Tiling(rightmost_tiling_dict)

        yield EquivalenceStrategy( "Inserting the left most point in to the cell " + str(cell), leftmost_tiling )
        yield EquivalenceStrategy( "Inserting the right most point in to the cell " + str(cell),  rightmost_tiling )


def all_equivalent_minimum_row_placements(tiling, **kwargs):
    for row in range(tiling.dimensions.j):
        if len(tiling.get_row(row)) != 1:
            continue

        cell, block = tiling.get_row(row)[0]

        if not isinstance(block, PositiveClass) or block is Block.point:
            # Row inelegible as it is not a PositiveClass
            continue

        if any( sum(1 for _, col_block in tiling.get_col(cell.i)
               if isinstance(col_block, PositiveClass)
               or col_block is Block.point) != 1 for cell, _ in tiling.get_row(row) ):
            # Row ineligible because there is a cell that is not
            # the sole non-class cell in its respective col
            continue

        if block is PositiveClass(Block.decreasing):
            for strategy in all_minimum_decreasing( tiling, cell ):
                yield strategy
            continue

        if block is PositiveClass(Block.increasing):
            for strategy in all_minimum_increasing( tiling, cell ):
                yield strategy
            continue

        if block is PositiveClass(Block.point_or_empty):
            for strategy in all_unique_point_or_empty( tiling, cell ):
                yield strategy
            continue
        bottommost_tiling_dict = {}

        for new_cell, new_block in tiling:
            if new_cell.i == cell.i:
                # same cell
                if new_cell.j == cell.j:
                    perm_class = new_block.perm_class

                    bottommost_tiling_dict[(cell.i + 0.5, cell.j + 0.5)] = perm_class
                    bottommost_tiling_dict[(cell.i - 0.5, cell.j + 0.5)] = perm_class
                    bottommost_tiling_dict[cell] = Block.point

                # same column, but different row
                else:
                    bottommost_tiling_dict[(new_cell.i + 0.5, new_cell.j)] = new_block
                    bottommost_tiling_dict[(new_cell.i - 0.5, new_cell.j)] = new_block

            # same row, but different column
            elif new_cell.j == cell.j:
                bottommost_tiling_dict[(new_cell.i, new_cell.j + 0.5)] = new_block
                bottommost_tiling_dict[(new_cell.i, new_cell.j - 0.5)] = new_block

            # different row and column
            else:
                bottommost_tiling_dict[new_cell] = new_block

        bottommost_tiling = Tiling(bottommost_tiling_dict)

        yield EquivalenceStrategy( "Inserting the bottom most point in to the cell " + str(cell), bottommost_tiling )


def all_equivalent_leftmost_column_placements(tiling, **kwargs):
    for col in range(tiling.dimensions.i):
        if len(tiling.get_col(col)) != 1:
            continue

        cell, block = tiling.get_col(col)[0]

        if not isinstance(block, PositiveClass) or block is Block.point:
            # Row inelegible as it is not a PositiveClass
            continue

        if any( sum(1 for _, row_block in tiling.get_row(cell.j)
               if isinstance(row_block, PositiveClass)
               or row_block is Block.point) != 1 for cell, _ in tiling.get_col(col) ):
            # Col ineligible because there is a cell that is not
            # the sole non-class cell in its respective row
            continue

        if block is PositiveClass(Block.decreasing):
            for strategy in all_maximum_decreasing( tiling, cell ):
                yield strategy
            continue

        if block is PositiveClass(Block.increasing):
            for strategy in all_minimum_increasing( tiling, cell ):
                yield strategy
            continue

        if block is PositiveClass(Block.point_or_empty):
            for strategy in all_unique_point_or_empty( tiling, cell ):
                yield strategy
            continue

        leftmost_tiling_dict = {}

        for new_cell, new_block in tiling:
            if new_cell.i == cell.i:
                # same cell
                if new_cell.j == cell.j:
                    perm_class = new_block.perm_class
                    leftmost_tiling_dict[(cell.i + 0.5, cell.j + 0.5)] = perm_class
                    leftmost_tiling_dict[(cell.i + 0.5, cell.j - 0.5)] = perm_class
                    leftmost_tiling_dict[new_cell] = Block.point

                # same column, but different row
                else:
                    leftmost_tiling_dict[(new_cell.i + 0.5, new_cell.j)] = new_block
                    leftmost_tiling_dict[(new_cell.i - 0.5, new_cell.j)] = new_block

            # same row, but different column
            elif new_cell.j == cell.j:
                leftmost_tiling_dict[(new_cell.i, new_cell.j + 0.5)] = new_block
                leftmost_tiling_dict[(new_cell.i, new_cell.j - 0.5)] = new_block

            # different row and column
            else:
                leftmost_tiling_dict[new_cell] = new_block

        leftmost_tiling = Tiling(leftmost_tiling_dict)

        yield EquivalenceStrategy( "Inserting the left most point in to the cell " + str(cell), leftmost_tiling )
