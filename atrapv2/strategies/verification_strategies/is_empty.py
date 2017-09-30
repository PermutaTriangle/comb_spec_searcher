"""A verification strategy for dealing with tilings that only generate containers."""


from atrap.tools import tiling_generates_avoider
from grids import PositiveClass
from comb_spec_searcher import VerificationStrategy


def is_empty_strategy(tiling, basis=None, basis_partitioning=None, **kwargs):
    """Yield VerificationStrategy if for a tiling T, Av(B) intersected with T is the emptyset."""
    verification_length = tiling.total_points + len(basis[-1])
    verification_length += sum(1 for _, block in tiling.non_points if isinstance(block, PositiveClass))

    for length in range(verification_length + 1):
        if tiling_generates_avoider(tiling, length, basis):
            return False
    return True
