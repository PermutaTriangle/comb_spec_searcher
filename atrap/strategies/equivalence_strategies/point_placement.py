
from grids import Block
from grids import PositiveClass
from grids import Tiling

from .equivalence_class import EquivalenceStrategy


def point_separation(tiling, **kwargs):

    for cell, block in tiling.non_points:
        if not isinstance(block, PositiveClass):
            continue

        hor_split = True
        vert_split = True

        if sum(1 for _, col_block in tiling.get_col(cell.i)) != 1:
            # Cell ineligible because cell is not the sole non-class cell
            # in its respective col
            hor_split = False

        if sum(1 for _, row_block in tiling.get_row(cell.j)) != 1:
             # Cell ineligible because cell is not the sole non-class cell
             # in its respective row
            vert_split = False

        # print("tiling is:")
        # print(tiling)
        # print("H:",hor_split,"\tV:",vert_split)

        topmost_tiling_dict = dict(tiling)
        bottommost_tiling_dict = dict(tiling)
        leftmost_tiling_dict = dict(tiling)
        rightmost_tiling_dict = dict(tiling)

        if vert_split:
            topmost_tiling_dict[cell] = block.perm_class
            topmost_tiling_dict[(cell.i, cell.j + 0.5)] = Block.point
            bottommost_tiling_dict[cell] = block.perm_class
            bottommost_tiling_dict[(cell.i, cell.j - 0.5)] = Block.point

            # print("T:")
            # print(Tiling( topmost_tiling_dict ))

            # print("B:")
            # print(Tiling( bottommost_tiling_dict ))

            yield EquivalenceStrategy( "Separting the topmost point from cell " + str(cell), Tiling( topmost_tiling_dict ))
            yield EquivalenceStrategy( "Separting the bottommost point from cell " + str(cell), Tiling( bottommost_tiling_dict ))

        if hor_split:
            leftmost_tiling_dict[cell] = block.perm_class
            leftmost_tiling_dict[(cell.i - 0.5, cell.j)] = Block.point
            rightmost_tiling_dict[cell] = block.perm_class
            rightmost_tiling_dict[(cell.i + 0.5, cell.j)] = Block.point

            # print("L:")
            # print(Tiling( leftmost_tiling_dict ))

            # print("R:")
            # print(Tiling( rightmost_tiling_dict ))

            yield EquivalenceStrategy( "Separting the leftmost point from cell " + str(cell), Tiling( leftmost_tiling_dict ))
            yield EquivalenceStrategy( "Separting the rightmost point from cell " + str(cell), Tiling( rightmost_tiling_dict ))


def all_point_placements(tiling, **kwargs):

    for cell, block in tiling.non_points:
        if not isinstance(block, PositiveClass):
            continue

        if sum(1 for _, col_block in tiling.get_col(cell.i)
               if isinstance(col_block, PositiveClass)
               or col_block is Block.point) != 1:
            # Cell ineligible because cell is not the sole non-class cell
            # in its respective col
            continue

        if sum(1 for _, row_block in tiling.get_row(cell.j)
               if isinstance(row_block, PositiveClass)
               or row_block is Block.point) != 1:
             # Cell ineligible because cell is not the sole non-class cell
             # in its respective row
            continue

        if block is PositiveClass( Block.decreasing ):
            for strategy in all_minimum_and_maximum_decreasing( tiling, cell ):
                yield strategy
            continue

        if block is PositiveClass( Block.increasing ):
            for strategy in all_minimum_and_maximum_increasing( tiling, cell ):
                yield strategy
            continue

        if block is PositiveClass( Block.point_or_empty ):
            for strategy in all_unique_point_or_empty( tiling, cell ):
                yield strategy
            continue

        topmost_tiling_dict = {}
        bottommost_tiling_dict = {}
        leftmost_tiling_dict = {}
        rightmost_tiling_dict = {}

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


                    leftmost_tiling_dict[(cell.i + 0.5, cell.j + 0.5)] = perm_class
                    leftmost_tiling_dict[(cell.i + 0.5, cell.j - 0.5)] = perm_class
                    leftmost_tiling_dict[new_cell] = Block.point

                    rightmost_tiling_dict[(cell.i - 0.5, cell.j + 0.5)] = perm_class
                    rightmost_tiling_dict[(cell.i - 0.5, cell.j - 0.5)] = perm_class
                    rightmost_tiling_dict[new_cell] = Block.point

                # same column, but different row
                else:
                    topmost_tiling_dict[(new_cell.i + 0.5, new_cell.j)] = new_block
                    topmost_tiling_dict[(new_cell.i - 0.5, new_cell.j)] = new_block

                    bottommost_tiling_dict[(new_cell.i + 0.5, new_cell.j)] = new_block
                    bottommost_tiling_dict[(new_cell.i - 0.5, new_cell.j)] = new_block

                    leftmost_tiling_dict[(new_cell.i + 0.5, new_cell.j)] = new_block
                    leftmost_tiling_dict[(new_cell.i - 0.5, new_cell.j)] = new_block

                    rightmost_tiling_dict[(new_cell.i + 0.5, new_cell.j)] = new_block
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

        yield EquivalenceStrategy( "Inserting the top most point in to the cell " + str(cell), topmost_tiling )
        yield EquivalenceStrategy( "Inserting the left most point in to the cell " + str(cell), leftmost_tiling )
        yield EquivalenceStrategy( "Inserting the bottom most point in to the cell " + str(cell), bottommost_tiling )
        yield EquivalenceStrategy( "Inserting the right most point in to the cell " + str(cell),  rightmost_tiling )

def all_minimum_decreasing( tiling, cell ):
    '''Assumes that the block in the cell is decreasing '''
    bottommost_tiling_dict = {}

    for new_cell, new_block in tiling:
        if new_cell.i == cell.i:
            # same cell
            if new_cell.j == cell.j:
                perm_class = new_block.perm_class

                bottommost_tiling_dict[(cell.i - 0.5, cell.j + 0.5)] = Block.decreasing
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

def all_maximum_decreasing( tiling, cell ):
    '''Assumes that the block in the cell is decreasing '''
    topmost_tiling_dict = {}

    for new_cell, new_block in tiling:
        if new_cell.i == cell.i:
            # same cell
            if new_cell.j == cell.j:
                perm_class = new_block.perm_class
                topmost_tiling_dict[(cell.i + 0.5, cell.j - 0.5)] = Block.decreasing
                topmost_tiling_dict[cell] = Block.point

            # same column, but different row
            else:
                topmost_tiling_dict[(new_cell.i + 0.5, new_cell.j)] = new_block
                topmost_tiling_dict[(new_cell.i - 0.5, new_cell.j)] = new_block

        # same row, but different column
        elif new_cell.j == cell.j:
            topmost_tiling_dict[(new_cell.i, new_cell.j + 0.5)] = new_block
            topmost_tiling_dict[(new_cell.i, new_cell.j - 0.5)] = new_block

        # different row and column
        else:
            topmost_tiling_dict[new_cell] = new_block

    topmost_tiling = Tiling(topmost_tiling_dict)

    yield EquivalenceStrategy( "Inserting the top most point in to the cell " + str(cell), topmost_tiling )

def all_minimum_and_maximum_decreasing( tiling, cell ):
    '''Assumes that the block in the cell is decreasing '''
    topmost_tiling_dict = {}
    bottommost_tiling_dict = {}

    for new_cell, new_block in tiling:
        if new_cell.i == cell.i:
            # same cell
            if new_cell.j == cell.j:
                perm_class = new_block.perm_class
                topmost_tiling_dict[(cell.i + 0.5, cell.j - 0.5)] = Block.decreasing
                topmost_tiling_dict[cell] = Block.point

                bottommost_tiling_dict[(cell.i - 0.5, cell.j + 0.5)] = Block.decreasing
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


def all_minimum_increasing( tiling, cell ):
    '''Assumes that the block in the cell is increasing '''
    bottommost_tiling_dict = {}

    for new_cell, new_block in tiling:
        if new_cell.i == cell.i:
            # same cell
            if new_cell.j == cell.j:
                perm_class = new_block.perm_class

                bottommost_tiling_dict[(cell.i + 0.5, cell.j + 0.5)] = Block.decreasing
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

def all_maximum_increasing( tiling, cell ):
    '''Assumes that the block in the cell is increasing '''
    topmost_tiling_dict = {}

    for new_cell, new_block in tiling:
        if new_cell.i == cell.i:
            # same cell
            if new_cell.j == cell.j:
                perm_class = new_block.perm_class
                topmost_tiling_dict[(cell.i - 0.5, cell.j - 0.5)] = Block.increasing
                topmost_tiling_dict[cell] = Block.point

            # same column, but different row
            else:
                topmost_tiling_dict[(new_cell.i + 0.5, new_cell.j)] = new_block
                topmost_tiling_dict[(new_cell.i - 0.5, new_cell.j)] = new_block

        # same row, but different column
        elif new_cell.j == cell.j:
            topmost_tiling_dict[(new_cell.i, new_cell.j + 0.5)] = new_block
            topmost_tiling_dict[(new_cell.i, new_cell.j - 0.5)] = new_block

        # different row and column
        else:
            topmost_tiling_dict[new_cell] = new_block

    topmost_tiling = Tiling(topmost_tiling_dict)

    yield EquivalenceStrategy( "Inserting the top most point in to the cell " + str(cell), topmost_tiling )


def all_minimum_and_maximum_increasing( tiling, cell ):
    '''Assumes that the block in the cell is increasing '''
    topmost_tiling_dict = {}
    bottommost_tiling_dict = {}

    for new_cell, new_block in tiling:
        if new_cell.i == cell.i:
            # same cell
            if new_cell.j == cell.j:
                perm_class = new_block.perm_class
                topmost_tiling_dict[(cell.i - 0.5, cell.j - 0.5)] = Block.increasing
                topmost_tiling_dict[cell] = Block.point

                bottommost_tiling_dict[(cell.i + 0.5, cell.j + 0.5)] = Block.increasing
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

def all_unique_point_or_empty( tiling, cell ):
    '''Assumes that the block in the cell is decreasing '''
    topmost_tiling_dict = {}

    for new_cell, new_block in tiling:
        if new_cell.i == cell.i:
            # same cell
            if new_cell.j == cell.j:
                perm_class = new_block.perm_class
                topmost_tiling_dict[cell] = Block.point

            # same column, but different row
            else:
                topmost_tiling_dict[(new_cell.i + 0.5, new_cell.j)] = new_block
                topmost_tiling_dict[(new_cell.i - 0.5, new_cell.j)] = new_block

        # same row, but different column
        elif new_cell.j == cell.j:
            topmost_tiling_dict[(new_cell.i, new_cell.j + 0.5)] = new_block
            topmost_tiling_dict[(new_cell.i, new_cell.j - 0.5)] = new_block

        # different row and column
        else:
            topmost_tiling_dict[new_cell] = new_block

    topmost_tiling = Tiling(topmost_tiling_dict)

    yield EquivalenceStrategy( "Placing the unique most point in to the cell " + str(cell), topmost_tiling )



def all_maximum_point_placements(tiling, **kwargs):

    for cell, block in tiling.non_points:
        if not isinstance(block, PositiveClass):
            continue

        if sum(1 for _, col_block in tiling.get_col(cell.i)
               if isinstance(col_block, PositiveClass)
               or col_block is Block.point) != 1:
            # Cell ineligible because cell is not the sole non-class cell
            # in its respective col
            continue

        if sum(1 for _, row_block in tiling.get_row(cell.j)
               if isinstance(row_block, PositiveClass)
               or row_block is Block.point) != 1:
             # Cell ineligible because cell is not the sole non-class cell
             # in its respective row
            continue

        if block is PositiveClass( Block.decreasing ):
            for strategy in all_maximum_decreasing( tiling, cell ):
                yield strategy
            continue

        if block is PositiveClass( Block.increasing ):
            for strategy in all_maximum_increasing( tiling, cell ):
                yield strategy
            continue

        if block is PositiveClass( Block.point_or_empty ):
            for strategy in all_unique_point_or_empty( tiling, cell ):
                yield strategy
            continue

        topmost_tiling_dict = {}

        for new_cell, new_block in tiling:
            if new_cell.i == cell.i:
                # same cell
                if new_cell.j == cell.j:
                    perm_class = new_block.perm_class
                    topmost_tiling_dict[(cell.i + 0.5, cell.j - 0.5)] = perm_class
                    topmost_tiling_dict[(cell.i - 0.5, cell.j - 0.5)] = perm_class
                    topmost_tiling_dict[cell] = Block.point

                # same column, but different row
                else:
                    topmost_tiling_dict[(new_cell.i + 0.5, new_cell.j)] = new_block
                    topmost_tiling_dict[(new_cell.i - 0.5, new_cell.j)] = new_block

            # same row, but different column
            elif new_cell.j == cell.j:
                topmost_tiling_dict[(new_cell.i, new_cell.j + 0.5)] = new_block
                topmost_tiling_dict[(new_cell.i, new_cell.j - 0.5)] = new_block

            # different row and column
            else:
                topmost_tiling_dict[new_cell] = new_block

        topmost_tiling = Tiling(topmost_tiling_dict)

        yield EquivalenceStrategy( "Inserting the maximum point in to the cell " + str(cell),  topmost_tiling )


def all_leftmost_point_placements(tiling, **kwargs):

    for cell, block in tiling.non_points:
        if not isinstance(block, PositiveClass):
            continue

        if sum(1 for _, col_block in tiling.get_col(cell.i)
               if isinstance(col_block, PositiveClass)
               or col_block is Block.point) != 1:
            # Cell ineligible because cell is not the sole non-class cell
            # in its respective col
            continue

        if sum(1 for _, row_block in tiling.get_row(cell.j)
               if isinstance(row_block, PositiveClass)
               or row_block is Block.point) != 1:
             # Cell ineligible because cell is not the sole non-class cell
             # in its respective row
            continue

        if block is PositiveClass( Block.decreasing ):
            for strategy in all_maximum_decreasing( tiling, cell ):
                yield strategy
            continue

        if block is PositiveClass( Block.increasing ):
            for strategy in all_minimum_increasing( tiling, cell ):
                yield strategy
            continue

        if block is PositiveClass( Block.point_or_empty ):
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
