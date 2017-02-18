import time
import atrap
from permuta import *
from permuta.misc.symmetry import *
from itertools import combinations

perms = tuple(PermSet(3))
def perm_to_str(perm):
    return "".join([str(i) for i in list(perm)])

def perms_to_str(perms):
    return "_".join(perm_to_str(perm) for perm in perms)

for i in range(1, len(perms)):
    for basis in combinations(perms,i):
        if lex_min(basis) == basis:
            input_set = PermSet.avoiding(basis)
            if len(basis) != len(input_set.basis):
                continue
            recipes = [atrap.recipes.all_cell_insertions, atrap.recipes.all_row_and_column_insertions]
            bakery = atrap.patisserie.Bakery(input_set, recipes)
            task = perms_to_str(basis)


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
