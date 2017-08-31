import sys
import os
import random

from atrapv2 import TileScope
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


tilescope = TileScope(patts, **STRATS_TO_USE)
start = time()

proof_tree = tilescope.auto_search(1,f=f)

end = time()

json = proof_tree.to_json()

print("I took", end - start, "seconds",file=f)

if spectrum_mode:
    print(end-start,file=spectrum_results)
    print(json, file=spectrum_results)
    spectrum_results.close()

if f != sys.stdout:
    f.close()
