from grids import Tiling, PositiveClass
from atrap.tools import tiling_generates_container
from .verification_class import VerificationStrategy
from .one_by_one_verification import one_by_one_verification

def subset_verified(tiling, basis, basis_partitioning=None):
    """Check that a tiling is a subset of Av(basis)."""
    if not isinstance(tiling, Tiling):
        raise TypeError

    if len(basis) < 1:
        return True

    if len(tiling) <= 1:
        for verification_strategy in one_by_one_verification(tiling, basis):
            yield verification_strategy
        return

    else:
        # We only need to check permutations up to this length because any longer
        # perm can be reduced to a perm of this length and still contain the patt
        # if it already did
        verified = True
        if len(tiling) == tiling.total_points:
            verification_length = tiling.total_points
            if tiling_generates_container(tiling, verification_length, basis):
                verified = False
        else:
            verification_length = tiling.total_points + len(basis[-1])
            verification_length += sum(1 for _, block in tiling.non_points if isinstance(block, PositiveClass))

            '''
            We can start searching for bad permutations at length tiling.total_points
            since the tiling has already been inferred
            '''
            for length in range(tiling.total_points, verification_length + 1):
                if tiling_generates_container(tiling, length, basis):
                    verified = False
                    break
                # partitions = basis_partitioning(tiling, length, basis)
                # containing_perms, _ = partitions
                # if containing_perms:
                #     verified = False
                #     break



        # Tiling is verified if all perms avoid; i.e., none contain
        if verified:
            yield VerificationStrategy( "The tiling is a subset of the subclass" )
