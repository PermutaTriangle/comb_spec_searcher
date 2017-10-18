from comb_spec_searcher import BatchStrategy
from grids_two import Tiling
from itertools import chain, combinations
from copy import copy

def point_isolations(tiling, **kwargs):
    for cell in tiling.point_cells:
        if not tiling.only_positive_in_col(cell):
            for strategy in isolate_point_in_column(tiling, cell):
                yield strategy

        if not tiling.only_cell_in_row(cell):
             for strategy in isolate_point_in_row(tiling, cell):
                 yield strategy

def isolate_point_in_row(tiling, cell_to_be_isolated):
    positive_cells = []
    possibly_empty = []
    point_cells = []
    in_row_positive_cells = []
    in_row_points = []

    for cell in tiling.positive_cells:
        x,y = cell
        if y == cell_to_be_isolated[1]:
            if x == cell_to_be_isolated[0]:
                raise ValueError("Can't isolate a non-point cell.")
            else:
                in_row_positive_cells.append((x, y))
        else:
            if y > cell_to_be_isolated[1]:
                y += 2
            positive_cells.append((x, y))

    for cell in tiling.point_cells:
        x, y = cell
        if y == cell_to_be_isolated[1]:
            if x == cell_to_be_isolated[0]:
                point_cells.append((x, y + 1))
            else:
                in_row_points.append((x, y))
        else:
            if y > cell_to_be_isolated[1]:
                y += 2
            point_cells.append((x, y))

    for cell in tiling.possibly_empty:
        x, y = cell
        if y == cell_to_be_isolated[1]:
            if x == cell_to_be_isolated[0]:
                raise ValueError("Can't isolate non-point cell.")
            else:
                possibly_empty.append((x, y))
                possibly_empty.append((x, y + 2))
        else:
            if y > cell_to_be_isolated[1]:
                y += 2
            possibly_empty.append((x, y))

    # print(tiling.to_old_tiling())
    # print(tiling)
    # print(cell_to_be_isolated)
    # print(positive_cells)
    # print(point_cells)
    # print(possibly_empty)
    obstructions = []
    for ob in tiling:
        # print("========")
        # L = [o for o in ob.isolate_point_row(cell_to_be_isolated)]
        # print(ob)
        # for o in L:
        #     print(o)
        obstructions.extend([o for o in ob.isolate_point_row(cell_to_be_isolated)])
    if not in_row_points and not in_row_positive_cells:
        # print("Isolated the point at {} in its row on the tiling".format(cell_to_be_isolated))
        # print(tiling.to_old_tiling())
        # print("it gave")
        # print(Tiling(positive_cells=positive_cells,
        #         point_cells=point_cells,
        #         possibly_empty=possibly_empty,
        #         obstructions=obstructions).to_old_tiling())
        # print()
        # print("---------")
        yield BatchStrategy("Isolated the point at {} in its row".format(cell_to_be_isolated),
                            [Tiling(positive_cells=positive_cells,
                                    point_cells=point_cells,
                                    possibly_empty=possibly_empty,
                                    obstructions=obstructions)])
    isolated_tilings = []
    for subset in powerset(in_row_points + in_row_positive_cells):
        above_empty_cells = []
        below_empty_cells = []

        above_possibly_empty = copy(possibly_empty)
        below_possibly_empty = copy(possibly_empty)

        above_point_cells = copy(point_cells)
        below_point_cells = copy(point_cells)

        above_positive_cells = copy(positive_cells)
        below_positive_cells = copy(positive_cells)

        for cell in in_row_positive_cells:
            x, y = cell
            if cell in subset:
                below_positive_cells.append((x, y))
                above_positive_cells.append((x, y))

                y += 2
                below_possibly_empty.append((x, y))
                above_empty_cells.append((x, y))
            else:
                below_empty_cells.append((x, y))
                above_possibly_empty.append((x, y))

                y+= 2
                below_positive_cells.append((x, y))
                above_positive_cells.append((x, y))

        for cell in in_row_points:
            x, y = cell
            if cell in subset:
                below_point_cells.append((x, y))
                above_point_cells.append((x, y))

                y += 2
                below_empty_cells.append((x, y))
                above_empty_cells.append((x, y))
            else:
                below_empty_cells.append((x, y))
                above_empty_cells.append((x, y))

                y+= 2
                below_point_cells.append((x, y))
                above_point_cells.append((x, y))
        # print(tiling)
        # print(above_point_cells, above_empty_cells, above_possibly_empty)
        above_obstructions = [o for o in obstructions if not any(o.occupies(c) for c in above_empty_cells)]
        # for o in above_obstructions:
        #      print(o)
        above_tiling = Tiling(point_cells=above_point_cells,
                              possibly_empty=above_possibly_empty,
                              positive_cells=above_positive_cells,
                              obstructions=[o for o in obstructions
                                            if not any(o.occupies(c)
                                                       for c in above_empty_cells)])
        # print(above_tiling)
        below_tiling = Tiling(point_cells=below_point_cells,
                              possibly_empty=below_possibly_empty,
                              positive_cells=below_positive_cells,
                              obstructions=[o for o in obstructions
                                            if not any(o.occupies(c)
                                                       for c in below_empty_cells)])

        isolated_tilings.append((above_tiling, below_tiling))

    for i in range(2):

        # print("Isolated the point at {} in its row on the tiling".format(cell_to_be_isolated))
        # print(tiling.to_old_tiling())
        # print("it gave")
        # for t in [t[i] for t in isolated_tilings]:
        #     print(t.to_old_tiling())
        #     print()
        # print()
        # print("---------")
        yield BatchStrategy("Isolated the point at {} in its row".format(cell_to_be_isolated), [t[i] for t in isolated_tilings])


def isolate_point_in_column(tiling, cell_to_be_isolated):
    positive_cells = []
    possibly_empty = []
    point_cells = []
    in_col_positive_cells = []
    in_col_points = []

    for cell in tiling.positive_cells:
        x,y = cell
        if x == cell_to_be_isolated[0]:
            if y == cell_to_be_isolated[1]:
                raise ValueError("Can't isolate a non-point cell.")
            else:
                in_col_positive_cells.append((x, y))
        else:
            if x > cell_to_be_isolated[0]:
                x += 2
            positive_cells.append((x, y))

    for cell in tiling.point_cells:
        x, y = cell
        if x == cell_to_be_isolated[0]:
            if y == cell_to_be_isolated[1]:
                point_cells.append((x + 1, y))
            else:
                in_col_points.append((x, y))
        else:
            if x > cell_to_be_isolated[0]:
                x += 2
            point_cells.append((x, y))

    for cell in tiling.possibly_empty:
        x, y = cell
        if x == cell_to_be_isolated[0]:
            if y == cell_to_be_isolated[1]:
                raise ValueError("Can't isolate non-point cell.")
            else:
                possibly_empty.append((x, y))
                possibly_empty.append((x + 2, y))
        else:
            if x > cell_to_be_isolated[0]:
                x += 2
            possibly_empty.append((x, y))

    # print(tiling.to_old_tiling())
    # print(tiling)
    # print(cell_to_be_isolated)
    # print(positive_cells)
    # print(point_cells)
    # print(possibly_empty)
    obstructions = []
    for ob in tiling:
        # print("========")
        # L = [o for o in ob.isolate_point_row(cell_to_be_isolated)]
        # print(ob)
        # for o in L:
        #     print(o)
        obstructions.extend([o for o in ob.isolate_point_col(cell_to_be_isolated)])
    if not in_col_points and not in_col_positive_cells:
        # print("Isolated the point at {} in its col on the tiling".format(cell_to_be_isolated))
        # print(tiling.to_old_tiling())
        # print("it gave")
        # print(Tiling(positive_cells=positive_cells,
        #         point_cells=point_cells,
        #         possibly_empty=possibly_empty,
        #         obstructions=obstructions).to_old_tiling())
        # print()
        # print("---------")
        yield BatchStrategy("Isolated the point at {} in its col".format(cell_to_be_isolated),
                            [Tiling(positive_cells=positive_cells,
                                    point_cells=point_cells,
                                    possibly_empty=possibly_empty,
                                    obstructions=obstructions)])
    isolated_tilings = []
    for subset in powerset(in_col_points + in_col_positive_cells):
        above_empty_cells = []
        below_empty_cells = []

        above_possibly_empty = copy(possibly_empty)
        below_possibly_empty = copy(possibly_empty)

        above_point_cells = copy(point_cells)
        below_point_cells = copy(point_cells)

        above_positive_cells = copy(positive_cells)
        below_positive_cells = copy(positive_cells)

        for cell in in_col_positive_cells:
            x, y = cell
            if cell in subset:
                below_positive_cells.append((x, y))
                above_positive_cells.append((x, y))

                x += 2
                below_possibly_empty.append((x, y))
                above_empty_cells.append((x, y))
            else:
                below_empty_cells.append((x, y))
                above_possibly_empty.append((x, y))

                x += 2
                below_positive_cells.append((x, y))
                above_positive_cells.append((x, y))

        for cell in in_col_points:
            x, y = cell
            if cell in subset:
                below_point_cells.append((x, y))
                above_point_cells.append((x, y))

                x += 2
                below_empty_cells.append((x, y))
                above_empty_cells.append((x, y))
            else:
                below_empty_cells.append((x, y))
                above_empty_cells.append((x, y))

                x += 2
                below_point_cells.append((x, y))
                above_point_cells.append((x, y))
        # print(tiling)
        # print(above_point_cells, above_empty_cells, above_possibly_empty)
        above_obstructions = [o for o in obstructions if not any(o.occupies(c) for c in above_empty_cells)]
        # for o in above_obstructions:
        #      print(o)
        above_tiling = Tiling(point_cells=above_point_cells,
                              possibly_empty=above_possibly_empty,
                              positive_cells=above_positive_cells,
                              obstructions=[o for o in obstructions
                                            if not any(o.occupies(c)
                                                       for c in above_empty_cells)])
        # print(above_tiling)
        below_tiling = Tiling(point_cells=below_point_cells,
                              possibly_empty=below_possibly_empty,
                              positive_cells=below_positive_cells,
                              obstructions=[o for o in obstructions
                                            if not any(o.occupies(c)
                                                       for c in below_empty_cells)])

        isolated_tilings.append((above_tiling, below_tiling))

    for i in range(2):

        # print("Isolated the point at {} in its col on the tiling".format(cell_to_be_isolated))
        # print(tiling.to_old_tiling())
        # print("it gave")
        # for t in [t[i] for t in isolated_tilings]:
        #     print(t.to_old_tiling())
        #     print()
        # print()
        # print("---------")
        yield BatchStrategy("Isolated the point at {} in its col".format(cell_to_be_isolated), [t[i] for t in isolated_tilings])


def powerset(l):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    return chain.from_iterable(combinations(l, r) for r in range(len(l)+1))
