

from atrap.strategies import all_cell_insertions
from atrap.strategies import row_and_column_separations

from grids import Tiling

from permuta import PermSet
from permuta.descriptors import Basis


NODAL_STRATEGIES = []#all_point_placements, row_column_separations]
BRANCHING_STRATEGIES = [all_cell_insertions]


INFINITY = 9999990  # It's computationally infeasible to reach this depth


class MetaTreeNode(object):
    def __init__(self):
        # The minimum distance down to an unexpanded frontier node
        # If leaf node, then 0
        # If no such node below it, then INFINITY
        self.frontier_radius = 0


class MetaTree(object):
    def __new__(cls, basis):
        # TODO: Nice dispatching?
        if not basis:
            return FiniteClassMetaTree(basis)
        else:
            return GenericMetaTree(basis)


class GenericMetaTree(object):
    def __init__(self,
                 basis,
                 nodal_strategies=NODAL_STRATEGIES,
                 branching_strategies=BRANCHING_STRATEGIES):
        # Store the strategies
        self.nodal_strategies = nodal_strategies
        self.branching_strategies = branching_strategies

        # Store basis and input set
        self.basis = Basis(basis)
        self.input_set = PermSet.avoiding(basis)

        # Create the first tiling
        root_tiling = Tiling({(0, 0): self.input_set})

        # Create the root of the tree
        root_node = MetaTreeNode()
        root_node.tilings = {root_tiling: []}
        root_node.parents = []
        self.root_node = root_node

        # Global tiling to node dictionary
        self.tiling_cache = {root_tiling: root_node}

    def do_level(self, requested_depth=None):
        if requested_depth is None:
            self.do_level(self.root_node.frontier_radius + 1)
        else:
            self._do_level_helper(self.root_node, requested_depth)

    def _do_level_helper(self, root, requested_depth):
        if root.frontier_radius >= requested_depth:
            # No expansion will happen below this node, we can short-circuit.
            # If not this case, then we know that we need to expand a node in
            # the tree below this node or the node itself.
            return
        elif root.frontier_radius > 0:
            # We need to move further down
            pass
        elif root.frontier_radius == 0:
            # We need to expand before moving further down
            for tiling, child_batch in root.tilings.items():
                child_batch.extend(all_cell_insertions(tiling))
        else:
            raise RuntimeError("Unexpected do_level case")
