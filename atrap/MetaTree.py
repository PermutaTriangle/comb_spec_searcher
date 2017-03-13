

from atrap.strategies import all_cell_insertions
from atrap.strategies import row_and_column_separations

from grids import Tiling

from permuta import PermSet
from permuta.descriptors import Basis


NODAL_STRATEGIES = []#all_point_placements, row_column_separations]
BRANCHING_STRATEGIES = [all_cell_insertions]


class MetaTreeNode(object):
    def __init__(self):
        # The minimum distance down to an unexpanded frontier node
        # If 0, then leaf node
        self.frontier_radius = 0


class MetaTree(object):
    def __new__(cls, basis):
        # TODO: Nice dispatching?
        if basis is describing_finite:
            return FiniteClassMetaTree(basis)
        else:
            return GenericMetaTree(basis)


class GenericMetaTree(object):
    def __init__(self,
                 basis,
                 nodal_strategies=NODAL_STRATEGIES,
                 branching_strategies=BRANCHING_STRATEGIES):
        # Store the strategies
        self.node_strategies = node_strategies
        self.branching_strategies = branching_strategies

        # Store basis and input set
        self.basis = Basis(basis)
        self.input_set = PermSet.avoiding(basis)

        # Create the first tiling
        root_tiling = Tiling({(0, 0): input_set})

        # Create the root of the tree
        self.root_node = MetaTreeNode()
        self.root_node.tilings = [root_tiling]
        self.root_node.parents = []


#    def do_level(self, level_number=None):
#        if level_number is None:
#            do_level(ONE MORE THAN THE LEVEL)
#        else:
#            for chilren of root:
#                do_level for each
