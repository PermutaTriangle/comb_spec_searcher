"""An inferral function that tries to separate cells in rows and columns."""


from collections import defaultdict
from grids_two import Tiling, Obstruction
from itertools import combinations
from comb_spec_searcher import InferralStrategy

def row_and_column_inequalities_of_tiling(tiling):
    smaller_than_row = defaultdict(dict)
    smaller_than_col = defaultdict(dict)
    for ob in tiling.obstructions:
        if len(ob) == 2:
            if ob.is_single_cell():
                continue
            c1, c2 = ob.pos
            if c1[0] == c2[0]:
                col = c1[0]
                if col not in smaller_than_col:
                    smaller_than_col[col] = {cell: set()
                                        for cell in tiling.cells_in_col(col)}
                # then they are in the same column
                if ob.patt[0] == 0:
                    # then the obstruction is 01, so c2 < c1 (further left)
                    smaller_than_col[col][c2].add(c1)
                else:
                    # the obstruction is 10, so c1 < c2 (further left)
                    smaller_than_col[col][c2].add(c1)
            elif c1[1] == c2[1]:
                row = c1[1]
                if row not in smaller_than_row:
                    smaller_than_row[row] = {cell: set()
                                        for cell in tiling.cells_in_row(row)}
                # then they are in the same row
                if ob.patt[0] == 0:
                    # then the obstruction is 01, so c2 < c1 (further left)
                    smaller_than_row[row][c2].add(c1)
                else:
                    # the obstruction is 10, so c1 < c2 (further left)
                    smaller_than_row[row][c1].add(c2)
        elif len(ob) > 2:
            # obstructions are ordered by length
            break
    return smaller_than_row, smaller_than_col


def separations(inequalities, unprocessed_cells=None, current_cell=None, current_state=None):
    """
    A  recursive function for generating the splittings of a row/column from the given inequalities.

    It will split the cells from the row/column into parts. Any two cells in the same part must be on the the
    same row/column as one another. A part to the left of another must be below/further to the left than the
    other. For example in the tiling given by (0,0):Av(132), (1,1): Point, (2,0) Av(132) the separations of
    the first row will look like [ [(2,0)] [(0,0)]] ] and [ [(0,0), (2,0)] ]. The second is the trivial
    solution and is always returned.
    """
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


def row_and_column_separation(tiling, **kwargs):
    '''First we calculate the set of inequalities for all the rows and columns'''
    row_ineqs, col_ineqs = row_and_column_inequalities_of_tiling(tiling)

    # new_tiling_dict = dict(tiling)
    '''When creating the new tiling, we need to keep track of the shifted cell we
    add, in case a cell appears on a separated row and column'''
    inferred = False
    row_map = {}
    shift = 0
    for row in range(tiling.dimensions[1]):
        inequalities = row_ineqs[row]
        if inequalities:
            '''Calculate the separation, described in the function'''
            row_separations = separations(inequalities)
            if len(row_separations) == 1:
                '''This must be the trivial solution'''
                separation = row_separations[0]
            '''sort them by length, i.e. number of parts in the separation'''
            row_separations.sort(key=len)
            if len(row_separations) == 1:
                '''This must be the trivial solution'''
                separation = row_separations[0]
            else:
                '''pick the one with most'''
                separation = row_separations[-1]
                second_last = row_separations[-2]
                if len(separation) == len(second_last):
                    '''only use it if it is the unique longest'''
                    # print("Multiple solutions")
                    # print(tiling)
                    # print(row, separation, second_last)
                    separation = row_separations[0]
                else:
                    inferred = True
        else:
            separation = [[c for c in tiling.cells_in_row(row)]]

        for index, cells in enumerate(separation):
            for cell in cells:
                row_map[cell] = cell[1] + shift + index
        shift += len(separation) - 1

    col_map = {}
    shift = 0
    for col in range(tiling.dimensions[0]):
        '''Calculate the separation, described in the function'''
        inequalities = col_ineqs[col]
        if inequalities:
            column_separations = separations(inequalities)
            '''sort them by length, i.e. number of parts in the separation'''
            column_separations.sort(key=len)
            if len(column_separations) == 1:
                '''This must be the trivial solution'''
                separation = column_separations[0]
            else:
                '''pick the one with most'''
                separation = column_separations[-1]
                second_last = column_separations[-2]
                if len(separation) == len(second_last):
                    '''only use it if it is the unique longest'''
                    # print("Multiple solutions")
                    # print(tiling)
                    # print(col, separation, second_last)
                    separation = column_separations[0]
                else:
                    inferred = True
        else:
            separation = [[c for c in tiling.cells_in_col(col)]]

        for index, cells in enumerate(separation):
            for cell in cells:
                col_map[cell] = cell[0] + shift + index
        shift += len(separation) - 1

    if inferred:
        cell_map = lambda c: (col_map[c], row_map[c])

        point_cells = [cell_map(c) for c in tiling.point_cells]
        possibly_empty = [cell_map(c) for c in tiling.possibly_empty]
        positive_cells = [cell_map(c) for c in tiling.positive_cells]

        obstructions = []
        for ob in tiling.obstructions:
            if len(ob) != 2:
                obstructions.append(Obstruction(ob.patt,
                                                [cell_map(c) for c in ob.pos]))
            else:
                c1, c2 = ob.pos
                new_c1 = cell_map(c1)
                new_c2 = cell_map(c2)
                if new_c2[0] < new_c1[0]:
                    # print(ob, new_c1, new_c2)
                    continue
                elif ob.patt[0] == 0:
                    if new_c2[1] < new_c1[1]:
                        # print(ob, new_c1, new_c2)
                        continue
                elif new_c2[1] > new_c1[1]:
                    # print(ob, new_c1, new_c2)
                    continue
                obstructions.append(Obstruction(ob.patt,
                                                [new_c1, new_c2]))
        # print(point_cells)
        # print(possibly_empty)
        # print(positive_cells)
        # for o in obstructions:
        #     print(o)

        separated_tiling = Tiling(point_cells=point_cells,
                                  possibly_empty=possibly_empty,
                                  positive_cells=positive_cells,
                                  obstructions=obstructions)
        # print(tiling.to_old_tiling())
        # print(tiling)
        # print(separated_tiling.to_old_tiling())
        # print("")
        # print(separated_tiling)
        '''we only return it if it is different'''
        # TODO: add the rows and columns separated to the formal_step
        formal_step = "Separated the rows and columns"
        yield InferralStrategy(formal_step, separated_tiling)
