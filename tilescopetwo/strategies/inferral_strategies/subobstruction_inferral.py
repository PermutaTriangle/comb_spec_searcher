from grids_two import Tiling
from .inferral_class import InferralStrategy
from itertools import combinations, chain
from math import factorial


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

#
# # TODO: Discuss below with Henning and Tomas - giving weird results!
# def powerset(S):
#     return chain.from_iterable(combinations(S,n) for n in range(min(3, len(S) + 1)))
#
# def super_subobstruction_inferral(tiling, **kwargs):
#     addedobstructions = []
#     removedcells = []
#     for subset in powerset(tiling.positive_cells):
#         obstructions = [ob.remove_cells(subset)
#                        for ob in tiling.obstructions
#                        if all(sum(1 for _ in ob.points_in_cell(cell)) == 1 for cell in subset)]
#         last = None
#         for ob in sorted(obstructions):
#             last = ob
#             count = sum(1 for o in obstructions if o in ob)
#             theocount = 1
#             for cell in subset:
#                 theocount *= ((sum(1 for _ in ob.get_points_row(cell[1])) + 1) *
#                               (sum(1 for _ in ob.get_points_col(cell[0])) + 1))
#             if count == theocount:
#                 addedobstructions.append(ob)
#                 removedcells.append(tuple(subset))
#
#     new_tiling = Tiling(point_cells=tiling.point_cells,
#            positive_cells=tiling.positive_cells,
#            possibly_empty=tiling.possibly_empty,
#            obstructions=tiling.obstructions + tuple(addedobstructions))
#
#     if any(len(x) > 2 for x in removedcells):
#         print(tiling)
#         print(("The cells {} imply the reduction to the following obstructions: \n{}").format(removedcells, "\n".join(map(str, addedobstructions))))
#     if tiling != new_tiling:
#         yield InferralStrategy(
#             ("The cells {} imply the reduction to the following obstructions: \n{}"
#              ).format(removedcells, "\n".join(map(str, addedobstructions))),
#              new_tiling)
