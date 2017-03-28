'''We first need to import the MetaTree and Perm class from atrap and permuta respectively'''
from atrap import MetaTree
from permuta import Perm

'''If you wish to use strategies not included in the default settings you should import them here'''
'''For example I want to use subclass_inferral and subset_verified'''
from atrap.strategies import subclass_inferral
from atrap.strategies import subset_verified


'''In this example we look for a proof tree on the class Av(012,210)'''
'''The first step is to initialise the basis, this should be an iterable of Perms'''
basis = [Perm((0,1,2)), Perm((2,1,0))]

'''We then need to initialise the MetaTree'''
meta_tree = MetaTree(basis)

'''In order to search we use the do_level function'''
'''Calling it without an integer will search one level deeper, and thus can
be used to perform a breadth first search'''
meta_tree.do_level()

'''If you want to try depth first, then give the do_level function some integer,
for example, this does depth first search to depth 3'''
meta_tree.do_level(3)

'''If the do_level function finds a proof tree, it will return the ProofTree object'''
while not meta_tree.has_proof_tree():
    meta_tree.do_level()

'''To find the ProofTre use the find proof tree function'''
proof_tree = meta_tree.find_proof_tree()

'''To print the proof tree we use the ProofTree's pretty print function'''
proof_tree.pretty_print()

'''The following strategy types can be used:

    - BatchStrategy: This returns a list of tilings of at least length two.
        - For example, the default setting uses the BatchStrategy cell insertion.

    - EquivalenceStrategy: This returns a single tiling.
        - For example, the default setting uses the EquivalenceStrategy point placement.

    - InferralStrategy: This returns a single tiling.
        - For example, the default setting uses the InferralStrategy empty cell inferral.

    - RecursiveStrategy: This returns a list of tilings of at least length two.
        - For example, the default setting uses the RecursiveStrategy components.

    - VerificationStrategy: This tells you if a tiling is verified.
        - For example, the default setting uses the VerificationStrategy one by one verification.

If you wish to make your own strategies then make sure you work out which it belongs to and
use the relevant ProofStrategy classes which can be found in the folder "strategies"

If you wish to use something other than the default settings, you can. For example, I will
rerun the example with the subclass inferral and subset verified strategies.

We intitialise by telling the tree the strategies that ca be used in a list'''
meta_tree = MetaTree( basis, inferral_strategies=[subclass_inferral], verification_strategies=[subset_verified])

'''We then search again for the proof tree'''
while not meta_tree.has_proof_tree():
    meta_tree.do_level()

'''and find it'''
proof_tree = meta_tree.find_proof_tree()

'''and print it'''
proof_tree.pretty_print()

'''If you run this file, the choice of strategies massively changes the size of this proof tree'''

'''That ends the tutorial. Any questions, feel free to ask :)'''
