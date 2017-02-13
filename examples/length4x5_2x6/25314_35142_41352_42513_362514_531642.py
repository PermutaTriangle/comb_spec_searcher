import time
import atrap
from permuta import *

# sum closure of 321
tasks = ['25314_35142_41352_42513_362514_531642']

for task in tasks:
    patts = [ Perm([ int(c) - 1 for c in p ]) for p in task.split('_') ]
    input_set = PermSet.avoiding(patts)

    #recipes = [atrap.recipes.all_row_and_column_insertions]
    recipes = [atrap.recipes.all_cell_insertions]
    # recipes = [atrap.recipes.all_cell_insertions, atrap.recipes.all_row_and_column_insertions]
    bakery = atrap.patisserie.Bakery(input_set, recipes)

    with open(task, "w") as f:

        print("Finding proof for:\n",file=f)
        print(input_set,file=f)
        print("\n",file=f)

        tp_L = "└──── "
        tp_pipe = "│     "
        tp_tee = "├──── "
        tp_empty = "      "


        def print_tree(tree, depth, legend, prefix="root: ", tail=False):
            label_counter = legend[0][1]
            print(prefix, label_counter, sep="", file=f)
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
            print("Baking generation", number,file=f)
            good = bakery.bake()
            if good:
                print("Found proof",file=f)
                print()
                print("Here are the leaves",file=f)
                proof, tree = bakery.give_me_proof()
                for data in proof:
                    if isinstance(data, list):
                        for stuff in data:
                            print(stuff,file=f)
                    else:
                        print(data,file=f)
                print("\n",file=f)
                print("Here is the tree",file=f)
                print("\n",file=f)
                legend = [["label counter:", 0]]
                print_tree(tree, 0, legend)
                print("\n",file=f)
                for label, tiling in legend:
                    if isinstance(tiling, int):
                        continue
                    print(label,file=f)
                    print(tiling,file=f)
                    print("\n",file=f)
                print("\n",file=f)
                break

        print("\n",file=f)
        print("I took", int(time.time() - start_time), "seconds",file=f)
