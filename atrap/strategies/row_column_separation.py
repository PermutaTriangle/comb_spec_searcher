from collections import defaultdict
from grids import Tiling, Block, PositiveClass
from atrap.tools import basis_partitioning
from permuta import Perm, PermSet
from copy import copy

def row_and_column_inequalities_of_tiling(tiling, basis):
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
        partitions = basis_partitioning(tiling, length, basis)

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

# returns the order that a cell must be plit into only if rows and columns have unique word
def row_and_column_splits_of_tiling(tiling, basis):
    # find the set of inequalities for the words
    smaller_than_row, smaller_than_col = row_and_column_inequalities_of_tiling(tiling, basis)

    # find the word for each row and column
    row_splits = defaultdict(list)
    col_splits = defaultdict(list)

    for row in range(tiling.dimensions.j):
        # pick out the rows inequalites
        inequalities = smaller_than_row[row]
        if len(inequalities) > 0:
            splits = inequality_word(smaller_than_row[row])
            row_splits[row] = splits

    for col in range(tiling.dimensions.i):
        # pick out the cols inequalites
        inequalities = smaller_than_col[col]
        if len(inequalities) > 0:
            splits = inequality_word(smaller_than_col[col])
            col_splits[col] = splits

    return row_splits, col_splits

def inequality_word( inequalities ):

    keys = sorted( list(inequalities.keys()) )

    words = inequality_word_helper( [], keys, inequalities, keys )

    if len(words) > 1:
        # print("hmmmmm row column separation is still not producing a unique guy")
        # print( words )
        # print("lets makes sure all words are using as many letters as possible")
        max_words = []
        max_letter = 0
        for word in words:
            current_max_letter = max(word)
            if current_max_letter == max_letter:
                max_words.append(word)
            elif current_max_letter > max_letter:
                max_letter = current_max_letter
                max_words = [word]
        if len(max_words) > 1:
            print("hmmmmm row column separation is still not producing a unique guy")
            print("even more hmmmmm, also the word with most letters isn't unique")
            print("I will choose the lexicographically smallest")
            max_words.sort()
            print(inequalities)
            assert len(max_words) > 1

        return max_words[0]

    if words:
        return words[0]
    return []

def inequality_word_helper( word_so_far, keys, inequalities, original_keys ):
    if keys:
        new_keys = copy(keys)
        next_key = new_keys.pop(0)
        min_value = 0
        max_value = len(inequalities)
        for position in range(len(word_so_far)):
            value_of_position = word_so_far[position]
            key_of_position = original_keys[position]
            if key_of_position in inequalities[next_key]:
                if min_value < value_of_position:
                    min_value = value_of_position
                if next_key in inequalities[key_of_position]:
                    if max_value > value_of_position + 1:
                        max_value = value_of_position + 1
            elif next_key in inequalities[key_of_position]:
                if max_value > value_of_position + 1:
                    max_value = value_of_position + 1
            else:
                if min_value < value_of_position:
                    min_value = value_of_position
                if max_value > value_of_position + 1:
                    max_value = value_of_position + 1
            if min_value >= max_value:
                return []
        if new_keys:
            L = []
            for letter in range(min_value, max_value):
                L = L + [ [letter] + word for word in inequality_word_helper( word_so_far + [letter], new_keys, inequalities, original_keys ) ]
            return L
        else:
            letters_used = set(word_so_far)
            unused_letters_needed = []
            for i in range(len(letters_used)):
                if i not in word_so_far:
                    if unused_letters_needed:
                        return []
                    unused_letters_needed.append(i)
            if unused_letters_needed:
                unused_letter_needed = unused_letters_needed[0]
                if unused_letter_needed >= min_value and unused_letter_needed < max_value:
                    return [ [unused_letter_needed] ]
            else:
                new_max = len(letters_used)
                if new_max >= min_value and new_max < max_value:
                    return [ [new_max] ]
                else:
                    if max_value == min_value + 1:
                        return [ [min_value] ]
            return []
    else:
        return [[]]


def tile_splitter( tiling, row_and_column_splits ):
    # print(tiling)
    # print()
    # print(row_and_column_splits)
    row_splits, col_splits = row_and_column_splits

    split_row_tiling_dict = {}

    for row in range(tiling.dimensions.j):
        if row_splits[row]:
            current_row_splits = row_splits[row]
            length_of_row = len(current_row_splits)

            index_in_row = 0
            # This is sorted
            for (i,j), block in tiling.get_row(row):
                split_row_tiling_dict[ i, j + current_row_splits[index_in_row]/length_of_row ] = block
                index_in_row += 1
        else:
            for (i,j), block in tiling.get_row(row):
                split_row_tiling_dict[i,j] = block

    # TODO: I only make this tiling so I can use the get_col functionality.
    # so perhaps we should store the cols as we go, rather than make the tiling.
    split_row_tiling = Tiling(split_row_tiling_dict)

    split_row_and_col_tiling_dict = {}

    for col in range(split_row_tiling.dimensions.i):
        if col_splits[col]:
            current_col_splits = col_splits[col]
            length_of_col = len(col_splits[col])
            index_in_col = 0
            # This is sorted
            for (i,j), block in split_row_tiling.get_col(col):
                split_row_and_col_tiling_dict[ i + current_col_splits[index_in_col]/length_of_col, j ] = block
                index_in_col += 1
        else:
            for (i,j), block in split_row_tiling.get_col(col):
                split_row_and_col_tiling_dict[i,j] = block

    return Tiling(split_row_and_col_tiling_dict)

def row_and_column_separations(tiling, basis):

    row_and_column_splits = row_and_column_splits_of_tiling(tiling, basis)

    return tile_splitter(tiling, row_and_column_splits)
