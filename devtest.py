import sys

from atrap import MetaTree
from permuta import Perm, Av

from time import time
from atrap.strategies import *
from atrap.ProofTree import ProofTree
from atrap import StrategyPacks

from atrap.Helpers import taylor_expand

# task = "0123_0132_0213_0231_0312_1023_1203_1230_2013_3012"
task = "0123_0132_0213_0231_0312_1203_1230_2013_3012"
# task = "0123_0132_0213_0231_0312_1203_1230_2013_3012"
# task = "0123_0132_0213_0231_0312_1023_1203_1230_2013"

# patts = [ Perm([ int(c) - 1 for c in p ]) for p in task.split('_') ]

# task = '0123_0132_0213_0231_0312_1023_1203_1230_2013_2301_3012'

patts = [ Perm([ int(c) for c in p ]) for p in task.split('_') ]

strategies = StrategyPacks.binary_pattern_placement

mtree = MetaTree(patts, **strategies)

print("Using the strategies:", file=sys.stderr)
print(strategies, file=sys.stderr)
print(mtree.symmetry, file=sys.stderr)

print(mtree.basis, file=sys.stderr)

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

start = time()
max_time = 500
while not mtree.has_proof_tree():
    print("===============================", file=sys.stderr)
    mtree.do_level(max_time=max_time)
    print("We had {} inferral cache hits and {} partitioning cache hits.".format(mtree.inferral_cache_hits, mtree.partitioning_cache_hits), file=sys.stderr)
    print("The partitioning cache has {} tilings in it right now.".format( len(mtree._basis_partitioning_cache)), file=sys.stderr)
    print("The inferral cache has {} tilings in it right now.".format( len(mtree._inferral_cache)), file=sys.stderr)
    print("There are {} tilings in the search tree.".format( len(mtree.tiling_cache)), file=sys.stderr)
    print("There are {} verified tilings.".format(count_verified_tilings(mtree)), file=sys.stderr)
    print("There are {} SiblingNodes of which {} are verified.".format(*count_sibling_nodes(mtree)), file=sys.stderr)
    print("Time taken so far is {} seconds.".format( time() - start), file=sys.stderr)
    print("")
    for function_name, calls in mtree._partitioning_calls.items():
        print("The function {} called the partitioning cache *{}* times, ({} originating)".format(function_name, calls[0], calls[1]), file=sys.stderr)
    print("There were {} cache misses".format(mtree._cache_misses), file=sys.stderr)
    if mtree.depth_searched == 15 or mtree.timed_out:# or time() - start > max_time:
        break

if mtree.has_proof_tree():
    proof_tree = mtree.find_proof_tree()
    proof_tree.pretty_print()
    json = proof_tree.to_json(indent="  ")
    print(json)
    assert ProofTree.from_json(json).to_json(indent="  ") == json

end = time()

print("I took", end - start, "seconds", file=sys.stderr)
