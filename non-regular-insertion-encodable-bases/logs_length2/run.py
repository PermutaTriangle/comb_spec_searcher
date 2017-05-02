from permuta import *
from atrap import MetaTree
from atrap.strategies import *
from atrap.ProofTree import ProofTree

from time import time
from time import gmtime, strftime

all_strategies = [ [all_cell_insertions, all_row_placements], [all_equivalent_row_placements, all_point_placements], [empty_cell_inferral, jays_subclass_inferral, row_and_column_separation], [reversibly_deletable_cells, components], [subset_verified, is_empty] ]

mimic_regular_insertion_encoding = [ [all_cell_insertions, all_minimum_row_placements], [all_equivalent_minimum_row_placements], [empty_cell_inferral], [reversibly_deletable_cells], [one_by_one_verification, is_empty]]

standard_strategies_w_left_col = [ [all_cell_insertions, all_leftmost_column_placements], [all_equivalent_leftmost_column_placements], [empty_cell_inferral, row_and_column_separation, subclass_inferral], [components, reversibly_deletable_cells], [subset_verified, is_empty] ]
standard_strategies_w_min_row = [ [all_cell_insertions, all_minimum_row_placements], [all_equivalent_minimum_row_placements], [empty_cell_inferral, row_and_column_separation, subclass_inferral], [components, reversibly_deletable_cells], [subset_verified, is_empty] ]
standard_strategies_w_left_col_min_row = [ [all_cell_insertions, all_leftmost_column_placements, all_minimum_row_placements], [all_equivalent_leftmost_column_placements, all_equivalent_minimum_row_placements], [empty_cell_inferral, row_and_column_separation, subclass_inferral], [components, reversibly_deletable_cells], [subset_verified, is_empty] ]
standard_strategies_w_all_cols = [ [all_cell_insertions, all_column_placements], [all_equivalent_column_placements], [empty_cell_inferral, row_and_column_separation, subclass_inferral], [components, reversibly_deletable_cells], [subset_verified, is_empty] ]
standard_strategies_w_all_rows = [ [all_cell_insertions, all_row_placements], [all_equivalent_row_placements], [empty_cell_inferral, row_and_column_separation, subclass_inferral], [components, reversibly_deletable_cells], [subset_verified, is_empty] ]
standard_strategies_w_all_rows_cols = [ [all_cell_insertions, all_row_placements, all_column_placements], [all_equivalent_row_placements, all_equivalent_column_placements], [empty_cell_inferral, row_and_column_separation, subclass_inferral], [components, reversibly_deletable_cells], [subset_verified, is_empty] ]
standard_strategies_point_pl = [ [all_cell_insertions], [all_point_placements], [empty_cell_inferral, row_and_column_separation, subclass_inferral,], [components, reversibly_deletable_cells], [subset_verified, is_empty] ]

# First one is best
finite_strategies_w_min_row = [ [all_cell_insertions, all_minimum_row_placements], [all_equivalent_minimum_row_placements], [empty_cell_inferral, row_and_column_separation, subclass_inferral], [], [subset_verified, is_empty] ]
finite_strategies_w_max_point_pl = [ [all_cell_insertions], [all_maximum_point_placements], [empty_cell_inferral, row_and_column_separation, subclass_inferral], [], [subset_verified, is_empty] ]

# import sys


def perm_to_str(perm):
    return "".join([str(i) for i in list(perm)])

def perms_to_str(perms):
    return "_".join(perm_to_str(perm) for perm in perms)

length_to_process = '2'

# 1
strat_pack = standard_strategies_w_left_col
strat_pack_desc = 'standard_strategies_w_left_col'
max_depth = 8

first_failure = False
first_success = False

# with open('length'+length_to_process) as g:
# with open('test') as f:
with open('length'+length_to_process+'_failed') as g:
    content = g.readlines()
    content = [x.strip() for x in content]

    for i in range(len(content)):
        if content[len(content)-1-i].split() and content[len(content)-1-i].split()[0] == 'Maximum':
            i = i-2
            break

    content = content[len(content)-1-i::]

    for task in content:

        if task == '':
            continue

        print('Now processing {}'.format(task))

        patts = [ Perm([ int(c) for c in p ]) for p in task.split('_') ]
        mtree = MetaTree(patts, *strat_pack)

        with open(task, "w") as f:

            print(task, file=f)
            print("Log created ", strftime("%a, %d %b %Y %H:%M:%S", gmtime()),file=f)

            start_time = time()
            depth_tried = 0

            while not mtree.has_proof_tree():

                if mtree.depth_searched == max_depth:
                    break

                mtree.do_level()
                depth_tried += 1

                print("We had {} inferral cache hits and {} partitioning cache hits".format(mtree.inferral_cache_hits, mtree.partitioning_cache_hits))
                print("The partitioning cache has {} tilings in it right now".format( len(mtree._basis_partitioning_cache) ) )
                print("The inferral cache has {} tilings in it right now".format( len(mtree._inferral_cache) ) )
                print("There are {} tilings in the search tree".format( len(mtree.tiling_cache)))
                print("Time taken so far is {} seconds".format( time() - start_time ) )
                print('')

            end_time = time()

            if mtree.has_proof_tree():
                proof_tree = mtree.find_proof_tree()

                print("Finding the proof tree took", int(end_time - start_time), "seconds", file=f)
                print('The depth searched was {}'.format(depth_tried), file=f)
                print("",file=f)
                print('Strategies applied: {}'.format(strat_pack_desc), file=f)
                print('Maximum depth set at {}'.format(str(max_depth)), file=f)
                print("",file=f)
                print("Human readable:", file=f)
                print("",file=f)

                proof_tree.pretty_print(file=f)

                print("",file=f)
                print("Computer readable (JSON):", file=f)
                print("", file=f)
                print(proof_tree.to_json(sort_keys=True), file=f)

                if not first_success:
                    first_success = True
                    with open('length{}_succeeded'.format(length_to_process), 'a+') as f:
                        print('', file=f)
                        print('Strategies applied: {}'.format(strat_pack_desc), file=f)
                        print('Maximum depth set at {}'.format(str(max_depth)), file=f)
                        print('', file=f)

                with open('length{}_succeeded'.format(length_to_process), 'a+') as e:
                    print(task, file=e)

            else:
                print('No proof tree found. Tried for {} seconds'.format(int(end_time - start_time)), file=f)
                print("",file=f)
                print("",file=f)
                print('Strategies applied: {}'.format(strat_pack_desc), file=f)
                print('Maximum depth set at {}'.format(str(max_depth)), file=f)
                print("",file=f)

                if not first_failure:
                    first_failure = True
                    with open('length{}_failed'.format(length_to_process), 'a+') as f:
                        print('', file=f)
                        print('Strategies applied: {}'.format(strat_pack_desc), file=f)
                        print('Maximum depth set at {}'.format(str(max_depth)), file=f)
                        print('', file=f)

                with open('length{}_failed'.format(length_to_process), 'a+') as e:
                    print(task, file=e)

if not first_failure:
    with open('length{}_failed'.format(length_to_process), 'a+') as f:
        print('', file=f)
        print('Strategies applied: {}'.format(strat_pack_desc), file=f)
        print('Maximum depth set at {}'.format(str(max_depth)), file=f)
        print('', file=f)

else:
    with open('length{}_failed'.format(length_to_process), 'a+') as f:
        print('', file=f)

if not first_success:
    with open('length{}_succeeded'.format(length_to_process), 'a+') as f:
        print('', file=f)
        print('Strategies applied: {}'.format(strat_pack_desc), file=f)
        print('Maximum depth set at {}'.format(str(max_depth)), file=f)
        print('', file=f)

else:
    with open('length{}_succeeded'.format(length_to_process), 'a+') as f:
        print('', file=f)
