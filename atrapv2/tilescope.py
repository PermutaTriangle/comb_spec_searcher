"""
  _______ __
 /_  __(_) /__ ___ _______  ___  ___
  / / / / / -_|_-</ __/ _ \/ _ \/ -_)
 /_/ /_/_/\__/___/\__/\___/ .__/\__/
                         /_/
"""

from .equivdb import EquivalenceDB
from .ruledb import RuleDB
from .tilingdb import TilingDB
from .tilingqueue import TilingQueue
from .LRUCache import LRUCache
from .ProofTree import ProofTree
from .ProofTree import ProofTreeNode
from .Helpers import taylor_expand
from grids import Tiling
from permuta import Av
from permuta.descriptors import Basis
from atrap.strategies import is_empty
from .tree_searcher import prune, proof_tree_dfs
from collections import defaultdict


from atrap.strategies import BatchStrategy
from atrap.strategies import EquivalenceStrategy
from atrap.strategies import InferralStrategy
from atrap.strategies import RecursiveStrategy
from atrap.strategies import VerificationStrategy

class TileScope(object):
    """
    An instance of TileScope is used to build up knowledge about tilings with
    respect to the given basis.
    """
    def __init__(self,
                 basis,
                 batch_strategies=None,
                 equivalence_strategies=None,
                 inferral_strategies=None,
                 recursive_strategies=None,
                 verification_strategies=None,
                 non_interleaving_recursion=False,
                 symmetry=False,
                 early_splitting_only=False,
                 start_tiling=None):
        self.basis = Basis(basis)
        self.equivdb = EquivalenceDB()
        self.ruledb = RuleDB()
        self.tilingdb = TilingDB()
        self.tilingqueue = TilingQueue()
        self._inferral_cache = LRUCache(100000)
        if start_tiling is None:
            start_tiling = Tiling({(0,0): Av(basis)})

        self.tilingdb.add(start_tiling, expandable=True)
        self.tilingqueue.add_to_working(self.tilingdb.get_label(start_tiling))

        self.start_label = self.tilingdb.get_label(start_tiling)


        if batch_strategies is not None:
            self.strategy_generators = batch_strategies
        else:
            self.batch_strategy_generators = [all_cell_insertions]
        if equivalence_strategies is not None:
            self.strategy_generators.extend(equivalence_strategies)
        else:
            self.strategy_generators.extend([all_point_placements])
        if recursive_strategies is not None:
            self.strategy_generators.extend(recursive_strategies)
        else:
            self.strategy_generators.extend([components])
        if inferral_strategies is not None:
            self.inferral_strategy_generators = inferral_strategies
        else:
            self.inferral_strategy_generators = [empty_cell_inferral]
        if verification_strategies is not None:
            self.verification_strategy_generators = verification_strategies
        else:
            self.verification_strategy_generators = [one_by_one_verification]

    def try_verify(self, tiling):
        label = self.tilingdb.get_label(tiling)
        if self.equivdb.is_verified(label):
            return
        for verification_generator in self.verification_strategy_generators:
            for verification_strategy in verification_generator(tiling,
                                                                basis=self.basis,
                                                                basis_partitioning=self._basis_partitioning):
                if not isinstance(verification_strategy, VerificationStrategy):
                    raise TypeError("Attempting to verify with non VerificationStrategy.")
                formal_step = verification_strategy.formal_step
                self.tilingdb.set_verified(tiling, formal_step)
                self.tilingdb.set_strategy_verified(tiling)
                label = self.tilingdb.get_label(tiling)
                self.equivdb.update_verified(label)
                return

    def is_empty(self, tiling):
        label = self.tilingdb.get_label(tiling)
        if self.tilingdb.is_empty(tiling) is not None:
            return self.tilingdb.is_empty(tiling)
        for strategy in is_empty(tiling, self.basis):
            self.tilingdb.set_empty(tiling)
            return True
        self.tilingdb.set_empty(tiling, empty=False)
        return False


    def _inferral(self, tiling):
        """Return fully inferred tiling using InferralStrategies."""
        inferred_tiling = self._inferral_cache.get(tiling)
        semi_inferred_tilings = []
        if inferred_tiling is None:
            inferred_tiling = tiling
            fully_inferred = False
            for inferral_strategy_generator in self.inferral_strategy_generators:
                '''For each inferral strategy,'''
                if fully_inferred:
                    break
                for inferral_strategy in inferral_strategy_generator(inferred_tiling,
                                                                     basis=self.basis,
                                                                     basis_partitioning=self._basis_partitioning):
                    if not isinstance(inferral_strategy, InferralStrategy):
                        raise TypeError("Attempted to infer on a non InferralStrategy")
                    formal_step = inferral_strategy.formal_step
                    '''we infer as much as possible about the tiling and replace it.'''
                    soon_to_be_tiling = inferral_strategy.tiling

                    if soon_to_be_tiling is inferred_tiling:
                        continue

                    if soon_to_be_tiling in self._inferral_cache:
                        soon_to_be_tiling = self._inferral_cache.get(soon_to_be_tiling)
                        semi_inferred_tilings.append(inferred_tiling)
                        inferred_tiling = soon_to_be_tiling
                        fully_inferred = True
                        break
                    else:
                        semi_inferred_tilings.append(inferred_tiling)
                        inferred_tiling = soon_to_be_tiling
            for semi_inferred_tiling in semi_inferred_tilings:
                self._inferral_cache.set(semi_inferred_tiling, inferred_tiling)
                # '''Clean up the cache'''
                # if semi_inferred_tiling in self._basis_partitioning_cache:
                #     self._basis_partitioning_cache.pop(semi_inferred_tiling)
            self._inferral_cache.set(inferred_tiling, inferred_tiling)
        return inferred_tiling

    def _basis_partitioning(self, tiling, length, basis, function_name=None):
        # no caching for now - shortcut to see things working!
        return tiling.basis_partitioning(length, basis)

    def do_level(self,cap=None):
        for label in self.tilingqueue.do_level(cap=cap):
            if self.tilingdb.is_expanded(label) or self.tilingdb.is_verified(label):
                continue
            elif not self.tilingdb.is_expandable(label):
                continue
            tiling = self.tilingdb.get_tiling(label)
            print(tiling)
            for generator in self.strategy_generators:
                for strategy in generator(tiling,
                                          basis=self.basis,
                                          basis_partitioning=self._basis_partitioning):
                    if isinstance(strategy, BatchStrategy):
                        tilings = strategy.tilings
                    elif isinstance(strategy, EquivalenceStrategy):
                        tilings = [strategy.tiling]
                    elif isinstance(strategy, RecursiveStrategy):
                        tilings = strategy.tilings
                        back_maps = strategy.back_maps
                    formal_step = strategy.formal_step
                    tilings = [self._inferral(t) for t in tilings]
                    tilings = [t for t in tilings if not self.is_empty(t)]
                    # put information about deleted empty tilings into the formal step

                    # If we have an equivalent strategy
                    if len(tilings) == 1:
                        other_label = self.tilingdb.get_label(tilings[0])
                        self.equivdb.union(label, other_label, formal_step)
                        self.tilingqueue.add_to_working(other_label)
                        if isinstance(strategy, EquivalenceStrategy) or isinstance(strategy, BatchStrategy):
                            self.tilingdb.set_expandable(other_label)
                        self.try_verify(tilings[0])
                    else:
                        for t in tilings:
                            self.try_verify(t)
                        end_labels = [self.tilingdb.get_label(t) for t in tilings]
                        self.ruledb.add(label, end_labels, formal_step)
                        for x in end_labels:
                            if isinstance(strategy, BatchStrategy):
                                # TODO: When labelled occurrences, we can also work from decomposed tilings
                                # so you can add to the queue all the time.
                                self.tilingqueue.add_to_next(x)
                                self.tilingdb.set_expandable(x)
                        if isinstance(strategy, RecursiveStrategy):
                            if label not in self.ruledb.back_maps:
                                self.ruledb.back_maps[label] = {}
                            self.ruledb.back_maps[label][tuple(sorted(end_labels))] = back_maps
            self.tilingdb.set_expanded(label)

    def find_tree(self):
        rules_dict = defaultdict(set)
        # convert rules to equivalent labels
        for rule in self.ruledb:
            first, rest = rule
            first = self.equivdb[first]
            rest = tuple(sorted(self.equivdb[x] for x in rest))
            # this means union
            rules_dict[first] |= set((tuple(rest),))
        # add an empty rule, that represents verified in the tree searcher
        for x in self.tilingdb.verified_labels():
            verified_label = self.equivdb[x]
            rules_dict[verified_label] |= set(((),))

        # Prune all unverifiable labels (recursively)
        rules_dict = prune(rules_dict)

        already_verified = len(set([self.equivdb[x] for x in self.tilingdb.verified_labels()]))
        print("Number previously verified: " + str(already_verified))
        print("Number now verified: " + str(len(rules_dict.keys())))
        print("Difference: " + str(len(rules_dict.keys()) - already_verified))
        for label in rules_dict.keys():
            self.equivdb.update_verified(label)

        # only verified labels in rules_dict, in particular, there is a tree if
        # the start label is in the rules_dict
        if self.equivdb[self.start_label] in rules_dict:
            print("A tree was found! :)")
            _, proof_tree = proof_tree_dfs(rules_dict, root=self.equivdb[self.start_label])
            print(proof_tree)
            return proof_tree
        else:
            print("No tree was found. :(")

    def get_proof_tree(self, count=False):
        proof_tree_node = self.find_tree()
        if proof_tree_node is not None:
            proof_tree = ProofTree(self._get_proof_tree(proof_tree_node))
            print(proof_tree.to_json())
            if count:
                f = proof_tree.get_genf()
                print(f)
            return proof_tree
        else:
            print("There is no proof tree yet.")

    def _get_proof_tree(self, proof_tree_node, in_label=None):
        label = proof_tree_node.label
        children_labels = sorted([x.label for x in proof_tree_node.children])
        if in_label is not None:
            in_tiling = self.tilingdb.get_tiling(in_label)
        if children_labels:
            for rule in self.ruledb:
                start, ends = rule
                if self.equivdb[start] == label:
                    equiv_labels = [self.equivdb[x] for x in ends]
                    if sorted(equiv_labels) == children_labels:
                        # we have a match!
                        formal_step = self.ruledb.explanation(start, ends)
                        out_tiling = self.tilingdb.get_tiling(start)
                        if in_label is None:
                            in_label = start
                            in_tiling = out_tiling
                        relation = self.equivdb.get_explanation(in_label, start)
                        identifier = label
                        children = [self._get_proof_tree(proof_tree_node.children[i], next_label) for i, next_label in enumerate(ends)]
                        back_maps = None
                        if start in self.ruledb.back_maps:
                            ends = tuple(sorted(ends))
                            if ends in self.ruledb.back_maps[start]:
                                back_maps = self.ruledb.back_maps[start][ends]
                        return ProofTreeNode(formal_step, in_tiling, out_tiling, relation, identifier, children=children, recurse=back_maps, strategy_verified=False)
        else:
            # we are verified by strategy or recursion
            for x in self.tilingdb:
                if self.equivdb[x] == label and self.tilingdb.is_strategy_verified(x):
                    formal_step = "Verified"
                    children = []
                    if in_label is None:
                        in_label = start
                        in_tiling = out_tiling
                    relation = self.equivdb.get_explanation(in_label, x)
                    out_tiling = self.tilingdb.get_tiling(x)
                    identifier = label
                    return ProofTreeNode(formal_step, in_tiling, out_tiling, relation, identifier, children=children, recurse=None, strategy_verified=True)
            # else we are recursively verified
            formal_step = "recurse"
            if in_label is None:
                in_tiling = self.tilingdb.get_tiling(in_label)
                out_tiling = in_tiling
            else:
                in_tiling = self.tilingdb.get_tiling(in_label)
                out_tiling = in_tiling
            identifier = label
            relation = self.equivdb.get_explanation(in_label, in_label)
            return ProofTreeNode(formal_step, in_tiling, out_tiling, relation, identifier, children=None, recurse=None, strategy_verified=False)
