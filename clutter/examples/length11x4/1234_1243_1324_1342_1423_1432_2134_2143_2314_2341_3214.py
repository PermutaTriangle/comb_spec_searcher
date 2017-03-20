import time
import atrap
from permuta import *

tasks = ['1234_1243_1324_1342_1423_1432_2134_2143_2314_2341_3214']

for task in tasks:
    patts = [ Perm([ int(c) - 1 for c in p ]) for p in task.split('_') ]
    input_set = PermSet.avoiding(patts)

    # recipes = [atrap.recipes.all_row_and_column_insertions]
    # recipes = [atrap.recipes.all_cell_insertions]
    recipes = [atrap.recipes.all_cell_insertions, atrap.recipes.all_row_and_column_insertions]
    bakery = atrap.patisserie.Bakery(input_set, recipes)

    start_time = time.time()

    while True:
        #print("Size of frontier:", len(bakery.frontier))
        good = bakery.bake(verbose=True)
        if good:
            break
    task = task + "row_column_insertions_and_cell_insertions_unmixed"
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
