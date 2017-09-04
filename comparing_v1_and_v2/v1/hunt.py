import sys
import os
import random

from atrap import MetaTree
from permuta import Perm,Av

from time import time
from atrap.ProofTree import ProofTree

from atrap import StrategyPacks







### SET THESE VARIABLES ###
OUTPUT_TO_FILE = False # automatically set to True if called from spectrum_test or run_batch
STRATS_TO_USE = StrategyPacks.row_and_column_placements
###########################


spectrum_mode = False
batch_mode = False



def perm_to_str(perm):
    return "".join([str(i) for i in list(perm)])

def perms_to_str(perms):
    return "_".join(perm_to_str(perm) for perm in perms)


if len(sys.argv) == 1:
    print("form: hunt.py p1 p2 p3 ... -> Av(p1, p2, p3, ...)")

if sys.argv[1] == 'spectrum':
    OUTPUT_TO_FILE = True
    spectrum_mode = True
    perms = sys.argv[3:]
elif sys.argv[1] == 'batch':
    OUTPUT_TO_FILE = True
    batch_mode = True
    perms = sys.argv[2:]
else:
    perms = sys.argv[1:]

task = "_".join(perm for perm in perms)
patts = [ Perm([ int(c) for c in p ]) for p in task.split('_') ]

# print(sys.argv)
if spectrum_mode:
    spectrum_results = open('spectrum_results/spectrum_'+task+'_'+sys.argv[2]+'_results.txt', 'w')
    f = open(os.devnull, 'w')

    strats_file = open('spectrum_results/stratsused.txt', 'w')
    for strat_type in STRATS_TO_USE.values():
        if isinstance(strat_type, bool):
            continue
        strats_file.write(", ".join([fff.__name__ for fff in strat_type]))
        strats_file.write("\n")
    strats_file.close()
else:
    # f = (open('results/hunt_'+task+'_'+str(random.randint(0,10**4))+'_results.txt', 'w') if OUTPUT_TO_FILE else sys.stdout)
    f = (open('results/hunt_'+task+'_results.txt', 'w') if OUTPUT_TO_FILE else sys.stdout)


mtree = MetaTree( patts, **STRATS_TO_USE)

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
    mtree.do_level(f=f)
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
    f.flush()


if mtree.has_proof_tree():
    proof_tree = mtree.find_proof_tree()
    proof_tree.pretty_print(file=f)
    json = proof_tree.to_json(indent="  ")
    print(json,file=f)
    if not ProofTree.from_json(json).to_json(indent="  ") == json:
        print('**ASSERT FAILURE** assert ProofTree.from_json(json).to_json(indent="  ") == json')


end = time()

print("I took", end - start, "seconds",file=f)

if spectrum_mode:
    print(end-start,file=spectrum_results)
    print(json, file=spectrum_results)
    spectrum_results.close()

if f != sys.stdout:
    f.close()
