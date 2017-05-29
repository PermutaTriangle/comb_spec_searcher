from atrap.tools import tiling_generates_avoider
from grids import PositiveClass
from .verification_class import VerificationStrategy


def is_empty(tiling, basis, basis_partitioning=None):
    '''This checks if for a tiling T, Av(B) intersected with T is the emptyset'''
    verification_length = tiling.total_points + len(basis[-1])
    verification_length += sum(1 for _, block in tiling.non_points if isinstance(block, PositiveClass))
    empty = True
    for length in range(verification_length + 1):
        if tiling_generates_avoider(tiling, length, basis):
            empty = False
            break
    if empty:
        yield VerificationStrategy("This tiling contains no avoiding perms")
