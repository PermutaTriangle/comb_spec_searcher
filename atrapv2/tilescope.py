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
from permuta import Av, Perm
from permuta.descriptors import Basis
from atrap.strategies import is_empty
from .tree_searcher import prune, proof_tree_dfs
from collections import defaultdict

import tqdm
import sys

from atrap.tools import find_symmetries

from .strategies import Strategy
from .strategies import InferralStrategy
from .strategies import VerificationStrategy

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
        # symmetry, early_splitting_only, non_interleaving_recursion are NOT implemented
        if isinstance(basis, str):
            self.basis = Basis([ Perm([ int(c) for c in p ]) for p in basis.split('_') ])
        else:
            self.basis = Basis(basis)
        self.equivdb = EquivalenceDB()
        self.ruledb = RuleDB()
        self.tilingdb = TilingDB()
        self.tilingqueue = TilingQueue()
        self._inferral_cache = LRUCache(100000)
        self._basis_partitioning_cache = {}
        self._cache_hits = set()
        self._cache_misses = 0
        self._cache_hits_count = 0
        if symmetry:
            '''A list of symmetry functions of tilings.'''
            self.symmetry = find_symmetries(self.basis)
        else:
            self.symmetry = []
        if start_tiling is None:
            start_tiling = Tiling({(0,0): Av(self.basis)})

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
                if self.symmetry:
                    for sym_semi_inferred_tiling, sym_inferred_tiling in zip(self._symmetric_tilings(semi_inferred_tiling, ordered=True),
                                                                             self._symmetric_tilings(inferred_tiling, ordered=True)):
                        self._inferral_cache.set(sym_semi_inferred_tiling, sym_inferred_tiling)
                # '''Clean up the cache'''
                # if semi_inferred_tiling in self._basis_partitioning_cache:
                #     self._basis_partitioning_cache.pop(semi_inferred_tiling)
            self._inferral_cache.set(inferred_tiling, inferred_tiling)
        return inferred_tiling

    def _symmetric_tilings(self, tiling, ordered=False):
        """Return all symmetries of tiling.

        This function only works if symmetry is set to true.
        It returns precisely those symmetries which are different from original tiling.
        Sometimes, the order symmetries are appied are important. Therefore, if order=True,
        this will return a list with each symmetry applied. This functionality is
        needed for inferral.
        """
        if ordered:
            return [sym(tiling) for sym in self.symmetry]
        else:
            symmetric_tilings = set()
            for sym in self.symmetry:
                symmetric_tiling = sym(tiling)
                if symmetric_tiling != tiling:
                    symmetric_tilings.add(symmetric_tiling)

        return symmetric_tilings

    def _basis_partitioning(self, tiling, length, basis, function_name=None):
        # no caching for now - shortcut to see things working!
        assert len(self._basis_partitioning_cache) < 2
        basis_partitioning_cache = self._basis_partitioning_cache.get(tiling)
        if basis_partitioning_cache is None:
            if tiling in self._cache_hits:
                print("!!CACHE MISS!!")
                self._cache_misses += 1
            else:
                self._cache_hits.add(tiling)
            basis_partitioning_cache = {}
            self._basis_partitioning_cache[tiling] = basis_partitioning_cache

        basis_partitioning = basis_partitioning_cache.get(length)
        if basis_partitioning is None:
            basis_partitioning = tiling.basis_partitioning(length, basis)
            basis_partitioning_cache[length] = basis_partitioning
        else:
            self._cache_hits_count += 1

        return basis_partitioning

    def _clean_partitioning_cache(self, tiling):
        try:
            self._basis_partitioning_cache.pop(tiling)
        except KeyError:
            pass

    def expand(self, label):
        tiling = self.tilingdb.get_tiling(label)
        for generator in self.strategy_generators:
            for strategy in generator(tiling,
                                      basis=self.basis,
                                      basis_partitioning=self._basis_partitioning):
                if not isinstance(strategy, Strategy):
                    print(strategy)
                    print(strategy.formal_step)
                    print(generator)
                    raise TypeError("Strategy given not of the right form.")

                tilings = strategy.tilings
                formal_step = strategy.formal_step
                workable = strategy.workable
                back_maps = strategy.back_maps

                tilings = [self._inferral(t) for t in tilings]
                for t, w in zip(tilings, workable):
                    self.try_verify(t)
                    if w:
                        self.tilingdb.set_expandable(t)

                tilings = [t for t in tilings if not self.is_empty(t)]
                # put information about deleted empty tilings into the formal step

                if self.symmetry:
                    for t in tilings:
                        if self.tilingdb.is_symmetry_expanded(t):
                            continue
                        for sym_t in self._symmetric_tilings(t):
                            self.tilingdb.add(sym_t, expanding_other_sym=True, symmetry_expanded=True)
                            self.equivdb.union(label, self.tilingdb.get_label(sym_t), "a symmetry")
                            if self.tilingdb.is_expanded(x) or self.tilingdb.is_expanding_other_sym(x):
                                continue
                            self.tilingqueue.add_to_working(x)

                # If we have an equivalent strategy
                if len(tilings) == 1:
                    other_label = self.tilingdb.get_label(tilings[0])
                    self.equivdb.union(label, other_label, formal_step)
                    x = self.tilingdb.get_label(tilings[0])
                    if not (self.tilingdb.is_expanded(x) or self.tilingdb.is_expanding_other_sym(x)):
                        self.tilingqueue.add_to_working(x)
                else:
                    end_labels = [self.tilingdb.get_label(t) for t in tilings]
                    self.ruledb.add(label, end_labels, formal_step)
                    for x in end_labels:
                        # TODO: When labelled occurrences, we can also work from decomposed tilings
                        # so you can add to the queue all the time.
                        if self.tilingdb.is_expanded(x) or self.tilingdb.is_expanding_other_sym(x):
                            continue
                        self.tilingqueue.add_to_next(x)
                if back_maps is not None:
                    if label not in self.ruledb.back_maps:
                        self.ruledb.back_maps[label] = {}
                    self.ruledb.back_maps[label][tuple(sorted(end_labels))] = back_maps

        self._clean_partitioning_cache(tiling)
        self.tilingdb.set_expanded(label)

    def do_level(self,cap=None):
        if cap is None:
            for label in self.tilingqueue.do_level():
                if self.tilingdb.is_expanded(label) or self.tilingdb.is_verified(label):
                    continue
                elif not self.tilingdb.is_expandable(label):
                    continue
                elif self.tilingdb.is_expanding_other_sym(label):
                    continue
                self.expand(label)
        else:
            count = 0
            while count < cap:
                label = self.tilingqueue.next()
                if label is None:
                    count = cap
                    continue
                if self.tilingdb.is_expanded(label) or self.tilingdb.is_verified(label):
                    continue
                elif not self.tilingdb.is_expandable(label):
                    continue
                elif self.tilingdb.is_expanding_other_sym(label):
                    continue
                count += 1
                self.expand(label)


    def auto_search(self,cap=None,f=sys.stdout):
        while True:
            self.do_level(cap=cap)
            proof_tree = self.get_proof_tree()
            if proof_tree is not None:
                proof_tree.pretty_print(file=f)
                return proof_tree

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
        # print("Number previously verified: " + str(already_verified))
        # print("Number now verified: " + str(len(rules_dict.keys())))
        # print("Difference: " + str(len(rules_dict.keys()) - already_verified))
        for label in rules_dict.keys():
            self.equivdb.update_verified(label)

        # only verified labels in rules_dict, in particular, there is a tree if
        # the start label is in the rules_dict
        if self.equivdb[self.start_label] in rules_dict:
            # print("A tree was found! :)")
            _, proof_tree = proof_tree_dfs(rules_dict, root=self.equivdb[self.start_label])
            # print(proof_tree)
            return proof_tree
        else:
            pass
            # print("No tree was found. :(")

    def get_proof_tree(self, count=False):
        proof_tree_node = self.find_tree()
        if proof_tree_node is not None:
            proof_tree = ProofTree(self._get_proof_tree(proof_tree_node))
            # print(proof_tree.to_json())
            if count:
                f = proof_tree.get_genf()
                # print(f)
            return proof_tree
        else:
            pass
            # print("There is no proof tree yet.")

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
