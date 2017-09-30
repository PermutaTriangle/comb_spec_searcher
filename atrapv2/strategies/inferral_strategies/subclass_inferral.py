"""Determine what class in cells based on points already placed."""

from permuta import Perm, PermSet
from grids import Tiling, Block, PositiveClass
from comb_spec_searcher import InferralStrategy


def subclass_inferral(tiling, basis=None, **kwargs):
    """
    Return a new tiling where all non-points have been inferred.

    This is a more primitive approach avoiding using the basis
    partitioning function.
    """
    total_points = tiling.total_points + tiling.total_other

    '''This will be the inferred tiling that is returned'''
    inferred_tiling_dict = {}
    '''We will add a perm to this tiling, to determine if it is forbidden in a cell'''
    point_tiling_dict = {}
    for cell in tiling.point_cells:
        inferred_tiling_dict[cell] = Block.point
        point_tiling_dict[cell] = Block.point
    for cell, positive_class in tiling.other:
        point_tiling_dict[cell] = Block.point

    for cell, block in tiling.non_points:
        '''For all non point cells, we want to try and add to the original basis'''
        original_basis = list(block.basis)
        if isinstance(block, PositiveClass):
            temp_total_points = total_points - 1
        else:
            temp_total_points = total_points
        for length in range(1, len(basis[-1])):
            '''The maximum length of pattern that can be added is the size of the last'''
            inferral_length = temp_total_points + length
            for patt in PermSet.avoiding(original_basis).of_length(length):
                '''For each potential pattern, to add it to the basis, we need that it
                always creates a bad permutation with all the points
                TODO Say that 01 and 012 are both avoiders of original_basis.
                If we add 01 to the original basis, will 012 not be considered
                because original_basis is updated and that changes what we are
                looping over?'''
                point_tiling_dict[cell] = PermSet([patt])
                if any(perm.avoids(*basis) for perm in Tiling(point_tiling_dict).perms_of_length(inferral_length)):
                    point_tiling_dict.pop(cell)
                    if isinstance(block, PositiveClass):
                        point_tiling_dict[cell] = Block.point
                    continue
                original_basis.append(patt)
                point_tiling_dict.pop(cell)
                if isinstance(block, PositiveClass):
                    point_tiling_dict[cell] = Block.point
        '''We updated the inferred_tiling'''
        if isinstance(block, PositiveClass):
            if Perm((0,)) in original_basis:
                new_block = Block.point
            else:
                new_block = PositiveClass(PermSet.avoiding(original_basis))
        else:
            if Perm((0,)) in original_basis:
                continue
            new_block = PermSet.avoiding(original_basis)

        inferred_tiling_dict[cell] = new_block

    inferred_tiling = Tiling(inferred_tiling_dict)
    # print("-------------------------------------------")
    # print(basis)
    # print(tiling)
    # print(jays_subclass_inferral(tiling,basis).tiling)
    # print(inferred_tiling)
    # assert ( jays_subclass_inferral(tiling,basis).tiling
    #         == InferralStrategy("After tiling subset inferral", inferred_tiling).tiling)
    if not tiling == inferred_tiling:

        yield InferralStrategy("After tiling subset inferral", inferred_tiling)
