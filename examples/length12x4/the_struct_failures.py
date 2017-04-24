import time
import atrap
from permuta import *

tasks = ['1234_1243_1324_1342_1423_1432_2134_2143_2314_2341',
         '1234_1243_1324_1342_1423_1432_2134_2143_2314_3214',
         '1234_1243_1324_1342_1423_1432_2134_2143_2341_3214',
         '1234_1243_1324_1342_1423_1432_2134_2314_2341_3214',
         '1234_1243_1324_1342_1423_1432_2143_2314_2341_3214',
         '1234_1243_1324_1342_1423_2134_2143_2314_2341_3214',
         '1234_1243_1324_1342_1432_2134_2143_2314_2341_3214',
         '1234_1243_1324_1342_1432_2134_2143_2341_3124_3214',
         '1234_1243_1324_1342_1432_2143_2314_2341_3124_3214',
         '1234_1243_1324_1432_2143_2314_3124_3214_3241_4213',
         '1234_1243_1342_1423_1432_2134_2143_2314_2341_3214',
         '1243_1324_1342_1423_1432_2134_2143_2314_2341_3214',
        ]

proof_strat = 'ci'

for task in tasks:
    patts = [ Perm([ int(c) - 1 for c in p ]) for p in task.split('_') ]
    input_set = PermSet.avoiding(patts)


    if proof_strat == 'rci':
        recipes = [atrap.recipes.all_row_and_column_insertions]
    elif proof_strat == 'ci':
        recipes = [atrap.recipes.all_cell_insertions]
    elif proof_strat == 'both':
        recipes = [atrap.recipes.all_cell_insertions, atrap.recipes.all_row_and_column_insertions]

    bakery = atrap.patisserie.Bakery(input_set, recipes)

    start_time = time.time()

    gaur = 0
    while True:
        print("Size of frontier:", len(bakery.frontier))
        good = bakery.bake(verbose=True)
        if good:
            break
        gaur += 1
        if gaur > 3: break
    task = task + proof_strat
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
