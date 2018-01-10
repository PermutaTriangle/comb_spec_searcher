from comb_spec_searcher import VerificationStrategy
from permuta import Perm
from permuta.descriptors import Basis

def miner_verified(tiling, basis, **kwargs):
    if ((tiling.dimensions[0] is 1 and tiling.dimensions[1] is 2) or
        (tiling.dimensions[0] is 2 and tiling.dimensions[1] is 1)):
        top = []
        bottom = []
        topbool = None
        bottombool = None
        for ob in tiling:
            if ob.is_single_cell():
                if ob.pos[0] == (0, 0):
                    bottom.append(ob.patt)
                else:
                    top.append(ob.patt)
            else:
                if topbool is not None or bottombool is not None:
                    return None
                if ob.patt == Perm((0, 1, 2)):
                    if ob.pos[0] == (0, 0) and ob.pos[1] == (0, 0):
                        bottombool = 0
                    else:
                        topbool = 0
                elif ob.patt == Perm((2, 1, 0)):
                    if ob.pos[1] == (0, 0) and ob.pos[2] == (0, 0):
                        bottombool = 1
                    elif ob.pos[0] == (0, 1) and ob.pos[1] == (0, 1):
                        topbool = 1
                    else:
                        return None
                elif ob.patt == Perm((0, 2, 1)):
                    if ob.pos[1] == ob.pos[2]:
                        topbool = 1
                    else:
                        return None
                elif ob.patt == Perm((1, 0, 2)):
                    if ob.pos[0] == ob.pos[1]:
                        bottombool = 1
                    else:
                        return None
                elif ob.patt == Perm((1, 2, 0)):
                    if ob.pos[0] == (0, 0) and ob.pos[1] == (0, 0):
                        bottombool = 0
                    elif ob.pos[0] == (0, 1) and ob.pos[1] == (0, 1):
                        topbool = 0
                    else:
                        return None
                elif ob.patt == Perm((2, 0, 1)):
                    if ob.pos[1] == (0, 0) and ob.pos[2] == (0, 0):
                        bottombool = 0
                    elif ob.pos[1] == (1, 0) and ob.pos[2] == (0, 0):
                        topbool = 0
                    else:
                        return None

                else:
                    return None
        if topbool is not None:
            topbasis = Basis(top)
            if ((topbool == 0 and topbasis == Basis([Perm((0, 1, 2))]))
                or (topbool == 1 and topbasis == Basis([Perm((2, 1, 0))]))):
                return VerificationStrategy("Miner verified!")
        elif bottombool is not None:
            bottombasis = Basis(bottom)
            if ((bottombool == 0 and Basis(bottom) == Basis([Perm((0, 1, 2))]))
                or (bottombool == 1 and bottombasis == Basis([Perm((2, 1, 0))]))):
                return VerificationStrategy("Miner verified!")
