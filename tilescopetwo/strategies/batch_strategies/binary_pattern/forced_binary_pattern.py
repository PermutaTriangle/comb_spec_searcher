from permuta import Perm, PermSet
from permuta.misc import DIR_EAST, DIR_WEST, DIR_SOUTH, DIR_NORTH, DIR_NONE
from grids_two import Obstruction, Tiling
from .util import generate_minimal_binary_forces as binary_forces
from .util import make_force_strength_func
from bisect import bisect, bisect_left
from itertools import chain, combinations


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
        if cell[0] == insert[0] and cell[1] == insert[1]:
            res.append((cell[0] + 2, cell[1] + 2))
        if cell[0] == insert[0]:
            res.append((cell[0] + 2, cell[1]))
        if cell[1] == insert[1]:
            res.append((cell[0], cell[1] + 2))
        res.append(translate(insert, cell))
    return res


def place_forced_pattern_failed(tiling, cell, patt, force):
    workobs = [Obstruction.single_cell(patt, cell)]
    worktiling = tiling
    insertedind, insertedval = list(), list()
    for (index, dire) in force:
        # print(worktiling)
        insert_cell = (bisect(insertedind, index) * 2,
                       bisect(insertedval, patt[index]) * 2)
        insertedind.append(index)
        insertedval.append(patt[index])
        obs = list(chain.from_iterable(ob.place_point(insert_cell, DIR_NONE)
                                       for ob in worktiling.obstructions))

        fromworkobs = list(chain.from_iterable(
            ob.place_point(insert_cell, opposite_dir(dire)) for ob in workobs))

        # print("OBS")
        # for ob in obs:
            # print(ob)

        # print("FROMWORKOBS")
        # for ob in fromworkobs:
            # print(ob)

        workobs = list(ob for ob in fromworkobs
                       if len(ob) < len(patt) - len(insertedind) + 1)

        # print("WORKOBS")
        # for ob in workobs:
            # print(ob)

        addedobs = list(ob for ob in fromworkobs
                        if len(ob) == len(patt) - len(insertedind) + 1)

        # print("ADDEDOBS")
        # for ob in addedobs:
            # print(ob)

        # print("INSERT_CELL:", insert_cell)

        # print(translate_set(insert_cell, worktiling.possibly_empty))

        worktiling = Tiling(
            point_cells=(translate_set(insert_cell, worktiling.point_cells) +
                         [(insert_cell[0] + 1, insert_cell[1] + 1)]),
            positive_cells=translate_set(insert_cell,
                                         worktiling.positive_cells),
            possibly_empty=translate_set(insert_cell,
                                         worktiling.possibly_empty),
            obstructions=obs + addedobs,
            remove_empty=False)

    # print(worktiling)
    worktiling._minimize(True)
    # print(worktiling)
    for ob in worktiling.obstructions:
        print(ob)

    for index in range(len(patt)):
        if index in insertedind:
            continue
        insert_cell = (bisect(insertedind, index) * 2,
                       bisect(insertedval, patt[index]) * 2)
        insertedind.append(index)
        insertedval.append(patt[index])
        obs = list(chain.from_iterable(ob.place_point(insert_cell, DIR_NONE)
                                       for ob in worktiling.obstructions))
        worktiling = Tiling(
            point_cells=(translate_set(insert_cell, worktiling.point_cells) +
                         [(insert_cell[0] + 1, insert_cell[1] + 1)]),
            positive_cells=translate_set(insert_cell,
                                         worktiling.positive_cells),
            possibly_empty=translate_set(insert_cell,
                                         worktiling.possibly_empty),
            obstructions=obs)
    # for ob in worktiling.obstructions:
        # print(ob)
    # print(worktiling)

    return worktiling


def forced_obstructions_failed(placedidx, placedval, curpos,
                               contr, patt, forces, pattpos):
    assert len(curpos) == len(placedval)
    assert len(placedidx) == len(placedval)
    assert sorted([patt[i] for i in placedidx]) == placedval

    pattinv = patt.inverse()

    def insert_point(index, force=None):
        idx = bisect_left(placedidx, index)
        validx = bisect_left(placedval, patt[index])
        if idx != len(placedidx) and placedidx[idx] == index:
            return

        mindex, maxdex, minval, maxval = 0, len(patt), 0, len(patt)
        if idx > 0:
            mindex = curpos[idx - 1][0]
        if idx < len(curpos):
            maxdex = curpos[idx][0]
        if validx > 0:
            loweridx = pattinv[placedval[validx - 1]]
            minval = curpos[bisect_left(placedidx, loweridx)][1]
        if validx < len(curpos):
            # print(validx, placedval, curpos)
            upperidx = pattinv[placedval[validx]]
            maxval = curpos[bisect_left(placedidx, upperidx)][1]
        if force == DIR_EAST:
            mindex = pattpos[i][0] + 1
        if force == DIR_NORTH:
            minval = pattpos[i][1] + 1
        if force == DIR_WEST:
            maxdex = pattpos[i][0] - 1
        if force == DIR_SOUTH:
            maxval = pattpos[i][1] - 1

        assert mindex <= maxdex
        assert minval <= maxval

        for x in range(mindex, maxdex + 1, 2):
            for y in range(minval, maxval + 1, 2):
                indices = placedidx[:]
                indices.insert(idx, index)
                vals = placedval[:]
                vals.insert(idx, patt[index])
                pos = curpos[:]
                pos.insert(idx, (x, y))

                perm = perm_from_points(patt, [(i * 2 + 1, patt[i] * 2 + 1)
                                               for i in range(len(patt))],
                                        Perm.to_standard(
                                            patt[i] for i in indices),
                                        [p for p in pos if p[0] % 2 == 0])

                if perm.count_occurrences_of(patt) > 1:
                    yield Obstruction(Perm(patt[i] for i in indices), pos)
                else:
                    for ob in forced_obstructions_failed(indices, vals, pos,
                                                         contr, patt, forces,
                                                         pattpos):
                        yield ob
    if contr:
        for i in range(len(patt)):
            for ob in insert_point(i):
                print("CC")
                yield ob
    else:
        for (i, f) in forces:
            print(placedidx, placedval, curpos)
            idx = bisect_left(placedidx, i)
            if idx != len(placedidx) and placedidx[idx] == i:
                continue
            indices = placedidx[:]
            indices.insert(idx, i)
            vals = placedval[:]
            vals.insert(idx, patt[i])
            pos = curpos[:]
            pos.insert(idx, pattpos[i])

            for ob in forced_obstructions_failed(indices,
                                                 vals,
                                                 pos,
                                                 False,
                                                 patt,
                                                 forces,
                                                 pattpos):
                print("AA")
                yield ob
            for ob in insert_point(idx, f):
                print("BB")
                yield ob


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
    sortedbyval = sorted(combined,
                         key=lambda valpoint: (valpoint[1][1],
                                               valpoint[0][1]))

    # Enumerate these sorted tuples ((i, p[i]), (x, y)) such that they become
    # (e, ((i, p[i]), (x, y))) and then sort them by (x, i) their column and
    # break ties with the index within the permutation.
    #
    # Extract the enumeration and construct a permutation.
    perm = Perm(i for (i, ev)
                in sorted(enumerate(sortedbyval),
                          key=lambda enumvalpoint: (enumvalpoint[1][1][0],
                                                    enumvalpoint[1][0][0])))
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
        # for i in range(len(patt)):
        validx = bisect_left(placedval, patt[idx])
        print(patt, pos, idx)
        print(validx)
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


def forced_obstructions(patt, force, pattpos):
    subpatts = set()
    for length in range(1, len(patt) + 1):
        subpatts |= set(map(Perm.to_standard, combinations(patt, length)))
    obs = list()
    force_strength = make_force_strength_func(force)
    for subpatt in sorted(subpatts):
        for pos in all_pattern_placements(subpatt,
                                          2*len(patt) + 1,
                                          2*len(patt) + 1):
            (perm, pattidx) = perm_from_points(patt, pattpos, subpatt, pos)
            for occ in perm.occurrences_of(patt):
                # print(perm, patt, occ, pattidx, force)
                ob = Obstruction(subpatt, pos)
                if (occ != pattidx and
                        force_strength(occ, perm) > force_strength(pattidx, perm) and
                        not any(o in ob for o in obs)):
                    obs.append(ob)
    return obs


def place_forced_pattern(tiling, patt, force, cell=(0, 0)):
    pattpos = []
    insertedval = list()
    for idx in range(len(patt)):
        insert_cell = (idx * 2,
                       bisect(insertedval, patt[idx]) * 2)
        insertedval.append(patt[idx])
        inserted_cell = (insert_cell[0] + 1, insert_cell[1] + 1)
        pattpos.append(inserted_cell)
        tiling = Tiling(point_cells=translate_set(insert_cell, tiling.point_cells) + [inserted_cell],
                        positive_cells=translate_set(insert_cell, tiling.positive_cells),
                        possibly_empty=translate_set(insert_cell, tiling.possibly_empty),
                        obstructions=chain.from_iterable(ob.place_point(insert_cell) for ob in tiling.obstructions),
                        remove_empty=False)

    # obstructions = tuple(forced_obstructions([], [], [], False, patt, force, pattpos))
    obstructions = tuple(forced_obstructions(patt, force, pattpos))
    print(obstructions)
    for ob in obstructions:
        print(ob)
    return Tiling(
        point_cells=tiling.point_cells,
        positive_cells=tiling.positive_cells,
        possibly_empty=tiling.possibly_empty,
        obstructions=(tiling.obstructions +
                      obstructions))


def forced_binary_pattern(tiling, **kwargs):
    if tiling.dimensions != (1, 1):
        return

    maxlen = kwargs.get('maxlen')
    basis = [ob.patt for ob in tiling.obstructions]

    for pattlen in range(1, maxlen + 1):
        for patt in PermSet(pattlen):
            for force in binary_forces(patt, basis):
                yield place_forced_pattern(tiling, patt, force)
