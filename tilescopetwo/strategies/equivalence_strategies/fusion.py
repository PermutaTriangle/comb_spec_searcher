from grids_two import Tiling
from permuta.misc import DIR_EAST, DIR_NORTH
from itertools import chain
from comb_spec_searcher import EquivalenceStrategy

def fusion(tiling, **kwargs):
    if tiling.requirements:
        return
    n, m = tiling.dimensions
    array_tiling = [[[] for i in range(m)] for j in range(n)]

    for ob in tiling:
        # assumed that ob in tiling is sorted
        if ob.is_single_cell():
            i, j = ob.pos[0]
            array_tiling[i][j].append(ob.patt)

    pos_cols = []
    pos_rows = []
    for cell in chain(tiling.point_cells, tiling.positive_cells):
        pos_cols.append(cell[0])
        pos_rows.append(cell[1])

    for col in range(n - 1):
        if col in pos_cols or col + 1 in pos_cols:
            continue
        if all(array_tiling[col][i] == array_tiling[col + 1][i] for i in range(m)):
            # row and row + 1 are the same
            fused = fuse_tiling(tiling, col=col)
            split = split_tiling(fused, col=col)
            if split == tiling:
                yield EquivalenceStrategy("Fuse column {}".format(col),
                                          fused)

    for row in range(m - 1):
        if row in pos_rows or row + 1 in pos_rows:
            continue
        if all(array_tiling[i][row] == array_tiling[i][row + 1] for i in range(n)):
            # row and row + 1 are the same
            fused = fuse_tiling(tiling, row=row)
            split = split_tiling(fused, row=row)
            if split == tiling:
                yield EquivalenceStrategy("Fuse row {}".format(row),
                                          fused)

def fuse_tiling(tiling, row=None, col=None):
    # fuses row and row plus one, and fuse col and col plus one
    # assumes no requirements
    return Tiling(point_cells=[x for x in tiling.point_cells
                               if not col == x[0] and not row == x[1]],
                  possibly_empty=[x for x in tiling.possibly_empty
                                  if not col == x[0] and not row == x[1]],
                  positive_cells=[x for x in tiling.positive_cells
                                  if not col == x[0] and not row == x[1]],
                  obstructions=[ob for ob in tiling
                                if all(not cell[0] == col and not cell[1] == row
                                       for cell in ob.pos)])

def split_tiling(tiling, row=None, col=None):
    n, m = tiling.dimensions
    point_cells = []
    possibly_empty = []
    positive_cells = []
    for cell in tiling.possibly_empty:
        x, y = cell
        if x == col:
            if y == row:
                raise ValueError("Only split in one direction.")
            possibly_empty.append((x, y))
            possibly_empty.append((x + 2, y))
        elif y == row:
            possibly_empty.append((x, y))
            possibly_empty.append((x, y + 2))
        else:
            if col is not None and x > col:
                x += 2
            if row is not None and y > row:
                y += 2
            possibly_empty.append((x, y))

    for cell in tiling.positive_cells:
        x, y = cell
        if x == col or y == row:
            raise ValueError("Don't split row or column with positive cell")
        if col is not None and x > col:
            x += 2
        if row is not None and y > row:
            y += 2
        positive_cells.append((x, y))

    for cell in tiling.point_cells:
        x, y = cell
        if x == col or y == row:
            raise ValueError("Don't split row or column with point cell")
        if col is not None and x > col:
            x += 2
        if row is not None and y > row:
            y += 2
        point_cells.append((x, y))

    split_cell = (col if col is not None else 999, row if row is not None else 999)
    if col is not None:
        direction = DIR_NORTH
    elif row is not None:
        direction = DIR_EAST
    else:
        raise ValueError(("Don't split row and column"))

    return Tiling(point_cells=point_cells,
                  possibly_empty=possibly_empty,
                  positive_cells=positive_cells,
                  obstructions=[o for ob in tiling
                                for o in ob.place_point(split_cell, direction)])
