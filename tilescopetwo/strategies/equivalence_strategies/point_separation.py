from comb_spec_searcher import EquivalenceStrategy
from grids_two import Tiling
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST  # , DIRS


def point_separation(tiling, **kwargs):
    # print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    # print("The tiling:")
    # print(tiling.to_old_tiling())
    # print("Gives the tilings:")
    for cell in tiling.positive_cells:
        if tiling.only_cell_in_row(cell):
            for direction in (DIR_NORTH, DIR_SOUTH):
                yield EquivalenceStrategy(formal_step="Separate point in cell {} in direction {}.".format(cell, direction),
                                          tiling=point_separate(tiling, cell, direction))
        if tiling.only_cell_in_col(cell):
            for direction in (DIR_EAST, DIR_WEST):
                yield EquivalenceStrategy(formal_step="Separate point in cell {} in direction {}.".format(cell, direction),
                                          tiling=point_separate(tiling, cell, direction))

def point_separate(tiling, cell, direction):
    positive_cells = []
    point_cells = []
    possibly_empty = []

    for old_cell in tiling.positive_cells:
        x,y = old_cell
        if old_cell == cell:
            if direction == DIR_EAST:
                point_cells.append((x + 1, y))
                possibly_empty.append((x, y))
            elif direction == DIR_WEST:
                point_cells.append((x, y))
                possibly_empty.append((x + 1, y))
            elif direction == DIR_NORTH:
                point_cells.append((x, y + 1))
                possibly_empty.append((x, y))
            elif direction == DIR_SOUTH:
                point_cells.append((x, y))
                possibly_empty.append((x, y + 1))
            else:
                raise ValueError("Only point separate left, right, top or bottom")
        else:
            if direction == DIR_EAST or direction == DIR_WEST:
                if x > cell[0]:
                    x += 1
            elif direction == DIR_NORTH or direction == DIR_SOUTH:
                if y > cell[1]:
                    y += 1
            else:
                raise ValueError("Only point separate left, right, top or bottom")
            positive_cells.append((x, y))

    for old_cell in tiling.possibly_empty:
        x, y = old_cell
        if direction == DIR_EAST or direction == DIR_WEST:
            if x > cell[0]:
                x += 1
        elif direction == DIR_NORTH or direction == DIR_SOUTH:
            if y > cell[1]:
                y += 1
        else:
            raise ValueError("Only point separate left, right, top or bottom")
        possibly_empty.append((x, y))

    for old_cell in tiling.point_cells:
        x, y = old_cell
        if direction == DIR_EAST or direction == DIR_WEST:
            if x > cell[0]:
                x += 1
        elif direction == DIR_NORTH or direction == DIR_SOUTH:
            if y > cell[1]:
                y += 1
        else:
            raise ValueError("Only point separate left, right, top or bottom")
        point_cells.append((x, y))

    obstructions = []
    for ob in tiling:
        obstructions.extend(ob.point_separation(cell, direction))


    # print(tiling,cell,direction)
    # print(positive_cells)
    # print(point_cells)
    # print(possibly_empty)
    # print(obstructions)
    # print(Tiling(positive_cells=positive_cells,
    #               point_cells=point_cells,
    #               possibly_empty=possibly_empty,
    #               obstructions=obstructions).to_old_tiling())
    # print()

    return Tiling(positive_cells=positive_cells,
                  point_cells=point_cells,
                  possibly_empty=possibly_empty,
                  obstructions=obstructions)
