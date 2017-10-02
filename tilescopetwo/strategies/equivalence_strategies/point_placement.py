from grids_two import Tiling
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST  # , DIRS
from comb_spec_searcher import EquivalenceStrategy
ALL_DIR = [DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST]

def all_point_placements(tiling, **kwargs):
    for cell in tiling.positive_cells:
        if tiling.only_positive_in_row_and_column(cell):
            for DIR in ALL_DIR:
                yield point_placement(tiling, cell, DIR)

def point_placement(tiling, cell, direction):
    new_positive_cells = []
    new_point_cells = []
    new_possibly_empty = []
    for old_cell in tiling.positive_cells:
        if old_cell == cell:
            x = old_cell[0]
            y = old_cell[1]
            new_point_cells.append((x + 1, y + 1))
            if direction == DIR_EAST:
                new_possibly_empty.append((x, y))
                new_possibly_empty.append((x, y + 2))
            elif direction == DIR_WEST:
                new_possibly_empty.append((x + 2, y))
                new_possibly_empty.append((x + 2, y + 2))
            elif direction == DIR_NORTH:
                new_possibly_empty.append((x, y))
                new_possibly_empty.append((x + 2, y))
            elif direction == DIR_SOUTH:
                new_possibly_empty.append((x, y + 2))
                new_possibly_empty.append((x + 2, y + 2))
        else:
            x = old_cell[0]
            y = old_cell[1]
            if old_cell[0] > cell[0]:
                x += 2
            if old_cell[1] > cell[1]:
                y += 2
            new_positive_cells.append((x,y))
    for old_cell in tiling.possibly_empty:
        if old_cell[0] == cell[0]:
            x = old_cell[0]
            y = old_cell[1]
            if old_cell[1] > cell[1]:
                y += 2
            new_possibly_empty.append((x, y))
            new_possibly_empty.append((x + 2, y))
        elif old_cell[1] == cell[1]:
            x = old_cell[0]
            y = old_cell[1]
            if old_cell[0] > cell[0]:
                x += 2
            new_possibly_empty.append((x, y))
            new_possibly_empty.append((x, y + 2))
        else:
            x = old_cell[0]
            y = old_cell[1]
            if old_cell[0] > cell[0]:
                x += 2
            if old_cell[1] > cell[1]:
                y += 2
            new_possibly_empty.append((x,y))

    for old_cell in tiling.point_cells:
        x = old_cell[0]
        y = old_cell[1]
        if old_cell[0] > cell[0]:
            x += 2
        if old_cell[1] > cell[1]:
            y += 2
        new_point_cells.append((x, y))

    obstructions = []
    for ob in tiling:
        obstructions.extend(ob.place_point(cell, direction))

    point_placed_tiling = Tiling(point_cells=new_point_cells, positive_cells=new_positive_cells,
                 possibly_empty=new_possibly_empty, obstructions=obstructions)

    return EquivalenceStrategy(formal_step="Placed point in cell {} in direction {}".format(cell, direction), tiling = point_placed_tiling)
