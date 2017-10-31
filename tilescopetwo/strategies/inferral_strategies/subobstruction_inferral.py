from grids_two import Tiling
from comb_spec_searcher import InferralStrategy
from itertools import combinations, chain
from math import factorial
from collections import defaultdict
from copy import copy
from itertools import chain



def subobstruction_inferral_rec(tiling, **kwargs):

    positive_cells = list(tiling.positive_cells.union(tiling.point_cells))

    subobstructions = set()
    for obstruction in tiling.obstructions:
        if all(c not in positive_cells for c in obstruction.pos):
            continue
        for subobstruction in obstruction.all_subobs():
            subobstructions.add(subobstruction)

    adding = []
    for subobstruction in sorted(subobstructions):
        if any(ob in subobstruction for ob in adding):
            continue
        if can_add_obstruction(tiling, subobstruction, copy(positive_cells)):
            adding.append(subobstruction)

    # if adding:
    #     print("To the tiling:")
    #     print(tiling.to_old_tiling())
    #     print(tiling)
    #     print("We are adding:")
    #     for o in adding:
    #         print(o)

    new_tiling = Tiling(point_cells=tiling.point_cells,
                        positive_cells=tiling.positive_cells,
                        possibly_empty=tiling.possibly_empty,
                        obstructions=tiling.obstructions + tuple(adding))

    return InferralStrategy(
        ("Adding the following obstructions: \n{}"
         ).format("\n".join(map(str, adding))),
         new_tiling)

def can_add_obstruction(tiling, obstruction, positive_cells):
    while positive_cells:
        cell = positive_cells.pop()
        if obstruction.occupies(cell):
            continue
        obs = list(obstruction.insert_point(cell))
        if all(any(o in ob for o in tiling.obstructions) for ob in obs):
            return True
        return all(can_add_obstruction(tiling, ob, positive_cells) for ob in obs)
    return any(o in obstruction for o in tiling.obstructions)


def subobstruction_inferral(tiling, **kwargs):
    addedobstructions = []
    removedcells = []
    for cell in chain(tiling.positive_cells, tiling.point_cells):
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
                if not ob.patt:
                    print("adding empty")
                    print("theocount", theocount)
                    print("count", count)
                addedobstructions.append(ob)
                removedcells.append(cell)
    new_tiling = Tiling(point_cells=tiling.point_cells,
           positive_cells=tiling.positive_cells,
           possibly_empty=tiling.possibly_empty,
           obstructions=tiling.obstructions + tuple(addedobstructions))
    if tiling != new_tiling:
        return InferralStrategy(
            ("The cells {} imply the reduction to the following obstructions: \n{}"
             ).format(removedcells, "\n".join(map(str, addedobstructions))),
             new_tiling)




#
# # TODO: Discuss below with Henning and Tomas - giving weird results!
# def powerset(S):
#     return chain.from_iterable(combinations(S,n) for n in range(1,len(S) + 1))
#
# def binomial(x, y):
#     try:
#         binom = factorial(x) // factorial(y) // factorial(x - y)
#     except ValueError:
#         binom = 0
#     return binom
#
# def interleaving_count_cells(ob, cells):
#     '''Return the number of ways that an obstruction can be interleaved with
#     points in the cells.'''
#     rows = defaultdict(int)
#     cols = defaultdict(int)
#     for cell in cells:
#         rows[cell[1]] += 1
#         cols[cell[0]] += 1
#     count = 1
#     for row, row_count in rows.items():
#         i = row_count
#         k = sum(1 for _ in ob.get_points_row(row))
#         count *= factorial(i) * binomial(i + k, i)
#     for col, col_count in cols.items():
#         j = col_count
#         l = sum(1 for _ in ob.get_points_col(col))
#         count *= factorial(j) * binomial(j + l, j)
#     return count
#
# def super_subobstruction_inferral(tiling, **kwargs):
#     addedobstructions = []
#     removedcells = []
#     positive_cells = tuple(tiling.positive_cells.union(tiling.point_cells))
#     obstructions = set()
#     d = dict()
#     for subset in powerset(positive_cells):
#         obstructions.update(ob.remove_cells(subset)
#                             for ob in tiling.obstructions
#                             if all(sum(1 for _ in ob.points_in_cell(cell)) == 1 for cell in subset))
#         for ob in tiling.obstructions:
#             if all(sum(1 for _ in ob.points_in_cell(cell)) == 1 for cell in subset):
#                 d[ob.remove_cells(subset)] = subset
#
#     for ob in sorted(obstructions):
#         # print("Trying to get:", ob)
#         theocount = interleaving_count_cells(ob, [c for c in positive_cells if not ob.occupies(c)])
#         # print("Theoretical:", theocount)
#         count = 0
#         print("Now considering", ob)
#         for o in tiling:
#             if any(sum(1 for _ in o.points_in_cell(cell)) > 1 for cell in positive_cells):
#                 continue
#             new_o = o.remove_cells(positive_cells)
#             if new_o in ob:
#                 print("new_o:", new_o, "came from", o)
#                 unaccounted_for = [c for c in positive_cells if not o.occupies(c)]
#                 occs = len(list(new_o.occurrences_in(ob)))
#                 print(occs)
#                 print(occs * interleaving_count_cells(ob, unaccounted_for))
#                 # print(o)
#                 # print(occs)
#                 # print(occs * interleaving_count_cells(ob, unaccounted_for))
#                 count += occs * interleaving_count_cells(ob, unaccounted_for)
#         # print("Actual:", count)
#
#         subset = d[ob]
#         if len(subset) == 1:
#             cell = subset[0]
#             old_count = sum(1 for o in obstructions if o in ob)
#             if old_count != count:
#                 print("Trying to add:", ob)
#                 print("Obstructions:")
#                 print("Using cell:", cell)
#                 print(old_count, count)
#                 old_theocount = ((sum(1 for _ in ob.get_points_row(cell[1])) + 1) *
#                                  (sum(1 for _ in ob.get_points_col(cell[0])) + 1))
#                 print(old_theocount, theocount)
#                 print(tiling)
#                 for o in tiling:
#                     print(o)
#                 assert old_theocount == theocount
#             old_theocount = ((sum(1 for _ in ob.get_points_row(cell[1])) + 1) *
#                              (sum(1 for _ in ob.get_points_col(cell[0])) + 1))
#             assert old_count == count
#             old_theocount = ((sum(1 for _ in ob.get_points_row(cell[1])) + 1) *
#                              (sum(1 for _ in ob.get_points_col(cell[0])) + 1))
#             assert old_theocount == theocount
#
#         if count == theocount:
#             subset = d[ob]
#             if ob not in addedobstructions and len(subset) > 1:
#                 print("")
#                 print(tiling.to_old_tiling())
#                 print("Point cells:",tiling.point_cells)
#                 print("Positive cells:",tiling.positive_cells)
#                 print("Possible empty cells:",tiling.possibly_empty)
#                 print("Obstructions:")
#                 for o in tiling:
#                     print(o)
#                 print("We can add the obstruction:", ob)
#                 print("Due to points in cells:", subset)
#                 print("Theoretical:", interleaving_count_cells(ob, positive_cells))
#
#             addedobstructions.append(ob)
#             removedcells.append(tuple(subset))
#
#
#     new_tiling = Tiling(point_cells=tiling.point_cells,
#            positive_cells=tiling.positive_cells,
#            possibly_empty=tiling.possibly_empty,
#            obstructions=tiling.obstructions + tuple(addedobstructions))
#
#     # if any(len(x) > 2 for x in removedcells):
#     #     print(tiling)
#     #     print(("The cells {} imply the reduction to the following obstructions: \n{}").format(removedcells, "\n".join(map(str, addedobstructions))))
#     if tiling != new_tiling:
#         yield InferralStrategy(
#             ("The cells {} imply the reduction to the following obstructions: \n{}"
#              ).format(removedcells, "\n".join(map(str, addedobstructions))),
#              new_tiling)
