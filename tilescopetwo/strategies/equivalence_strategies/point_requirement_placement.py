"""The point_requirement_placement strategy tries all possible ways of
placing one of the points in a requirement with any possible force"""

from grids_two import Tiling
from permuta.misc import DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST, DIR_NONE  # , DIRS
from comb_spec_searcher import EquivalenceStrategy
ALL_DIR = [DIR_EAST, DIR_NORTH, DIR_SOUTH, DIR_WEST]

def all_point_requirement_placements(tiling, **kwargs):
    n, m = tiling.dimensions
    array_tiling = [[[] for i in range(m)] for j in range(n)]

    for ob in tiling:
        # assumed that ob in tiling is sorted
        if ob.is_single_cell():
            i, j = ob.pos[0]
            array_tiling[i][j].append(ob.patt)


    for reqs in tiling.requirements:
        if len(reqs) > 1:
            continue
        req = reqs[0]
        for i, cell in enumerate(req.pos):
            basis = array_tiling[cell[0]][cell[1]]
            if len(basis) == 2 and all(len(b) == 2 for b in basis):
                yield point_requirement_placement(tiling, cell, req, i, DIR_NORTH)
            elif len(basis) == 1 and len(basis[0]) == 2:
                yield point_requirement_placement(tiling, cell, req, i, DIR_EAST)
                yield point_requirement_placement(tiling, cell, req, i, DIR_WEST)
            else:
                for force in ALL_DIR:
                    yield point_requirement_placement(tiling, cell, req, i, force)


def point_requirement_placement(tiling, cell, req, index, force):
    new_positive_cells = []
    new_point_cells = []
    new_possibly_empty = []

    for old_cell in tiling.positive_cells:
        if old_cell == cell:
            x = old_cell[0]
            y = old_cell[1]
            new_point_cells.append((x + 1, y + 1))
            new_possibly_empty.append((x, y))
            new_possibly_empty.append((x, y + 2))
            new_possibly_empty.append((x + 2, y))
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
        if old_cell == cell:
                x = old_cell[0]
                y = old_cell[1]
                new_point_cells.append((x + 1, y + 1))
                new_possibly_empty.append((x, y))
                new_possibly_empty.append((x, y + 2))
                new_possibly_empty.append((x + 2, y))
                new_possibly_empty.append((x + 2, y + 2))
        elif old_cell[0] == cell[0]:
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
        obstructions.extend(ob.place_point(cell, DIR_NONE))

    requirements = []
    for req_list in tiling.requirements:
        if req_list == (req,):
            reqs, obs = req.forced_point(cell, force, index)
            obstructions.extend(obs)
            if len(req) > 1:
                requirements.append(reqs)
        else:
            reqs = []
            for r in req_list:
                reqs.extend(r.place_point(cell, (force+2)%4))
            requirements.append([r for r in reqs if r])
    point_placed_tiling = Tiling(point_cells=new_point_cells,
                                 positive_cells=new_positive_cells,
                                 possibly_empty=new_possibly_empty,
                                 obstructions=obstructions,
                                 requirements=requirements)

    return EquivalenceStrategy(formal_step="Placed point at index {} in requirement {} with force {}".format(index, repr(req), force),
                               tiling = point_placed_tiling)
