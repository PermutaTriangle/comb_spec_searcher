import atrap
import pytest
import random

from grids import Tiling, Cell, Block, PositiveClass
from permuta import Perm, PermSet
from permuta.descriptors import Basis


@pytest.fixture(scope="module", params=(
    PermSet.avoiding([Perm.random(random.randint(0, 5))])
    for _ in range(32)))
def random_principal_class(request):
    """A random principal class."""
    return request.param


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


def test_is_verified_trivial(random_principal_class):
    """Test whether tiling verification verifies trivial cases."""
    perm_class = random_principal_class
    basis = perm_class.basis
    tiling = Tiling({(0, 0): perm_class})
    assert atrap.tools.is_verified(tiling, basis)


def test_is_verified(random_tiling_dict, random_basis):
    """Use the brute-force verification method to test the smart one."""
    tiling = Tiling(random_tiling_dict)
    basis = random_basis

    # This is the maximum length needed to check for containment of patt
    maximum_length = tiling.total_points + len(basis[-1])

    # Search for a counter-example
    for length in range(maximum_length + 1):
        expected_result = all(perm.avoids(*basis) for perm
                              in set(tiling.perms_of_length(length)))
        if not expected_result:
            break

    assert atrap.tools.is_verified(tiling, basis) == expected_result


def test_is_verified_special_case_1():
    tiling = Tiling({(0, 1): Block.increasing, (1, 0): Block.increasing})
    assert atrap.tools.is_verified(tiling, Basis([Perm((3, 0, 2, 1))]))


def test_tiling_inferral(random_tiling_dict, random_basis):
    tiling = Tiling(random_tiling_dict)
    basis = random_basis

    point_tiling_dict = {cell: Block.point for cell in tiling.point_cells}
    new_tiling_dict = point_tiling_dict.copy()
    point_tiling_dict.update({cell: Block.point
                              for cell, block in tiling.non_points
                              if isinstance(block, PositiveClass)})

    for cell, block in tiling.non_points:
        new_basis_elements = []
        maximum_length = len(block.basis[-1])
        for length in range(1, maximum_length + 1):
            for perm in block.of_length(length):
                new_block = PermSet([perm])
                test_tiling_dict = point_tiling_dict.copy()
                test_tiling_dict[cell] = new_block
                test_tiling = Tiling(test_tiling_dict)
                if any(perm.avoids(*basis) for perm
                       in test_tiling.perms_of_length(length + test_tiling.total_points)):
                    continue
                else:
                    new_basis_elements.append(perm)
        new_basis_elements.extend(block.basis)
        new_block = PermSet.avoiding(new_basis_elements)
        if len(new_block.basis[0]) == 1:
            continue
        if isinstance(block, PositiveClass):
            new_block = PositiveClass(new_block)
        new_tiling_dict[cell] = new_block

    print(basis)
    print(tiling)
    print(Tiling(new_tiling_dict))
    print(atrap.tools.tiling_inferral(tiling, basis))
    assert dict(Tiling(new_tiling_dict)) == dict(atrap.tools.tiling_inferral(tiling, basis))
