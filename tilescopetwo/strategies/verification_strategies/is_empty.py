from atrap.tools import tiling_generates_avoider
from grids import PositiveClass

def is_empty_strategy(tiling, basis, **kwargs):
    if tiling.is_empty():
        return True
    else:
        old_tiling = tiling.to_old_tiling()
        verification_length = old_tiling.total_points + len(basis[-1])
        verification_length += sum(1 for _, block in old_tiling.non_points if isinstance(block, PositiveClass))
        for length in range(verification_length + 1):
            if tiling_generates_avoider(old_tiling, length, basis):
                return False
        if empty:
            print("Emptiness not due to an empty obstruction:")
            print(tiling)
            return True
