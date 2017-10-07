from permuta import Perm, PermSet
from permuta.misc import DIR_EAST, DIR_WEST, DIR_SOUTH, DIR_NORTH, DIR_NONE
from grids_two import Obstruction, Tiling
from .util import generate_minimal_binary_forces as binary_forces
from .util import make_force_strength_func
from bisect import bisect, bisect_left
from itertools import chain, combinations
from comb_spec_searcher import BatchStrategy


def opposite_dir(direction):
    if direction == DIR_WEST:
        return DIR_EAST
    if direction == DIR_EAST:
        return DIR_WEST
    if direction == DIR_NORTH:
        return DIR_SOUTH
    if direction == DIR_SOUTH:
        return DIR_NORTH
    return DIR_NONE


def translate(insert, cell):
    cell = list(cell)
    if cell[0] > insert[0]:
        cell[0] += 2
    if cell[1] > insert[1]:
        cell[1] += 2
    return tuple(cell)


def translate_set(insert, cells):
    res = []
    for cell in cells:
        translated = translate(insert, cell)
        if cell[0] == insert[0] and cell[1] == insert[1]:
            res.append((translated[0] + 2, translated[1] + 2))
        if cell[0] == insert[0]:
            res.append((translated[0] + 2, translated[1]))
        if cell[1] == insert[1]:
            res.append((translated[0], translated[1] + 2))
        res.append(translated)
    return res


def perm_from_points(patt1, pos1, patt2, pos2):
    # Make sure that the patterns are placed such that they do not share any
    # row or column.
    assert len(set(y for (x, y) in pos1) & set(y for (x, y) in pos2)) == 0
    assert len(set(x for (x, y) in pos1) & set(x for (x, y) in pos2)) == 0

    # Combined consists of ((i, p[i]), (x, y)) where i is the index in the
    # pattern p and and (x, y) is the location of the point (i, p[i])
    combined = chain(zip(enumerate(patt1), pos1), zip(enumerate(patt2), pos2))

    # Sort these tuples ((i, p[i]), (x, y)) by (y, p[i]), first by row and then
    # break ties with the value
    sortedbyval = list(sorted(combined,
                          key=lambda valpoint: (valpoint[1][1],
                                                valpoint[0][1])))

    # Enumerate these sorted tuples ((i, p[i]), (x, y)) such that they become
    # (e, ((i, p[i]), (x, y))) and then sort them by (x, i) their column and
    # break ties with the index within the permutation.
    #
    # Extract the enumeration and construct a permutation.
    perm = Perm(i for (i, ev)
                in sorted(enumerate(sortedbyval),
                          key=lambda enumvalpoint: (enumvalpoint[1][1][0],
                                                    enumvalpoint[1][0][0])))

    # Compute the indices of patt1 in the new permutation
    left, right = 0, 0
    fromleft = []
    for i in range(len(perm)):
        if left == len(pos1):
            break
        elif right == len(pos2):
            fromleft.append(i)
            left += 1
        else:
            if pos1[left][0] < pos2[right][0]:
                fromleft.append(i)
                left += 1
            else:
                right += 1
    assert len(fromleft) == len(patt1)
    return (perm, tuple(fromleft))


def all_pattern_placements(patt, rows, columns):
    pattinv = patt.inverse()

    def place_next(placedval, pos):
        idx = len(pos)
        if idx == len(patt):
            yield pos
            return
        validx = bisect_left(placedval, patt[idx])
        miny, maxy = 0, rows - 1
        placedval = placedval[:]
        if validx > 0:
            miny = pos[pattinv[placedval[validx-1]]][1]
        if validx < len(placedval):
            maxy = pos[pattinv[placedval[validx]]][1]
        placedval.insert(validx, patt[idx])
        for x in range(pos[-1][0] if pos else 0, columns, 2):
            for y in range(miny, maxy + 1, 2):
                for p in place_next(placedval, pos + [(x, y)]):
                    yield p
    for p in place_next([], []):
        yield p


def forced_obstructions(patt, force, pattpos, legal_cells):
    subpatts = set()
    for length in range(1, len(patt) + 1):
        subpatts |= set(map(Perm.to_standard, combinations(patt, length)))
    force_strength = make_force_strength_func(force)
    obs = list()
    for subpatt in sorted(subpatts):
        for pos in all_pattern_placements(subpatt,
                                          2*len(patt) + 1,  # Assumes (0, 0)
                                          2*len(patt) + 1):
            (perm, pattidx) = perm_from_points(patt, pattpos, subpatt, pos)
            for occ in perm.occurrences_of(patt):
                if force_strength(occ, perm) > force_strength(pattidx, perm):
                    ob = Obstruction(subpatt, pos)
                    if (not any(o in ob for o in obs) and
                            not any(p not in legal_cells for p in pos)):
                        obs.append(ob)
    return obs


def place_pattern(tiling, patt):
    pattpos = []
    insertedval = list()
    for idx in range(len(patt)):
        validx = bisect(insertedval, patt[idx])
        insert_cell = (idx * 2,
                       validx * 2)
        insertedval.insert(validx, patt[idx])
        inserted_cell = (insert_cell[0] + 1, insert_cell[1] + 1)
        pattpos = translate_set(insert_cell, pattpos)
        pattpos.append(inserted_cell)
        tiling = Tiling(point_cells=(translate_set(insert_cell,
                                                   tiling.point_cells) +
                                     [inserted_cell]),
                        positive_cells=translate_set(insert_cell,
                                                     tiling.positive_cells),
                        possibly_empty=translate_set(insert_cell,
                                                     tiling.possibly_empty),
                        obstructions=chain.from_iterable(
                            ob.place_point(insert_cell, DIR_NONE)
                            for ob in tiling.obstructions),
                        remove_empty=False)
    return (tiling, pattpos)


def place_forced_pattern(tiling, patt, pattpos, force, cell=(0, 0)):
    obstructions = tuple(forced_obstructions(patt, force, pattpos,
                                             tiling.possibly_empty |
                                             tiling.positive_cells))
    tiling = Tiling(
        point_cells=tiling.point_cells,
        positive_cells=tiling.positive_cells,
        possibly_empty=tiling.possibly_empty,
        obstructions=tiling.obstructions + obstructions)
    return tiling


def forced_binary_pattern(tiling, **kwargs):
    if tiling.dimensions != (1, 1) or (0, 0) not in tiling.possibly_empty:
        return

    maxpattlen = kwargs.get('pattlen')
    maxforcelen = kwargs.get('forcelen')
    basis = [ob.patt for ob in tiling.obstructions]
    if maxpattlen is None:
        maxpattlen = max(map(len, basis)) - 1
    if maxforcelen is None:
        maxforcelen = maxpattlen

    for pattlen in range(2, maxpattlen + 1):
        for patt in PermSet(pattlen):
            (placedtiling, pattpos) = place_pattern(tiling, patt)
            for force in binary_forces(patt, basis, maxforcelen):
                forcedtiling = place_forced_pattern(placedtiling, patt,
                                                    pattpos, force)
                avoidingtiling = Tiling(
                    tiling.point_cells,
                    tiling.positive_cells,
                    tiling.possibly_empty,
                    tiling.obstructions + (Obstruction.single_cell(patt,
                                                                   (0, 0)),))
                assert avoidingtiling.dimensions == (1, 1)
                assert forcedtiling.dimensions != (1, 1)

                yield BatchStrategy(
                    formal_step="Placing pattern {} with force {}".format(
                        patt, force),
                    tilings=[avoidingtiling, forcedtiling])
