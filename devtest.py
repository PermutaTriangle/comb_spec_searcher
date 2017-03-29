from atrap import MetaTree
from permuta import Perm


from time import time
from atrap.strategies import subclass_inferral, subset_verified, reversibly_deletable_points, reversibly_deletable_cells, all_point_placements, all_row_placements, all_equivalent_row_placements, all_cell_insertions, empty_cell_inferral, one_by_one_verification, all_minimum_row_placements, all_equivalent_minimum_row_placements

mimic_regular_insertion_encoding = [ [all_cell_insertions, all_minimum_row_placements], [all_equivalent_minimum_row_placements], [empty_cell_inferral], [reversibly_deletable_points], [one_by_one_verification] ]

# mtree = MetaTree(descriptors.Basis([Perm((0,2,1)), Perm((0,1,2,3)), Perm((3,2,0,1)), Perm((2,3,0,1))]))

# mtree = MetaTree(descriptors.Basis([Perm((0,1,2,3))]))

# mtree = MetaTree([Perm((0,2,1))], recursive_strategies=[reversibly_deletable_cells] )

# mtree = MetaTree(descriptors.Basis([Perm((0,1))]))

# mtree = MetaTree([Perm((0,1,2))], batch_strategies=[all_cell_insertions, all_row_placements], inferral_strategies=[subclass_inferral], recursive_strategies=[reversibly_deletable_cells], verification_strategies=[subset_verified])

# mtree = MetaTree([])

mtree = MetaTree([Perm((0,2,1)), Perm((0,1,2,3)), Perm((3,2,0,1)), Perm((2,3,0,1))], *mimic_regular_insertion_encoding )



#mtree.do_level()
start = time()

while not mtree.has_proof_tree():
    mtree.do_level()
    if mtree.depth_searched == 8:
        break

proof_tree = mtree.find_proof_tree()

end = time()

print("I took", end - start, "seconds")






# proof_tree = mtree.find_proof_tree()
#
# print( proof_tree.to_json(indent="    ") )
