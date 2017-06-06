from grids import Tiling, Block, PositiveClass, Cell
from permuta import Av
from copy import copy

from .batch_class import BatchStrategy

PERFORM_INSERTION_ON_ROW_COL_OF_SIZE_1 = True

# doesn't quite make sense for finite classes??

def all_row_and_column_insertions(tiling, **kwargs):
    for strategy, tilings in all_row_insertions(tiling):
        if len(tilings) > 0:
            yield BatchStrategy( strategy, tilings )
    for strategy, tilings in all_col_insertions(tiling):
        if len(tilings) > 0:
            yield BatchStrategy( strategy, tilings )

def all_row_insertions(tiling):
    num_rows = tiling.dimensions[1]

    to_return = []

    for row_num in range(num_rows):
        min_row_size = 1 if PERFORM_INSERTION_ON_ROW_COL_OF_SIZE_1 else 2
        if len(tiling.get_row(row_num)) >= min_row_size:
            to_return.extend(row_insertions_at_row(tiling, row_num))

    return to_return

def all_col_insertions(tiling):
    num_cols = tiling.dimensions[0]

    to_return = []

    for col_num in range(num_cols):
        min_col_size = 1 if PERFORM_INSERTION_ON_ROW_COL_OF_SIZE_1 else 2
        if len(tiling.get_col(col_num)) >= min_col_size:
            to_return.extend(col_insertions_at_col(tiling, col_num))

    return to_return

def row_insertions_at_row(tiling, row_num):
    to_return = [topmost_row_insertion(tiling, row_num), bottommost_row_insertion(tiling, row_num)]
    return to_return


def col_insertions_at_col(tiling, col_num):
    to_return = [leftmost_col_insertion(tiling, col_num), rightmost_col_insertion(tiling, col_num)]
    return to_return


def topmost_row_insertion(tiling, row_num):

    tilings_to_return = []
    strategy = "insert topmost point into row "+str(row_num)

    # double check that the row is eligible
    min_row_size = 1 if PERFORM_INSERTION_ON_ROW_COL_OF_SIZE_1 else 2
    if len(tiling.get_row(row_num)) < min_row_size:
        return [strategy, []]

    row_cells = tiling.get_row(row_num)
    if min_row_size == 1 and len(row_cells) == 1 and row_cells[0][1] is Block.point:
        # all this does is return the same tiling, because the point is not moving above anything!
        return [strategy, []]

    template_tiling = Tiling({cell:block for (cell,block) in tiling if cell[1] != row_num})

    can_be_empty = all([not isinstance(block, PositiveClass) for (cell, block) in row_cells])
    if can_be_empty:
        tilings_to_return.append(Tiling(dict(template_tiling)))

    for cell, block in row_cells:
        tiling_in_progress = dict(tiling)
        # if isinstance(block, PositiveClass):
        if block is Block.point:
            tiling_in_progress.pop(cell)
            tiling_in_progress[Cell(cell[0], cell[1] + 0.5)] = Block.point
        else:
            tiling_in_progress[cell] = Av(block.basis)
            tiling_in_progress[Cell(cell[0], cell[1] + 0.5)] = Block.point
        tilings_to_return.append(Tiling(tiling_in_progress))

    if len(tilings_to_return) > 1:
        return [strategy, tilings_to_return]
    else:
        return [strategy, []]


def bottommost_row_insertion(tiling, row_num):

    tilings_to_return = []
    strategy = "insert bottommost point into row "+str(row_num)

    # double check that the row is eligible
    min_row_size = 1 if PERFORM_INSERTION_ON_ROW_COL_OF_SIZE_1 else 2
    if len(tiling.get_row(row_num)) < min_row_size:
        return [strategy, []]

    row_cells = tiling.get_row(row_num)
    if min_row_size == 1 and len(row_cells) == 1 and row_cells[0][1] is Block.point:
        # all this does is return the same tiling, because the point is not moving above anything!
        return [strategy, []]

    template_tiling = Tiling({cell:block for (cell,block) in tiling if cell[1] != row_num})

    can_be_empty = all([not isinstance(block, PositiveClass) for (cell, block) in row_cells])
    if can_be_empty:
        tilings_to_return.append(Tiling(dict(template_tiling)))

    for cell, block in row_cells:
        tiling_in_progress = dict(tiling)
        # if isinstance(block, PositiveClass):
        if block is Block.point:
            tiling_in_progress.pop(cell)
            tiling_in_progress[Cell(cell[0], cell[1] - 0.5)] = Block.point
        else:
            tiling_in_progress[cell] = Av(block.basis)
            tiling_in_progress[Cell(cell[0], cell[1] - 0.5)] = Block.point
        tilings_to_return.append(Tiling(tiling_in_progress))

    if len(tilings_to_return) > 1:
        return [strategy, tilings_to_return]
    else:
        return [strategy, []]


def leftmost_col_insertion(tiling, col_num):

    tilings_to_return = []
    strategy = "insert leftmost point into col "+str(col_num)

    # double check that the col is eligible
    min_col_size = 1 if PERFORM_INSERTION_ON_ROW_COL_OF_SIZE_1 else 2
    if len(tiling.get_col(col_num)) < min_col_size:
        return [strategy, []]

    col_cells = tiling.get_col(col_num)
    if min_col_size == 1 and len(col_cells) == 1 and col_cells[0][1] is Block.point:
        # all this does is return the same tiling, because the point is not moving above anything!
        return [strategy, []]

    template_tiling = Tiling({cell:block for (cell,block) in tiling if cell[0] != col_num})

    can_be_empty = all([not isinstance(block, PositiveClass) for (cell, block) in col_cells])
    if can_be_empty:
        tilings_to_return.append(Tiling(dict(template_tiling)))

    for cell, block in col_cells:
        tiling_in_progress = dict(tiling)
        # if isinstance(block, PositiveClass):
        if block is Block.point:
            tiling_in_progress.pop(cell)
            tiling_in_progress[Cell(cell[0] - 0.5, cell[1])] = Block.point
        else:
            tiling_in_progress[cell] = Av(block.basis)
            tiling_in_progress[Cell(cell[0] - 0.5, cell[1])] = Block.point
        tilings_to_return.append(Tiling(tiling_in_progress))

    if len(tilings_to_return) > 1:
        return [strategy, tilings_to_return]
    else:
        return [strategy, []]



def rightmost_col_insertion(tiling, col_num):

    tilings_to_return = []
    strategy = "insert rightmost point into col "+str(col_num)

    # double check that the col is eligible
    min_col_size = 1 if PERFORM_INSERTION_ON_ROW_COL_OF_SIZE_1 else 2
    if len(tiling.get_col(col_num)) < min_col_size:
        return [strategy, []]

    col_cells = tiling.get_col(col_num)
    if min_col_size == 1 and len(col_cells) == 1 and col_cells[0][1] is Block.point:
        # all this does is return the same tiling, because the point is not moving above anything!
        return [strategy, []]

    template_tiling = Tiling({cell:block for (cell,block) in tiling if cell[0] != col_num})

    can_be_empty = all([not isinstance(block, PositiveClass) for (cell, block) in col_cells])
    if can_be_empty:
        tilings_to_return.append(Tiling(dict(template_tiling)))

    for cell, block in col_cells:
        tiling_in_progress = dict(tiling)
        # if isinstance(block, PositiveClass):
        if block is Block.point:
            tiling_in_progress.pop(cell)
            tiling_in_progress[Cell(cell[0] + 0.5, cell[1])] = Block.point
        else:
            tiling_in_progress[cell] = Av(block.basis)
            tiling_in_progress[Cell(cell[0] + 0.5, cell[1])] = Block.point
        tilings_to_return.append(Tiling(tiling_in_progress))

    if len(tilings_to_return) > 1:
        return [strategy, tilings_to_return]
    else:
        return [strategy, []]




    
    









