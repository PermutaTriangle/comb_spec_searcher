import time
# import atrap
# from permuta import *
#   from permuta.misc.symmetry import *
from itertools import combinations

from atrap import MetaTree
from permuta import *
from permuta.permutils import *


from time import time
from atrap.strategies import *

all_strategies = [ [all_cell_insertions, all_row_placements], [all_equivalent_row_placements, all_point_placements], [empty_cell_inferral, jays_subclass_inferral, row_and_column_separation], [reversibly_deletable_cells, components], [subset_verified, is_empty] ]

mimic_regular_insertion_encoding = [ [all_cell_insertions, all_minimum_row_placements], [all_equivalent_minimum_row_placements], [empty_cell_inferral], [reversibly_deletable_cells], [one_by_one_verification, is_empty]]

standard_strategies_w_jay = [ [all_cell_insertions], [all_point_placements], [jays_subclass_inferral, row_and_column_separation], [reversibly_deletable_cells], [subset_verified] ]
standard_strategies = [ [all_cell_insertions], [all_point_placements], [subclass_inferral, row_and_column_separation], [reversibly_deletable_cells], [subset_verified] ]


perms = tuple(PermSet(3))
def perm_to_str(perm):
    return "".join([str(i) for i in list(perm)])

def perms_to_str(perms):
    return "_".join(perm_to_str(perm) for perm in perms)

tasks = ['021_2310_3120',
         '021_1023_1230_2130_2301_2310_3102',
         '021_2301_2310_3210',
         '021_2301_2310_3120_3210',
         '021_0123_2103_2301',
         '021_0123_1023_1203_3201',
         '021_2301_2310_3120_3201',
         '021_1023_1203_1230_2130_2301_2310_3012_3102',
         '012_0321_1032_2103',
         '021_1230_3012_3210',
         '012_1032_2301_3120',
         '021_2301_2310_3201_3210',
         '012_1032_1320',
         '021_2310_3210',
         '021_2301_2310_3120',
         '012_0321_2103',
         '021_2301_2310_3201',
         '021_2301_2310_3120_3201_3210',
         '021_2310_3201',
         '021_1023_1230_2130_2301_3102',
         '012_1032_2301_2310',
         '021_1023_1203_1230_2130_2301_3012_3102',
         '021_2310_3120_3210',
         '012_3120',
         '012_1032_1320_3120',
         '021_1023_1203_3201',
         '012_1032_3120',
         '012_1032_2301_2310_3120']

for task in tasks:

    # task = perms_to_str(task)
    print(task)
    patts = [ Perm([ int(c) for c in p ]) for p in task.split('_') ]

    mtree = MetaTree( patts, *standard_strategies )


    #mtree.do_level()
    start_time = time()

    while not mtree.has_proof_tree():
        mtree.do_level()
        # print(len(mtree.tiling_cache))
        # for tiling, node in mtree.tiling_cache.items():
        #     print(tiling)
        #     print(node.sibling_node.verification)
        #     for verification in node.sibling_node.verification:
        #         for t in verification:
        #             print(t)
        #     print("--------------")
        # if mtree.depth_searched == 5:
            # break

    proof_tree = mtree.find_proof_tree()
    # proof_tree.pretty_print()

    end_time = time()

    # print("I took", end_time - start_time, "seconds")

    with open(task, "w") as f:
        # tree = bakery.get_proof_tree()

        print("",file=f)
        print("Finding the proof tree for", task ,  "took", int(end_time - start_time), "seconds",file=f)
        print("",file=f)
        print("Human readable:",file=f)
        print("",file=f)

        # tree.pretty_print(file=f)
        proof_tree.pretty_print(file=f)

        # print("",file=f)
        # print("Computer readable (JSON):",file=f)
        # print("",file=f)
        # print(tree.to_json(indent="    ", sort_keys=True), file=f)
