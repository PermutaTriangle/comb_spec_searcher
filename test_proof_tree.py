import time
import atrap
from permuta import *


input_set = PermSet.avoiding([Perm((2, 1, 0)), Perm((1, 0, 3, 2))])
#input_set = PermSet.avoiding([Perm((2, 1, 0)).reverse(), Perm((0, 3, 2, 1))])


#recipes = [atrap.recipes.all_row_and_column_insertions]
#recipes = [atrap.recipes.all_cell_insertions]
recipes = [atrap.recipes.all_cell_insertions, atrap.recipes.all_row_and_column_insertions]
bakery = atrap.patisserie.Bakery(input_set, recipes)


start_time = time.time()

while True:
    #print("Size of frontier:", len(bakery.frontier))
    good = bakery.bake(verbose=True)
    if good:
        break

tree = bakery.get_proof_tree()

print()
print("Finding the proof tree took", int(time.time() - start_time), "seconds")
print()
print("Human readable:")
print()

tree.pretty_print()

print()
print("Computer readable (JSON):")
print()
print(tree.to_json(indent="    ", sort_keys=True))
