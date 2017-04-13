from .equivalence_class import EquivalenceStrategy

from permuta.permutils.symmetry import reverse_set, inverse_set, rotate_set
from permuta import PermSet

from grids import Block, Tiling, PositiveClass

mem = {}
def all_symmetric_tilings( tiling, basis, **kwargs ):
    valid_symmetries = mem.get(tuple(basis))
    if valid_symmetries is None:
        basis = set(basis)
        valid_symmetries = []

        if inverse_set( basis ) == basis:
            valid_symmetries.append(inverse)

        if rotate_set( basis ) == basis:
            valid_symmetries.append(rotate_90)

        elif rotate_set( rotate_set( basis ) ) == basis:
            valid_symmetries.append( rotate_180 )

        mem[tuple(basis)] = valid_symmetries

    for symmetry in valid_symmetries:
        yield symmetry( tiling )

def rotate_90( tiling ):
    new_tiling_dict = {}
    height = tiling.dimensions.j
    width = tiling.dimensions.i
    for cell, block in tiling:
        if block is Block.point:
            new_block = Block.point
        else:
            new_basis = [ perm.rotate() for perm in block.basis ]

            new_block = PermSet.avoiding(new_basis)
            if isinstance(block, PositiveClass):
                new_block = PositiveClass( new_block )

        new_tiling_dict[ (cell.j, height - cell.i) ] = new_block
    return EquivalenceStrategy( "Tiling was rotated 90 degrees", Tiling(new_tiling_dict) )

def rotate_180( tiling ):
    new_tiling_dict = {}
    height = tiling.dimensions.j
    width = tiling.dimensions.i
    for cell, block in tiling:
        if block is Block.point:
            new_block = Block.point
        else:
            new_basis = [ perm._rotate_180() for perm in block.basis ]

            new_block = PermSet.avoiding(new_basis)
            if isinstance(block, PositiveClass):
                new_block = PositiveClass( new_block )

        new_tiling_dict[ (height - cell.i, width - cell.j) ] = new_block
    return EquivalenceStrategy( "Tiling was rotated 180 degrees", Tiling(new_tiling_dict) )

def inverse( tiling ):
    new_tiling_dict = {}
    height = tiling.dimensions.j
    width = tiling.dimensions.i
    for cell, block in tiling:
        if block is Block.point:
            new_block = Block.point
        else:
            new_basis = [ perm.inverse() for perm in block.basis ]

            new_block = PermSet.avoiding(new_basis)
            if isinstance(block, PositiveClass):
                new_block = PositiveClass( new_block )

        new_tiling_dict[ (cell.j, cell.i) ] = new_block
    return EquivalenceStrategy( "The inverse of the tiling", Tiling(new_tiling_dict) )
