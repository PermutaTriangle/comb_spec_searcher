import atrap
import pytest
import random

from atrap.strategies import row_and_column_inequalities_of_tiling
from grids import Tiling, Cell, Block, PositiveClass
from permuta import Perm, PermSet
from permuta.descriptors import Basis
from collections import defaultdict
from itertools import permutations
from copy import copy

@pytest.fixture(scope="module",
        params=[{cell: random.choice([PermSet.avoiding(Perm.random(random.randint(2, 7))),  # A principal class of a random permutations
                                      PositiveClass(PermSet.avoiding(Perm.random(random.randint(2, 7)))),  # ... or similarly a positive class
                                      Block.point,  # ... or a point
                                      Block.increasing,  # ... or a increasing permutation
                                      Block.decreasing])  # ... or a decreasing permutation
                 for cell in set((random.randint(0, 7),  # Random cell i value
                                  random.randint(0, 7))  # Random cell j value
                                  for _ in range(random.randint(0, 7)))}  # Amount of cells in dict
                for _ in range(32)] + [{}])  # Add the empty dict always
def random_tiling_dict(request):
    """Random dictionaries for creating tilings."""
    return request.param

@pytest.fixture
def random_basis():
    """A random basis whose elements range from length 2 to 4 inclusive."""
    population = set()
    for length in range(2, 5):
        population.update(PermSet(length))
    sample_size = random.randint(1, 7)
    basis_elements = random.sample(population, sample_size)
    return Basis(basis_elements)


def test_row_and_column_inequalities(random_tiling_dict, random_basis):
    """Use brute force to find inequalities rather than smart one"""
    tiling = Tiling(random_tiling_dict)
    basis = random_basis


    # create the tiling with all points, plus add a point where there is a positive class.
    point_tiling_dict = {cell: Block.point for cell in tiling.point_cells}
    point_tiling_dict.update({cell: Block.point
                              for cell, block in tiling.non_points
                              if isinstance(block, PositiveClass)})

    # we will create the actual_smaller_than_* returned by the function
    actual_smaller_than_row = defaultdict(dict)
    actual_smaller_than_col = defaultdict(dict)

    # for each row
    for row in range(tiling.dimensions.j):
        # we collect the cells
        row_cells = tiling.get_row(row)
        # only consider when the row has more than one cell
        if len(row_cells) > 1:
            # we create a dictionary that points a cell to what it is less than
            smaller_than_cells_of_row = {}
            for pairi, pairj in permutations(row_cells, 2):
                # the goal is to show that celli is less than cellj
                celli, _ = pairi
                cellj, _ = pairj
                # create the tiling with celli and cellj containing the point, with all other points still there
                testing_point_tiling_dict = copy(point_tiling_dict)
                testing_point_tiling_dict[celli] = Block.point
                testing_point_tiling_dict[cellj] = Block.point
                testing_point_tiling = Tiling(testing_point_tiling_dict)

                # we look for some perm with celli value greater than cellj that avoids the basis for a contradiction
                less_than = True
                for perm, cell_info in testing_point_tiling.perms_of_length_with_cell_info( testing_point_tiling.total_points ):
                    _, valuesi, _ = cell_info[testing_point_tiling.cell_map(celli)] # TODO this needs to be the place celli mapped to after flattening of testing_point_tiling
                    _, valuesj, _ = cell_info[testing_point_tiling.cell_map(cellj)] # TODO this needs to be the place cellj mapped to after flattening of testing_point_tiling
                    if valuesi[0] > valuesj[0]:
                        if perm.avoids(*basis):
                            less_than = False
                            # The one that broke it
                            print(celli, cellj, perm)
                            break
                if celli not in smaller_than_cells_of_row:
                    smaller_than_cells_of_row[celli] = set()
                # if less than implies that all perms with celli greater than cellj contain the basis, therefore celli < cellj
                if less_than:
                    # and we add cellj to the set of what celli is less than
                    smaller_than_cells_of_row[celli].add(cellj)
            # we then append this set of inequalites to the dictionary, ready to be returned
            actual_smaller_than_row[row] = smaller_than_cells_of_row

    # for each col
    for col in range(tiling.dimensions.i):
        # we collect the cells
        col_cells = tiling.get_col(col)
        if len(col_cells) > 1:
            smaller_than_cells_of_col = {}
            for pairi, pairj in permutations(col_cells, 2):
                # the goal is to show that celli is less than cellj
                celli, _ = pairi
                cellj, _ = pairj
                # create the tiling with celli and cellj containing the point, with all other points still there
                testing_point_tiling_dict = copy(point_tiling_dict)
                testing_point_tiling_dict[celli] = Block.point
                testing_point_tiling_dict[cellj] = Block.point
                testing_point_tiling = Tiling(testing_point_tiling_dict)

                # we look for some perm with celli value greater than cellj that avoids the basis for a contradiction
                less_than = True
                for perm, cell_info in testing_point_tiling.perms_of_length_with_cell_info( testing_point_tiling.total_points ):
                    _, _, indicesi = cell_info[testing_point_tiling.cell_map(celli)] # TODO this needs to be the place celli mapped to after flattening of testing_point_tiling
                    _, _, indicesj = cell_info[testing_point_tiling.cell_map(cellj)] # TODO this needs to be the place cellj mapped to after flattening of testing_point_tiling
                    if indicesi[0] > indicesj[0]:
                        if perm.avoids(*basis):
                            less_than = False
                            # The one that broke it
                            print(celli, cellj, perm)
                            break
                # if less than implies that all perms with celli to the right of cellj contain the basis, therefore celli < cellj
                if celli not in smaller_than_cells_of_col:
                    smaller_than_cells_of_col[celli] = set()
                # if less than implies that all perms with celli to the right of cellj contain the basis, therefore celli < cellj
                if less_than:
                    # and we add cellj to the set of what celli is less than
                    smaller_than_cells_of_col[celli].add(cellj)
            # we then append this set of inequalites to the dictionary, ready to be returned
            actual_smaller_than_col[col] = smaller_than_cells_of_col
    print(basis)
    print(tiling)
    smaller_than_row, smaller_than_col = row_and_column_inequalities_of_tiling(tiling, basis)
    print("actual row")
    print(actual_smaller_than_row)
    print("smart row")
    print(smaller_than_row)
    print("actual col")
    print(actual_smaller_than_col)
    print("smart col")
    print(smaller_than_col)
    assert actual_smaller_than_row == smaller_than_row
    assert actual_smaller_than_col == smaller_than_col


def test_specific_row_and_col_inequalities():
    tiling = Tiling({ (0,0): Block.point_or_empty, (0,1): Block.point_or_empty, (0,2): Block.point_or_empty})
    expected_row = {}
    expected_col = {0: {Cell(i=0, j=0): set(), Cell(i=0, j=1): {Cell(i=0, j=0)}, Cell(i=0, j=2): {Cell(i=0, j=1), Cell(i=0, j=0)}}}
    basis = Basis([Perm((0,1))])
    answer_row, answer_col = atrap.strategies.row_and_column_inequalities_of_tiling(tiling, basis)
    print(basis)
    print(tiling)
    print(expected_col)
    print(dict(answer_col))
    assert answer_row == expected_row
    assert answer_col == expected_col
