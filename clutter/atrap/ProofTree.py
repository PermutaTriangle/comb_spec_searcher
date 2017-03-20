import sys

from grids import Tiling, TilingTree, TilingTreeNode


class ProofTreeNode(TilingTreeNode):
    def __init__(self, tiling, children=[], verified_by=[], formal_step=""):
        super(ProofTreeNode, self).__init__(tiling, children)
        self.verified_by = list(verified_by)
        self.formal_step = formal_step

    def _to_json(self):
        attr_dict = super(ProofTreeNode, self)._to_json()
        attr_dict["verified_by"] = [tiling._to_json()
                                    for tiling
                                    in self.verified_by]
        return attr_dict

    @classmethod
    def _from_attr_dict(cls, attr_dict):
        result = cls(**cls._prepare_attr_dict(attr_dict))
        return result

    @classmethod
    def _prepare_attr_dict(cls, attr_dict):
        attr_dict = super(ProofTreeNode, cls)._prepare_attr_dict(attr_dict)
        attr_dict["verified_by"] = [Tiling._from_attr_dict(tiling_json)
                                    for tiling_json
                                    in attr_dict["verified_by"]]
        return attr_dict


class ProofTree(TilingTree):
    _NODE_CLASS = ProofTreeNode

    def pretty_print(self, file=sys.stdout):
        super(ProofTree, self).pretty_print(file=file)
        print("\nHere are the recursions\n", file=file)
        self.print_recursions(file)
        print("\n--------------------- END RECURSIONS", file=file)

    def print_recursions(self, file=sys.stdout):
        self._print_recursions(self.root, file)

    @classmethod
    def _prepare_attr_dict(cls, attr_dict):
        return super(ProofTree, cls)._prepare_attr_dict(attr_dict)

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
