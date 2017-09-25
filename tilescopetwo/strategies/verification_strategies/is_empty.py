from atrap.tools import tiling_generates_avoider
from grids import PositiveClass
from .verification_class import VerificationStrategy

def is_empty(tiling, basis):
    old_tiling = tiling.to_old_tiling()
    verification_length = old_tiling.total_points + len(basis[-1])
    verification_length += sum(1 for _, block in old_tiling.non_points if isinstance(block, PositiveClass))
    empty = True
    for length in range(verification_length + 1):
        if tiling_generates_avoider(old_tiling, length, basis):
            empty = False
            break
    if empty:
        print(old_tiling)
        print(tiling)
        yield VerificationStrategy("This tiling contains no avoiding perms")
