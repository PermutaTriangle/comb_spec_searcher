
from grids import Tiling, Block, PositiveClass, Cell
from permuta import Av
from copy import copy

from comb_spec_searcher import EquivalenceStrategy

def all_equivalent_row_and_column_insertions(tiling, **kwargs):
    for strategy, tilings in all_equivalent_row_insertions(tiling):
        if len(tilings) > 0:
            yield EquivalenceStrategy( strategy, tilings )
    for strategy, tilings in all_equivalent_col_insertions(tiling):
        if len(tilings) > 0:
            yield EquivalenceStrategy( strategy, tilings )

def all_equivalent_row_insertions(tiling):
    num_rows = tiling.dimensions[1]

    to_return = []

    for row_num in range(num_rows):
        if len(tiling.get_row(row_num)) == 1:
            to_return.extend(equivalent_row_insertions_at_row(tiling, row_num))

    return to_return

def all_equivalent_col_insertions(tiling):
    num_cols = tiling.dimensions[0]

    to_return = []

    for col_num in range(num_cols):
        if len(tiling.get_col(col_num)) == 1:
            to_return.extend(equivalent_col_insertions_at_col(tiling, col_num))

    return to_return

def equivalent_row_insertions_at_row(tiling, row_num):
    to_return = [equivalent_topmost_row_insertion(tiling, row_num), equivalent_bottommost_row_insertion(tiling, row_num)]
    return to_return

def equivalent_col_insertions_at_col(tiling, col_num):
    to_return = [equivalent_leftmost_col_insertion(tiling, col_num), equivalent_rightmost_col_insertion(tiling, col_num)]
    return to_return


def equivalent_topmost_row_insertion(tiling, row_num):

    tilings_to_return = []
    strategy = "equivalent insert topmost point into row "+str(row_num)

    # double check eligibility
    row_cells = tiling.get_row(row_num)
    if len(row_cells) != 1 or row_cells[0][1] is Block.point:
        return [strategy, []]
    if not isinstance(row_cells[0][1], PositiveClass):
        return [strategy, []]

    for cell, block in row_cells:
        tiling_in_progress = dict(tiling)
        # if isinstance(block, PositiveClass):
        if block is Block.point:
            tiling_in_progress.pop(cell)
            tiling_in_progress[Cell(cell[0], cell[1]+0.5)] = Block.point
        else:
            tiling_in_progress[cell] = Av(block.basis)
            tiling_in_progress[Cell(cell[0], cell[1] + 0.5)] = Block.point
        tilings_to_return.append(Tiling(tiling_in_progress))

    if len(tilings_to_return) == 1:
        # print(tilings_to_return)
        return [strategy, tilings_to_return[0]]
    else:
        print("You've done something terrible in equivalent_row_column_insertion")
        return [strategy, []]


def equivalent_bottommost_row_insertion(tiling, row_num):

    tilings_to_return = []
    strategy = "equivalent insert bottommost point into row "+str(row_num)

    # double check eligibility
    row_cells = tiling.get_row(row_num)
    if len(row_cells) != 1 or row_cells[0][1] is Block.point:
        return [strategy, []]
    if not isinstance(row_cells[0][1], PositiveClass):
        return [strategy, []]

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

    if len(tilings_to_return) == 1:
        # print(tilings_to_return)
        return [strategy, tilings_to_return[0]]
    else:
        print("You've done something terrible in equivalent_row_column_insertion")
        return [strategy, []]


def equivalent_leftmost_col_insertion(tiling, col_num):

    tilings_to_return = []
    strategy = "equivalent insert leftmost point into col "+str(col_num)

    # double check eligibility
    col_cells = tiling.get_col(col_num)
    if len(col_cells) != 1 or col_cells[0][1] is Block.point:
        return [strategy, []]
    if not isinstance(col_cells[0][1], PositiveClass):
        return [strategy, []]

    for cell, block in col_cells:
        tiling_in_progress = dict(tiling)
        # if isinstance(block, PositiveClass):
        if block is Block.point:
            tiling_in_progress.pop(cell)
            tiling_in_progress[Cell(cell[0]-0.5, cell[1])] = Block.point
        else:
            tiling_in_progress[cell] = Av(block.basis)
            tiling_in_progress[Cell(cell[0]-0.5, cell[1])] = Block.point
        tilings_to_return.append(Tiling(tiling_in_progress))

    if len(tilings_to_return) == 1:
        # print(tilings_to_return)
        return [strategy, tilings_to_return[0]]
    else:
        print("You've done something terrible in equivalent_row_column_insertion")
        return [strategy, []]


def equivalent_rightmost_col_insertion(tiling, col_num):

    tilings_to_return = []
    strategy = "equivalent insert leftmost point into col "+str(col_num)

    # double check eligibility
    col_cells = tiling.get_col(col_num)
    if len(col_cells) != 1 or col_cells[0][1] is Block.point:
        return [strategy, []]
    if not isinstance(col_cells[0][1], PositiveClass):
        return [strategy, []]

    for cell, block in col_cells:
        tiling_in_progress = dict(tiling)
        # if isinstance(block, PositiveClass):
        if block is Block.point:
            tiling_in_progress.pop(cell)
            tiling_in_progress[Cell(cell[0]+0.5, cell[1])] = Block.point
        else:
            tiling_in_progress[cell] = Av(block.basis)
            tiling_in_progress[Cell(cell[0]+0.5, cell[1])] = Block.point
        tilings_to_return.append(Tiling(tiling_in_progress))

    if len(tilings_to_return) == 1:
        # print(tilings_to_return)
        return [strategy, tilings_to_return[0]]
    else:
        print("You've done something terrible in equivalent_row_column_insertion")
        return [strategy, []]
