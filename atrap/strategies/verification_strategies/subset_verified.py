from grids import Tiling
from atrap.tools import basis_partitioning
from .verification_class import VerificationStrategy
from .one_by_one_verification import one_by_one_verification

def subset_verified(tiling, basis):
    """Check that a tiling is a subset of Av(basis)."""
    if not isinstance(tiling, Tiling):
        raise TypeError

    if len(basis) < 1:
        return True

    if len(tiling) <= 1:
        one_by_one_verification(tiling, basis)

    else:
        # We only need to check permutations up to this length because any longer
        # perm can be reduced to a perm of this length and still contain the patt
        # if it already did
        if len(tiling) == tiling.total_points:
            verification_length = tiling.total_points
        else:
            verification_length = tiling.total_points + len(basis[-1])

        verified = True
        for length in range(tiling.total_points, verification_length + 1):
            partitions = basis_partitioning(tiling, length, basis)
            containing_perms, _ = partitions
            if containing_perms:
                verified = False
                break



        # Tiling is verified if all perms avoid; i.e., none contain
        if verified:
            yield VerificationStrategy( "The tiling is a subset of the subclass" )
