import sys

from grids import TilingTree, TilingTreeNode


class ProofTreeNode(TilingTreeNode):
    def __init__(self, tiling, children=[]):
        super(ProofTreeNode, self).__init__(tiling, children)
        self.verified_by = []
        self.formal_step = ""
        self.label = None

    def _to_json(self):
        attr_dict = super(ProofTreeNode, self)._to_json()
        attr_dict["verified_by"] = [tiling._to_json()
                                    for tiling
                                    in self.verified_by]
        return attr_dict


class ProofTree(TilingTree):
    __NODE_CLASS = ProofTreeNode

    def pretty_print(self, file=sys.stdout):
        super(ProofTree, self).pretty_print(file=file)
        print("\nHere are the recursions\n", file=file)
        self.print_recursions(file)
        print("\n--------------------- END RECURSIONS", file=file)

    def print_recursions(self, file=sys.stdout):
        self._print_recursions(self.root, file)
    
    def _print_recursions(self, root, file):
        if root.verified_by:
            print("-----------------\n\nTILING:", file=file)
            print(root.tiling, file=file)
            print(root.formal_step, file=file)
            print(file=file)
            print("Recursively verified by:", file=file)
            for tiling in root.verified_by:
                print(tiling, file=file)
        for child in root.children:
            self._print_recursions(child, file)
