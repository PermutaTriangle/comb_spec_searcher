import time
import atrap
from permuta import *

# task = "1234_1243_1342_1423_1432_2134_2143_2413_4213"
#
# patts = [ Perm([ int(c) - 1 for c in p ]) for p in task.split('_') ]
# input_set = PermSet.avoiding(patts)

#input_set = PermSet.avoiding([Perm((1, 0)), Perm((0, 1, 2))])
#input_set = PermSet.avoiding([Perm((0, 1)), Perm((1, 0))])
#input_set = PermSet.avoiding([Perm((0, 2, 1)), Perm((3, 2, 1, 0))])
#input_set = PermSet.avoiding([Perm((0, 2, 1)), Perm((2, 1, 0))])
input_set = PermSet.avoiding([Perm((2, 1, 0)), Perm((1, 0, 3, 2))])
#input_set = PermSet.avoiding([Perm((0, 1, 2))])
#input_set = PermSet.avoiding([Perm((0, 2, 1))])
#input_set = PermSet.avoiding([Perm((0, 1, 2)), Perm((0, 3, 2, 1))])
#input_set = PermSet.avoiding([Perm((0, 1, 2, 3)), Perm((3, 2, 1, 0))])
# input_set = PermSet.avoiding([Perm((2, 1, 0)), Perm((1, 0, 3, 2))])
# input_set = PermSet.avoiding([Perm((0, 1, 2))])
# input_set = PermSet.avoiding([Perm((0, 2, 1))])
# input_set = PermSet.avoiding([Perm((0, 1, 2)), Perm((0, 3, 2, 1))])
# input_set = PermSet.avoiding([Perm((0, 1, 2, 3)), Perm((3, 2, 1, 0))])
#input_set = PermSet.avoiding([Perm((0, 1, 2)), Perm((1, 0, 3, 2))])
#input_set = PermSet.avoiding([Perm((0, 1, 2, 3))])
#input_set = PermSet.avoiding([Perm((0,2,1,3))])

# recipes = [atrap.recipes.all_row_and_column_insertions]
recipes = [atrap.recipes.all_cell_insertions]
# recipes = [atrap.recipes.all_cell_insertions, atrap.recipes.all_row_and_column_insertions]
bakery = atrap.patisserie.Bakery(input_set, recipes)

#def print(*args, **kwargs):
#    pass


print("Finding proof for:\n")
print(input_set)
print()

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
