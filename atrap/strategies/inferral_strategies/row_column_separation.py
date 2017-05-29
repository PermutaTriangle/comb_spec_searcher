from collections import defaultdict
from grids import Tiling, Block, PositiveClass, Cell
from itertools import combinations
from .inferral_class import InferralStrategy


def row_and_column_inequalities_of_tiling(tiling, basis, basis_partitioning=None):

    point_cells = [cell for cell, block in tiling if isinstance(block, PositiveClass)]
    smaller_than_row = defaultdict(dict)
    smaller_than_col = defaultdict(dict)
    for row in range(tiling.dimensions.j):
        row_cells = [cell for cell, _ in tiling.get_row(row)]
        if len(row_cells) < 2:
            continue

        inequalities = {}

        for cell1, cell2 in combinations(row_cells, 2):
            if cell1 not in inequalities:
                inequalities[cell1] = set()
            if cell2 not in inequalities:
                inequalities[cell2] = set()

            point_tiling = {cell: Block.point for cell in point_cells}
            point_tiling[cell1] = Block.point
            point_tiling[cell2] = Block.point
            point_tiling = Tiling(point_tiling)

            new_cell1 = point_tiling.cell_map(cell1)
            new_cell2 = point_tiling.cell_map(cell2)

            containing_perms, avoiding_perms = point_tiling.basis_partitioning(point_tiling.total_points, basis)

            if all(all(cell_info[new_cell1][1] < cell_info[new_cell2][1]
                       for cell_info in cell_infos)
                   for cell_infos in avoiding_perms.values()):
                if not all(all(cell_info[new_cell1][1] < cell_info[new_cell2][1]
                               for cell_info in cell_infos)
                           for cell_infos in containing_perms.values()):
                    inequalities[cell1].add(cell2)
            if all(all(cell_info[new_cell1][1] > cell_info[new_cell2][1]
                       for cell_info in cell_infos)
                   for cell_infos in avoiding_perms.values()):
                if not all(all(cell_info[new_cell1][1] > cell_info[new_cell2][1]
                               for cell_info in cell_infos)
                           for cell_infos in containing_perms.values()):
                    inequalities[cell2].add(cell1)

        smaller_than_row[row] = inequalities

    for col in range(tiling.dimensions.i):
        col_cells = [cell for cell, _ in tiling.get_col(col)]
        if len(col_cells) < 2:
            continue

        inequalities = {}

        for cell1, cell2 in combinations(col_cells, 2):
            if cell1 not in inequalities:
                inequalities[cell1] = set()
            if cell2 not in inequalities:
                inequalities[cell2] = set()

            point_tiling = {cell: Block.point for cell in point_cells}
            point_tiling[cell1] = Block.point
            point_tiling[cell2] = Block.point

            point_tiling = Tiling(point_tiling)

            new_cell1 = point_tiling.cell_map(cell1)
            new_cell2 = point_tiling.cell_map(cell2)

            containing_perms, avoiding_perms = point_tiling.basis_partitioning(point_tiling.total_points, basis)

            if all(all(cell_info[new_cell1][2] < cell_info[new_cell2][2]
                       for cell_info in cell_infos)
                   for cell_infos in avoiding_perms.values()):
                if not all(all(cell_info[new_cell1][2] < cell_info[new_cell2][2]
                               for cell_info in cell_infos)
                           for cell_infos in containing_perms.values()):
                    inequalities[cell1].add(cell2)
            if all(all(cell_info[new_cell1][2] > cell_info[new_cell2][2]
                       for cell_info in cell_infos)
                   for cell_infos in avoiding_perms.values()):
                if not all(all(cell_info[new_cell1][2] > cell_info[new_cell2][2]
                               for cell_info in cell_infos)
                           for cell_infos in containing_perms.values()):
                    inequalities[cell2].add(cell1)

        smaller_than_col[col] = inequalities
    return smaller_than_row, smaller_than_col


def separations(inequalities, unprocessed_cells=None, current_cell=None, current_state=None):
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
        current_state.append([current_cell])
        if unprocessed_cells:
            '''we then take the next cell to pass to the recursive call'''
            next_cell = unprocessed_cells[0]
            return [separation for separation in separations(inequalities,
                                                             unprocessed_cells[1:],
                                                             next_cell,
                                                             current_state)]
        return [current_state]

    must_mix_with = [cell for cell in inequalities.keys() if (cell not in inequalities[current_cell]
                                                              and current_cell not in inequalities[cell]
                                                              and cell is not current_cell)]

    mixing_with_one = False
    for index, part in enumerate(current_state):
        if any(cell in part for cell in must_mix_with):
            if mixing_with_one:
                '''The cell has to mix with two necessarily separate parts, hence no solution'''
                return []
            mixing_with_one = True
            '''The cell must mix with this part'''
            mixing_with_index = index

    if mixing_with_one:
        for index, part in enumerate(current_state):
            if index < mixing_with_index:
                if any(current_cell not in inequalities[cell] for cell in part):
                    '''There is some element in the part to the left which can't appear below the current cell'''
                    return []
            elif index > mixing_with_index:
                if any(cell not in inequalities[current_cell] for cell in part):
                    '''There is some element in the part to the right which can't appear above the current cell'''
                    return []
        current_state[mixing_with_index].append(current_cell)
        if unprocessed_cells:
            next_cell = unprocessed_cells[0]
            return [separation for separation in separations(inequalities,
                                                             unprocessed_cells[1:],
                                                             next_cell,
                                                             current_state)]

        return [current_state]

    '''The cell didn't mix with a part'''
    furthest_left_index = 0
    furthest_right_index = len(current_state)
    '''We search for the interval where the current cell can be placed'''
    for index, part in enumerate(current_state):
        if any(cell not in inequalities[current_cell] for cell in part):
            '''The current cell may not appear to the left of this part'''
            furthest_left_index = index + 1

    for index, part in reversed(list(enumerate(current_state))):
        if any(current_cell not in inequalities[cell] for cell in part):
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
                return [separation for separation in separations(inequalities,
                                                                 unprocessed_cells[1:],
                                                                 next_cell, current_state)]
            return [current_state]
        return []

    '''We now need to create the potential states, for example, consider the "fake"
    current state [ [] [] [] [] [] [] [] ] then given the interval [1,3] then where
    you see an "x" the current cell can be placed [ [x] x [x] x [x] x [x] [] [] [] ]'''

    potential_states = []

    if furthest_left_index > 0:
        potential_state = (current_state[:furthest_left_index-1]
                           + [current_state[furthest_left_index - 1]
                           + [current_cell]]
                           + current_state[furthest_left_index:])
        # print("furthest left")
        # print(potential_state)
        potential_states.append(potential_state)

    for index in range(furthest_left_index, furthest_right_index + 1):
        if index == len(current_state):
            potential_state = current_state + [[current_cell]]
            # print("furthest right")
            # print(potential_state)
            potential_states.append(potential_state)

        else:
            potential_state = current_state[:index] + [current_state[index] + [current_cell]] + current_state[index+1:]
            # print("middle")
            # print(potential_state)
            potential_states.append(potential_state)

            potential_state = current_state[:index] + [[current_cell]] + current_state[index:]
            # print(potential_state)
            potential_states.append(potential_state)

    # print("all")
    # print(potential_states)

    if unprocessed_cells:
        next_cell = unprocessed_cells[0]
        final_states = []
        for potential_state in potential_states:
            '''for each potential state, we call recursively'''
            final_states.extend(separation for separation in separations(inequalities,
                                                                         unprocessed_cells[1:],
                                                                         next_cell,
                                                                         potential_state))
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
    row_ineqs, col_inequalities = row_and_column_inequalities_of_tiling(tiling,
                                                                        basis,
                                                                        basis_partitioning=basis_partitioning)
    new_tiling_dict = dict(tiling)
    '''When creating the new tiling, we need to keep track of the shifted cell we
    add, in case a cell appears on a separated row and column'''
    original_cell_to_shifted_cell_map = {}
    for row in range(tiling.dimensions.j):
        inequalities = row_ineqs[row]
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
        inequalities = col_inequalities[col]
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
        yield InferralStrategy(formal_step, separated_tiling)
