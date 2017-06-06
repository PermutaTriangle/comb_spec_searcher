from atrap import MetaTree
from permuta import Perm, Av


from time import time
from atrap.strategies import *
from atrap.ProofTree import ProofTree
from atrap import StrategyPacks

from atrap.Helpers import taylor_expand

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

# task = '012_3210'
# task = '0'
#
# task = '0123'
# task = '0213'
# task = '012_3210'

task = '021'

# task = '123'

# task = '0'

# task = '012'

# task = '0132_0213_0231_3120'

# task = '0213_0231'

# task = "1302_2031"

# task = '0231_1230_3012'

# task = '0231_0321'

# task = '0132_0213_0231_0312_0321_1032_1302_1320_2031_3021_3120'

# task = '0132_1302' # row_and_column_placements - no symmetry.
# task = '0213_0231' # row_and_column_placements - no symmetry.
# task = '0213_1302' # row_and_column_placements - one symmetry.
# task = '0231_1032' # row_and_column_placements - no symmetry.
# task = '0231_1320' # row_and_column_placements - one symmetry.
# task = '0321_1302' # column_placements - no symmetry.
# task = '0321_2301' # row_and_column_placements - one symmetry.
# task = '0132_1023' # point placements - three symmetry.
# task = '0231_0321' # point placements - no symmetry.
# task = '0231_1302' # row_and_column_placements - no symmetry.
# task = '0123_0132' # separation and isolation and splitting - one symmetry.
# task = '0132_0231' # point placements - no symmetry.
# task = '0213_1032' # point placements - three symmetries.
# task = '0231_1230' # separation and isolation - no symmetry.
# task = '0231_2031' # separation and isolation - no symmetry.
task = '1302_2031' # row_and_column_placements - seven symmetries.

# patts = [ Perm([ int(c) - 1 for c in p ]) for p in task.split('_') ]

#
# mtree = MetaTree( patts, *mimic_regular_insertion_encoding )
# strategies = [ [all_cell_insertions], [all_point_placements], [empty_cell_inferral], [components], [subset_verified, is_empty] ]
# task = '0123_0132_0213_0231_0312_1023_1203_1230_2013_2301_3012'
patts = [ Perm([ int(c) for c in p ]) for p in task.split('_') ]

strategies = StrategyPacks.point_placement
# strategies = enum_sch

mtree = MetaTree( patts, *strategies, symmetry=True, non_interleaving_recursion=False )

print("Using the strategies:")
print(strategies)
print(mtree.symmetry)

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
max_time = 500
while not mtree.has_proof_tree():
    print("===============================")
    mtree.do_level(max_time=max_time)
    print("We had {} inferral cache hits and {} partitioning cache hits.".format(mtree.inferral_cache_hits, mtree.partitioning_cache_hits))
    print("The partitioning cache has {} tilings in it right now.".format( len(mtree._basis_partitioning_cache) ) )
    print("The inferral cache has {} tilings in it right now.".format( len(mtree._inferral_cache) ) )
    print("There are {} tilings in the search tree.".format( len(mtree.tiling_cache)))
    print("There are {} verified tilings.".format(count_verified_tilings(mtree)))
    print("There are {} SiblingNodes of which {} are verified.".format(*count_sibling_nodes(mtree)))
    print("Time taken so far is {} seconds.".format( time() - start ) )
    print("")
    for function_name, calls in mtree._partitioning_calls.items():
        print("The function {} called the partitioning cache *{}* times, ({} originating)".format(function_name, calls[0], calls[1]))
    print("There were {} cache misses".format(mtree._cache_misses))
    if mtree.depth_searched == 15 or mtree.timed_out:# or time() - start > max_time:
        break

if mtree.has_proof_tree():
    proof_tree = mtree.find_proof_tree()
    proof_tree.pretty_print()
    json = proof_tree.to_json(indent="  ")
    print(json)
    assert ProofTree.from_json(json).to_json(indent="  ") == json
    # try:
    #     f = proof_tree.get_genf()
    #     print( f )
    #     print("The coefficients from the generating function are")
    #     print( taylor_expand(f, terms=10) )
    #     print("The actual coefficients are")
    #     print( [ len( Av(mtree.basis).of_length(i) ) for i in range(11)])
    # except RuntimeError as e:
    #     print(str(e))

end = time()

print("I took", end - start, "seconds")
