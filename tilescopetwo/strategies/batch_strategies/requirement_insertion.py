from comb_spec_searcher import Strategy
from permuta import PermSet, Perm
from grids_two import Obstruction, Requirement, Tiling


def all_requirement_insertions(tiling, basis, **kwargs):
    if tiling.dimensions != (1, 1):
        return

    if tiling.requirements and (len(tiling.requirements) != 1 or
                                len(tiling.requirements[0]) != 1):
        return

    if ((0, 0) not in tiling.positive_cells and
            (0, 0) not in tiling.possibly_empty):
        return

    maxreqlen = kwargs.get('maxreqlength')
    patterns = kwargs.get('patterns')

    if not tiling.requirements:
        req = Requirement.single_cell(Perm(), (0, 0))
    else:
        req = tiling.requirements[0][0]

    if not patterns and maxreqlen and len(req) >= maxreqlen:
        return
    elif patterns and not maxreqlen:
        if not any(patt.contains(req.patt) for patt in patterns):
            raise ValueError(("Requirement pattern {} not contained in any of "
                             "the target patterns {}").format(req.patt,
                                                              patterns))

    for patt in PermSet.avoiding(basis).of_length(len(req) + 1):
        if patterns and not any(p.contains(patt) for p in patterns):
            continue
        yield Strategy(
            formal_step=(
                "Inserting requirement {} into cell {}").format(patt, (0, 0)),
            objects=[Tiling(tiling.point_cells,
                            tiling.positive_cells,
                            tiling.possibly_empty,
                            tiling.obstructions + (
                                Obstruction.single_cell(patt, (0, 0)),),
                            tiling.requirements),
                     Tiling(tiling.point_cells,
                            tiling.positive_cells | {(0, 0)},  # Make cell
                            tiling.possibly_empty - {(0, 0)},  # positive
                            tiling.obstructions,
                            [[Requirement.single_cell(patt, (0, 0))]])],
            workable=[False, True])
