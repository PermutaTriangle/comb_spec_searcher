from grids import Tiling


__all__ = ["basis_partitioning", "is_verified"]


_BASIS_PARTITIONING_CACHE = {}


def basis_partitioning(tiling, length, basis):
    """A cached basis partitioning function."""
    cache = _BASIS_PARTITIONING_CACHE.setdefault(tiling, {})
    if length not in cache:
        cache[length] = tiling.basis_partitioning(length, basis)
    return cache[length]


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

    partitioning = basis_partitioning(tiling, verification_length, basis)
    containing_perms, _ = partitioning

    # Tiling is verified if all perms avoid; i.e., none contain
    return not containing_perms
