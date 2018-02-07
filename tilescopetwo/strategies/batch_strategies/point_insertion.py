"""The point insertion strategy places either a point obstruction or the
point requirement into a cell"""

from grids_two import Tiling, Requirement
from permuta import Perm
from comb_spec_searcher import BatchStrategy

from permuta import Perm, PermSet

def all_point_insertions(tiling, **kwargs):
    for cell in tiling._possibly_empty:
        if any(all(req.occupies(cell) for req in reqlist) for reqlist in tiling.requirements):
            continue
        yield BatchStrategy(formal_step="Insert point requirement into cell {}.".format(cell),
                            tilings=[tiling.add_single_cell_obstruction(cell, Perm((0,))),
                                     tiling.add_single_cell_requirement(cell, Perm((0,)))])

def all_requirement_insertions(tiling, **kwargs):
    maxreqlen = kwargs.get('maxreqlen')
    patterns = kwargs.get('patterns')
    if len(tiling.requirements) > 1:
        return
    if maxreqlen is None:
        maxreqlen = 3

    for cell in tiling._possibly_empty:
        basis = [ob.patt for ob in tiling
                 if ob.is_single_cell() and ob.pos[0] == cell]

        for length in range(1, maxreqlen + 1):
            for patt in PermSet.avoiding(basis).of_length(length):
                yield BatchStrategy(
                    formal_step=(
                        "Inserting requirement {} in cell {}").format(patt, cell),
                    tilings=[tiling.add_single_cell_obstruction(cell, patt),
                             tiling.add_single_cell_requirement(cell, patt)])
