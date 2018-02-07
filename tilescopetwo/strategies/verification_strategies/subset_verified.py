"""A strategy for checking if a tiling is a subset of the class."""

from comb_spec_searcher import VerificationStrategy
from permuta.descriptors import Basis


def subset_verified(tiling, basis, **kwargs):
    """Return a strategy if tiling is subset verified."""
    if tiling.dimensions == (1, 1):
        if one_by_one_verified(tiling, basis):
            return VerificationStrategy(formal_step="The tiling is a subset of the class.")
    elif all(ob.is_single_cell() for ob in tiling):
        if all(all(r.is_single_cell() for r in req) for req in tiling.requirements):
            return VerificationStrategy(formal_step="The tiling is a subset of the class.")

def one_by_one_verified(tiling, basis):
    """Return true if tiling is a subset of the Av(basis)."""
    if basis is not None:
        patts = Basis([ob.patt for ob in tiling])
        if basis == patts:
            return False
        return True
