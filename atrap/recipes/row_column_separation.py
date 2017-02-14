from grids import *
from permuta import *
from copy import copy

# take in a tiling and tell you if a rows cells can be separated.
def row_column_separations( tiling, input_set ):
    rows = {}
    columns = {}
    points = set()
    # points = {}
    for (i,j), block in tiling.items():
        if i in rows:
            rows[i].add((i,j))
        else:
            rows[i] = set([(i,j)])
        if j in columns:
            columns[j].add((i,j))
        else:
            columns[j] = set([(i,j)])
        if block is Block.point:
            points.add((j,i)) #Note we will standardize to a permutation later
            # points[(i,j)] = block

    # print("row")
    # print()
    row_splits = {}
    for row in rows:
        # print(row)
        valid_splits = list( row_separation( rows[row], points, input_set ) )
        # print(valid_splits)
        # print()
        if valid_splits:
            # print("max")
            max_split_size, max_split = max_splits(valid_splits)
            if max_split_size > 1:
                # TODO:  Taking the first, we should take lexicographically smallest splitting.
                row_splits[row] = max_split_size, max_split[0]
                # print(max_split)
                # print()
            # else:
            #     print( "no non-trivial split")
            #     print()

    # print("columns")
    # print()
    column_splits = {}
    for column in columns:
        # print(column)
        valid_splits = list( column_separation( columns[column], points, input_set ) )
        # print(valid_splits)
        # print()
        if valid_splits:
            # print("max")
            max_split_size, max_split = max_splits(valid_splits)
            if max_split_size > 1:
                column_splits[column] = max_split_size, max_split[0]
                # print(max_split)
                # print()
            # else:
            #     print( "no non-trivial split")
            #     print()
    # print("column_splits")
    # print(column_splits)
    # print("row_splits")
    # print(row_splits)

    return tile_splitter( tiling, row_splits, column_splits )


def tile_splitter( tiling, row_splits, column_splits ):
    # print(tiling)
    # print(dict(tiling))
    # print()
    # print(row_splits)
    # print()
    # print(column_splits)
    # print()
    split_tile = {}
    for (i,j), block in tiling.items():
        n = i
        m = j
        for row in row_splits:
            if i > row:
                n += row_splits[row][0]
            elif i == row:
                n += row_splits[row][0] - row_splits[row][1][(i,j)]
        for column in column_splits:
            if j > column:
                m += column_splits[column][0]
            elif j == column:
                m += column_splits[column][1][(i,j)]
        split_tile[(n,m)] = block
    return Tiling(split_tile)

def max_splits(valid_splits):
    key = lambda split: len(set(split.values()))
    m, max_list = key(valid_splits[0]), []
    for s in valid_splits:
        k = key(s)
        if k > m:
            m, max_list = k, [s]
        elif k == m:
            max_list.append(s)
    return m, max_list

def row_separation( row_cells, points, input_set ):

    greater_than = {}
    less_than = {}

    for cell_working_on in row_cells:
        for cell_comparing_with in row_cells:
            if cell_working_on < cell_comparing_with:
                # print()
                # print(cell_working_on, cell_comparing_with)
                # print()

                if is_greater_than_row( cell_working_on, cell_comparing_with, points, input_set ):
                    # print( "is greater than")
                    if cell_working_on in greater_than:
                        greater_than[cell_working_on].add(cell_comparing_with)
                    else:
                        greater_than[cell_working_on] = set([cell_comparing_with])

                    if cell_comparing_with in less_than:
                        less_than[cell_comparing_with].add(cell_working_on)
                    else:
                        less_than[cell_comparing_with] = set([cell_working_on])


                    if is_less_than_row( cell_working_on, cell_comparing_with, points, input_set ):

                        if cell_working_on in less_than:
                            less_than[cell_working_on].add(cell_comparing_with)
                        else:
                            less_than[cell_working_on] = set([cell_comparing_with])

                        if cell_comparing_with in greater_than:
                            greater_than[cell_comparing_with].add(cell_working_on)
                        else:
                            greater_than[cell_comparing_with] = set([cell_working_on])

                elif is_less_than_row( cell_working_on, cell_comparing_with, points, input_set ):

                    if cell_working_on in less_than:
                        less_than[cell_working_on].add(cell_comparing_with)
                    else:
                        less_than[cell_working_on] = set([cell_comparing_with])

                    if cell_comparing_with in greater_than:
                        greater_than[cell_comparing_with].add(cell_working_on)
                    else:
                        greater_than[cell_comparing_with] = set([cell_working_on])

    # We now have the dictionaries, less_than and greater_than
    # print("less_than dict: ", less_than)
    # print()
    # print("greater_than dict: ", greater_than)
    # print()

    if less_than or greater_than:
        new_row_cells = copy(row_cells)
        current_word = {}
        n = len(row_cells)
        for w in valid_position_finder( current_word, less_than, greater_than, new_row_cells, n ):
            yield w


def column_separation( column_cells, points, input_set ):

    greater_than = {}
    less_than = {}

    for cell_working_on in column_cells:
        for cell_comparing_with in column_cells:
            if cell_working_on < cell_comparing_with:
                # print()
                # print(cell_working_on, cell_comparing_with)
                # print()

                if is_greater_than_column( cell_working_on, cell_comparing_with, points, input_set ):
                    # print( "is greater than")
                    if cell_working_on in greater_than:
                        greater_than[cell_working_on].add(cell_comparing_with)
                    else:
                        greater_than[cell_working_on] = set([cell_comparing_with])

                    if cell_comparing_with in less_than:
                        less_than[cell_comparing_with].add(cell_working_on)
                    else:
                        less_than[cell_comparing_with] = set([cell_working_on])


                    if is_less_than_column( cell_working_on, cell_comparing_with, points, input_set ):

                        if cell_working_on in less_than:
                            less_than[cell_working_on].add(cell_comparing_with)
                        else:
                            less_than[cell_working_on] = set([cell_comparing_with])

                        if cell_comparing_with in greater_than:
                            greater_than[cell_comparing_with].add(cell_working_on)
                        else:
                            greater_than[cell_comparing_with] = set([cell_working_on])

                elif is_less_than_column( cell_working_on, cell_comparing_with, points, input_set ):

                    if cell_working_on in less_than:
                        less_than[cell_working_on].add(cell_comparing_with)
                    else:
                        less_than[cell_working_on] = set([cell_comparing_with])

                    if cell_comparing_with in greater_than:
                        greater_than[cell_comparing_with].add(cell_working_on)
                    else:
                        greater_than[cell_comparing_with] = set([cell_working_on])

    # We now have the dictionaries, less_than and greater_than
    # print("less_than dict: ", less_than)
    # print()
    # print("greater_than dict: ", greater_than)
    # print()

    if less_than or greater_than:
        new_column_cells = copy(column_cells)
        current_word = {}
        n = len(column_cells)
        for w in valid_position_finder( current_word, less_than, greater_than, new_column_cells, n ):
            yield w

def valid_position_finder( current_word, less_than, greater_than, row_cells, n ):
    if row_cells:
        new_row_cells = copy(row_cells)
        current_cell = new_row_cells.pop()
        for new_letter in range(n):
            # print()
            # print(current_cell, new_letter)
            # print()

            # If I get through the following checks I can continue.
            is_valid = True
            for cell, letter in current_word.items():
                # print( "checking against: ", cell, letter)
                if new_letter < letter and ( current_cell not in less_than or cell not in less_than[current_cell] ):
                    is_valid = False
                    break
                elif new_letter > letter and ( current_cell not in greater_than or cell not in greater_than[current_cell] ):
                    is_valid = False
                    break
            if is_valid:
                # print()
                # print( " in is_valid with new_letter = ", new_letter)
                # print()
                new_current_word = copy(current_word)
                new_current_word[current_cell] = new_letter
                if new_row_cells:
                    for w in valid_position_finder( new_current_word, less_than, greater_than, new_row_cells, n ):
                        yield w
                else:
                    if len(set(new_current_word.values())) > 1:
                        yield new_current_word



# def is_greater_than_row( cell1, cell2, points, input_set ):
#     new_points = copy(points)
#
#     new_points[cell1] = Block.point
#     new_points[cell2] = Block.point
#
#     print(new_points)
#     print()
#
#     perms_created = PermSetTiled( Tiling( new_points ) )
#
#     for perm, positions in perms_created.of_length_with_positions( len(new_points) ):
#         if perm in input_set:
#              print(perm, positions)
#              positions = dict(map(reversed, positions.items()))
#              print(positions)
#              print()
#              # This will not work due to cleaning up tiles.
#              if positions[cell1] > positions[cell2]:
#                  return False
#     return True

# def is_less_than_row( cell1, cell2, points, input_set ):
#     new_points = copy(points)
#
#     new_points[cell1] = Block.point
#     new_points[cell2] = Block.point
#
#     print(new_points)
#     print()
#
#     perms_created = PermSetTiled( Tiling( new_points ) )
#
#     for perm, positions in perms_created.of_length_with_positions( len(new_points) ):
#         if perm in input_set:
#              print(perm, positions)
#              positions = dict(map(reversed, positions.items()))
#              print(positions)
#              print()
#              # This will not work due to cleaning up tiles.
#              if positions[cell1] < positions[cell2]:
#                  return False
#     return True


def is_greater_than_row( cell1, cell2, points, input_set ):
    new_points = copy(points)
    # TODO: This is assuming no points in the column.
    if (cell1[1], cell1[0]) not in points:
        new_points.add( (cell1[1], cell1[0] + 0.5) )
    if (cell2[1], cell2[0]) not in points:
        new_points.add( (cell2[1], cell2[0] - 0.5) )
    # TODO: we're sorting this way to often - this approach is dumb and convoluted
    if Perm.to_standard( [ y for (x,y) in sorted( list(new_points) ) ] ).complement() in input_set:
        return False
    return True

def is_greater_than_column( cell1, cell2, points, input_set ):
    new_points = copy(points)
    # TODO: This is assuming no points in the column.
    if (cell1[1], cell1[0]) not in points:
        new_points.add( (cell1[1] - 0.5, cell1[0]) )
    if (cell2[1], cell2[0]) not in points:
        new_points.add( (cell2[1] + 0.5, cell2[0]) )
    # TODO: we're sorting this way to often - this approach is dumb and convoluted
    if Perm.to_standard( [ y for (x,y) in sorted( list(new_points) ) ] ).complement() in input_set:
        return False
    return True


# We are taking complement since tilings are upside down.

def is_less_than_row( cell1, cell2, points, input_set ):
    new_points = copy(points)
    # TODO: This is assuming no points in the column.
    if (cell1[1], cell1[0]) not in points:
        new_points.add( (cell1[1], cell1[0] - 0.5 ) )
    if (cell2[1], cell2[0]) not in points:
        new_points.add( (cell2[1], cell2[0] + 0.5) )

    # TODO: we're sorting this way to often - this approach is dumb and convoluted
    if Perm.to_standard( [ y for (x,y) in sorted( list(new_points) ) ] ).complement() in input_set:
        return False
    return True

def is_less_than_column( cell1, cell2, points, input_set ):
    new_points = copy(points)
    # TODO: This is assuming no points in the column.
    if (cell1[1], cell1[0]) not in points:
        new_points.add( (cell1[1] + 0.5, cell1[0] ) )
    if (cell2[1], cell2[0]) not in points:
        new_points.add( (cell2[1] - 0.5, cell2[0]) )

    # TODO: we're sorting this way to often - this approach is dumb and convoluted
    if Perm.to_standard( [ y for (x,y) in sorted( list(new_points) ) ] ).complement() in input_set:
        return False
    return True
