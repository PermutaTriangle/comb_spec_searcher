
from permuta import Perm, PermSet
from permuta.descriptors import Basis
from grids import Tiling, Block, PositiveClass
from atrap.tools import get_class, get_perms_to_check
from .inferral_class import InferralStrategy

import time

def cell_inferral(tiling, the_cell, input_set):
    point_cells = {}

    for cell, block in tiling:
        if block is Block.point:
            point_cells[cell] = block
        elif cell != the_cell and isinstance(block, PositiveClass):
            point_cells[cell] = Block.point

    max_length = max([0,len(input_set.basis[-1])-1])

    inferred_basis = input_set.basis
    # for length in range(1, max_length+1):
        # perm_set = get_class(inferred_basis)
    for patt in get_perms_to_check(inferred_basis):
        point_cells[the_cell] = PermSet([patt])
        T = Tiling(point_cells)

        # print("playing with:")
        # print(T)

        if all(perm not in input_set for perm in T.perms_of_length(len(point_cells) - 1 + len(patt))):
            inferred_basis = Basis(inferred_basis+(patt,))


    return inferred_basis



def jays_subclass_inferral(tiling, basis, **kwargs):
    """Return a new tiling where all non-points have been inferred."""

    # print("inferring...")
    # print(tiling)

    tiling_dict = {}

    # TODO: Shouldn't we pass this in instead of regenerating?
    input_set = get_class(basis)

    for cell, block in tiling:
        # print("\tinferrring (",cell,",",repr(block),")")
        if block is Block.point:
            tiling_dict[cell] = block
            # print("\t\tjust a point")
        else:
            inferred_basis = cell_inferral(tiling, cell, input_set)

            if Perm((0,)) in inferred_basis:
                continue

            if isinstance(block, PositiveClass):
                tiling_dict[cell] = PositiveClass(PermSet.avoiding(inferred_basis))
            else:
                tiling_dict[cell] = PermSet.avoiding(inferred_basis)

            # print("\t\t",repr(block),"\t--->\t",repr(tiling_dict[cell]))

    new_tiling = Tiling(tiling_dict)
    # print("new tiling:")
    # print(new_tiling)

    if not tiling == new_tiling:
        yield  InferralStrategy("After tiling subset inferral", new_tiling)
