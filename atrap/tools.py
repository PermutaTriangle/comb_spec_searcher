from collections import defaultdict
from grids import Tiling, Block, PositiveClass
from permuta import Perm, PermSet
from itertools import chain
from permuta.permutils import rotate_90_clockwise_set, rotate_180_clockwise_set, rotate_270_clockwise_set
from permuta.permutils import inverse_set, complement_set, reverse_set, antidiagonal_set

__all__ = ("basis_partitioning", "is_verified", "tiling_inferral")


# _BASIS_PARTITIONING_CACHE = {}
#
# _OCCURRENCES_OF_CACHE = {}


_CLASS_CACHE = {}

_PERMS_TO_CHECK = {}


# def basis_partitioning(tiling, length, basis):
#     """A cached basis partitioning function."""
#     key = (tiling, basis)
#     cache = _BASIS_PARTITIONING_CACHE.setdefault(key, {})
#     if length not in cache:
#         cache[length] = tiling.basis_partitioning(length, basis)
#     else:
#         # print('**cache repeat!!**')
#         pass
#     return cache[length]
#
# def basis_partitioning(tiling, length, basis):
#     return tiling.basis_partitioning(length, basis)

def tiling_generates_container(tiling, length, basis):
    return any(not perm.avoids(*basis) for perm in tiling.perms_of_length(length))

def tiling_generates_avoider(tiling, length, basis):
    return any(perm.avoids(*basis) for perm in tiling.perms_of_length(length))

def cells_of_occurrences(tiling, basis, basis_partitioning=None):
    return tuple( set( chain( *cells_of_occurrences_by_perms(tiling, basis, basis_partitioning=basis_partitioning) ) ) )

def cells_of_occurrences_by_perms(tiling, basis, basis_partitioning=None):
    '''A cached occurrences of patts function for a tiling. The occurrences are
    stored as a set of occurrence by perm it is in. An occurrence is returned
    as a set of cells containing the patt.  '''
    all_cells_of_occurrences_by_perms= set()

    verification_length = tiling.total_points + len(basis[-1])
    verification_length += sum(1 for _, block in tiling.non_points if isinstance(block, PositiveClass))
    for perm_length in range(verification_length + 1):
        containing_perms, _ = basis_partitioning(tiling, perm_length, basis, "cells_of_occurrences_by_perms")
        for perm, cell_infos in containing_perms.items():
            perms_occurrences = set()
            if len(cell_infos) != 1:
                print(cell_infos)
                print(tiling)
                print("OH NO! You tried a recursive strategy on a tiling that creates duplicates :(")
                assert len(cell_infos) == 1
            for cell_info in cell_infos:
                cell_perm = [ 0 for i in range(len(perm))]
                for cell in cell_info.keys():
                    _, _, cell_indices = cell_info[cell]
                    for index in cell_indices:
                        cell_perm[index] = cell

                for patt in basis:
                    for occurrence in perm.occurrences_of(patt):
                        cells_of_occurrence = set( cell_perm[i] for i in occurrence )
                        # print('for',patt,'adding:',tuple(cells_of_occurrence))
                        perms_occurrences.add(tuple(cells_of_occurrence))
                        # print('\t\tresult:',perms_occurrences)

                # print('\n\n*current output:',all_cells_of_occurrences_by_perms)
                # print('*adding:',tuple(perms_occurrences))
                all_cells_of_occurrences_by_perms.add(tuple(perms_occurrences))
                # print('*result:',all_cells_of_occurrences_by_perms,'\n\n')

    return all_cells_of_occurrences_by_perms




# def basis_partitioning(tiling, length, basis):
#     return tiling.basis_partitioning(length, basis)

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

    partitions = basis_partitioning(tiling, verification_length, basis, "is_verified")
    containing_perms, _ = partitions

    # Tiling is verified if all perms avoid; i.e., none contain
    return not containing_perms

def empty_cell_inferral(tiling, basis):

    new_tiling_dict = dict(tiling)

    point_cells = {}
    for cell, block in tiling:
        if block is Block.point or isinstance(block, PositiveClass):
            point_cells[cell] = Block.point

    for cell, block in tiling.classes:
        point_cells[cell] = Block.point
        verification_length = len(point_cells)
        point_cell_tiling = Tiling(point_cells)
        point_cells.pop(cell)
        if any( perm.avoids(*basis) for perm in point_cell_tiling.perms_of_length(verification_length) ):
            continue
        new_tiling_dict.pop(cell)

    return Tiling(new_tiling_dict)

def one_by_one_verified(tiling, basis):
    if tiling.dimensions.i == 1 and tiling.dimensions.j == 1:
        if len(tiling) > 0:
            perm_class = tiling[(0,0)]
            if isinstance(perm_class, PositiveClass):
                perm_class = perm_class.perm_class
            if perm_class == PermSet.avoiding(basis):
                return False
        return True
    return False

def one_by_one_verification(tiling, basis):
    if one_by_one_verified(tiling, basis):
        yield "one by one tiling, surely you can handle it", []


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
        partitions = basis_partitioning(tiling, length, basis, "tiling_inferral")

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

def get_class(basis):
    # print(basis)
    if basis not in _CLASS_CACHE:
        _CLASS_CACHE[basis] = PermSet.avoiding(basis)
    return _CLASS_CACHE[basis]

def get_perms_to_check(basis):
    if basis not in _PERMS_TO_CHECK:
        to_check = list(basis)
        perm_class = get_class(basis)
        length_to_check = len(basis[-1])-1

        for length in range(1, length_to_check+1):
            for patt in perm_class.of_length(length):
                if any(b.contains(patt) for b in basis):
                    to_check.append(patt)

        _PERMS_TO_CHECK[basis] = PermSet(to_check)

    return _PERMS_TO_CHECK[basis]


def find_symmetries(basis):
    """
    Return a list of symmetry functions, where the basis is closed with respect to the symmetries.

    The functions returned return a symmetry of the input tiling. The symmetry
    use will be closed  return corresponding symmetry of tiling.
    """
    valid_symmetries = []
    basis = set(basis)
    if rotate_90_clockwise_set(basis) == basis:
        valid_symmetries.append(rotate_90_clockwise)
    if rotate_180_clockwise_set(basis) == basis:
        valid_symmetries.append(rotate_180_clockwise)
    if rotate_270_clockwise_set(basis) == basis:
        valid_symmetries.append(rotate_270_clockwise)
    if inverse_set(basis) == basis:
        valid_symmetries.append(inverse)
    if antidiagonal_set(basis) == basis:
        valid_symmetries.append(antidiagonal)
    if reverse_set(basis) == basis:
        valid_symmetries.append(reverse)
    if complement_set(basis) == basis:
        valid_symmetries.append(complement)

    return valid_symmetries


def rotate_90_clockwise(tiling):
    """Return tiling rotated 90 degrees clockwise."""
    new_tiling_dict = {}
    height = tiling.dimensions.j
    for cell, block in tiling:
        if block is Block.point:
            new_block = Block.point
        else:
            new_basis = [perm._rotate_right() for perm in block.basis]
            new_block = PermSet.avoiding(new_basis)
            if isinstance(block, PositiveClass):
                new_block = PositiveClass(new_block)
        new_tiling_dict[(cell.j, height - cell.i)] = new_block
    return Tiling(new_tiling_dict)


def rotate_180_clockwise(tiling):
    """Return tiling rotated 180 degrees clockwise."""
    new_tiling_dict = {}
    height = tiling.dimensions.j
    width = tiling.dimensions.i
    for cell, block in tiling:
        if block is Block.point:
            new_block = Block.point
        else:
            new_basis = [perm._rotate_180() for perm in block.basis]
            new_block = PermSet.avoiding(new_basis)
            if isinstance(block, PositiveClass):
                new_block = PositiveClass(new_block)
        new_tiling_dict[(height - cell.i, width - cell.j)] = new_block
    return Tiling(new_tiling_dict)


def rotate_270_clockwise(tiling):
    """Return tiling rotated 270 degrees clockwise."""
    new_tiling_dict = {}
    width = tiling.dimensions.i
    for cell, block in tiling:
        if block is Block.point:
            new_block = Block.point
        else:
            new_basis = [perm._rotate_left() for perm in block.basis]
            new_block = PermSet.avoiding(new_basis)
            if isinstance(block, PositiveClass):
                new_block = PositiveClass(new_block)
        new_tiling_dict[(width-cell.j, cell.i)] = new_block
    return Tiling(new_tiling_dict)


def inverse(tiling):
    """Return inverse of tiling."""
    new_tiling_dict = {}
    for cell, block in tiling:
        if block is Block.point:
            new_block = Block.point
        else:
            new_basis = [perm.inverse() for perm in block.basis]
            new_block = PermSet.avoiding(new_basis)
            if isinstance(block, PositiveClass):
                new_block = PositiveClass(new_block)
        new_tiling_dict[(cell.j, cell.i)] = new_block
    return Tiling(new_tiling_dict)


def reverse(tiling):
    """Return reverse of tiling."""
    new_tiling_dict = {}
    width = tiling.dimensions.i
    for cell, block in tiling:
        if block is Block.point:
            new_block = Block.point
        else:
            new_basis = [perm.reverse() for perm in block.basis]
            new_block = PermSet.avoiding(new_basis)
            if isinstance(block, PositiveClass):
                new_block = PositiveClass(new_block)
        new_tiling_dict[(width-cell.i, cell.j)] = new_block
    return Tiling(new_tiling_dict)


def antidiagonal(tiling):
    """Return antidiagonal of tiling."""
    new_tiling_dict = {}
    height = tiling.dimensions.j
    width = tiling.dimensions.i
    for cell, block in tiling:
        if block is Block.point:
            new_block = Block.point
        else:
            new_basis = [perm.flip_antidiagonal() for perm in block.basis]
            new_block = PermSet.avoiding(new_basis)
            if isinstance(block, PositiveClass):
                new_block = PositiveClass(new_block)
        new_tiling_dict[(width-cell.j, height-cell.i)] = new_block
    return Tiling(new_tiling_dict)


def complement(tiling):
    """Return complement of tiling."""
    new_tiling_dict = {}
    height = tiling.dimensions.j
    for cell, block in tiling:
        if block is Block.point:
            new_block = Block.point
        else:
            new_basis = [perm.complement() for perm in block.basis]
            new_block = PermSet.avoiding(new_basis)
            if isinstance(block, PositiveClass):
                new_block = PositiveClass(new_block)
        new_tiling_dict[(cell.i, height-cell.j)] = new_block
    return Tiling(new_tiling_dict)
