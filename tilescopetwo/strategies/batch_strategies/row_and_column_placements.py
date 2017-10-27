from comb_spec_searcher import BatchStrategy
from grids_two import Tiling
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST  # , DIRS


def row_placements(tiling, all_positive_in_row=True, **kwargs):
    # print("")
    # print("The tiling:")
    # print(tiling.to_old_tiling())
    # print(tiling)
    # print("Gives the strategies:")
    for i in range(tiling.dimensions[1]):
        row = tiling.cells_in_row(i)
        if all_positive_in_row:
            if not all(c in tiling.positive_cells or c in tiling.point_cells for c in row):
                continue
        if len(row) == 1 and row[0] in tiling.point_cells:
            continue
        if not all(tiling.only_positive_in_col(c) for c in row):
            continue
        north = []
        south = []
        for cell in row:
            if cell not in tiling.possibly_empty:
                north.append(row_place(tiling, cell, DIR_NORTH))
                south.append(row_place(tiling, cell, DIR_SOUTH))
        if not north:
            continue
        # print("-----")
        # for t in north:
        #     print(t.to_old_tiling())
        #     print(t.is_empty())
        #     print(t)
        # print("-----")
        # for t in south:
        #     print(t.to_old_tiling())
        #     print(t.is_empty())
        #     print(t)
        yield BatchStrategy(formal_step="Place maximum into row {}".format(i), tilings=north)
        yield BatchStrategy(formal_step="Place minimum into row {}".format(i), tilings=south)
    # print("END")


def row_place(tiling, cell, direction):
    positive_cells = []
    point_cells = []
    possibly_empty = []
    empty_cells = []
    col, row = cell

    for old_cell in tiling.positive_cells:
        x, y = old_cell
        if x == col:
            if y == row:
                point_cells.append((x + 1, y + 1))
                if direction == DIR_NORTH:
                    possibly_empty.append((x, y))
                    possibly_empty.append((x + 2, y))
                elif direction == DIR_SOUTH:
                    possibly_empty.append((x, y + 2))
                    possibly_empty.append((x + 2, y + 2))
            else:
                raise ValueError("Can't row place due to positive_cell in column {}.".format(col))
        else:
            if x > col:
                x += 2
            if y == row:
                if direction == DIR_SOUTH:
                    positive_cells.append((x, y + 2))
                    empty_cells.append((x, y))
                elif direction == DIR_NORTH:
                    positive_cells.append((x, y))
                    empty_cells.append((x, y + 2))
                else:
                    raise ValueError("Only row place north or south.")
            else:
                if y > row:
                    y += 2
                positive_cells.append((x, y))

    for old_cell in tiling.possibly_empty:
        x, y = old_cell
        if x == col:
            if y == row:
                raise ValueError("Can't insert into possibly_empty.")
            else:
                if y > row:
                    y += 2
                possibly_empty.append((x, y))
                possibly_empty.append((x + 2, y))
        else:
            if x > col:
                x += 2
            if y == row:
                possibly_empty.append((x, y))
                possibly_empty.append((x, y + 2))
            else:
                if y > row:
                    y += 2
                possibly_empty.append((x, y))

    for old_cell in tiling.point_cells:
        x, y = old_cell
        if x == col:
            if y == row:
                point_cells.append((x + 1, y + 1))
                if direction == DIR_NORTH:
                    empty_cells.append((x, y))
                    empty_cells.append((x + 2, y))
                elif direction == DIR_SOUTH:
                    empty_cells.append((x, y + 2))
                    empty_cells.append((x + 2, y + 2))
            else:
                raise ValueError("Can't row place due to positive cell in column {}.".format(col))
        else:
            if x > col:
                x += 2
            if y == row:
                if direction == DIR_SOUTH:
                    point_cells.append((x, y + 2))
                    empty_cells.append((x, y))
                elif direction == DIR_NORTH:
                    point_cells.append((x, y))
                    empty_cells.append((x, y + 2))
                else:
                    raise ValueError("Only row place north or south.")
            else:
                if y > row:
                    y += 2
                point_cells.append((x, y))



    obstructions = []
    for ob in tiling:
        obstructions.extend([o for o in ob.place_point(cell, direction)
                             if not any(o.occupies(c) for c in empty_cells)])
    # print("points:", point_cells)
    # print("positive:", positive_cells)
    # print("possibly_empty:", possibly_empty)
    # print("empty_cells:", empty_cells)
    # print(Tiling(point_cells=point_cells, positive_cells=positive_cells,
    #               possibly_empty=possibly_empty, obstructions=obstructions).to_old_tiling())
    return Tiling(point_cells=point_cells, positive_cells=positive_cells,
                  possibly_empty=possibly_empty, obstructions=obstructions)


def col_placements(tiling, all_positive_in_col=True, **kwargs):
    # print("")
    # print("The tiling:")
    # print(tiling.to_old_tiling())
    # print(tiling)
    # print("Gives the strategies:")
    for i in range(tiling.dimensions[0]):
        col = tiling.cells_in_col(i)
        if all_positive_in_col:
            if not all(c in tiling.positive_cells or c in tiling.point_cells for c in col):
                continue
        if len(col) == 1 and col[0] in tiling.point_cells:
            continue
        if not all(tiling.only_positive_in_row(c) for c in col):
            continue
        left = []
        right = []
        for cell in col:
            if cell not in tiling.possibly_empty:
                left.append(col_place(tiling, cell, DIR_WEST))
                right.append(col_place(tiling, cell, DIR_EAST))
        if not left:
            continue
        # print("-----")
        # for t in left:
        #     print(t.to_old_tiling())
        #     print(t.is_empty())
        #     print(t)
        # print("-----")
        # for t in right:
        #     print(t.to_old_tiling())
        #     print(t.is_empty())
        #     print(t)
        yield BatchStrategy(formal_step="Place leftmost into col {}".format(i), tilings=left)
        yield BatchStrategy(formal_step="Place rightmost into col {}".format(i), tilings=right)
    # print("END")


def col_place(tiling, cell, direction):
    positive_cells = []
    point_cells = []
    possibly_empty = []
    empty_cells = []
    col, row = cell

    for old_cell in tiling.positive_cells:
        x, y = old_cell
        if y == row:
            if x == col:
                point_cells.append((x + 1, y + 1))
                if direction == DIR_EAST:
                    possibly_empty.append((x, y))
                    possibly_empty.append((x, y + 2))
                elif direction == DIR_WEST:
                    possibly_empty.append((x + 2, y))
                    possibly_empty.append((x + 2, y + 2))
                else:
                    raise ValueError("Only col place east or west.")
            else:
                raise ValueError("Can't col place due to positive cell in row {}.".format(row))
        else:
            if y > row:
                y += 2
            if x == col:
                if direction == DIR_EAST:
                    positive_cells.append((x, y))
                    empty_cells.append((x + 2, y))
                elif direction == DIR_WEST:
                    positive_cells.append((x + 2, y))
                    empty_cells.append((x, y))
                else:
                    raise ValueError("Only col place east or west.")
            else:
                if x > col:
                    x += 2
                positive_cells.append((x, y))

    for old_cell in tiling.possibly_empty:
        x, y = old_cell
        if y == row:
            if x == col:
                raise ValueError("Can't insert into possibly_empty.")
            else:
                if x > col:
                    x += 2
                possibly_empty.append((x, y))
                possibly_empty.append((x, y + 2))
        else:
            if y > row:
                y += 2
            if x == col:
                possibly_empty.append((x, y))
                possibly_empty.append((x + 2, y))
            else:
                if x > col:
                    x += 2
                possibly_empty.append((x, y))

    for old_cell in tiling.point_cells:
        x, y = old_cell
        if y == row:
            if x == col:
                point_cells.append((x + 1, y + 1))
                if direction == DIR_EAST:
                    empty_cells.append((x, y))
                    empty_cells.append((x, y + 2))
                elif direction == DIR_WEST:
                    empty_cells.append((x + 2, y))
                    empty_cells.append((x + 2, y + 2))
                else:
                    raise ValueError("Only col place east or west.")
            else:
                raise ValueError("Can't col place due to point cell in row {}.".format(row))
        else:
            if y > row:
                y += 2
            if x == col:
                if direction == DIR_EAST:
                    point_cells.append((x, y))
                    empty_cells.append((x + 2, y))
                elif direction == DIR_WEST:
                    point_cells.append((x + 2, y))
                    empty_cells.append((x, y))
                else:
                    raise ValueError("Only col place east or west.")
            else:
                if x > col:
                    x += 2
                point_cells.append((x, y))

    obstructions = []
    for ob in tiling:
        obstructions.extend([o for o in ob.place_point(cell, direction)
                             if not any(o.occupies(c) for c in empty_cells)])
    # print("points:", point_cells)
    # print("positive:", positive_cells)
    # print("possibly_empty:", possibly_empty)
    # print("empty_cells:", empty_cells)
    # print(Tiling(point_cells=point_cells, positive_cells=positive_cells,
    #               possibly_empty=possibly_empty, obstructions=obstructions).to_old_tiling())
    return Tiling(point_cells=point_cells, positive_cells=positive_cells,
                  possibly_empty=possibly_empty, obstructions=obstructions)
