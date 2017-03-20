

from atrap.strategies import all_cell_insertions
from atrap.strategies import row_and_column_separations
from atrap.strategies import all_row_and_col_placements

from grids import Tiling

from permuta import PermSet
from permuta.descriptors import Basis


INFINITY = 9999990  # It's computationally infeasible to reach this depth


class OrNode(object):
    def __init__(self):
        # The minimum distance down to an unexpanded frontier or node
        # If leaf node, then 0
        # If no such node below it, then INFINITY
        self.frontier_radius = 0
        self.children = []
        self.parents = []
        self.tiling = None
        self.siblings = None


class AndNode(object):
    def __init__(self, formal_step=""):
        self.formal_step = formal_step
        self.children = []
        self.parents = []


class MetaTree(object):
    def __init__(self, basis):
        # Store basis and input set
        self.basis = Basis(basis)
        self.input_set = PermSet.avoiding(basis)

        # Create the first tiling
        root_tiling = Tiling({(0, 0): self.input_set})

        # Create and store the root AND and OR node of the tree
        root_and_node = AndNode()
        formal_step = "We start off with a 1x1 tiling where the single block is the input set."
        root_and_node.formal_step = formal_step

        root_or_node = OrNode()
        root_or_node.tiling = root_tiling
        root_or_node.parents.append(root_and_node)
        root_or_node.siblings = [root_or_node]
        root_and_node.children.append(root_or_node)

        self.root_and_node = root_and_node
        self.root_or_node = root_or_node

        # Tiling to OR node dictionary
        self.tiling_cache = {root_tiling: root_or_node}

    def do_level(self, requested_depth=None):
        if requested_depth is None:
            self.do_level(self.root_or_node.frontier_radius + 1)
        else:
            self._or_helper(self.root_or_node, requested_depth)

    def _and_helper(self, root_and_node, requested_depth):
        for child_or_node in root_and_node.children:
            for sibling_or_node in child_or_node.siblings:
                self._or_helper(sibling_or_node, requested_depth - 1)

    def _or_helper(self, root_or_node, requested_depth):
        if root_or_node.frontier_radius >= requested_depth:
            # No expansion will happen below this node, we can short-circuit.
            # If not this case, then we know that we need to expand a node in
            # the tree below this node or the node itself.
            return
        elif root_or_node.frontier_radius > 0:
            # We need to move further down
            for child_and_node in root_or_node.children:
                self._and_helper(child_and_node, requested_depth)
        elif root_or_node.frontier_radius == 0:
            # We need to expand before moving further down
            #for tiling, child_batch in root_or_node.tilings.items():
            #    child_batch.extend(all_cell_insertions(tiling))
            for cell_insertion in all_cell_insertions(root_or_node.tiling):
                formal_step, strategy = cell_insertion
                child_and_node = AndNode(formal_step)
                for tiling in strategy:
                    child_or_node = self.tiling_cache.get(tiling)
                    if child_or_node is None:
                        child_or_node = OrNode()
                        child_or_node.tiling = tiling
                        child_or_node.siblings = []
                        for sibling_tiling in all_row_and_col_placements(tiling):
                            if sibling_tiling:
                                sibling_tiling = sibling_tiling[0]
                            else:
                                continue
                            sibling_node = self.tiling_cache.get(sibling_tiling)
                            if sibling_node is None:
                                sibling_node = OrNode()
                                sibling_node.tiling = tiling
                                sibling_node.siblings = child_or_node.siblings
                                child_or_node.siblings.append(sibling_node)
                                self.tiling_cache[sibling_tiling] = sibling_node
                            else:
                                raise RuntimeError("you need to do coding")
                        self.tiling_cache[tiling] = child_or_node
                    child_or_node.parents.append(child_and_node)
                    child_and_node.children.append(child_or_node)
                child_and_node.parents.append(root_or_node)
                root_or_node.children.append(child_and_node)
            self._propogate_frontier_radius(root_or_node)
            self._or_helper(root_or_node, requested_depth)
        else:
            raise RuntimeError("Unexpected do_level case")

    def _propogate_frontier_radius(self, root_or_node):
        ## Get minimum frontier radius of children OR nodes
        #frontier_radius = min(child_or_node.frontier_radius
        #                      for child_or_node
        #                      in root_and_node.children)
        #frontier_radius += 1
        ## Propagate it up
        #for parent_or_node in root_and_node.parents:
        frontier_radius = INFINITY
        for child_and_node in root_or_node.children:
            for child_or_node in child_and_node.children:
                for sibling in child_or_node.siblings:
                    frontier_radius = min(frontier_radius, sibling.frontier_radius)
        if frontier_radius != INFINITY:
            frontier_radius += 1
        if frontier_radius > root_or_node.frontier_radius:
            root_or_node.frontier_radius = frontier_radius
            for parent_and_node in root_or_node.parents:
                for parent_or_node in parent_and_node.parents:
                    self._propogate_frontier_radius(parent_or_node)
