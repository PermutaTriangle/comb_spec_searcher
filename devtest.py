from atrap import MetaTree
from permuta import Perm


from time import time
from atrap.strategies import *
from atrap.ProofTree import ProofTree

all_strategies = [ [all_cell_insertions, all_row_placements, all_column_placements], [all_point_placements, all_equivalent_row_placements, all_equivalent_column_placements, all_symmetric_tilings], [empty_cell_inferral, subclass_inferral, row_and_column_separation], [splittings, reversibly_deletable_cells, components], [subset_verified, is_empty] ]

mimic_regular_insertion_encoding = [ [all_cell_insertions, all_minimum_row_placements], [all_equivalent_minimum_row_placements], [empty_cell_inferral], [reversibly_deletable_points], [one_by_one_verification, is_empty]]

standard_strategies = [ [all_cell_insertions], [all_point_placements, all_symmetric_tilings], [empty_cell_inferral, row_and_column_separation, subclass_inferral], [components, reversibly_deletable_cells], [subset_verified, is_empty] ]
# standard_strategies = [ [all_cell_insertions], [all_point_placements, all_symmetric_tilings], [empty_cell_inferral, row_and_column_separation, subclass_inferral], [splittings], [subset_verified, is_empty] ]
standard_strategies_w_all_row_cols = [ [all_cell_insertions, all_row_placements, all_column_placements], [all_equivalent_row_placements, all_equivalent_column_placements, all_symmetric_tilings], [empty_cell_inferral, row_and_column_separation, subclass_inferral], [components, reversibly_deletable_cells], [subset_verified, is_empty] ]

# finite_strategies = [ [all_cell_insertions, all_row_placements], [all_equivalent_row_placements], [empty_cell_inferral, subclass_inferral], [], [subset_verified, is_empty] ]
finite_strategies_w_min_row = [ [all_cell_insertions, all_minimum_row_placements], [all_equivalent_minimum_row_placements], [empty_cell_inferral, row_and_column_separation, subclass_inferral], [], [subset_verified, is_empty] ]
finite_strategies_w_point_pl = [ [all_cell_insertions], [all_point_placements], [empty_cell_inferral, row_and_column_separation, subclass_inferral], [], [subset_verified, is_empty] ]

finite_strategies = [ [all_cell_insertions, all_minimum_row_placements], [all_equivalent_minimum_row_placements], [empty_cell_inferral, subclass_inferral], [], [subset_verified, is_empty] ]

basic = [ [all_cell_insertions], [all_maximum_point_placements], [row_and_column_separation], [reversibly_deletable_cells], [one_by_one_verification] ]

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

# task = '1234_1243_1324_1342_1423_1432_2134_2143_2314_2341_3214'

# task = '012_2301'

# task = '012_0321_2103'

# task = '012_0321_1032_2103'
#
# task = '012_1032_2301_2310'

task = '1302_2031'
# task = '012_3210'
# task = '0'
#
# task = '0123'
# task = '012'

# task = '021'

# task = '4213_3142'

# task = '0'

# task = '0132_0213_0231_3120'

patts = [ Perm([ int(c) for c in p ]) for p in task.split('_') ]

# patts = [ Perm([ int(c) - 1 for c in p ]) for p in task.split('_') ]

#
# mtree = MetaTree( patts, *mimic_regular_insertion_encoding )
mtree = MetaTree( patts, *standard_strategies_w_all_row_cols )

print(mtree.basis)


def count_verified_tilings(mt):
    count = 0
    for tiling, or_node in mt.tiling_cache.items():
        if or_node.sibling_node.is_verified():
            count += 1
    return count

def count_sibling_nodes(mt):
    s = set()
    verified = 0
    for tiling, or_node in mt.tiling_cache.items():
        if or_node.sibling_node in s:
            continue
        if or_node.sibling_node.is_verified():
            verified += 1
        s.add(or_node.sibling_node)
    return len(s), verified

#mtree.do_level()
start = time()

while not mtree.has_proof_tree():
    mtree.do_level()
    print("We had {} inferral cache hits and {} partitioning cache hits.".format(mtree.inferral_cache_hits, mtree.partitioning_cache_hits))
    print("The partitioning cache has {} tilings in it right now.".format( len(mtree._basis_partitioning_cache) ) )
    print("The inferral cache has {} tilings in it right now.".format( len(mtree._inferral_cache) ) )
    print("There are {} tilings in the search tree.".format( len(mtree.tiling_cache)))
    print("There are {} verified tilings.".format(count_verified_tilings(mtree)))
    print("There are {} SiblingNodes of which {} are verified.".format(*count_sibling_nodes(mtree)))
    print("Time taken so far is {} seconds.".format( time() - start ) )
    for function_name, calls in mtree._partitioning_calls.items():
        print("The function {} called the partitioning cache {} many times".format(function_name, calls))
    print("There were {} cache misses".format(mtree._cache_misses))
    # if mtree.depth_searched == 10:
    #     break



if mtree.has_proof_tree():
    proof_tree = mtree.find_proof_tree()
    proof_tree.pretty_print()
    json = proof_tree.to_json(indent="  ")
    print(json)
    assert ProofTree.from_json(json).to_json(indent="  ") == json


end = time()

print("I took", end - start, "seconds")
