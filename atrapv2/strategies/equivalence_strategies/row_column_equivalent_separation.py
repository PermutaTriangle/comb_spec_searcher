from grids import Tiling, Block, PositiveClass
from grids import Cell
from permuta.misc import ordered_set_partitions
import itertools

from comb_spec_searcher import EquivalenceStrategy

# TODO: Pass in whole class to simplify basis testing, maybe?

"""
    Generates integer partitions
    From: http://stackoverflow.com/questions/10244180/python-generating-integer-partitions
    To get the integer compositions of n, do ruleGen(n, 1, lambda x: 1)
"""
def ruleGen(n, m, sigma):
    """
    Generates all interpart restricted compositions of n with first part
    >= m using restriction function sigma. See Kelleher 2006, 'Encoding
    partitions as ascending compositions' chapters 3 and 4 for details.
    """
    a = [0 for i in range(n + 1)]
    k = 1
    a[0] = m - 1
    a[1] = n - m + 1
    while k != 0:
        x = a[k - 1] + 1
        y = a[k] - 1
        k -= 1
        while sigma(x) <= y:
            a[k] = x
            x = sigma(x)
            y -= x
            k += 1
        a[k] = x + y
        yield a[:k + 1]

""" TODO: Not caching. Should I be? Probably not worth it. """
def all_ordered_set_partitions(lst):
    integer_comps = ruleGen(len(lst), 1, lambda x : 1)
    all_osp = [ordered_set_partitions(lst, comp) for comp in integer_comps]
    return itertools.chain.from_iterable(all_osp)

""" From: https://docs.python.org/3/library/itertools.html#recipes """
def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return itertools.chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


def equivalent_row_separation( tiling, basis, **kwargs ):

    num_rows = tiling.dimensions[1]

    point_cells = {}
    for cell, block in tiling:
        if block is Block.point:
            point_cells[cell] = block
        elif isinstance(block, PositiveClass):
            point_cells[cell] = Block.point

    # print('\n\n\n')
    # print('=========================================')
    # print('for the tiling')
    # print(tiling)
    # print('I claim that the point cells are')
    # print(point_cells)

    new_tilings  = [tiling]

    for row_num in range(num_rows)[::-1]:

        if len(tiling.get_row(row_num)) <= 1:
            continue

        row_ineqs = row_inequalities(tiling, basis, row_num, point_cells)
        if all (c1==c2 for (c1,c2) in row_ineqs):
            continue

        new_tilings = row_inequalities_to_new_tilings( new_tilings, row_num, row_ineqs )

    max_height = max([nt.dimensions[1] for nt in new_tilings])
    new_tilings = [nt for nt in new_tilings if nt.dimensions[1] == max_height]


    if len(new_tilings) > 2:
        print('\n\n\n')
        print('=========================================')
        print('for the tiling')
        print(tiling)
        print('new tilings are:')
        for (index,new_tiling) in enumerate(new_tilings):
            print('\ttiling #',index+1)
            print(new_tiling)
            print('')


    for new_tiling in new_tilings:
        yield EquivalenceStrategy ( "row separation", new_tiling)


def row_inequalities( tiling, basis , row_num , point_cells):

    row_blocks = tiling.get_row(row_num)
    if len(row_blocks) < 2:
        return []

    inequalities = []
    for cell1, class1 in row_blocks:
        for cell2, class2 in row_blocks:
            if cell1 == cell2:
                # we add all pairs (C,C) to make checking easier later
                # shouldnt't (?) cause any problems
                inequalities.append((cell1,cell1))
                continue

            # add a 1 in cell1 and a 2 in cell2
            point_copy = dict(point_cells)
            point_copy[Cell(cell1[0], cell1[1]-0.5)] = Block.point
            point_copy[Cell(cell2[0], cell2[1]+0.5)] = Block.point

            size_of_tiling = len(point_copy)
            testing_tiling = Tiling(point_copy)

            if all(not perm.avoids(*basis) for perm in testing_tiling.perms_of_length(len(point_copy))):
                inequalities.append((cell1, cell2))

    # print('The nontrivial inequalities for row',row_num,'in tiling')
    # print(tiling)
    # print('are')
    # for (c1, c2) in inequalities:
    #     if c1 != c2:
    #         print((c1,c2))
    return inequalities


def row_inequalities_to_new_tilings( new_tilings, row_num, row_ineqs ):

    assert len(new_tilings) > 0, 'something has gone terribly wrong'

    tilings_to_return = list()

    new_row_arrangements = resolve_row_inequalities( dict(new_tilings[0].get_row(row_num)), row_ineqs )

    for tiling in new_tilings:
        tiling_template = dict(tiling)
        row_to_adjust = tiling.get_row(row_num)

        for cell, perm_class in row_to_adjust:
            tiling_template.pop(cell)

        for new_row_arr in new_row_arrangements:
            assert new_row_arr.keys().isdisjoint(tiling_template.keys()), 'unioning two nondisjoint dicts is bad'

            template_copy = dict(tiling_template)
            template_copy.update(new_row_arr)

            tilings_to_return.append(Tiling(template_copy))

    return tilings_to_return

# TODO: this could be sped up with a top-down recursion, but it made
#       my head hurt too much. For now, this is definitely the slow way!
def resolve_row_inequalities( row_data, row_ineqs ):

    all_osp = all_ordered_set_partitions(list(row_data.keys()))
    # print("\n\n############################")
    # print(list(row_data.keys()),'\n\n')
    # print(all_osp)
    # print("############################\n\n")
    valid_osps = []

    for osp in all_osp:
        still_valid = True
        for (index, part) in enumerate(osp):
            if not all( all( all ( (cell1, cell2) in row_ineqs for cell2 in other_part ) for other_part in osp[index+1:] ) for cell1 in part ):
                still_valid = False
                break
        if still_valid:
            valid_osps.append(osp)

    rows_to_return = []
    for osp in valid_osps:
        num_rows = len(osp)
        new_rows = {}
        for (index,row) in enumerate(osp[::-1]):
            for cell in row:
                new_rows[Cell(cell[0], cell[1] + index/(2*num_rows))] = row_data[cell]
        rows_to_return.append(new_rows)

    return rows_to_return





# def resolve_row_inequalities( row_data, row_ineqs, built=[{}], row_offset):

#     if len(row_data) == 0:
#         return built

#     row_cells = [cell for (cell, perm_class) in row_data]
#     new_row_height = row_cells[0][0] - 1/len(row_data) # SNEAKY!

#     candidates_for_top_row = [cell for cell in row_cells if all((cell, C) in row_ineqs for C in row_cells)]

#     new_built = []
#     top_row_subsets = powerset(candidates_for_top_row)
#     for top_row_subset in top_row_subsets:
#         if len(top_row_subset) == 0:
#             continue
#         new_top_row = {Cell(cell[0], new_row_height):row_data[cell] for cell in top_row_subset}

#         for old_built in built:
#             old_built_copy = dict(old_built)
#             old_built_copy.update(new_top_row)
#             new_built.append(old_built_copy)

#         unused_cells = [cell for cell in row_cells if cell not in top_row_subset]
#         resolve_row_inequalities()


#     return
