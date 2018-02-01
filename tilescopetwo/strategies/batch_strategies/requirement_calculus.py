"""The requirement calculus strategy takes an OR list of requirements and
splits it into multiple tilings such that it satisfies the OR list."""

from comb_spec_searcher import BatchStrategy
from permuta import PermSet, Perm
from grids_two import Obstruction, Requirement, Tiling

def requirement_calculus(tiling, **kwargs):
    if not tiling.requirements:
        return

    for i, reqs in enumerate(tiling.requirements):
        if len(reqs) == 1:
            continue

        obstruction_list = []
        tiling_list = []
        for req in reqs:
            tiling_list.append(Tiling(tiling._point_cells,
                                 tiling._positive_cells,
                                 tiling._possibly_empty,
                                 tiling._obstructions + tuple(obstruction_list),
                                 [req_list for j, req_list in enumerate(tiling.requirements) if i != j]
                                 + [[req]]))
            obstruction_list.append(Obstruction(req.patt, req.pos))

        yield BatchStrategy(
            formal_step=(
                "Calculus of requirement list {}").format(reqs),
                tilings=tiling_list)

    '''
        for req in reqs:
            tiling_list.append(Tiling(tiling._point_cells,
                                 tiling._positive_cells,
                                 tiling._possibly_empty,
                                 tiling._obstructions + obstruction_list,
                                 [req_list for j, req_list in enumerate(tiling.requirements) if i != j]
                                 + [req]))
            obstruction_list.append(Obstruction(req.patt, req.pos))

            yield BatchStrategy(
                formal_step=(
                    "Either we contain the requirement {} or we avoid it").format(req),
                    objects=[Tiling(tiling._point_cells,
                                    tiling._positive_cells,
                                    tiling._possibly_empty,
                                    tiling._obstructions,
                                    [req_list for j, req_list in enumerate(tiling.requirements) if i != j]
                                    + [req]),
                             Tiling(tiling._point_cells,
                                    tiling._positive_cells,
                                    tiling._possibly_empty,
                                    tiling._obstructions + [Obstruction(req.patt, req.pos)],
                                    [req_list for j, req_list in enumerate(tiling.requirements) if i != j])])'''
