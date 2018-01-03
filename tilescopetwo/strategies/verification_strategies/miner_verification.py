from comb_spec_searcher import VerificationStrategy
from permuta import Perm
from permuta.descriptors import Basis

def miner_verified(tiling, basis, **kwargs):
    if ((tiling.dimensions[0] is 1 and tiling.dimensions[1] is 2) or
        (tiling.dimensions[0] is 2 and tiling.dimensions[1] is 1)):
        top = []
        bottom = []
        topbool = False
        bottombool = False
        for ob in tiling:
            if ob.is_single_cell():
                if ob.pos[0] == (0, 0):
                    bottom.append(ob.patt)
                else:
                    top.append(ob.patt)
            else:
                if topbool or bottombool:
                    return None
                if ob.patt == Perm((0, 1, 2)):
                    if ob.pos[0] == (0, 0) and ob.pos[1] == (0, 0):
                        bottombool = True
                    else:
                        topbool = True
                elif ob.patt == Perm((2, 1, 0)):
                    if ob.pos[1] == (0, 0) and ob.pos[2] == (0, 0):
                        bottombool = True
                    elif ob.pos[0] == (0, 1) and ob.pos[1] == (0, 1):
                        topbool = True
        if topbool:
            Basis(top) == Basis([Perm((0, 1, 2))])
            if Basis(bottom) != basis:
                return VerificationStrategy("Miner verified!")
        elif bottombool:
            Basis(bottom) == Basis([Perm((0, 1, 2))])
            if Basis(top) != basis:
                return VerificationStrategy("Miner verified!")
