import time
import atrap
from permuta import *
from permuta.misc.symmetry import *
from itertools import combinations

def perm_to_str(perm):
    return "".join([str(i) for i in list(perm)])

def perms_to_str(perms):
    return "_".join(perm_to_str(perm) for perm in perms)

perms3 = PermSet(3)
perms4 = PermSet(4)

for i in range(1,len(perms3) + 1):
    for basis3 in combinations(perms3,i):
        perms4 = sorted(list( Av(basis3).of_length(4) ))
        for j in range(1, len(perms4) + 1):
            # if i == 1 and j < 8: #comment, made finding bases slightly smarter halfway through run.
            #     continue
            for basis4 in combinations(perms4,j):
                basis = basis3 + basis4
                if lex_min(basis) == basis:
                    input_set = PermSet.avoiding(basis)
                    if len(basis) != len(input_set.basis):
                        continue
                    recipes = [atrap.recipes.all_cell_insertions, atrap.recipes.all_row_and_column_insertions]
                    bakery = atrap.patisserie.Bakery(input_set, recipes)
                    task = perms_to_str(basis)
                    print(task)

                    start_time = time.time()

                    while True:
                        #print("Size of frontier:", len(bakery.frontier))
                        good = bakery.bake(verbose=True)
                        if good:
                            break
                    with open(task, "w") as f:

                        tree = bakery.get_proof_tree()

                        print("",file=f)
                        print("Finding the proof tree for", input_set.__repr__() ,  "took", int(time.time() - start_time), "seconds",file=f)
                        print("",file=f)
                        print("Human readable:",file=f)
                        print("",file=f)

                        tree.pretty_print(file=f)

                        print("",file=f)
                        print("Computer readable (JSON):",file=f)
                        print("",file=f)
                        print(tree.to_json(indent="    ", sort_keys=True), file=f)
