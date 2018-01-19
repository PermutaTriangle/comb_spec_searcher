from permuta import Perm
from grids_two import Obstruction, Tiling
from comb_spec_searcher import EquivalenceStrategy

def deflation(tiling, interleaving=True, **kwargs):
    if tiling.is_empty():
        return
    if tiling.requirements:
        return
    n, m = tiling.dimensions
    if n == m == 1:
        return
    array_tiling = [[[] for i in range(m)] for j in range(n)]

    for ob in tiling:
        # assumed that ob in tiling is sorted
        if ob.is_single_cell():
            i, j = ob.pos[0]
            array_tiling[i][j].append(ob.patt)
        else:
            pass
    for cell in tiling.point_cells:
        array_tiling[cell[0]][cell[1]] = "point"

    if not interleaving:
        rows = {}
        for i in range(len(array_tiling)):
            rows[i] = [j for j in range(len(array_tiling[0])) if array_tiling[i][j] != []]
        cols = {}
        for j in range(len(array_tiling[0])):
            cols[j] = [i for i in range(len(array_tiling)) if array_tiling[i][j] != []]

    for cell in tiling.possibly_empty:
        basis = array_tiling[cell[0]][cell[1]]
        if is_sum_indecomposable(basis):
            if not interleaving:
                if can_deflate_interleaving(tiling, cell, rows[cell[0]],
                                            cols[cell[1]]):
                    yield EquivalenceStrategy("Sum deflate cell {}".format(cell),
                                              deflated_tiling(tiling, cell))
            else:
                non_interleaving_cells = can_deflate(tiling, cell)
                if non_interleaving_cells is not None:
                    formal_step = "Sum deflate cell {}".format(cell)
                    if non_interleaving_cells:
                        formal_step += ", but don't interleave {}".format(non_interleaving_cells)
                    yield EquivalenceStrategy(formal_step,
                                              deflated_tiling(tiling, cell))

        if is_skew_indecomposable(basis):
            if not interleaving:
                if can_deflate_interleaving(tiling, cell, rows[cell[0]],
                                            cols[cell[1]], sum_decomp=False):
                    yield EquivalenceStrategy("Skew deflate cell {}".format(cell),
                                              deflated_tiling(tiling, cell,
                                                              sum_decomp=False))
            else:
                non_interleaving_cells = can_deflate(tiling, cell,
                                                     sum_decomp=False)
                if non_interleaving_cells is not None:
                    formal_step = "Skew deflate cell {}".format(cell)
                    if non_interleaving_cells:
                        formal_step += ", but don't interleave {}".format(non_interleaving_cells)
                    yield EquivalenceStrategy(formal_step,
                                              deflated_tiling(tiling, cell,
                                                              sum_decomp=False))


def deflated_tiling(tiling, cell, sum_decomp=True):
    if sum_decomp:
        extra = Obstruction.single_cell(Perm((1, 0)), cell)
    else:
        extra = Obstruction.single_cell(Perm((0, 1)), cell)
    # print("in tiling")
    # print(tiling.to_old_tiling())
    # for o in tiling:
    #     if not o.is_single_cell():
    #         print(o)
    # print("out_tiling")
    # out_tiling = Tiling(point_cells=tiling.point_cells,
    #               positive_cells=tiling.positive_cells,
    #               possibly_empty=tiling.possibly_empty,
    #               requirements=tiling.requirements,
    #               obstructions=tiling.obstructions + (extra, ))
    # print(out_tiling.to_old_tiling())
    # for o in out_tiling:
    #     if not o.is_single_cell():
    #         print(o)
    return Tiling(point_cells=tiling.point_cells,
                  positive_cells=tiling.positive_cells,
                  possibly_empty=tiling.possibly_empty,
                  requirements=tiling.requirements,
                  obstructions=tiling.obstructions + (extra, ))

def can_deflate(tiling, cell, sum_decomp=True):
    '''
    Return None if can not deflate, else return the possibly_empty list of non
    interleaving cells for defation.
    '''
    non_interleaving_cells = []
    # print()
    # print(tiling.to_old_tiling())
    # for o in tiling:
    #     if not o.is_single_cell():
    #         print(repr(o))
    # print("considiring:", cell, sum_decomp)
    # print()
    for ob in tiling:
        if ob.is_single_cell() or len(ob) <= 2 or not ob.occupies(cell):
            continue
        n = sum(1 for c in ob.pos if c == cell)
        if n == 1:
            continue
        if n != 2:
            return None
        else:
            if len(ob.patt) != 3:
                return None
            other_cell = [c for c in ob.pos if c != cell][0]
            # print("considered:", repr(ob), other_cell)
            if all(x != y for x, y in zip(other_cell, cell)):
                return None
            elif other_cell[0] == cell[0]:
                if other_cell[1] > cell[1]:
                    if ((sum_decomp and ob.patt == Perm((1, 2, 0))) or
                        (not sum_decomp and ob.patt == Perm((0, 2, 1)))):
                        non_interleaving_cells.append(other_cell)
                    else:
                        return None
                else:
                    if ((sum_decomp and ob.patt == Perm((2, 0, 1))) or
                        (not sum_decomp and ob.patt == Perm((1, 0, 2)))):
                        non_interleaving_cells.append(other_cell)
                    else:
                        return None
            else:# other_cell[1] == other_cell[1]:
                if other_cell[0] > cell[0]:
                    if ((sum_decomp and ob.patt == Perm((2, 0, 1))) or
                        (not sum_decomp and ob.patt == Perm((0, 2, 1)))):
                        non_interleaving_cells.append(other_cell)
                    else:
                        return None
                else:
                    if ((sum_decomp and ob.patt == Perm((1, 2, 0))) or
                        (not sum_decomp and ob.patt == Perm((1, 0, 2)))):
                        non_interleaving_cells.append(other_cell)
                    else:
                        return None
    return non_interleaving_cells

def can_deflate_interleaving(tiling, cell, row, col, sum_decomp=True):
    col_deflatable = {i: False for i in row if i != cell[1]}
    row_deflatable = {j: False for j in col if j != cell[0]}
    if not row_deflatable and not col_deflatable:
        return False
    for ob in tiling:
        if not ob.is_single_cell():
            if ob.occupies(cell):
                if len(ob.patt) == 2:
                    other_cell = [c for c in ob.pos if c != cell][0]
                    if other_cell[0] == cell[0]:
                        col_deflatable[other_cell[1]] = True
                    elif other_cell[1] == cell[1]:
                        row_deflatable[other_cell[0]] = True
                    else:
                        return False

                n = sum(1 for c in ob.pos if c == cell)
                if n > 2:
                    return False
                if n == 2:
                    if len(ob.patt) != 3:
                        return False
                    other_cell = [c for c in ob.pos if c != cell][0]
                    if other_cell[0] == cell[0]:
                        if other_cell[1] > cell[1]:
                            if sum_decomp and ob.patt != Perm((1, 2, 0)):
                                return False
                            elif not sum_decomp and ob.patt != Perm((0, 2, 1)):
                                return False
                            else:
                                col_deflatable[other_cell[1]] = True
                        else:
                            if sum_decomp and ob.patt != Perm((2, 0, 1)):
                                return False
                            elif not sum_decomp and ob.patt != Perm((1, 0, 2)):
                                return False
                            else:
                                col_deflatable[other_cell[1]] = True
                    elif other_cell[1] == other_cell[1]:
                        if other_cell[0] > cell[0]:
                            if sum_decomp and ob.patt != Perm((2, 0, 1)):
                                return False
                            elif not sum_decomp and ob.patt != Perm((0, 2, 1)):
                                return False
                            else:
                                row_deflatable[other_cell[0]] = True
                        else:
                            if sum_decomp and ob.patt != Perm((1, 2, 0)):
                                return False
                            elif not sum_decomp and ob.patt != Perm((1, 0, 2)):
                                return False
                            else:
                                row_deflatable[other_cell[0]] = True
                    else:
                        return False
    if all(x for x in row_deflatable.values()) and all(x for x in col_deflatable.values()):
        return True


def is_skew_indecomposable(basis):
    if all(len(patt) == 2 for patt in basis):
        return False
    return all(not p.is_skew_decomposable() for p in basis)

def is_sum_indecomposable(basis):
    if all(len(patt) == 2 for patt in basis):
        return False
    return all(not p.is_sum_decomposable() for p in basis)
