from grids import Tiling, PositiveClass
from permuta import PermSet
from .verification_class import VerificationStrategy

def is_one_by_one_verified(tiling, basis,**kwargs):
    if tiling.dimensions.i == 1 and tiling.dimensions.j == 1:
        if len(tiling) > 0:
            perm_class = tiling[(0,0)]
            if isinstance(perm_class, PositiveClass):
                perm_class = perm_class.perm_class
            if perm_class == PermSet.avoiding(basis):
                return False
        return True
    return False

def one_by_one_verification(tiling, basis, **kwargs):
    if is_one_by_one_verified(tiling, basis):
        yield VerificationStrategy( "Verified because it is a one by one tiling with a subclass" )
