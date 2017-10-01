from grids_two import Tiling
from comb_spec_searcher import InferralStrategy
from itertools import combinations, chain
from math import factorial
from collections import defaultdict


def subobstruction_inferral(tiling, **kwargs):
    addedobstructions = []
    removedcells = []
    for cell in tiling.positive_cells:
        obstructions = [ob.remove_cells((cell,))
                        for ob in tiling.obstructions
                        if sum(1 for _ in ob.points_in_cell(cell)) == 1]
        last = None
        for ob in sorted(obstructions):
            if ob == last:
                continue
            last = ob
            count = sum(1 for o in obstructions if o in ob)
            theocount = ((sum(1 for _ in ob.get_points_row(cell[1])) + 1) *
                         (sum(1 for _ in ob.get_points_col(cell[0])) + 1))
            if count == theocount:
                addedobstructions.append(ob)
                removedcells.append(cell)
    new_tiling = Tiling(point_cells=tiling.point_cells,
           positive_cells=tiling.positive_cells,
           possibly_empty=tiling.possibly_empty,
           obstructions=tiling.obstructions + tuple(addedobstructions))
    if tiling != new_tiling:
        yield InferralStrategy(
            ("The cells {} imply the reduction to the following obstructions: \n{}"
             ).format(removedcells, "\n".join(map(str, addedobstructions))),
             new_tiling)


# TODO: Discuss below with Henning and Tomas - giving weird results!
def powerset(S):
    return chain.from_iterable(combinations(S,n) for n in range(1,len(S) + 1))

def binomial(x, y):
    try:
        binom = factorial(x) // factorial(y) // factorial(x - y)
    except ValueError:
        binom = 0
    return binom

def interleaving_count_cells(ob, cells):
    rows = defaultdict(int)
    cols = defaultdict(int)
    for cell in cells:
        rows[cell[1]] += 1
        cols[cell[0]] += 1
    count = 1
    for row, row_count in rows.items():
        for col, col_count in cols.items():
            i = row_count
            j = col_count
            k = sum(1 for _ in ob.get_points_row(row))
            l = sum(1 for _ in ob.get_points_col(col))
            count = factorial(i) * factorial(j) * binomial(i + k, i) * binomial(j + l, j)
    return count

def super_subobstruction_inferral(tiling, **kwargs):
    addedobstructions = []
    removedcells = []
    for subset in powerset(tiling.positive_cells):
        obstructions = [ob.remove_cells(subset)
                        for ob in tiling.obstructions
                        if all(sum(1 for _ in ob.points_in_cell(cell)) == 1 for cell in subset)]

        other_obs = [(ob.remove_cells(subset), tuple(c for c in subset if not ob.occupies(c)))
                     for ob in tiling.obstructions
                     if all(sum(1 for _ in ob.points_in_cell(cell)) <= 1 for cell in subset)]
        last = None
        for ob in sorted(obstructions):
            last = ob
            count = sum(interleaving_count_cells(o, cells) for o, cells in other_obs if o in ob)

            theocount = interleaving_count_cells(ob, subset)

            # if len(subset) == 1:
            #     cell = subset[0]
            #     old_count = sum(1 for o in obstructions if o in ob)
            #     # if old_count != count:
            #         # print("Trying to remove:", ob)
            #         # print("Obstructions:")
            #         # print(other_obs)
            #         # for ob in obstructions:
            #         #     print(ob)
            #         # print("Using cell:", cell)
            #         # print(old_count, count)
            #         # print(theocount)
            #         # print(tiling)
            #     assert old_count == count
            #     old_theocount = ((sum(1 for _ in ob.get_points_row(cell[1])) + 1) *
            #                      (sum(1 for _ in ob.get_points_col(cell[0])) + 1))
            #     assert old_theocount == theocount

            if count == theocount:
                addedobstructions.append(ob)
                removedcells.append(tuple(subset))
                # if len(subset) > 1:
                #     print("")
                #
                #     print("Point cells:",tiling.point_cells)
                #     print("Positive cells:",tiling.positive_cells)
                #     print("Possible empty cells:",tiling.possibly_empty)
                #     print("Obstructions:")
                #     for o in tiling:
                #         print(o)
                #     print("From the subset of positive cells:", subset)
                #     print("We can add the obstruction:", ob)
                #     print("")

    new_tiling = Tiling(point_cells=tiling.point_cells,
           positive_cells=tiling.positive_cells,
           possibly_empty=tiling.possibly_empty,
           obstructions=tiling.obstructions + tuple(addedobstructions))

    # if any(len(x) > 2 for x in removedcells):
    #     print(tiling)
    #     print(("The cells {} imply the reduction to the following obstructions: \n{}").format(removedcells, "\n".join(map(str, addedobstructions))))
    if tiling != new_tiling:
        yield InferralStrategy(
            ("The cells {} imply the reduction to the following obstructions: \n{}"
             ).format(removedcells, "\n".join(map(str, addedobstructions))),
             new_tiling)
