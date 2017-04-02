
from permuta import Perm, PermSet
from grids import Tiling, Block, PositiveClass
from .inferral_class import InferralStrategy
from collections import defaultdict
from atrap.tools import basis_partitioning
from .jays_subclass_inferral import jays_subclass_inferral

def subclass_inferral(tiling, basis, **kwargs):
    '''Return a new tiling where all non-points have been inferred.
    This is a more primitive approach avoiding using the basis
    partitioning function'''
    total_points = tiling.total_points + len(tiling.other)

    '''This will be the inferred tiling that is returned'''
    inferred_tiling_dict = { }
    '''We will add a perm to this tiling, to determine if it is forbidden in a cell'''
    point_tiling_dict = {}
    for cell in tiling.point_cells:
        inferred_tiling_dict[cell] = Block.point
        point_tiling_dict[cell] = Block.point
    for cell, positive_class in tiling.other:
        point_tiling_dict[cell] = positive_class

    for cell, block in tiling.non_points:
        '''For all non point cells, we want to try and add to the original basis'''
        original_basis = list(block.basis)
        if isinstance(block, PositiveClass):
            temp_total_points = total_points - 1
        else:
            temp_total_points = total_points
        for length in range(1,len(basis[-1])):
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
                if any( perm.avoids(*basis) for perm in Tiling(point_tiling_dict).perms_of_length(inferral_length)):
                    point_tiling_dict.pop(cell)
                    if isinstance(block, PositiveClass):
                        point_tiling_dict[cell] = Block.point
                    continue
                original_basis.append(patt)
                point_tiling_dict.pop(cell)
                if isinstance(block, PositiveClass):
                    point_tiling_dict[cell] = Block.point
        '''We updated the inferred_tiling'''
        if Perm( (0,) ) in original_basis:
            continue
        if isinstance(block, PositiveClass):
            new_block = PositiveClass(PermSet.avoiding(original_basis))
        else:
            new_block = PermSet.avoiding(original_basis)

        inferred_tiling_dict[cell] = new_block



    inferred_tiling = Tiling(inferred_tiling_dict)
    # print("-------------------------------------------")
    # print(basis)
    # print(tiling)
    # print(jays_subclass_inferral(tiling,basis).tiling)
    # print(inferred_tiling)
    # assert jays_subclass_inferral(tiling,basis).tiling == InferralStrategy("After tiling subset inferral", inferred_tiling).tiling
    if not tiling == inferred_tiling:

        yield InferralStrategy("After tiling subset inferral", inferred_tiling)




'''CODE BELOW IS UNTESTED AND SEEMS BROKEN'''




def old_subclass_inferral(tiling, basis, basis_partitioning=basis_partitioning):
    """Return a new tiling where all non-points have been inferred."""

    # The containing/avoiding perms_of_cells dictionary
    perms_of_cells_dicts = (defaultdict(set), defaultdict(set))

    # We only need to check permutations up to this length because any longer
    # perm can be reduced to a perm of this length and still contain the patt
    # if it already did
    verification_length = tiling.total_points + len(basis[-1])
    verification_length += sum(1 for _, block in tiling.non_points if isinstance(block, PositiveClass))

    for length in range(verification_length + 1):
        # Get the partitioning into containing/avoiding perms
        partitions = basis_partitioning(tiling, length, basis)

        # For containing and avoiding
        for partition, perms_of_cells in zip(partitions, perms_of_cells_dicts):
            # For each perm and its associated info
            for cell_infos in partition.values():
                # Store for each cell its contribution to the perm
                #print(partition)
                #print(perms_of_cells)
                #print(cell_infos)
                for cell_info in cell_infos:
                    for cell, info in cell_info.items():
                        cell_perm, _, _ = info
                        perms_of_cells[cell].add(cell_perm)

    # Now we have for all cells, the ways they contributed perms to perm
    containing_perms_of_cells, avoiding_perms_of_cells = perms_of_cells_dicts

    # Keep all the points, no need to infer on them
    tiling_dict = {cell: Block.point for cell in tiling.point_cells}

    # However, for all non-points
    for cell, block in tiling.non_points:
        # If an element exclusively contributes to containing perms,
        # we add this element to the basis
        # print(cell, containing_perms_of_cells[cell], avoiding_perms_of_cells[cell])
        new_basis_elements = containing_perms_of_cells[cell] \
                           - avoiding_perms_of_cells[cell]

        #print(cell, block)
        #print()
        #print(containing_perms_of_cells[cell])
        #print()
        #print(avoiding_perms_of_cells[cell])
        #print()
        #print(new_basis_elements)
        #print()
        # If basis contains the point, the block will consist
        # solely of the empty perm, so no need to add to the new tiling
        if Perm((0,)) in new_basis_elements:
            continue

        # Add the new basis elements to the old basis elements
        new_basis = new_basis_elements.union(block.basis)
        #print(new_basis)
        #print()
        #print()
        #print()
        #print()

        # Create the new block for the new tiling
        new_block = PermSet.avoiding(new_basis)
        if isinstance(block, PositiveClass):
            # Positive classes remain positive
            new_block = PositiveClass(new_block)

        # Put the block into the cell of the new tiling
        tiling_dict[cell] = new_block
    new_tiling = Tiling(tiling_dict)
    return new_tiling
    # if not tiling == new_tiling:
    #     yield InferralStrategy("After tiling subset inferral", new_tiling)
