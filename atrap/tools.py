from collections import defaultdict
from grids import Tiling, Block, PositiveClass
from permuta import Perm, PermSet


__all__ = ["basis_partitioning", "is_verified", "tiling_inferral"]


_BASIS_PARTITIONING_CACHE = {}


def basis_partitioning(tiling, length, basis):
    """A cached basis partitioning function."""
    key = (tiling, basis)
    cache = _BASIS_PARTITIONING_CACHE.setdefault(key, {})
    if length not in cache:
        cache[length] = tiling.basis_partitioning(length, basis)
    return cache[length]

def basis_partitioning(tiling, length, basis):
    return tiling.basis_partitioning(length, basis)

def is_verified(tiling, basis):
    """Check that a tiling is a subset of Av(basis)."""
    if not isinstance(tiling, Tiling):
        raise TypeError

    if len(basis) < 1:
        return True

    # We only need to check permutations up to this length because any longer
    # perm can be reduced to a perm of this length and still contain the patt
    # if it already did
    # TODO: if tiling.total_points is greater than len(basis[-1]) and it only
    #       contains points then this fails.
    verification_length = tiling.total_points + len(basis[-1])

    partitions = basis_partitioning(tiling, verification_length, basis)
    containing_perms, _ = partitions

    # Tiling is verified if all perms avoid; i.e., none contain
    return not containing_perms


def tiling_inferral(tiling, basis):
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

    return Tiling(tiling_dict)
