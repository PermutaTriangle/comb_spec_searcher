"""A strategy for checking if a tiling is a subset of the class."""

from .verification_class import VerificationStrategy
from permuta.descriptors import Basis


def subset_verified(tiling, basis):
    """Return a strategy if tiling is subset verified."""
    if tiling.dimensions == (1, 1):
        if one_by_one_verified(tiling, basis):
            yield VerificationStrategy(formal_step="The tiling is a subset of the class.")
    if all(ob.is_single_cell() for ob in tiling):
        yield VerificationStrategy(formal_step="The tiling is a subset of the class.")

def one_by_one_verified(tiling, basis):
    """Return true if tiling is a subset of the Av(basis)."""
    patts = Basis([ob.patt for ob in tiling])
    if basis == patts:
        return True
    return False
