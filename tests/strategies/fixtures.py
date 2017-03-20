import atrap
import pytest
import random

from atrap.strategies.row_column_separation import row_and_column_inequalities_of_tiling
from atrap.strategies import row_and_column_separations
from atrap.strategies import all_cell_insertions
from grids import Tiling, Cell, Block, PositiveClass
from permuta import Perm, PermSet
from permuta.descriptors import Basis
from collections import defaultdict
from itertools import permutations
from copy import copy


__all__ = ["random_tiling_dict",
           "random_basis",
           "external_strategy",
           "internal_strategy"
          ]


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


@pytest.fixture(scope="module",
        params=[all_cell_insertions]
)
def external_strategy(request):
    # TODO Docstring
    return request.param


@pytest.fixture(scope="module",
        params=[row_and_column_separations]
)
def internal_strategy(request):
    # TODO Docstring
    return request.param
