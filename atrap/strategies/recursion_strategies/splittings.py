"""
    
    ==================

    We need a "recursive cleaner". A recursive strategy may return a boatload of redudant splittings.
    For example, suppose the tiling T splits into five parts A / B / C / D / E, where B / C / D / E are
    all subset verified. Clearly we don't want to consider the many different options formed by combining 
    B / C / D / E in various ways, such as:
      A / B / C / D / E
      A / BC / DE
      A / BCD / E
      A / BCDE
      etc

    But, we also don't necessarily want to just combine them all together! For example, suppose T splits
    into three parts A / B / C, where B and C are subset verified. It's possible that A is not an ancestor
    but A+B together will be. In which case, the splitting A / B / C does us no good, but AB / C does!

    I think the right place for this analysis is not within the Rescursive Strategy, but back in the Metatree.
    So, this will return the "maximally split" splittings, and leave it to the metatree to decide what to
    do with them.

    ==================

    Currently, points are NOT shared between components of a splitting

    ==================

    TOTHINK: Do we need to check every length UP TO the verification length or can we just check the
       verification length itself? If we don't NEED TO, then is it maybe advantageous anyway because
       we can exit early?

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
from atrap.tools import basis_partitioning
from atrap.tools import cells_of_occurrences
from .recursive_class import RecursiveStrategy

def splittings(tiling, basis, basis_partitioning=basis_partitioning):

    all_valid_splittings = find_good_splittings(tiling, basis, basis_partitioning=basis_partitioning)

    # turn the list of lists of lists into a list of lists of Tilings
    for good_split in all_valid_splittings:
        # print('good split:',good_split)
        strategy = [Tiling({x:tiling[x] for x in part}) for part in good_split]
        yield RecursiveStrategy( "A splitting of the tiling", strategy )


    # TODO: maybe here I need to filter out maximal things????

def find_good_splittings(tiling, basis, basis_partitioning=basis_partitioning, built=[]):

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
    verification_length = max([len(P) for P in basis]) + tiling.total_points + sum(1 for _, block in tiling.non_points if isinstance(block, PositiveClass))
    containing_perms, _ = basis_partitioning(tiling, verification_length, basis)

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
