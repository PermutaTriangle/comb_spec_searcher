from grids import Tiling, Block, PositiveClass

from .equivalence_class import EquivalenceStrategy
from .point_placement import all_unique_point_or_empty, all_maximum_point_placements, all_maximum_point_placements

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

        if block is Block.decreasing:
            for strategy in all_minimum_and_maximum_decreasing( tiling, cell ):
                yield strategy
            continue

        if block is Block.increasing:
            for strategy in all_minimum_and_maximum_increasing( tiling, cell ):
                yield strategy
            continue

        if block is Block.point_or_empty:
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

def all_equivalent_minimum_row_placements(tiling, **kwargs):
    for row in range(tiling.dimensions.j):
        if len(tiling.get_row(row)) != 1:
            continue

        if all( block is Block.point for _, block in tiling.get_row(row) ):
            continue

        if any( not (block is Block.point or isinstance(block, PositiveClass)) for _, block in tiling.get_row(row) ):
            # Row inelegible as some block is not a point.
            continue

        if any( sum(1 for _, col_block in tiling.get_col(cell.i)
               if isinstance(col_block, PositiveClass)
               or col_block is Block.point) != 1 for cell, _ in tiling.get_row(row) ):
            # Row ineligible because there is a cell that is not
            # the sole non-class cell in its respective col
            continue

        bottommost_tiling_dicts = [ {} for _ in tiling.get_row(row) ]
        for cell, block in tiling:

            for index, value in enumerate(tiling.get_row(row)):
                cell_being_placed, _ = value

                if cell.i == cell_being_placed.i:
                    if cell.j == cell_being_placed.j:
                        # same cell

                        bottommost_tiling_dicts[index][cell] = Block.point

                        if isinstance(block, PositiveClass):
                            perm_class = block.perm_class
                            bottommost_tiling_dicts[index][(cell.i - 0.5, cell.j + 0.5)] = perm_class
                            bottommost_tiling_dicts[index][(cell.i + 0.5, cell.j + 0.5)] = perm_class
                    else:
                        # same column, different row
                        bottommost_tiling_dicts[index][(cell.i + 0.5, cell.j)] = block
                        bottommost_tiling_dicts[index][(cell.i - 0.5, cell.j)] = block
                elif cell.j == cell_being_placed.j:
                    #same row, different column
                    bottommost_tiling_dicts[index][(cell.i, cell.j + 0.5)] = block
                else:
                    # different row and different column
                    bottommost_tiling_dicts[index][cell] = block

        bottommost_tilings = [ Tiling(tiling_dict) for tiling_dict in bottommost_tiling_dicts]
        assert len(bottommost_tilings) == 1
        bottommost_formal_step = "Placing the minimum point into row {}".format(row)
        yield EquivalenceStrategy( bottommost_formal_step, bottommost_tilings[0] )

def all_equivalent_column_placements(tiling, **kwargs):
    for col in range(tiling.dimensions.i):
        if len(tiling.get_col(col)) != 1:
            continue

        if any( not (block is Block.point or isinstance(block, PositiveClass)) for _, block in tiling.get_col(col) ):
            # Col inelegible as some block is not a point.
            continue

        if any( sum(1 for _, row_block in tiling.get_row(cell.j)
               if isinstance(row_block, PositiveClass)
               or row_block is Block.point) != 1 for cell, _ in tiling.get_col(col) ):
            # Col ineligible because there is a cell that is not
            # the sole non-class cell in its respective row
            continue

        leftmost_tiling_dicts = [ {} for _ in tiling.get_col(col) ]
        rightmost_tiling_dicts = [ {} for _ in tiling.get_col(col) ]
        for cell, block in tiling:

            for index, value in enumerate(tiling.get_col(col)):
                cell_being_placed, _ = value

                if cell.j == cell_being_placed.j:
                    if cell.i == cell_being_placed.i:
                        # same cell

                        leftmost_tiling_dicts[index][cell] = Block.point
                        rightmost_tiling_dicts[index][cell] = Block.point

                        if isinstance(block, PositiveClass):
                            perm_class = block.perm_class
                            leftmost_tiling_dicts[index][(cell.i + 0.5, cell.j + 0.5)] = perm_class
                            rightmost_tiling_dicts[index][(cell.i + 0.5, cell.j - 0.5)] = perm_class
                            leftmost_tiling_dicts[index][(cell.i - 0.5, cell.j + 0.5)] = perm_class
                            rightmost_tiling_dicts[index][(cell.i - 0.5, cell.j - 0.5)] = perm_class
                    else:
                        # same row, different col
                        leftmost_tiling_dicts[index][(cell.i, cell.j + 0.5)] = block
                        leftmost_tiling_dicts[index][(cell.i, cell.j - 0.5)] = block
                        rightmost_tiling_dicts[index][(cell.i, cell.j + 0.5)] = block
                        rightmost_tiling_dicts[index][(cell.i, cell.j - 0.5)] = block
                elif cell.i == cell_being_placed.i:
                    #same col, different row
                    leftmost_tiling_dicts[index][(cell.i + 0.5, cell.j)] = block
                    rightmost_tiling_dicts[index][(cell.i - 0.5, cell.j)] = block
                else:
                    # different row and different column
                    leftmost_tiling_dicts[index][cell] = block
                    rightmost_tiling_dicts[index][cell] = block

        leftmost_tilings = [ Tiling(tiling_dict) for tiling_dict in leftmost_tiling_dicts]
        leftmost_formal_step = "Placing the leftmost point into column {}".format(col)
        yield EquivalenceStrategy( leftmost_formal_step, leftmost_tilings[0] )

        rightmost_tilings = [ Tiling(tiling_dict) for tiling_dict in rightmost_tiling_dicts ]
        rightmost_formal_step = "Placing the rightmost point into column {}".format(col)
        yield EquivalenceStrategy( rightmost_formal_step, rightmost_tilings[0] )

def all_equivalent_leftmost_column_placements(tiling, **kwargs):
    for col in range(tiling.dimensions.i):
        if len(tiling.get_col(col)) != 1:
            continue

        if any( not (block is Block.point or isinstance(block, PositiveClass)) for _, block in tiling.get_col(col) ):
            # Col inelegible as some block is not a point.
            continue

        if any( sum(1 for _, row_block in tiling.get_row(cell.j)
               if isinstance(row_block, PositiveClass)
               or row_block is Block.point) != 1 for cell, _ in tiling.get_col(col) ):
            # Col ineligible because there is a cell that is not
            # the sole non-class cell in its respective row
            continue

        leftmost_tiling_dicts = [ {} for _ in tiling.get_col(col) ]
        for cell, block in tiling:

            for index, value in enumerate(tiling.get_col(col)):
                cell_being_placed, _ = value

                if cell.j == cell_being_placed.j:
                    if cell.i == cell_being_placed.i:
                        # same cell

                        leftmost_tiling_dicts[index][cell] = Block.point

                        if isinstance(block, PositiveClass):
                            perm_class = block.perm_class
                            leftmost_tiling_dicts[index][(cell.i + 0.5, cell.j + 0.5)] = perm_class
                            leftmost_tiling_dicts[index][(cell.i - 0.5, cell.j + 0.5)] = perm_class
                    else:
                        # same row, different col
                        leftmost_tiling_dicts[index][(cell.i, cell.j + 0.5)] = block
                        leftmost_tiling_dicts[index][(cell.i, cell.j - 0.5)] = block
                elif cell.i == cell_being_placed.i:
                    #same col, different row
                    leftmost_tiling_dicts[index][(cell.i + 0.5, cell.j)] = block
                else:
                    # different row and different column
                    leftmost_tiling_dicts[index][cell] = block

        leftmost_tilings = [ Tiling(tiling_dict) for tiling_dict in leftmost_tiling_dicts]
        leftmost_formal_step = "Placing the leftmost point into column {}".format(col)
        yield EquivalenceStrategy( leftmost_formal_step, leftmost_tilings[0] )
