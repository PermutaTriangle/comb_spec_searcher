from collections import defaultdict
from grids import Tiling, Block, PositiveClass, Cell
from itertools import chain
import inspect
#
from .inferral_class import InferralStrategy



def row_and_column_inequalities_of_tiling(tiling, basis, basis_partitioning=None):
    # This will create the containing/avoiding less than cells of the permutation by row
    smaller_than_dicts_by_row = (defaultdict(dict), defaultdict(dict))
    smaller_than_dicts_by_col = (defaultdict(dict), defaultdict(dict))

    # We only need to check permutations up to this length because we are trying to show
    # one cell is less than another, so only patterns using the two cells need be considered.
    verification_length = tiling.total_points + 2
    # Add to the length the number of positive classes.
    # Of course positive classes contribute one extra in length since they can't be empty.
    verification_length += sum(1 for _, block in tiling.non_points if isinstance(block, PositiveClass))

    for length in range(verification_length + 1):
        # Get the partitioning into containing/avoiding perms
        partitions = basis_partitioning(tiling, length, basis, inspect.stack()[0][3])

        # For containing and avoiding
        for partition, cells_smaller_than_by_row, cells_smaller_than_by_col in zip(partitions, smaller_than_dicts_by_row, smaller_than_dicts_by_col):
            # For each perm and its associated info
            for cell_infos in partition.values():
                # Store for each cell its contribution to the perm
                for cell_info in cell_infos:

                    # we collect the cells and cell values, cell indices by row, column respectively
                    all_single_cells_indices_cols = defaultdict(list)
                    all_single_cells_values_rows = defaultdict(list)
                    for cell, info in cell_info.items():
                        _, cell_values, cell_indices = info
                        # we only consider the occurrences where there has been one point placed in the cells
                        if len(cell_values) == 1:
                            all_single_cells_indices_cols[cell.i].append( (cell, cell_indices[0]) )
                            all_single_cells_values_rows[cell.j].append( (cell, cell_values[0]) )

                    # for each row we now create the set of inequalities.
                    for row, all_single_cells_values in all_single_cells_values_rows.items():
                        # if there is only one cell in the row, there is no need, as we can't reorder the cells.
                        if len(all_single_cells_values) > 1:
                            # we sort by the values, thus the first element must be the smallest in value.
                            ordered_row = sorted(all_single_cells_values, key = lambda x: - x[1])
                            while len(ordered_row) > 1:
                                smallest_cell = ordered_row.pop(0)[0]
                                # then store that the smallest cell is smaller than the rest.
                                if smallest_cell in cells_smaller_than_by_row[row]:
                                    cells_smaller_than_by_row[row][smallest_cell].update( x[0] for x in ordered_row )
                                else:
                                    cells_smaller_than_by_row[row][smallest_cell] = set( [x[0] for x in ordered_row] )

                    # for each column we now create the set of inequalities
                    for col, all_single_cells_indices in all_single_cells_indices_cols.items():
                        # if there is only one cell in the column, there is no need, as we can't reorder the cells.
                        if len(all_single_cells_indices) > 1:
                            # we sort by the indices, thus the first element must be the leftmost/smallest in index.
                            ordered_col = sorted(all_single_cells_indices, key = lambda x: - x[1])
                            while len(ordered_col) > 1:
                                smallest_cell = ordered_col.pop(0)[0]
                                # then store that the smallest cell is smaller than the rest.
                                if smallest_cell in cells_smaller_than_by_col[col]:
                                    cells_smaller_than_by_col[col][smallest_cell].update( x[0] for x in ordered_col )
                                else:
                                    cells_smaller_than_by_col[col][smallest_cell] = set( [x[0] for x in ordered_col] )

    # we now have all the inequalities given by the perms, split by containing and avoiding.
    containing_smaller_than_row, avoiding_smaller_than_row = smaller_than_dicts_by_row
    containing_smaller_than_col, avoiding_smaller_than_col = smaller_than_dicts_by_col
    # print("row")
    # print(containing_smaller_than_row)
    # print(avoiding_smaller_than_row)
    # print("col")
    # print(containing_smaller_than_col)
    # print(avoiding_smaller_than_col)

    # we will create the actual inequalities, considering whether the perm avoids or contains
    # this dictionary points to a row that points to the cells.
    smaller_than_row = defaultdict(dict)
    smaller_than_col = defaultdict(dict)

    # for each row
    # TODO: this should be for all rows with two elements or more
    for row in range(tiling.dimensions.j):
        row_cells = tiling.get_row(row)
        if len(row_cells) > 1:
            # for each cell
            for cell, _ in row_cells:
                # pick out the inequalities for containing
                containing_cells_smaller_than = containing_smaller_than_row[row][cell] if cell in containing_smaller_than_row[row] else set()
                # pick out the inequalities for avoiding
                avoiding_cells_smaller_than = avoiding_smaller_than_row[row][cell] if cell in avoiding_smaller_than_row[row] else set()
                # then a cell is actually less than if and only if it is less than for only containing perms
                # hence we take the set minus.
                smaller_than_row[row][cell] = containing_cells_smaller_than - avoiding_cells_smaller_than

    # essentially repeat above for columns. for each column
    # TODO: this should be for all cols with two elements or more
    for col in range(tiling.dimensions.i):
        col_cells = tiling.get_col(col)
        if len(col_cells) > 1:
        # for each cell
            for cell, _ in col_cells:
                # pick out the inequalities for containing
                containing_cells_smaller_than = containing_smaller_than_col[col][cell] if cell in containing_smaller_than_col[col] else set()
                # pick out the inequalities for avoiding
                avoiding_cells_smaller_than = avoiding_smaller_than_col[col][cell] if cell in avoiding_smaller_than_col[col] else set()
                # then a cell is actually less than if and only if it is less than for only containing perms
                # hence we take the set minus.
                smaller_than_col[col][cell] = containing_cells_smaller_than - avoiding_cells_smaller_than

    # we then return these inequalities ready for parsing so as to determine how we can split rows and columns.
    return smaller_than_row, smaller_than_col

def separations( inequalities, unprocessed_cells=None, current_cell=None, current_state=None ):
    '''This is a recursive function for generating the splittings of a row/column from the given inequalities
    It will split the cells from the row/column into parts. Any two cells in the same part must be on the the
    same row/column as one another. A part to the left of another must be below/further to the left than the
    other. For example in the tiling given by (0,0):Av(132), (1,1): Point, (2,0) Av(132) the separations of
    the first row will look like [ [(2,0)] [(0,0)]] ] and [ [(0,0), (2,0)] ]. The second is the trivial
    solution and is always returned.'''
    if current_state is None:
        current_state = []
    if unprocessed_cells is None:
        unprocessed_cells = list(inequalities.keys())
    if current_cell is None:
        current_cell = unprocessed_cells[0]
        unprocessed_cells = unprocessed_cells[1:]

    # print("current state")
    # print(current_state)
    # print(current_cell)
    # print(unprocessed_cells)

    if current_state == []:
        '''The next state must be the one with exactly one part'''
        current_state.append( [current_cell] )
        if unprocessed_cells:
            '''we then take the next cell to pass to the recursive call'''
            next_cell = unprocessed_cells[0]
            return [ separation for separation in separations( inequalities, unprocessed_cells[1:], next_cell, current_state )]
        return [ current_state ]

    must_mix_with = [ cell for cell in inequalities.keys() if cell not in inequalities[current_cell] and current_cell not in inequalities[cell] and cell is not current_cell ]

    mixing_with_one = False
    for index, part in enumerate(current_state):
        if any( cell in part for cell in must_mix_with ):
            if mixing_with_one:
                '''The cell has to mix with two necessarily separate parts, hence no solution'''
                return []
            mixing_with_one = True
            '''The cell must mix with this part'''
            mixing_with_index = index

    if mixing_with_one:
        for index, part in enumerate(current_state):
            if index < mixing_with_index:
                if any( current_cell not in inequalities[cell] for cell in part ):
                    '''There is some element in the part to the left which can't appear below the current cell'''
                    return []
            elif index > mixing_with_index:
                if any( cell not in inequalities[current_cell] for cell in part ):
                    '''There is some element in the part to the right which can't appear above the current cell'''
                    return []
        current_state[mixing_with_index].append(current_cell)
        if unprocessed_cells:
            next_cell = unprocessed_cells[0]
            return [ separation for separation in separations( inequalities, unprocessed_cells[1:], next_cell, current_state )]

        return [current_state]

    '''The cell didn't mix with a part'''
    furthest_left_index = 0
    furthest_right_index = len(current_state)
    '''We search for the interval where the current cell can be placed'''
    for index, part in enumerate(current_state):
        if any( cell not in inequalities[current_cell] for cell in part ):
            '''The current cell may not appear to the left of this part'''
            furthest_left_index = index + 1

    for index, part in reversed( list(enumerate(current_state)) ):
        if any( current_cell not in inequalities[cell] for cell in part):
            '''The current cell may not appear to the right of this part'''
            furthest_right_index = index

    # print("current state")
    # print(current_state)
    # print(current_cell)
    # print(unprocessed_cells)
    # print("left index")
    # print(furthest_left_index)
    # print("right index")
    # print(furthest_right_index)


    if furthest_left_index > furthest_right_index:
        '''in which case the interval is empty'''
        if furthest_left_index == furthest_right_index + 1:
            '''Must mix with part with furthest_right_index'''
            current_state[furthest_right_index].append(current_cell)
            # print(current_state)
            if unprocessed_cells:
                next_cell = unprocessed_cells[0]
                return [ separation for separation in separations( inequalities, unprocessed_cells[1:], next_cell, current_state )]
            return [current_state]
        return []

    '''We now need to create the potential states, for example, consider the "fake"
    current state [ [] [] [] [] [] [] [] ] then given the interval [1,3] then where
    you see an "x" the current cell can be placed [ [x] x [x] x [x] x [x] [] [] [] ]'''

    potential_states = []

    if furthest_left_index > 0:
        potential_state = current_state[:furthest_left_index-1] + [ current_state[furthest_left_index - 1] + [current_cell] ] + current_state[furthest_left_index:]
        # print("furthest left")
        # print(potential_state)
        potential_states.append( potential_state )

    for index in range(furthest_left_index, furthest_right_index + 1):
        if index == len(current_state):
            potential_state = current_state + [ [current_cell] ]
            # print("furthest right")
            # print(potential_state)
            potential_states.append(potential_state)

        else:
            potential_state = current_state[:index] + [ current_state[index] + [current_cell] ] + current_state[index+1:]
            # print("middle")
            # print(potential_state)
            potential_states.append(potential_state)

            potential_state = current_state[:index] + [ [current_cell] ] + current_state[index:]
            # print(potential_state)
            potential_states.append( potential_state )

    # print("all")
    # print(potential_states)

    if unprocessed_cells:
        next_cell = unprocessed_cells[0]
        final_states = []
        for potential_state in potential_states:
            '''for each potential state, we call recursively'''
            final_states.extend(  separation for separation in separations( inequalities, unprocessed_cells[1:], next_cell, potential_state ) )
        return final_states

    return potential_states

def row_and_column_separation(tiling, basis, basis_partitioning=None):
    # print("----------------NOW CONSIDERING-------------")
    # print(tiling)
    # print(dict(tiling))
    # print(basis)

    if tiling.total_points + tiling.total_other + 2 < len(basis[0]):
        return


    '''First we calculate the set of inequalities for all the rows and columns'''
    row_inequalities, column_inequalities = row_and_column_inequalities_of_tiling(tiling, basis, basis_partitioning=basis_partitioning)
    new_tiling_dict = dict(tiling)
    '''When creating the new tiling, we need to keep track of the shifted cell we
    add, in case a cell appears on a separated row and column'''
    original_cell_to_shifted_cell_map = {}
    for row in range(tiling.dimensions.j):
        inequalities = row_inequalities[row]
        if inequalities:
            # print("------working on row {}------".format(row))
            # print(inequalities)
            '''Calculate the separation, described in the function'''
            row_separations = separations(inequalities)
            # print(row_separations)
            if len(row_separations) == 1:
                '''This must be the trivial solution'''
                continue
            '''sort them by length, i.e. number of parts in the separation'''
            row_separations.sort(key=len)
            '''pick the one with most'''
            separation = row_separations[-1]
            second_last = row_separations[-2]
            if len(separation) == len(second_last):
                '''only use it if it is the unique longest'''
                continue
            for cell, _ in tiling.get_row(row):
                '''we remove the cells, as we intend to readd it separated'''
                new_tiling_dict.pop(cell)
            for index, part in enumerate(separation):
                for cell in part:
                    '''the first part appears below the second, second below third etc,
                    so we shift the y coordinate by the position of the part/len(separation)'''
                    shifted_cell = Cell(cell.i, cell.j + index/len(separation))
                    '''we keep track of shifted cells for when we do the work for columns'''
                    original_cell_to_shifted_cell_map[cell] = shifted_cell
                    new_tiling_dict[shifted_cell] = tiling[cell]
    #         print(Tiling(new_tiling_dict))
    # print(original_cell_to_shifted_cell_map)
    for col in range(tiling.dimensions.i):
        '''Calculate the separation, described in the function'''
        inequalities = column_inequalities[col]
        if inequalities:
            # print("------working on col {}------".format(col))
            # print(inequalities)
            column_separations = separations(inequalities)
            # print(column_separations)
            if len(column_separations) == 1:
                '''This must be the trivial solution'''
                continue
            '''sort them by length, i.e. number of parts in the separation'''
            column_separations.sort(key=len)
            '''pick the one with most'''
            separation = column_separations[-1]
            second_last = column_separations[-2]
            if len(separation) == len(second_last):
                '''only use it if it is the unique longest'''
                continue
            for cell, _ in tiling.get_col(col):
                '''If it was moved already it will apear in our map and we use its shift,
                 else the cell will still be in the new tilings dictionary'''
                shifted_cell = original_cell_to_shifted_cell_map.get(cell)
                # print(cell)
                # print(shifted_cell)
                if shifted_cell is None:
                    shifted_cell = cell
                '''we remove the cells, as we intend to read it separated'''
                new_tiling_dict.pop(shifted_cell)

            for index, part in enumerate(separation):
                for cell in part:
                    '''If it was moved already it will apear in our map and we use its shift,
                     else the cell will still be in the new tilings dictionary'''
                    shifted_cell = original_cell_to_shifted_cell_map.get(cell)
                    if shifted_cell is None:
                        shifted_cell = cell
                    '''the first part appears to the left of the second, second to the left of the third etc,
                    so we shift the x coordinate by the position of the part/len(separation)'''
                    new_tiling_dict[(shifted_cell.i + index/len(separation), shifted_cell.j)] = tiling[cell]
            # print(Tiling(new_tiling_dict))

    '''We then take the tiling, which will of course flatten the tiling dictionary'''
    separated_tiling = Tiling(new_tiling_dict)
    if tiling != separated_tiling:
        '''we only return it if it is different'''
        # TODO: add the rows and columns separated to the formal_step
        formal_step = "Separated the rows and columns"
        yield InferralStrategy( formal_step, separated_tiling)
