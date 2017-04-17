from atrap import MetaTree
from permuta import Perm


from time import time
from atrap.strategies import *
from atrap.ProofTree import ProofTree

all_strategies = [ [all_cell_insertions, all_row_placements], [all_equivalent_row_placements, all_point_placements], [empty_cell_inferral, jays_subclass_inferral, row_and_column_separation], [reversibly_deletable_cells, components], [subset_verified, is_empty] ]

mimic_regular_insertion_encoding = [ [all_cell_insertions, all_minimum_row_placements], [all_equivalent_minimum_row_placements], [empty_cell_inferral], [reversibly_deletable_cells], [one_by_one_verification, is_empty]]

standard_strategies = [ [all_cell_insertions], [all_point_placements, all_symmetric_tilings], [subclass_inferral, row_and_column_separation], [components, reversibly_deletable_cells], [subset_verified, is_empty] ]

finite_strategies = [ [all_cell_insertions, all_minimum_row_placements], [all_equivalent_minimum_row_placements], [empty_cell_inferral, subclass_inferral], [], [subset_verified] ]


# mtree = MetaTree([Perm((0,2,1)), Perm((3,2,1,0))], *standard_strategies)

# mtree = MetaTree(descriptors.Basis([Perm((0,1,2,3))]))

# mtree = MetaTree([Perm((0,2,1))], recursive_strategies=[components], verification_strategies=[subset_verified] )

# mtree = MetaTree(descriptors.Basis([Perm((0,1))]))

# mtree = MetaTree([Perm((0,1,2))], *standard_strategies)

# mtree = MetaTree([])

# mtree = MetaTree([Perm((0,2,1)), Perm((0,1,2,3)), Perm((3,2,0,1)), Perm((2,3,0,1))], *all_strategies )

# mtree = MetaTree([Perm((0,2,1)), Perm((0,1,2))], *mimic_regular_insertion_encoding )

# mtree = MetaTree([Perm((1,3,0,2)), Perm((2,0,3,1))], *all_strategies)
#
task = '012_2103_2301'

# task = '1234_1243_1324_1342_1423_1432_2134_2143_2314_2341_3214'

# task = '012_2301'

# task = '012_0321_2103'

# task = '012_0321_1032_2103'
#
# task = '012_1032_2301_2310'

# task = '1302_2031'
#
# task = '012_3210'
#
# task = '012'

# task = '0'

# task = '0132_0213_0231_3120'

patts = [ Perm([ int(c) for c in p ]) for p in task.split('_') ]

# patts = [ Perm([ int(c) - 1 for c in p ]) for p in task.split('_') ]

#
mtree = MetaTree( patts, *standard_strategies )

print(mtree.basis)

#mtree.do_level()
start = time()

while not mtree.has_proof_tree():
    mtree.do_level()
    print("We had {} inferral cache hits and {} partitioning cache hits".format(mtree.inferral_cache_hits, mtree.partitioning_cache_hits))
    print("The partitioning cache has {} tilings in it right now".format( len(mtree._basis_partitioning_cache) ) )
    print("The inferral cache has {} tilings in it right now".format( len(mtree._inferral_cache) ) )
    print("There are {} tilings in the search tree".format( len(mtree.tiling_cache)))
    print("Time taken so far is {} seconds".format( time() - start ) )
    # if mtree.depth_searched == 3:
    #     break



if mtree.has_proof_tree():
    proof_tree = mtree.find_proof_tree()
    proof_tree.pretty_print()
    json = proof_tree.to_json(indent="  ")
    print(json)
    assert ProofTree.from_json(json).to_json(indent="  ") == json


end = time()

print("I took", end - start, "seconds")
