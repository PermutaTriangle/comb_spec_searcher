"""
    ==================

    TODO: Need to speedtest my standardize against the permuta version

    ==================

"""

def standardize(p_list):
    ordered = sorted(p_list)
    return tuple(ordered.index(x) for x in p_list)

import itertools
from grids import *
from permuta import *
from atrap.tools import cells_of_occurrences
from .recursive_class import RecursiveStrategy

SPLITTINGS_HACK = True

def splittings(tiling, basis, basis_partitioning=None, verification_strategies=None, tiling_cache=None):

    all_valid_splittings = find_good_splittings(tiling, basis, basis_partitioning=basis_partitioning)

    # turn the list of lists of lists into a list of lists of Tilings
    for good_split in all_valid_splittings:
        # print('good split:',good_split)
        strategy = [Tiling({x:tiling[x] for x in part}) for part in good_split]
        if SPLITTINGS_HACK:
            # This is redoing a lot of verification work that should be cached
            # And this should only happen when the strategy is "splittings"
            number_of_verified_results = 0

            for sub_tiling in strategy:
                child_or_node = tiling_cache.get(sub_tiling)
                if child_or_node is None:
                    verified = False
                    for verification_strategy_generator in verification_strategies:
                        for verification_strategy in verification_strategy_generator(tiling, basis=basis, basis_partitioning=basis_partitioning):
                            verified = True
                            number_of_verified_results += 1
                            break
                        if verified:
                            break
                else:
                    if child_or_node.is_verified():
                        number_of_verified_results += 1

                if number_of_verified_results > 1:
                    break

            if number_of_verified_results > 1:
                continue

        yield RecursiveStrategy( "A splitting of the tiling", strategy , [tiling._back_map for tiling in strategy])


    # TODO: maybe here I need to filter out maximal things????

def find_good_splittings(tiling, basis, basis_partitioning=None, built=[]):

    tiling_keys = dict(tiling).keys()
    occupied_cells = tuple(tiling_keys)
    occupied_cells_set = set(tiling_keys)

    # if len(built) == 0:
        # print("\tSplitting a tiling of size: "+str(len(occupied_cells_set))+"\tlen: "+str(max([len(P) for P in basis]) + tiling.total_points + sum(1 for _, block in tiling.non_points if isinstance(block, PositiveClass))))
    # else:
        # print("\t\t",len(built),"parts exist already.")
        # print(built)


    claimed = (set() if len(built) == 0 else set.union(*built))
    if len(claimed) == len(occupied_cells):
        # print('\nlen(claimed) = len(occupied_cells):')
        # print(claimed, occupied_cells)
        return [built]

    cells_to_check = occupied_cells_set.difference(claimed)
    must_contain = min(cells_to_check)
    cells_to_check.remove(must_contain)
    subsets_to_check = itertools.chain.from_iterable(itertools.combinations(cells_to_check, r) for r in range(0, len(cells_to_check)+1))


    good_splittings = []
    min_length = min([len(P) for P in basis])
    verification_length = max([len(P) for P in basis]) + tiling.total_points + sum(1 for _, block in tiling.non_points if isinstance(block, PositiveClass))

    for subset in subsets_to_check:

        new_part = set(subset)
        new_part.add(must_contain)

        other_cells = occupied_cells_set.difference(new_part).difference(claimed)
        # print('other_cells:',other_cells)
        # if len(other_cells) == 0:
            # continue

        if len(claimed) == 0 and len(new_part) == len(occupied_cells_set):
            continue

        partition_to_check = built + [new_part, other_cells]
        cell_to_part_dict = {}
        for (index, part) in enumerate(partition_to_check):
            for cell in part:
                cell_to_part_dict[cell] = index

        good_partition = True

        for length_to_check in range(min_length, verification_length+1):

            containing_perms, _ = basis_partitioning(tiling, length_to_check, basis, "splittings")

            if not good_partition:
                break

            for basis_element in containing_perms.keys():

                if not good_partition:
                    break

                for position_set in containing_perms[basis_element]:

                    partition_split = [[-1 for i in range(verification_length)] for p in partition_to_check]

                    for cell in position_set.keys():
                        cell_perm, cell_values, cell_indices = position_set[cell]

                        for index in range(len(cell_perm)):
                            partition_split[cell_to_part_dict[cell]][cell_indices[index]] = cell_values[index]

                    permize = ( Perm( standardize ([entry for entry in part_perm if entry != -1]) ) for part_perm in partition_split )

                    if not any( any ( perm.contains(basis_element) for basis_element in basis ) for perm in permize ):
                        # print('\tthis partition is bad')
                        # print('\t',partition_to_check)
                        # print('\t',position_set)
                        # print('\t', partition_split)
                        good_partition = False
                        break

        if good_partition:
            good_splittings.extend(find_good_splittings(tiling, basis, basis_partitioning=basis_partitioning, built=built+[new_part]))

    return good_splittings
