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


#This failed once.
def test_inferral_special_case_1():
    tiling = Tiling({(0, 0): Block.point, (1, 1): PermSet( Basis( (Perm((0, 1)),) ) ) })
    expected_tiling = Tiling({(0,0):Block.point})
    assert atrap.tools.tiling_inferral(tiling, Basis((Perm((0, 1)),))) == expected_tiling

def test_tiling_inferral(random_tiling_dict, random_basis):

    basis = random_basis
    basis_list = list(random_basis)
    tiling_dict = {}
    for cell, block in random_tiling_dict.items():
        if block is not Block.point:
            new_basis = basis_list + list(block.basis)
            if new_basis:
                block = PermSet.avoiding(new_basis)
        tiling_dict[cell] = block

    tiling = Tiling(tiling_dict)

    point_tiling_dict = {cell: Block.point for cell in tiling.point_cells}
    new_tiling_dict = point_tiling_dict.copy()
    point_tiling_dict.update({cell: Block.point
                              for cell, block in tiling.non_points
                              if isinstance(block, PositiveClass)})

    maximum_length = len(basis[-1])
    for cell, block in tiling.non_points:
        new_basis_elements = []
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

    # print(basis)
    # print(tiling)
    # print(Tiling(new_tiling_dict))
    # print(atrap.tools.tiling_inferral(tiling, basis))
    assert dict(Tiling(new_tiling_dict)) == dict(atrap.tools.tiling_inferral(tiling, basis))


def test_tiling_inferral_hardcoded():
    basis = Basis([Perm((0, 1, 2)),
                   Perm((0, 3, 2, 1)),
                   Perm((1, 3, 0, 2)),
                   Perm((1, 3, 2, 0)),
                   Perm((2, 3, 1, 0)),
                   Perm((3, 1, 0, 2)),
                   Perm((3, 1, 2, 0)),
                   Perm((3, 2, 0, 1)),
                  ])

    # The permsets
    input_set = PermSet(basis)
    point = Block.point
    dec = Block.decreasing
    five = PermSet(Basis([Perm((0, 1, 2)),
                          Perm((1, 0, 2)),
                          Perm((1, 2, 0)),
                          Perm((2, 0, 1)),
                          Perm((0, 3, 2, 1)),
                         ]))
    poe = Block.point_or_empty
    almost_poe = PermSet.avoiding([Perm((1, 0)), Perm((0, 1, 2))])

    # The pairs of a tiling and its inferred tiling
    pairs = [
        [
            Tiling({(0, 0): input_set,
                   }),
            Tiling({(0, 0): input_set,
                   })
        ],
        [
            Tiling({}),
            Tiling({})
        ],
        [
            Tiling({(0, 0): input_set,
                    (1, 1): point,
                    (2, 0): input_set,
                   }),
            Tiling({(0, 0): dec,
                    (1, 1): point,
                    (2, 0): five,
                   }),
        ],
        [
            Tiling({(0, 1): point,
                    (1, 0): five,
                   }),
            Tiling({(0, 1): point,
                    (1, 0): five,
                   }),
        ],
        [
            Tiling({(0, 0): dec,
                    (1, 1): point,
                    (2, 0): dec,
                    (3, 3): point,
                    (4, 2): five,
                    (5, 0): five,
                   }),
            Tiling({(0, 1): point,
                    (1, 0): dec,
                    (2, 3): point,
                    (3, 2): poe,
                    (4, 0): almost_poe,
                   })
        ],
        [
            Tiling({(0, 4): point,
                    (1, 1): dec,
                    (2, 2): point,
                    (3, 1): dec,
                    (4, 6): point,
                    (5, 5): poe,
                    (6, 0): almost_poe,
                    (7, 3): almost_poe,
                   }),
            Tiling({(0, 4): point,
                    (1, 2): point,
                    (2, 1): dec,
                    (3, 6): point,
                    (4, 5): poe,
                    (5, 0): poe,
                    (6, 3): poe,
                   })
        ],
        [
            Tiling({(0, 1): point,
                    (1, 3): point,
                    (2, 2): poe,
                    (3, 0): almost_poe,
                   }),
            Tiling({(0, 1): point,
                    (1, 3): point,
                    (2, 2): poe,
                    (3, 0): almost_poe,
                   }),
        ],
        [
            Tiling({(0, 1): point,
                    (1, 2): point,
                    (2, 0): almost_poe,
                   }),
            Tiling({(0, 1): point,
                    (1, 2): point,
                    (2, 0): almost_poe,
                   }),
        ],
        [
            Tiling({(0, 1): point,
                    (1, 4): point,
                    (2, 2): poe,
                    (3, 3): point,
                    (4, 2): poe,
                    (5, 0): almost_poe,
                   }),
            Tiling({(0, 0): point,
                    (1, 2): point,
                    (2, 1): point,
                   })
        ],
        [
            Tiling({(0, 3): point,
                    (1, 2): point,
                    (2, 1): dec,
                    (3, 5): point,
                    (4, 4): poe,
                    (5, 0): poe,
                   }),
            Tiling({(0, 3): point,
                    (1, 2): point,
                    (2, 1): dec,
                    (3, 5): point,
                    (4, 4): poe,
                    (5, 0): poe,
                   }),
        ],
        [
            Tiling({(0, 5): point,
                    (1, 2): point,
                    (2, 1): dec,
                    (3, 7): point,
                    (4, 6): poe,
                    (5, 0): poe,
                    (6, 3): poe,
                    (7, 4): point,
                    (8, 3): poe,
                   }),
            Tiling({(0, 2): point,
                    (1, 0): point,
                    (2, 3): point,
                    (3, 1): point,
                   })
        ],
        [
            Tiling({(0, 3): point,
                    (1, 2): point,
                    (2, 1): dec,
                    (3, 4): point,
                    (5, 0): poe,
                   }),
            Tiling({(0, 3): point,
                    (1, 2): point,
                    (2, 1): dec,
                    (3, 4): point,
                    (5, 0): poe,
                   }),
        ],
        [
            Tiling({(0, 3): point,
                    (1, 2): point,
                    (2, 1): dec,
                    (3, 6): point,
                    (4, 4): poe,
                    (5, 5): point,
                    (6, 4): poe,
                    (7, 0): poe,
                   }),
            Tiling({(0, 2): point,
                    (1, 1): point,
                    (2, 0): dec,
                    (3, 4): point,
                    (4, 3): point,
                   })
        ],
    ]

    # TODO: Parameterize or something
    for original, inferred in pairs:
        assert atrap.tools.tiling_inferral(original, basis) == inferred


def test_tiling_inferral_hardcoded_positive_class():
    basis = Basis([Perm((0, 1, 2)),
                   Perm((0, 3, 2, 1)),
                   Perm((1, 3, 0, 2)),
                   Perm((1, 3, 2, 0)),
                   Perm((2, 1, 3, 0)),
                  ])

    # The permsets
    input_set = PermSet(basis)
    point = Block.point
    dec = Block.decreasing
    three = PermSet(Basis([Perm((0, 1, 2)),
                           Perm((0, 2, 1)),
                           Perm((1, 0, 2)),
                          ]))
    poe = Block.point_or_empty
    pos_input_set = PositiveClass(input_set)
    pos_dec = PositiveClass(dec)
    pos_three = PositiveClass(three)
    pos_poe = PositiveClass(poe)  # TODO: This is the point?

    # The pairs of a tiling and its inferred tiling
    pairs = [
        [
            Tiling({(0, 0): input_set}),
            Tiling({(0, 0): input_set}),
        ],
        [
            Tiling({}),
            Tiling({}),
        ],
        [
            Tiling({(0, 0): pos_input_set}),
            Tiling({(0, 0): pos_input_set}),
        ],
        [
            Tiling({(0, 0): input_set,
                    (0, 2): input_set,
                    (1, 1): point,
                   }),
            Tiling({(0, 0): dec,
                    (0, 2): three,
                    (1, 1): point,
                   }),
        ],
        ]

    # TODO: Parameterize or something
    for original, inferred in pairs:
        assert atrap.tools.tiling_inferral(original, basis) == inferred
