from grids_two import Tiling
from .inferral_class import InferralStrategy


def subobstruction_inferral(tiling, **kwargs):

    addedobstructions = []
    removedcells = []
    for cell in tiling.positive_cells:
        obstructions = [ob.remove_cells((cell,))
                        for ob in tiling.obstructions if ob.occupies(cell)]
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
    return InferralStrategy(
        ("The cells {} imply the reduction to the following obstructions: \n{}"
         ).format(removedcells, "\n".join(map(str, addedobstructions))),
        Tiling(point_cells=tiling.point_cells,
               positive_cells=tiling.positive_cells,
               possibly_empty=tiling.possibly_empty,
               obstructions=tiling.obstructions + tuple(addedobstructions)))
