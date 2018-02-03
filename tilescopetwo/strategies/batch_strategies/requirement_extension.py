"""The requirement extension strategy tries to extend a requirement by one point
all possible ways"""

from comb_spec_searcher import Strategy
from permuta import PermSet, Perm
from grids_two import Obstruction, Requirement, Tiling

def all_requirement_extensions(tiling, **kwargs):
    # maxreqlen is the maximum length it tries to extend the requirement to
    maxreqlen = kwargs.get('maxreqlen')
    patterns = kwargs.get('patterns')
    if maxreqlen is None:
        maxreqlen = 3

    if not tiling.requirements:
        return

    for req in tiling.requirements:
        # It only tries to extend requirements that are definitely required
        # i.e. there is only one requirement in the OR list of requirements.
        if len(req) > 1:
            continue
        req = req[0]

        # Right now it only tries to extend requirements that are contained in a single cell
        if not req.is_single_cell():
            continue

        if len(req) >= maxreqlen:
            continue

        basis = [ob.patt for ob in tiling
                 if ob.is_single_cell() and ob.pos[0] == req.pos[0]]

        for patt in PermSet.avoiding(basis).of_length(len(req) + 1):
            if req.patt in patt:
                yield Strategy(
                    formal_step=(
                        "Extending requirement {} to {} in cell {}").format(req, patt, req.pos[0]),
                    objects=[tiling.add_single_cell_obstruction(req.pos[0], patt),
                             tiling.add_single_cell_requirement(req.pos[0], patt),],
                    workable=[True, True])
