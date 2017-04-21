from permuta import *
from atrap import MetaTree
from atrap.strategies import *
from atrap.ProofTree import ProofTree

from time import time
from time import gmtime, strftime

all_strategies = [ [all_cell_insertions, all_row_placements], [all_equivalent_row_placements, all_point_placements], [empty_cell_inferral, jays_subclass_inferral, row_and_column_separation], [reversibly_deletable_cells, components], [subset_verified, is_empty] ]

mimic_regular_insertion_encoding = [ [all_cell_insertions, all_minimum_row_placements], [all_equivalent_minimum_row_placements], [empty_cell_inferral], [reversibly_deletable_cells], [one_by_one_verification, is_empty]]

# Run 1
standard_strategies = [ [all_active_cell_insertions], [all_point_placements], [empty_cell_inferral, row_and_column_separation, subclass_inferral], [components, reversibly_deletable_cells], [subset_verified, is_empty] ]
# standard_strategies = [ [all_cell_insertions], [all_point_placements], [empty_cell_inferral, row_and_column_separation, subclass_inferral], [components, reversibly_deletable_cells], [subset_verified, is_empty] ]
standard_strategies = [ [all_cell_insertions, all_row_placements, all_column_placements], [all_equivalent_row_placements, all_equivalent_column_placements], [empty_cell_inferral, row_and_column_separation, subclass_inferral], [components, reversibly_deletable_cells], [subset_verified, is_empty] ]

# Run 2
# standard_strategies = [ [all_cell_insertions], [all_point_placements], [empty_cell_inferral, row_and_column_separation, subclass_inferral], [components, reversibly_deletable_cells], [subset_verified, is_empty] ]

# Next runs: Add symmetries, splittings, fission/fusion

finite_strategies = [ [all_cell_insertions, all_minimum_row_placements], [all_equivalent_minimum_row_placements], [empty_cell_inferral, subclass_inferral], [], [subset_verified] ]

# import sys


def perm_to_str(perm):
    return "".join([str(i) for i in list(perm)])

def perms_to_str(perms):
    return "_".join(perm_to_str(perm) for perm in perms)

length_to_process = '11'

with open('length'+length_to_process) as f:
# with open('length'+length_to_process+'_depth_geq4') as f:
    content = f.readlines()
    content = [x.strip() for x in content]
    for task in content:

        print('Now processing {}'.format(task))

        patts = [ Perm([ int(c) for c in p ]) for p in task.split('_') ]
        mtree = MetaTree(patts, *standard_strategies)

        with open(task, "w") as f:

            print(task, file=f)
            print('')
            print("Log created ", strftime("%a, %d %b %Y %H:%M:%S", gmtime()),file=f)

            start_time = time()

            while not mtree.has_proof_tree():
                mtree.do_level()
                print("We had {} inferral cache hits and {} partitioning cache hits".format(mtree.inferral_cache_hits, mtree.partitioning_cache_hits))
                print("The partitioning cache has {} tilings in it right now".format( len(mtree._basis_partitioning_cache) ) )
                print("The inferral cache has {} tilings in it right now".format( len(mtree._inferral_cache) ) )
                print("There are {} tilings in the search tree".format( len(mtree.tiling_cache)))
                print("Time taken so far is {} seconds".format( time() - start_time ) )
                print('')
                if mtree.depth_searched == 6:
                    break

            end_time = time()

            if mtree.has_proof_tree():
                proof_tree = mtree.find_proof_tree()

                print("Finding the proof tree for", task ,  "took", int(end_time - start_time), "seconds", file=f)
                print("",file=f)
                print("Human readable:", file=f)
                print("",file=f)

                proof_tree.pretty_print(file=f)

                print("",file=f)
                print("Computer readable (JSON):", file=f)
                print("", file=f)
                print(proof_tree.to_json(sort_keys=True), file=f)
            else:
                print('No proof tree found', file=f)
                print("Took", int(end_time - start_time), "seconds", file=f)
