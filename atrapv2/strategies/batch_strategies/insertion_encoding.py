"""The following strategies are used to mimic Regular Insertion Encoding."""

from grids import Tiling, PositiveClass, Block
from .batch_class import BatchStrategy


def insertion_encoding_row_placements(tiling, **kwargs):
    """Mimic regular insertion encoding."""

    if len(tiling) == 0:
        return
    if not isinstance(tiling, Tiling):
        raise TypeError("I expect a tiling!")
    for row in range(tiling.dimensions.j):

        if len(tiling.get_row(row)) == 1:
            if all( block is Block.point for _, block in tiling.get_row(row)):
                continue

        if any( not isinstance(block, PositiveClass) for _, block in tiling.get_row(row) ):
            # Row inelegible as some block is not a positive class
            continue

        if any( sum(1 for _, col_block in tiling.get_col(cell.i)
               if isinstance(col_block, PositiveClass)) != 1
                    for cell, _ in tiling.get_row(row) ):
            # Row ineligible because there is a cell that is not
            # the sole non-class cell in its respective col
            continue

        bottommost_tiling_dicts = [ [{} for _ in range(4)] for _ in tiling.get_row(row) ]
        topmost_tiling_dicts = [ [{} for _ in range(4)] for _ in tiling.get_row(row) ]
        # 0: fill, 1: left, 2: right, 3: middle

        for cell, block in tiling:
            """We will place this cell in all of the choices of minimum row"""

            for index, value in enumerate(tiling.get_row(row)):
                """The new minimum will be placed into column "index"""
                cell_being_placed, _ = value

                if cell.i == cell_being_placed.i:
                    if cell.j == cell_being_placed.j:
                        # same cell
                        for k in range(4):
                            bottommost_tiling_dicts[index][k][cell] = Block.point

                            topmost_tiling_dicts[index][k][cell] = Block.point

                        # if block is not Block.point:
                            # 0: fill, 1: left, 2: right, 3: middle

                        bottommost_tiling_dicts[index][1][(cell.i + 0.5, cell.j + 0.5)] = block
                        topmost_tiling_dicts[index][1][(cell.i + 0.5, cell.j - 0.5)] = block

                        bottommost_tiling_dicts[index][2][(cell.i - 0.5, cell.j + 0.5)] = block
                        topmost_tiling_dicts[index][2][(cell.i - 0.5, cell.j - 0.5)] = block


                        bottommost_tiling_dicts[index][3][(cell.i + 0.5, cell.j + 0.5)] = block
                        bottommost_tiling_dicts[index][3][(cell.i - 0.5, cell.j + 0.5)] = block
                        topmost_tiling_dicts[index][3][(cell.i + 0.5, cell.j - 0.5)] = block
                        topmost_tiling_dicts[index][3][(cell.i - 0.5, cell.j - 0.5)] = block
                    else:
                        # same column, different row
                        for k in range(4):
                            assert not isinstance(block, PositiveClass)
                            bottommost_tiling_dicts[index][k][(cell.i + 0.5, cell.j)] = block
                            bottommost_tiling_dicts[index][k][(cell.i - 0.5, cell.j)] = block
                            topmost_tiling_dicts[index][k][(cell.i + 0.5, cell.j)] = block
                            topmost_tiling_dicts[index][k][(cell.i - 0.5, cell.j)] = block
                else:
                    if cell.j == cell_being_placed.j:
                        # same row, different column
                        for k in range(4):
                            bottommost_tiling_dicts[index][k][(cell.i, cell.j + 0.5)] = block
                            topmost_tiling_dicts[index][k][(cell.i, cell.j - 0.5)] = block
                    else:
                        # different row and column
                        for k in range(4):
                            bottommost_tiling_dicts[index][k][cell] = block
                            topmost_tiling_dicts[index][k][cell] = block

        bottommost_tilings = [ Tiling(tiling_dict) for tiling_dicts in bottommost_tiling_dicts for tiling_dict in tiling_dicts  ]
        topmost_tilings = [ Tiling(tiling_dict) for tiling_dicts in topmost_tiling_dicts for tiling_dict in tiling_dicts  ]

        yield BatchStrategy("The insertion encoding minimum row placement using row {}".format(row), bottommost_tilings)
        yield BatchStrategy("The insertion encoding maximum row placement using row {}".format(row), topmost_tilings)

def minimum_insertion_encoding_row_placements(tiling, **kwargs):
    """Minimum row mimic regular insertion encoding."""

    if len(tiling) == 0:
        return
    if not isinstance(tiling, Tiling):
        raise TypeError("I expect a tiling!")
    for row in range(tiling.dimensions.j):

        if len(tiling.get_row(row)) == 1:
            if all( block is Block.point for _, block in tiling.get_row(row)):
                continue

        if any( not isinstance(block, PositiveClass) for _, block in tiling.get_row(row) ):
            # Row inelegible as some block is not a positive class
            continue

        if any( sum(1 for _, col_block in tiling.get_col(cell.i)
               if isinstance(col_block, PositiveClass)) != 1
                    for cell, _ in tiling.get_row(row) ):
            # Row ineligible because there is a cell that is not
            # the sole non-class cell in its respective col
            continue

        bottommost_tiling_dicts = [ [{} for _ in range(4)] for _ in tiling.get_row(row) ]
        # 0: fill, 1: left, 2: right, 3: middle

        for cell, block in tiling:
            """We will place this cell in all of the choices of minimum row"""

            for index, value in enumerate(tiling.get_row(row)):
                """The new minimum will be placed into column "index"""
                cell_being_placed, _ = value

                if cell.i == cell_being_placed.i:
                    if cell.j == cell_being_placed.j:
                        # same cell
                        for k in range(4):
                            bottommost_tiling_dicts[index][k][cell] = Block.point

                        # if block is not Block.point:
                            # 0: fill, 1: left, 2: right, 3: middle

                        bottommost_tiling_dicts[index][1][(cell.i + 0.5, cell.j + 0.5)] = block

                        bottommost_tiling_dicts[index][2][(cell.i - 0.5, cell.j + 0.5)] = block


                        bottommost_tiling_dicts[index][3][(cell.i + 0.5, cell.j + 0.5)] = block
                        bottommost_tiling_dicts[index][3][(cell.i - 0.5, cell.j + 0.5)] = block
                    else:
                        # same column, different row
                        for k in range(4):
                            assert not isinstance(block, PositiveClass)
                            bottommost_tiling_dicts[index][k][(cell.i + 0.5, cell.j)] = block
                            bottommost_tiling_dicts[index][k][(cell.i - 0.5, cell.j)] = block
                else:
                    if cell.j == cell_being_placed.j:
                        # same row, different column
                        for k in range(4):
                            bottommost_tiling_dicts[index][k][(cell.i, cell.j + 0.5)] = block
                    else:
                        # different row and column
                        for k in range(4):
                            bottommost_tiling_dicts[index][k][cell] = block

        bottommost_tilings = [ Tiling(tiling_dict) for tiling_dicts in bottommost_tiling_dicts for tiling_dict in tiling_dicts  ]

        yield BatchStrategy("The insertion encoding minimum row placement using row {}".format(row), bottommost_tilings)

def maximum_insertion_encoding_row_placements(tiling, **kwargs):
    """Maximum row regular insertion encoding."""

    if len(tiling) == 0:
        return
    if not isinstance(tiling, Tiling):
        raise TypeError("I expect a tiling!")
    for row in range(tiling.dimensions.j):

        if len(tiling.get_row(row)) == 1:
            if all( block is Block.point for _, block in tiling.get_row(row)):
                continue

        if any( not isinstance(block, PositiveClass) for _, block in tiling.get_row(row) ):
            # Row inelegible as some block is not a positive class
            continue

        if any( sum(1 for _, col_block in tiling.get_col(cell.i)
               if isinstance(col_block, PositiveClass)) != 1
                    for cell, _ in tiling.get_row(row) ):
            # Row ineligible because there is a cell that is not
            # the sole non-class cell in its respective col
            continue

        topmost_tiling_dicts = [ [{} for _ in range(4)] for _ in tiling.get_row(row) ]
        # 0: fill, 1: left, 2: right, 3: middle

        for cell, block in tiling:
            """We will place this cell in all of the choices of minimum row"""

            for index, value in enumerate(tiling.get_row(row)):
                """The new minimum will be placed into column "index"""
                cell_being_placed, _ = value

                if cell.i == cell_being_placed.i:
                    if cell.j == cell_being_placed.j:
                        # same cell
                        for k in range(4):
                            topmost_tiling_dicts[index][k][cell] = Block.point

                        # if block is not Block.point:
                            # 0: fill, 1: left, 2: right, 3: middle

                        topmost_tiling_dicts[index][1][(cell.i + 0.5, cell.j - 0.5)] = block

                        topmost_tiling_dicts[index][2][(cell.i - 0.5, cell.j - 0.5)] = block


                        topmost_tiling_dicts[index][3][(cell.i + 0.5, cell.j - 0.5)] = block
                        topmost_tiling_dicts[index][3][(cell.i - 0.5, cell.j - 0.5)] = block
                    else:
                        # same column, different row
                        for k in range(4):
                            topmost_tiling_dicts[index][k][(cell.i + 0.5, cell.j)] = block
                            topmost_tiling_dicts[index][k][(cell.i - 0.5, cell.j)] = block
                else:
                    if cell.j == cell_being_placed.j:
                        # same row, different column
                        for k in range(4):
                            topmost_tiling_dicts[index][k][(cell.i, cell.j - 0.5)] = block
                    else:
                        # different row and column
                        for k in range(4):
                            topmost_tiling_dicts[index][k][cell] = block

        topmost_tilings = [ Tiling(tiling_dict) for tiling_dicts in topmost_tiling_dicts for tiling_dict in tiling_dicts  ]

        yield BatchStrategy("The insertion encoding maximum row placement using row {}".format(row), topmost_tilings)

def insertion_encoding_column_placements(tiling, **kwargs):
    """Mimic regular insertion encoding."""

    if len(tiling) == 0:
        return
    if not isinstance(tiling, Tiling):
        raise TypeError("I expect a tiling!")
    for col in range(tiling.dimensions.i):

        if len(tiling.get_col(col)) == 1:
            if all( block is Block.point for _, block in tiling.get_col(col)):
                continue

        if any( not isinstance(block, PositiveClass) for _, block in tiling.get_col(col) ):
            # Row inelegible as some block is not a positive class
            continue

        if any( sum(1 for _, row_block in tiling.get_row(cell.j)
               if isinstance(row_block, PositiveClass)) != 1
                    for cell, _ in tiling.get_col(col) ):
            # Col ineligible because there is a cell that is not
            # the sole non-class cell in its respective row
            continue

        leftmost_tiling_dicts = [ [{} for _ in range(4)] for _ in tiling.get_col(col) ]
        rightmost_tiling_dicts = [ [{} for _ in range(4)] for _ in tiling.get_col(col) ]
        # 0: fill, 1: left, 2: right, 3: middle

        for cell, block in tiling:
            """We will place this cell in all of the choices of minimum row"""

            for index, value in enumerate(tiling.get_col(col)):
                """The new minimum will be placed into column "index"""
                cell_being_placed, _ = value

                if cell.i == cell_being_placed.i:
                    if cell.j == cell_being_placed.j:
                        # same cell
                        for k in range(4):
                            leftmost_tiling_dicts[index][k][cell] = Block.point

                            rightmost_tiling_dicts[index][k][cell] = Block.point

                        # if block is not Block.point:
                            # 0: fill, 1: left, 2: right, 3: middle

                        leftmost_tiling_dicts[index][1][(cell.i + 0.5, cell.j - 0.5)] = block
                        rightmost_tiling_dicts[index][1][(cell.i - 0.5, cell.j - 0.5)] = block

                        leftmost_tiling_dicts[index][2][(cell.i + 0.5, cell.j + 0.5)] = block
                        rightmost_tiling_dicts[index][2][(cell.i - 0.5, cell.j + 0.5)] = block


                        leftmost_tiling_dicts[index][3][(cell.i + 0.5, cell.j + 0.5)] = block
                        leftmost_tiling_dicts[index][3][(cell.i + 0.5, cell.j - 0.5)] = block
                        rightmost_tiling_dicts[index][3][(cell.i - 0.5, cell.j + 0.5)] = block
                        rightmost_tiling_dicts[index][3][(cell.i - 0.5, cell.j - 0.5)] = block
                    else:
                        # same column, different row
                        for k in range(4):
                            leftmost_tiling_dicts[index][k][(cell.i + 0.5, cell.j)] = block
                            rightmost_tiling_dicts[index][k][(cell.i - 0.5, cell.j)] = block
                else:
                    if cell.j == cell_being_placed.j:
                        # same row, different column
                        for k in range(4):
                            assert not isinstance(block, PositiveClass)
                            leftmost_tiling_dicts[index][k][(cell.i, cell.j + 0.5)] = block
                            leftmost_tiling_dicts[index][k][(cell.i, cell.j - 0.5)] = block
                            rightmost_tiling_dicts[index][k][(cell.i, cell.j + 0.5)] = block
                            rightmost_tiling_dicts[index][k][(cell.i, cell.j - 0.5)] = block

                    else:
                        # different row and column
                        for k in range(4):
                            leftmost_tiling_dicts[index][k][cell] = block
                            rightmost_tiling_dicts[index][k][cell] = block

        leftmost_tilings = [ Tiling(tiling_dict) for tiling_dicts in leftmost_tiling_dicts for tiling_dict in tiling_dicts  ]
        rightmost_tilings = [ Tiling(tiling_dict) for tiling_dicts in rightmost_tiling_dicts for tiling_dict in tiling_dicts  ]

        yield BatchStrategy("The insertion encoding leftmost column placement using column {}".format(col), leftmost_tilings)
        yield BatchStrategy("The insertion encoding rightmost column placement using column {}".format(col), rightmost_tilings)

def leftmost_insertion_encoding_column_placements(tiling, **kwargs):
    """Mimic regular insertion encoding."""

    if len(tiling) == 0:
        return
    if not isinstance(tiling, Tiling):
        raise TypeError("I expect a tiling!")
    for col in range(tiling.dimensions.i):

        if len(tiling.get_col(col)) == 1:
            if all( block is Block.point for _, block in tiling.get_col(col)):
                continue

        if any( not isinstance(block, PositiveClass) for _, block in tiling.get_col(col) ):
            # Row inelegible as some block is not a positive class
            continue

        if any( sum(1 for _, row_block in tiling.get_row(cell.j)
               if isinstance(row_block, PositiveClass)) != 1
                    for cell, _ in tiling.get_col(col) ):
            # Col ineligible because there is a cell that is not
            # the sole non-class cell in its respective row
            continue

        leftmost_tiling_dicts = [ [{} for _ in range(4)] for _ in tiling.get_col(col) ]
        # 0: fill, 1: left, 2: right, 3: middle

        for cell, block in tiling:
            """We will place this cell in all of the choices of minimum row"""

            for index, value in enumerate(tiling.get_col(col)):
                """The new minimum will be placed into column "index"""
                cell_being_placed, _ = value

                if cell.i == cell_being_placed.i:
                    if cell.j == cell_being_placed.j:
                        # same cell
                        for k in range(4):
                            leftmost_tiling_dicts[index][k][cell] = Block.point

                        # if block is not Block.point:
                            # 0: fill, 1: left, 2: right, 3: middle

                        leftmost_tiling_dicts[index][1][(cell.i + 0.5, cell.j - 0.5)] = block

                        leftmost_tiling_dicts[index][2][(cell.i + 0.5, cell.j + 0.5)] = block


                        leftmost_tiling_dicts[index][3][(cell.i + 0.5, cell.j + 0.5)] = block
                        leftmost_tiling_dicts[index][3][(cell.i + 0.5, cell.j - 0.5)] = block
                    else:
                        # same column, different row
                        for k in range(4):
                            leftmost_tiling_dicts[index][k][(cell.i + 0.5, cell.j)] = block
                else:
                    if cell.j == cell_being_placed.j:
                        # same row, different column
                        for k in range(4):
                            assert not isinstance(block, PositiveClass)
                            leftmost_tiling_dicts[index][k][(cell.i, cell.j + 0.5)] = block
                            leftmost_tiling_dicts[index][k][(cell.i, cell.j - 0.5)] = block

                    else:
                        # different row and column
                        for k in range(4):
                            leftmost_tiling_dicts[index][k][cell] = block

        leftmost_tilings = [ Tiling(tiling_dict) for tiling_dicts in leftmost_tiling_dicts for tiling_dict in tiling_dicts  ]

        yield BatchStrategy("The insertion encoding leftmost column placement using column {}".format(col), leftmost_tilings)


def rightmost_insertion_encoding_column_placements(tiling, **kwargs):
    """Mimic regular insertion encoding."""

    if len(tiling) == 0:
        return
    if not isinstance(tiling, Tiling):
        raise TypeError("I expect a tiling!")
    for col in range(tiling.dimensions.i):

        if len(tiling.get_col(col)) == 1:
            if all( block is Block.point for _, block in tiling.get_col(col)):
                continue

        if any( not isinstance(block, PositiveClass) for _, block in tiling.get_col(col) ):
            # Row inelegible as some block is not a positive class
            continue

        if any( sum(1 for _, row_block in tiling.get_row(cell.j)
               if isinstance(row_block, PositiveClass)) != 1
                    for cell, _ in tiling.get_col(col) ):
            # Col ineligible because there is a cell that is not
            # the sole non-class cell in its respective row
            continue

        rightmost_tiling_dicts = [ [{} for _ in range(4)] for _ in tiling.get_col(col) ]
        # 0: fill, 1: left, 2: right, 3: middle

        for cell, block in tiling:
            """We will place this cell in all of the choices of minimum row"""

            for index, value in enumerate(tiling.get_col(col)):
                """The new minimum will be placed into column "index"""
                cell_being_placed, _ = value

                if cell.i == cell_being_placed.i:
                    if cell.j == cell_being_placed.j:
                        # same cell
                        for k in range(4):
                            rightmost_tiling_dicts[index][k][cell] = Block.point

                        # if block is not Block.point:
                            # 0: fill, 1: left, 2: right, 3: middle

                        rightmost_tiling_dicts[index][1][(cell.i - 0.5, cell.j - 0.5)] = block

                        rightmost_tiling_dicts[index][2][(cell.i - 0.5, cell.j + 0.5)] = block

                        rightmost_tiling_dicts[index][3][(cell.i - 0.5, cell.j + 0.5)] = block
                        rightmost_tiling_dicts[index][3][(cell.i - 0.5, cell.j - 0.5)] = block
                    else:
                        # same column, different row
                        for k in range(4):
                            rightmost_tiling_dicts[index][k][(cell.i - 0.5, cell.j)] = block
                else:
                    if cell.j == cell_being_placed.j:
                        # same row, different column
                        for k in range(4):
                            assert not isinstance(block, PositiveClass)
                            rightmost_tiling_dicts[index][k][(cell.i, cell.j + 0.5)] = block
                            rightmost_tiling_dicts[index][k][(cell.i, cell.j - 0.5)] = block

                    else:
                        # different row and column
                        for k in range(4):
                            rightmost_tiling_dicts[index][k][cell] = block

        rightmost_tilings = [ Tiling(tiling_dict) for tiling_dicts in rightmost_tiling_dicts for tiling_dict in tiling_dicts  ]

        yield BatchStrategy("The insertion encoding rightmost column placement using column {}".format(col), rightmost_tilings)
