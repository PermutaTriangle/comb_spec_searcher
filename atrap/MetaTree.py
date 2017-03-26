from atrap.strategies import all_cell_insertions
from atrap.strategies import row_and_column_separations
from atrap.strategies import components
from atrap.strategies import all_point_placements
from atrap.strategies import one_by_one_verification
from atrap.strategies import empty_cell_inferral
from atrap.strategies import subset_verified
from atrap.ProofTree import ProofTree, ProofTreeNode

from grids import Tiling

from permuta import PermSet
from permuta.descriptors import Basis

from itertools import product, starmap

#
# class StrategyCache(object):
#     # TODO: Do better
#     def __init__(self, basis):
#         self.basis = basis
#
#         self.equivalence_strategy_generators = [all_row_and_col_placements,
#                                                 row_and_column_separations]
#         self.batch_strategy_generators = [all_cell_insertions]
#         self.recursive_strategy_generators = [components]
#
#         self.eq_tilings = {}
#         self.batch_tilings = {}
#         self.recursive_tilings = {}
#
#     def get_equivalence_strategies(self, tiling):
#         strats = self.eq_tilings.get(tiling)
#         if strats is None:
#             strats = []
#             for generator in self.equivalence_strategy_generators:
#                 try:
#                     strategies = generator(tiling, self.basis)
#                 except TypeError:
#                     strategies = generator(tiling)
#                 for strategy in strategies:
#                     # TODO: Need to fix it returning None.
#                     if not strategy:
#                         continue
#                     if not isinstance(strategy[0], str):
#                         strategy = ("formal step missing", strategy[0])
#                     strats.append(strategy)
#             self.eq_tilings[tiling] = strats
#         return strats
#
#     def get_batch_strategies(self, tiling):
#         strats = self.batch_tilings.get(tiling)
#         if strats is None:
#             strats = []
#             for generator in self.batch_strategy_generators:
#                 strategies = generator(tiling)
#                 for strategy in strategies:
#                     strats.append(strategy)
#             self.batch_tilings[tiling] = strats
#         return strats
#
#     # TODO: If we go back to the ancestor approach.
#     def get_recursive_strategies(self, tiling):
#

class SiblingNode(set):

    def __init__(self):
        self.natural = False
        self.verification = set() # set of sets of tilings.
                           # an empty set in the list implies verified without recursion

    # Can we initialise this here rather than do it in the tree?
    # def _init__(self, tiling, and_node, equivalence_strategy_generators):

    def add(self, or_node):
        # if or_node in self:
        #     print(or_node.tiling)
        #     raise RuntimeError("Attempting to add node already in sibling node")
        if not isinstance(or_node, OrNode):
            raise TypeError("Non-OR node added to sibling node")
        super(SiblingNode, self).add(or_node)
        or_node.sibling_node = self

    def get_children(self):
        # TODO: Do smarter
        children = set()
        for sibling in self:
            for child_and_node in sibling.children:
                for child_or_node in child_and_node.children:
                    children.add(child_or_node.sibling_node)
        return children

    def get_and_parents(self):
        for sibling in self:
            for parent_and_node in sibling.parents:
                yield parent_and_node

    def is_verified(self):
        return any( not x for x in self.verified )

    def __hash__(self):
        return hash(id(self))#hash(sum(hash(sibling) in self))


class OrNode(object):
    def __init__(self, tiling=None):
        self.children = []
        self.parents = []
        self.expanded = False
        self.tiling = tiling
        self.sibling_node = None
        self.equivalent_expanded = False

#    def get_child_sibling_nodes(self):
#        return_set = set()
#        for child_and_node in self.children:
#            for child_or_node in child_and_node.children:
#                return_set.add(child_or_node.sibling_node)
#        return return_set

    def __eq__(self, other):
        return self.tiling == other.tiling

    def __hash__(self):
        return hash(self.tiling)


class AndNode(object):
    def __init__(self, formal_step=""):
        self.formal_step = formal_step
        self.children = []
        self.parents = []
        self.verification = set() #list of sets of tilings

    def __eq__(self, other):
        return self.parents == other.parents and self.formal_step == other.formal_step

    def __hash__(self):
        return hash(id(self))


    #@property
    #def or_children(self):
    #    for child_or_node in root_and_node.children:
    #        for sibling_or_node in child_or_node.siblings:
    #            self._or_helper(sibling_or_node, requested_depth - 1)


class MetaTree(object):
    def __init__(self, basis):
        # Store basis
        self.basis = Basis(basis)

        # Generators for strategies
        self.equivalence_strategy_generators = [all_point_placements]
        self.batch_strategy_generators = [all_cell_insertions]
        self.recursive_strategy_generators = [components]
        self.inferral_strategy_generators = [empty_cell_inferral]
        self.verification_strategy_generators = [one_by_one_verification, subset_verified]
        self.proof_tree_found = False

        # Create the first tiling
        root_tiling = Tiling({(0, 0): PermSet.avoiding(basis)})

        # Create and store the root AND and OR node of the tree
        # Similarly create the sibling node
        root_and_node = AndNode()
        formal_step = "We start off with a 1x1 tiling where the single block is the input set."
        root_and_node.formal_step = formal_step

        root_or_node = OrNode(root_tiling)
        root_or_node.parents.append(root_and_node)
        root_and_node.children.append(root_or_node)

        root_sibling_node = SiblingNode()
        root_sibling_node.add(root_or_node)
        root_sibling_node.natural = True

        self.root_and_node = root_and_node
        self.root_or_node = root_or_node
        self.root_sibling_node = root_sibling_node

        # Tiling to OR node dictionary
        self.tiling_cache = {root_tiling: root_or_node}

        # How far the DFS or BFS have gone
        self.depth_searched = 0


    def do_level(self, requested_depth=None):
        if requested_depth is None:
            self.do_level(self.depth_searched + 1)
        else:
            if requested_depth <= self.depth_searched:
                print("Depth already searched")
                return
            print("Doing depth", requested_depth)
            if self._sibling_helper(self.root_sibling_node, requested_depth):
                print("A proof tree has been found.")
                self.find_proof_tree()
                self.proof_tree_found = True
            self.depth_searched = requested_depth

    def _sibling_helper(self, root_sibling_node, requested_depth):
        drill_set = set()  # Sibling nodes
        expand_set = set()  # OR nodes

        if requested_depth == 0:
            return
        elif requested_depth < 0:
            raise RuntimeError("Negative depth requested")

        for sibling_or_node in root_sibling_node:
            if sibling_or_node.expanded:
                # We need to move further down
                # print("Found that I need to move down on:")
                # print(sibling_or_node.tiling)
                for child_and_node in sibling_or_node.children:
                    for child_or_node in child_and_node.children:
                        drill_set.add(child_or_node.sibling_node)
            else:
                # print("Found that I need to expand down on:")
                # print(sibling_or_node.tiling)
                expand_set.add(sibling_or_node)

        # Expand the child nodes into sibling nodes and add to drill set
        for sibling_or_node in expand_set:
            # print("Expanding:")
            # print(sibling_or_node.tiling)
            if frozenset() not in sibling_or_node.sibling_node.verification:
                child_sibling_nodes = self._expand_helper(sibling_or_node)
                if frozenset() in self.root_and_node.verification:
                    return True
            else:
                child_sibling_nodes = set()
            drill_set.update(child_sibling_nodes)

        # Move down entire drill set

        for child_sibling_node in drill_set:
            # print("Moving down:")
            # print(child_sibling_node)
            if self._sibling_helper(child_sibling_node, requested_depth - 1):
                return True

    # returns child sibling nodes of the expanded or node
    def _expand_helper(self, root_or_node):
        # Expand OR node using batch strategies and return the sibling nodes
        child_sibling_nodes = set()
        and_nodes_to_be_propagataed = set()

        # Find all the recursive strategies and add 'em
        for recursive_generator in self.recursive_strategy_generators:
            for recursive_strategy in recursive_generator(root_or_node.tiling, basis=self.basis):
                print("on the tiling:")
                print(root_or_node.tiling)
                print("we get the following strategy")
                formal_step = recursive_strategy.formal_step
                tilings = recursive_strategy.tilings
                print(formal_step)
                for tiling in tilings:
                    print(tiling)
                print("----------------------")

                # if len(tilings) == 0:
                #     child_and_node = AndNode(formal_step)
                #     child_and_node.parents.append(root_or_node)
                #     root_or_node.children.append(child_and_node)
                #     sibling_node = self._get_recursive_sibling_node(root_or_node.tiling, child_and_node)
                #     child_sibling_nodes.add(sibling_node)
                #     sibling_node.verification.add(frozenset())
                #     and_nodes_to_be_propagataed.add(child_and_node)
                #     continue

                # Create the AND node and connect it to its parent OR node
                child_and_node = AndNode(formal_step)
                child_and_node.parents.append(root_or_node)
                root_or_node.children.append(child_and_node)
                # Go through all the tilings created for the AND node
                for tiling in tilings:
                    # Create/get a sibling node and connect it
                    verified = False
                    sibling_node = self._get_recursive_sibling_node(tiling, child_and_node)
                    for verification_generator in self.verification_strategy_generators:
                        if verified:
                            break
                        for verification_strategy in verification_generator(tiling, basis=self.basis):
                            # If I am in here, my tiling is verified.
                            verification_formal_step = verification_strategy.formal_step
                            print("The tiling")
                            print(tiling)
                            print("is verified using the strategy:")
                            print(verification_formal_step)
                            print("----------------------")
                            sibling_node.natural = True
                            verified_and_node = AndNode(verification_formal_step)
                            # Why was it in the cache?
                            verified_or_node = self.tiling_cache[tiling]
                            verified_or_node.children.append(verified_and_node)
                            verified_and_node.parents.append(verified_or_node)
                            verified_and_node.verification.add(frozenset())
                            self._propagate_and_node_verification(verified_and_node)
                            verified = True
                            break

                    if not verified:
                        sibling_node.verification.add( frozenset([tiling]) )

                    child_sibling_nodes.add(sibling_node)
                self._propagate_and_node_verification(child_and_node, set())

                    # if one_by_one_verified(tiling, self.basis):
                    #     print("I'm using one by one on the tiling:")
                    #     print(tiling)
                    #     sibling_node.natural = True
                    #     # sibling_node.verification.add(frozenset())
                    #     one_by_one_verified_and_node = AndNode("I am one-by-one verified")
                    #     one_by_one_or_node = self.tiling_cache[tiling]
                    #     one_by_one_or_node.children.append(one_by_one_verified_and_node)
                    #     one_by_one_verified_and_node.parents.append(one_by_one_or_node)
                    #     one_by_one_verified_and_node.verification.add(frozenset())
                    #     self._propagate_and_node_verification(one_by_one_verified_and_node)
                    # else:
                    #     sibling_node.verification.add( frozenset([tiling]) )
                    # Add it to the return set
                    # child_sibling_nodes.add(sibling_node)

                # self._propagate_and_node_verification(child_and_node, set())
        #
        # for and_node in and_nodes_to_be_propagataed:
        #     self._propagate_and_node_verification(and_node, set())
        #
        # and_nodes_to_be_propagataed = set()

        # Find all the batch strategies, and add 'em.

        for batch_strategy_generator in self.batch_strategy_generators:
            # TODO: Do we need to give it the basis for some strategies?
            for batch_strategy in batch_strategy_generator(root_or_node.tiling, basis=self.basis):
                print("on the tiling:")
                print(root_or_node.tiling)
                print("we get the following strategy")
                formal_step = batch_strategy.formal_step
                tilings = batch_strategy.tilings
                print(formal_step)
                for tiling in tilings:
                    print(tiling)
                print("----------------------")
                # Create the AND node and connect it to its parent OR node
                child_and_node = AndNode(formal_step)
                child_and_node.parents.append(root_or_node)
                root_or_node.children.append(child_and_node)
                # Go through all the tilings created for the AND node
                for index, tiling in enumerate(tilings):
                    for inferral_strategy_generator in self.inferral_strategy_generators:
                        for inferral_strategy in inferral_strategy_generator(tiling, basis=self.basis):
                            print("On tiling")
                            print(tiling)
                            print("I have the following inferral strategy")
                            formal_step = inferral_strategy.formal_step
                            tiling = inferral_strategy.tiling
                            print(formal_step)
                            print("giving the tiling")
                            print(tiling)
                            print("----------------------")
                            # TODO: Add the formal step to the parent node.
                            tilings[index] = tiling
                    # Create/get a sibling node and connect it
                    sibling_node = self._get_sibling_node(tiling, child_and_node)

                    # Add it to the return set
                    verified = False
                    for verification_generator in self.verification_strategy_generators:
                        if verified:
                            break
                        for verification_strategy in verification_generator(tiling, basis=self.basis):
                            # If I am in here, my tiling is verified.
                            verification_formal_step = verification_strategy.formal_step
                            print("The tiling")
                            print(tiling)
                            print("is verified using the strategy:")
                            print(verification_formal_step)
                            print("----------------------")
                            verified_and_node = AndNode(verification_formal_step)
                            verified_or_node = self.tiling_cache[tiling]
                            verified_or_node.children.append(verified_and_node)
                            verified_and_node.parents.append(verified_or_node)
                            verified_and_node.verification.add(frozenset())
                            self._propagate_and_node_verification(verified_and_node)
                            verified = True
                            break
                    child_sibling_nodes.add(sibling_node)
                if any( not or_node.sibling_node.natural for or_node in child_and_node.children):
                    for or_node in child_and_node.children:
                        or_node.sibling_node.natural = True
                    self._propagate_and_node_verification(child_and_node, set())


        #
        # for and_node in and_nodes_to_be_propagataed:
        #     self._propagate_and_node_verification(and_node, set())

        root_or_node.expanded = True
        return child_sibling_nodes

    def _get_recursive_sibling_node(self, tiling, and_node):
        or_node = self.tiling_cache.get(tiling)
        if or_node is None:
            # Make sure we only expand non-recursive strategies
            # therefore the sibling node created will have natural = False
            # unless found otherwise
            or_node = OrNode()
            or_node.tiling = tiling
            self.tiling_cache[tiling] = or_node
            sibling_node = SiblingNode()
            sibling_node.add(or_node)
        else:
            sibling_node = or_node.sibling_node

        or_node.parents.append(and_node)
        and_node.children.append(or_node)

        return sibling_node


    def _get_sibling_node(self, tiling, and_node):
        or_node = self.tiling_cache.get(tiling)

        if or_node is None:
            or_node = OrNode()
            or_node.tiling = tiling
            self.tiling_cache[tiling] = or_node

            # Our new OR node belongs to no sibling node yet
            sibling_node = self._fully_equivalent_sibling_node(or_node)
        else:
            sibling_node = or_node.sibling_node
            # Make sure we only expand batch strategies found.
            # Previously found by recursive strategy, but not batch
            # Therefore we want to expand it.
            if not sibling_node.natural:
                sibling_node = self._fully_equivalent_sibling_node(or_node)

        # Hook up the OR node with its parent AND node and vice-versa
        or_node.parents.append(and_node)
        and_node.children.append(or_node)

        return sibling_node

    def _fully_equivalent_sibling_node(self, or_node):
        # Our new OR node belongs to no sibling node yet
        new_or_nodes = set([or_node])
        # new_sibling_nodes_to_be_added
        existing_sibling_nodes = set()

        while new_or_nodes:
            new_or_node = new_or_nodes.pop()
            if new_or_node.equivalent_expanded:
                existing_sibling_nodes.add(new_or_node.sibling_node)
                continue
            new_sibling_node = SiblingNode()
            new_sibling_node.add(new_or_node)
            new_or_node.sibling_node = new_sibling_node
            for equivalence_generator in self.equivalence_strategy_generators:
                for equivalence_strategy in equivalence_generator(new_or_node.tiling, basis=self.basis):
                    formal_step = equivalence_strategy.formal_step
                    eq_tiling = equivalence_strategy.tiling
                    for inferral_strategy_generator in self.inferral_strategy_generators:
                        for inferral_strategy in inferral_strategy_generator(eq_tiling, basis=self.basis):
                            print("On tiling")
                            print(eq_tiling)
                            print("I have the following inferral strategy")
                            formal_step = inferral_strategy.formal_step
                            eq_tiling = inferral_strategy.tiling
                            print(formal_step)
                            print("giving the tiling")
                            print(eq_tiling)
                            print("----------------------")
                            # TODO: Add the formal step to sibling node.
                    verified = False
                    for verification_strategy_generator in self.verification_strategy_generators:
                        if verified:
                            break
                        for verification_strategy in verification_strategy_generator(eq_tiling, basis=self.basis):
                            # If I am in here, my tiling is verified.
                            verification_formal_step = verification_strategy.formal_step
                            print("The tiling")
                            print(eq_tiling)
                            print("is verified using the strategy:")
                            print(verification_formal_step)
                            print("----------------------")
                            verified_and_node = AndNode(verification_formal_step)
                            verified_or_node = self.tiling_cache.get(eq_tiling)
                            if not verified_or_node:
                                verified_or_node = OrNode(eq_tiling)
                                new_or_nodes.add(verified_or_node)
                                self.tiling_cache[eq_tiling] = verified_or_node
                                # new_or_nodes_to_be_added.add(sibling_or_node)
                                new_sibling_node.add(verified_or_node)
                                # verified_or_node.sibling_node = new_sibling_node

                            verified_or_node.children.append(verified_and_node)
                            verified_and_node.parents.append(verified_or_node)
                            verified_and_node.verification.add(frozenset())
                            self._propagate_and_node_verification(verified_and_node)
                            verified = True
                            break

                    sibling_or_node = self.tiling_cache.get(eq_tiling)
                    if sibling_or_node is None:
                        sibling_or_node = OrNode(eq_tiling)
                        self.tiling_cache[eq_tiling] = sibling_or_node
                        new_or_nodes.add(sibling_or_node)
                        # new_or_nodes_to_be_added.add(sibling_or_node)
                        new_sibling_node.add(sibling_or_node)
                        sibling_or_node.sibling_node = new_sibling_node
                    else:
                        # print(new_or_node.tiling)
                        if new_or_node.sibling_node.natural:
                            existing_sibling_nodes.add(sibling_or_node.sibling_node)
                        else:
                            new_or_node.sibling_node.natural = True
                            new_or_nodes.add(new_or_node)
                            existing_sibling_nodes.add(sibling_or_node.sibling_node)
            existing_sibling_nodes.add(new_sibling_node)
            new_or_node.equivalent_expanded = True

        sibling_node_iter = iter(existing_sibling_nodes)
        if len(existing_sibling_nodes) == 0:
            # Create new sibling node
            sibling_node = SiblingNode()
        else:
            sibling_node = next(sibling_node_iter)


        for existing_sibling_node in sibling_node_iter:
            # print("yeah!! let's combine our forces for the greater good!")
            sibling_node.verification.update(existing_sibling_node.verification)
            for sibling_or_node in existing_sibling_node:
                sibling_node.add(sibling_or_node)
        # for sibling_or_node in new_or_nodes_to_be_added:
        #     sibling_node.add(sibling_or_node)

        return sibling_node

    # I want to propagate verification to the parents of sibling_node
    # TODO: consider updating, rather than recomputing verification
    def _propagate_and_node_verification( self, and_node, seen_nodes=set() ):
        if and_node in seen_nodes:
            return
        seen_nodes.add(and_node)
        # print("attempting AND node propagation")
        if any( not child.sibling_node.verification for child in and_node.children):
            # print("there is an unverified child")
            # for child in and_node.children:
                # if not child.sibling_node.verification:
                    # print(child.tiling)
            # print("---")
            return
        if any( not child.sibling_node.natural for child in and_node.children):
            # print("there is an unnatural child DAMIAN!")
            # for child in and_node.children:
            #     if not child.sibling_node.natural:
                    # print(child.tiling)
            # print("---")
            return

        child_verifications = set()
        # input()
        # print(and_node.formal_step)

        # unflattened_verifications = product( child.sibling_node.verification for child in and_node.children )
        # new_verification = set()
        # print(unflattened_verifications)
        # for unflattened_verification in unflattened_verifications:
        #     print(unflattened_verification)
        #     new_verification.add( set().union( part for part in unflattened_verification) )

        # print("we're attempting to combine on an AND node")
        child_verifications = []

        for child in and_node.children:
            child_verifications.append( child.sibling_node.verification )
        # print(child_verifications)
        new_verification = set()
        for verification_product in product(*child_verifications):
            # print( verification_product )
            # print("the tilings in this set are")
            for fset in verification_product:
                for tiling in fset:
                    print(tiling)
            new_verification.add(frozenset().union(*verification_product))
        # print("our guess is:")
        # print(new_verification)


        # for child in and_node.children:
        #     # find all the child verifications
        #     print(child.tiling)
        #     print(child.sibling_node.verification)
        #     child_verifications.update(child.sibling_node.verification)
        #     # we will have now seen all of tilings on the sibling node
        #     seen_tilings.update( sibling.tiling for sibling in child.sibling_node )
        # print("we've seen these tilings so far:")
        # for tiling in seen_tilings:
        #     print(tiling)
        # # input()
        #
        # new_verification = set()
        # new_verification.add(frozenset.union(*child_verifications))
        #
        # if and_node.verification == new_verification:
        #     return
        and_node.verification = new_verification
        # print("the verification we give to the and_node is:")
        # print(new_verification)
        # input()
        if frozenset() in and_node.verification:
            # print("we've got a proof tree here!")
            and_node.verification = set([frozenset()])
            # input()
        # if and_node is self.root_and_node:
        #     # print("at root AND node")
        #     # input()
        #     if frozenset() in and_node.verification:
        #         print("we've got a proof tree here!")
        #         self.find_proof_tree()
        #         assert 2 == 3
                # input()
                # input()
                # input()
        # There is only one
        for parent_node in and_node.parents:
            self._propagate_sibling_node_verification( parent_node.sibling_node, seen_nodes )

    def _propagate_sibling_node_verification( self, sibling_node, seen_nodes=set() ):
        # if any( child.verification for child in sibling_node.children ):
        #     return
        # if any( child.sibling_node.natural for child in sibling_node.children ):
        #     return
        if sibling_node in seen_nodes:
            return
        seen_nodes.add(sibling_node)
        # if any( sibling.tiling in seen_tilings and not sibling.tiling == self.root_or_node.tiling for sibling in sibling_node ):
        #     return
        # print("sibling node propagation")
        # input()
        new_verification = set()
        # print("the child AND nodes have the following verifications:")
        for sibling in sibling_node:
            # print(sibling.tiling)
            for child_and_node in sibling.children:
                # print(child_and_node.verification)
                new_verification.update(child_and_node.verification)
        # print("the new verification for the sibling node is:")
        # print(new_verification)

        final_sibling_verification = set()
        for verification in new_verification:
            final_sibling_verification.add( frozenset( [tiling for tiling in verification if self.tiling_cache[tiling] not in sibling_node] ) )
        # if sibling_node.verification == final_sibling_verification:
        #     return
        sibling_node.verification = final_sibling_verification

        # input()
        for parent_and_node in sibling_node.get_and_parents():
            self._propagate_and_node_verification(parent_and_node, seen_nodes )

    def find_proof_tree(self):
        if not frozenset() in self.root_and_node.verification:
            print("there isn't one")
            return
        proof_tree = ProofTree( self._find_proof_tree_helper(self.root_or_node.children[0], self.root_or_node.tiling, set([self.root_or_node.tiling])) )
        proof_tree.pretty_print()
        return proof_tree

    def _find_proof_tree_helper(self, root_and_node, in_tiling, seen_tilings=set()):

        # if not root_and_node.children:
        #     return

        formal_step = root_and_node.formal_step
        out_tiling = root_and_node.parents[0].tiling
        tilings = [ sibling.tiling for sibling in root_and_node.parents[0].sibling_node ]
        seen_tilings.update(tilings)


        children = []
        for child_or_node in root_and_node.children:
            k = False
            if child_or_node.tiling in seen_tilings:
                sibling_tilings = [ sibling.tiling for sibling in child_or_node.sibling_node ]
                children.append(ProofTreeNode( "This is already in there", child_or_node.tiling, None, sibling_tilings, [] ))
                k = True
            for sibling in child_or_node.sibling_node:
                if k:
                    break
                for child_and_node in sibling.children:
                    if any(verification.issubset(seen_tilings) for verification in child_and_node.verification):
                        children.append( self._find_proof_tree_helper( child_and_node, child_or_node.tiling, seen_tilings ) )
                        k = True
                        break
        # print("+++++++++++++++++++++++")
        # print("in_tiling")
        # print(in_tiling)
        # print("out_tiling")
        # print(out_tiling)
        # print("formal_step")
        # print(root_and_node.formal_step)
        # print("children's in_tilings")
        # for child in children:
        #     print( child.in_tiling )
        # print("+++++++++++++++++++++++")
        return ProofTreeNode(formal_step, in_tiling, out_tiling, tilings, children)
