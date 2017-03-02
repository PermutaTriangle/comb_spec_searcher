import time
import atrap
from permuta import *

task = '210_0231'
patts = [ Perm([ int(c) for c in p ]) for p in task.split('_') ]
input_set = PermSet.avoiding(patts)

# recipes = [atrap.recipes.all_row_and_column_insertions]
recipes = [atrap.recipes.all_cell_insertions]
# recipes = [atrap.recipes.all_cell_insertions, atrap.recipes.all_row_and_column_insertions]
bakery = atrap.patisserie.Bakery(input_set, recipes)


print("Finding proof for:\n")
print(input_set)
print()

start_time = time.time()
number = 0
while True:
    number += 1
    print("Baking generation", number)
    good = bakery.bake()
    if good:
        print("Found proof")
        proof = bakery.give_me_proof()
        for tiling in proof:
            print(tiling)
        break

print()
print("I took", int(time.time() - start_time), "seconds")
