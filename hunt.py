import sys

from atrap import MetaTree
from permuta import Perm,Av

from time import time
from atrap.strategies import *
from atrap.ProofTree import ProofTree

## SET THIS TO TRUE TO OUTPUT TO A FILE
OUTPUT_TO_FILE = False





standard_strategies = [ [all_cell_insertions], [all_point_placements, all_symmetric_tilings], [empty_cell_inferral, row_and_column_separation, subclass_inferral], [splittings], [subset_verified, is_empty] ]
standard_strategies_w_all_row_cols = [ [all_cell_insertions, all_row_placements, all_column_placements], [all_equivalent_row_placements, all_equivalent_column_placements, all_symmetric_tilings], [empty_cell_inferral, row_and_column_separation, subclass_inferral], [splittings], [subset_verified, is_empty] ]
COMP_REC_standard_strategies_w_all_row_cols = [ [all_cell_insertions, all_row_placements, all_column_placements], [all_equivalent_row_placements, all_equivalent_column_placements, all_symmetric_tilings], [empty_cell_inferral, row_and_column_separation, subclass_inferral], [components, reversibly_deletable_cells], [subset_verified, is_empty] ]


STRATS_TO_USE = standard_strategies_w_all_row_cols




def perm_to_str(perm):
    return "".join([str(i) for i in list(perm)])

def perms_to_str(perms):
    return "_".join(perm_to_str(perm) for perm in perms)


if len(sys.argv) == 1:
    print("form: hunt.py p1 p2 p3 ... -> Av(p1, p2, p3, ...)")

perms = sys.argv[1:]
task = "_".join(perm for perm in perms)
patts = [ Perm([ int(c)-1 for c in p ]) for p in task.split('_') ]

# print(sys.argv)
f = (open('results/hunt_'+task+'_results.txt', 'w') if OUTPUT_TO_FILE else sys.stdout)

mtree = MetaTree( patts, *STRATS_TO_USE )

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

print("Hunting for proof tree for the class: "+str(Av(patts)), file=f)

f.flush()

while not mtree.has_proof_tree():
    print("===============================",file=f)
    mtree.do_level(file=f)
    print("We had {} inferral cache hits and {} partitioning cache hits.".format(mtree.inferral_cache_hits, mtree.partitioning_cache_hits),file=f)
    print("The partitioning cache has {} tilings in it right now.".format( len(mtree._basis_partitioning_cache) ) ,file=f)
    print("The inferral cache has {} tilings in it right now.".format( len(mtree._inferral_cache) ) ,file=f)
    print("There are {} tilings in the search tree.".format( len(mtree.tiling_cache)),file=f)
    print("There are {} verified tilings.".format(count_verified_tilings(mtree)),file=f)
    print("There are {} SiblingNodes of which {} are verified.".format(*count_sibling_nodes(mtree)),file=f)
    print("Time taken so far is {} seconds.".format( time() - start ) ,file=f)
    print("",file=f)
    for function_name, calls in mtree._partitioning_calls.items():
        print("The function {} called the partitioning cache *{}* times, ({} originating)".format(function_name, calls[0], calls[1]),file=f)
    print("There were {} cache misses".format(mtree._cache_misses),file=f)
    # if mtree.depth_searched == 10:
    #     break



if mtree.has_proof_tree():
    proof_tree = mtree.find_proof_tree()
    proof_tree.pretty_print(file=f)
    json = proof_tree.to_json(indent="  ")
    print(json,file=f)
    assert ProofTree.from_json(json).to_json(indent="  ") == json


end = time()

print("I took", end - start, "seconds",file=f)

if f != sys.stdout:
    f.close()