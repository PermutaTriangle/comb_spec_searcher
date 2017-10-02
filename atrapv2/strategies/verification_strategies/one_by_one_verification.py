"""A strategy that tests if a tiling is one by one verified."""


from grids import PositiveClass, Block
from permuta import PermSet, Perm
from comb_spec_searcher import VerificationStrategy


def is_one_by_one_verified(tiling, basis=None, **kwargs):
    """Return True if tiling is one by one and a subset of the class."""
    if tiling.dimensions.i == 1 and tiling.dimensions.j == 1:
        if len(tiling) > 0:
            perm_class = tiling[(0, 0)]
            if isinstance(perm_class, PositiveClass):
                if perm_class is Block.point and Perm((0,)).avoids(*basis):
                    return True
                perm_class = perm_class.perm_class
            if perm_class == PermSet.avoiding(basis):
                return False
        return True
    return False


def one_by_one_verification(tiling, basis, **kwargs):
    """Yield a verification strategy if one by one verified."""
    if is_one_by_one_verified(tiling, basis):
        yield VerificationStrategy("Verified because it is a one by one tiling with a subclass")
