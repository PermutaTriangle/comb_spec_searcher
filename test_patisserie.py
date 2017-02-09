import time
import atrap
from permuta import *

#input_set = PermSet.avoiding([Perm((1, 0)), Perm((0, 1, 2))])
#input_set = PermSet.avoiding([Perm((0, 1)), Perm((1, 0))])
#input_set = PermSet.avoiding([Perm((0, 2, 1)), Perm((3, 2, 1, 0))])
#input_set = PermSet.avoiding([Perm((0, 2, 1)), Perm((2, 1, 0))])
# input_set = PermSet.avoiding([Perm((2, 1, 0)), Perm((1, 0, 3, 2))])
# input_set = PermSet.avoiding([Perm((0, 1, 2))])
input_set = PermSet.avoiding([Perm((0, 2, 1))])
#input_set = PermSet.avoiding([Perm((0, 1, 2)), Perm((0, 3, 2, 1))])
#input_set = PermSet.avoiding([Perm((0, 1, 2)), Perm((1, 0, 3, 2))])
# input_set = PermSet.avoiding([Perm((0,2,1,3))])

#recipes = [atrap.recipes.all_row_and_column_insertions]
recipes = [atrap.recipes.all_cell_insertions]
#recipes = [atrap.recipes.all_cell_insertions, atrap.recipes.all_row_and_column_insertions]
bakery = atrap.patisserie.Bakery(input_set, recipes)


print("Finding proof for:\n")
print(input_set)
print()

tp_L = "└──── "
tp_pipe = "│     "
tp_tee = "├──── "
tp_empty = "      "


def print_tree(tree, depth, legend, prefix="root: ", tail=False):
    label_counter = legend[0][1]
    print(prefix, label_counter, sep="")
    legend.append([label_counter, tree[0]])
    legend[0][1] += 1
    for subtree_number in range(1, len(tree)-1):
        print_tree(tree[subtree_number], depth+1, legend, prefix[:-6] + (tp_pipe if tail else tp_empty) + tp_tee, True)
    if len(tree) > 1:
        print_tree(tree[-1], depth+1, legend, prefix[:-6] + (tp_pipe if tail else tp_empty) + tp_L, False)


start_time = time.time()
number = 0
while True:
    number += 1
    print("Baking generation", number)
    good = bakery.bake()
    if good:
        print("Found proof")
        print()
        print("Here are the leaves")
        proof, tree = bakery.give_me_proof()
        for data in proof:
            if isinstance(data, list):
                for stuff in data:
                    print(stuff)
            else:
                print(data)
        print()
        print("Here is the tree")
        print()
        legend = [["label counter:", 0]]
        print_tree(tree, 0, legend)
        print()
        for label, tiling in legend:
            if isinstance(tiling, int):
                continue
            print(label)
            print(tiling)
            print()
        print()
        break

print()
print("I took", int(time.time() - start_time), "seconds")
