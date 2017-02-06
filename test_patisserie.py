import time
import atrap
from permuta import *

#input_set = PermSet.avoiding([Perm((1, 0)), Perm((0, 1, 2))])
#input_set = PermSet.avoiding([Perm((0, 1)), Perm((1, 0))])
#input_set = PermSet.avoiding([Perm((0, 2, 1)), Perm((3, 2, 1, 0))])
#input_set = PermSet.avoiding([Perm((0, 2, 1)), Perm((2, 1, 0))])
input_set = PermSet.avoiding([Perm((2, 1, 0)), Perm((1, 0, 3, 2))])

#recipes = [atrap.recipes.all_row_and_column_insertions]
recipes = [atrap.recipes.all_cell_insertions]
#recipes = [atrap.recipes.all_cell_insertions, atrap.recipes.all_row_and_column_insertions]
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
