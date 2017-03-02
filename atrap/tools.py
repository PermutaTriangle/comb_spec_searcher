from grids import Tiling


def is_verified(tiling, basis):
    """Check that a tiling is a subset of Av(basis)."""
    if not isinstance(tiling, Tiling):
        raise TypeError

    if len(basis) < 1:
        return True

    # We only need to check permutations up to this length because any longer
    # perm can be reduced to a perm of this length and still contain the patt
    # if it already did
    verification_length = tiling.total_points + len(basis[-1])

    partitioning = tiling.basis_partitioning(verification_length, basis)
    containing_perms, _ = partitioning

    # Tiling is verified if all perms avoid; i.e., none contain
    return not containing_perms
