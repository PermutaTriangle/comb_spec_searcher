"""
 .--------'      .            .-.               .--------'
(_)   /   .-.   /       .--.-'                 (_)   /..-.     .-.  .--.    .-
     /    `-'  /   .-. (  (_).-.  .-._..-.   .-.    /    )   (    /    )`-'
    /    /    /  ./.-'_ `-. (    (   ) /  )./.-'_  /    /     \  /    /
 .-/.__.(__._/_.-(__.'_    ) `---'`-' /`-' (__.'.-/._  (   .   )(    /
(_/  `-              (_.--'          /         (_/  `-  `-' `-'  `-.'
"""

from tilescopetwo.strategies import is_empty_strategy

from grids_two import Obstruction, Tiling

from grids import Cell

from permuta import Perm
from permuta.descriptors import Basis

from comb_spec_searcher import CombinatorialSpecificationSearcher

from comb_spec_searcher.ProofTree import ProofTree, ProofTreeNode
from comb_spec_searcher.objectqueue import ObjectQueue


class TileScopeTWO(CombinatorialSpecificationSearcher):
    """
    An instance of TileScope is used to build up knowledge about tilings with
    respect to the given basis.
    """
    def __init__(self,
                 basis,
                 strategy_pack=None,
                 interleaving_decomposition=True,
                 symmetry=False,
                 compress=False,
                 objectqueue=ObjectQueue,
                 start_tiling=None):
        """Initialise TileScope."""
        if isinstance(basis, str):
            self.basis = Basis([Perm([int(c) for c in p])
                                for p in basis.split('_')])
        else:
            self.basis = Basis(basis)

        if symmetry:
            # A list of symmetry functions of tilings.
            # raise NotImplementedError("Symmetries don't exist for obstructions yet.")
            symmetries = [Tiling.inverse, Tiling.reverse, Tiling.complement,
                          Tiling.antidiagonal, Tiling.rotate90,
                          Tiling.rotate180, Tiling.rotate270]
        else:
            symmetries = []

        if start_tiling is None:
            start_tiling = Tiling(possibly_empty=[(0,0)], obstructions=[Obstruction.single_cell(patt, (0,0)) for patt in self.basis])

        function_kwargs = {"basis": self.basis,
                           "interleaving_decomposition": interleaving_decomposition}

        CombinatorialSpecificationSearcher.__init__(self,
                                            start_object=start_tiling,
                                            strategy_pack=strategy_pack,
                                            symmetry=symmetries,
                                            compress=compress,
                                            objectqueue=ObjectQueue,
                                            is_empty_strategy=is_empty_strategy,
                                            function_kwargs=function_kwargs)


    def _get_proof_tree(self, proof_tree_node, in_label=None):
        """
        Recursive function for returning the root node of the proof tree.

        The only difference from original is the 'to_old_tiling()' call.
        """
        label = proof_tree_node.label
        children_labels = sorted([x.label for x in proof_tree_node.children])
        if in_label is not None:
            in_tiling = self.objectdb.get_object(in_label)
        if children_labels:
            for rule in self.ruledb:
                start, ends = rule
                if self.equivdb.equivalent(start, label):
                    equiv_labels = [self.equivdb[x] for x in ends]
                    if sorted(equiv_labels) == children_labels:
                        # we have a match!
                        formal_step = self.ruledb.explanation(start, ends)
                        out_tiling = self.objectdb.get_object(start)
                        if in_label is None:
                            in_label = start
                            in_tiling = out_tiling
                        relation = self.equivdb.get_explanation(in_label, start)
                        identifier = label
                        children = []
                        for next_label in ends:
                            for child in proof_tree_node.children:
                                if self.equivdb.equivalent(next_label, child.label):
                                    children.append(self._get_proof_tree(child, next_label))
                                    break
                        back_maps = None
                        if start in self.ruledb.back_maps:
                            ends = tuple(sorted(ends))
                            if ends in self.ruledb.back_maps[start]:
                                back_maps = self.ruledb.back_maps[start][ends]
                                back_maps = [{Cell(*x): Cell(*y) for x,y in bm.items()} for bm in back_maps]
                        return ProofTreeNode(formal_step,
                                             in_tiling.to_old_tiling(),
                                             out_tiling.to_old_tiling(),
                                             relation,
                                             identifier,
                                             children=children,
                                             recurse=back_maps,
                                             strategy_verified=False)
        else:
            # we are verified by strategy or recursion
            for oth_label in self.objectdb:
                if (self.equivdb.equivalent(oth_label, label)
                        and self.objectdb.is_strategy_verified(oth_label)):
                    formal_step = self.objectdb.verification_reason(oth_label)
                    children = []
                    if in_label is None:
                        in_label = oth_label
                        in_tiling = out_tiling
                    relation = self.equivdb.get_explanation(in_label, oth_label)
                    out_tiling = self.objectdb.get_object(oth_label)
                    identifier = label
                    return ProofTreeNode(formal_step,
                                         in_tiling.to_old_tiling(),
                                         out_tiling.to_old_tiling(),
                                         relation,
                                         identifier,
                                         children=children,
                                         recurse=None,
                                         strategy_verified=True)
            # else we are recursively verified
            formal_step = "recurse" # this formal step is needed as hard coded in Arnar's code.
            if in_label is None:
                in_tiling = self.objectdb.get_object(in_label)
                out_tiling = in_tiling
            else:
                in_tiling = self.objectdb.get_object(in_label)
                out_tiling = in_tiling
            identifier = label
            relation = self.equivdb.get_explanation(in_label, in_label)
            return ProofTreeNode(formal_step,
                                 in_tiling.to_old_tiling(),
                                 out_tiling.to_old_tiling(),
                                 relation,
                                 identifier,
                                 children=None,
                                 recurse=None,
                                 strategy_verified=False)
