from atrap import MetaTree
from permuta import Perm


from time import time
# from atrap.strategies import subclass_inferral, subset_verified, reversibly_deletable_points, reversibly_deletable_cells, all_point_placements, all_row_placements, all_equivalent_row_placements, all_cell_insertions, empty_cell_inferral, one_by_one_verification, all_minimum_row_placements, all_equivalent_minimum_row_placements, is_empty, components
# from atrap.strategies import row_and_column_separation
# from atrap.strategies import jays_subclass_inferral
# from atrap.strategies import old_subclass_inferral
from atrap.strategies import *


all_strategies = [ [all_cell_insertions, all_row_placements], [all_equivalent_row_placements, all_point_placements], [empty_cell_inferral, jays_subclass_inferral, row_and_column_separation], [reversibly_deletable_cells, components], [subset_verified, is_empty] ]

mimic_regular_insertion_encoding = [ [all_cell_insertions, all_minimum_row_placements], [all_equivalent_minimum_row_placements], [empty_cell_inferral], [reversibly_deletable_cells], [one_by_one_verification, is_empty]]

standard_strategies = [ [all_active_cell_insertions], [all_point_placements], [jays_subclass_inferral, row_and_column_separation], [components], [subset_verified] ]

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
# task = '012_2103_2301'

# task = '012_2301'

# task = '012_0321_2103'

# task = '012_1032_2301_2310'

task = '1302_2031'
#
# task = '012_3210'
#
# task = '012'

patts = [ Perm([ int(c) for c in p ]) for p in task.split('_') ]
#
mtree = MetaTree( patts, *standard_strategies )

#mtree.do_level()
start = time()

while not mtree.has_proof_tree():
    mtree.do_level()
    print("We had {} inferral cache hits and {} partitioning cache hits".format(mtree.inferral_cache_hits, mtree.partitioning_cache_hits))
    print("The partitioning cache has {} tilings in it right now".format( len(mtree._basis_partitioning_cache) ) )
    print("The inferral cache has {} tilings in it right now".format( len(mtree._inferral_cache) ) )
    print("There are {} tilings in the search tree".format( len(mtree.tiling_cache)))
    print("Time taken so far is {} seconds".format( time() - start ) )
    # if mtree.depth_searched == 4:
    #     break



if mtree.has_proof_tree():
    proof_tree = mtree.find_proof_tree()
    proof_tree.pretty_print()
    print( proof_tree.to_json(indent="    ") )

end = time()

print("I took", end - start, "seconds")
