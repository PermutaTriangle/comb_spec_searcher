


from grids import Tiling

from permuta import PermSet
from permuta.descriptors import Basis


class MetaTree(object):
    def __init__(self, basis):
        # Store basis and input set
        self.basis = Basis(basis)
        self.input_set = PermSet.avoiding(basis)

        root_tiling = Tiling({(0, 0): input_set})
