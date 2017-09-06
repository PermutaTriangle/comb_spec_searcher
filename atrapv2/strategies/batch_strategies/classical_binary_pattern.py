"""A strategy for placing a classical pattern that is binary under the given
basis."""

from permuta import PermSet, Perm
from grids import Tiling, PositiveClass, Block
from .batch_class import BatchStrategy
from itertools import chain


def gen_classical_binary(basis, k):
    """Given a basis, generate all classical patterns up to length k that are
    binary under the basis"""
    perm_set = PermSet.avoiding(basis)
    patts = perm_set.of_length(k)
    for length in range(k + 1, 2*k + 1):
        for perm in perm_set.of_length(length):
            patts = list(filter(lambda x: x.count_occurrences_in(perm) < 2,
                patts))
    return patts


def tiling_from_classical_permutation(perm, perm_class):
    """Given a classical pattern and perm_class, generate a tiling where
    the classical pattern has been placed within the perm class."""
    tiling = {(2*i, 2*j): perm_class
            for i in range(len(perm) + 1) for j in range(len(perm) + 1)}
    for i in range(len(perm)):
        tiling[(2*i + 1, 2*perm[i] + 1)] = Block.point

    return Tiling(tiling)


def classical_binary_pattern(tiling, basis, **kwargs):
    """Returns a resulting list of tilings after applying the binary pattern
    strategy. The binary pattern strategy looks for binary patterns under the
    basis and places some found pattern."""

    if tiling.dimensions.i != 1 or tiling.dimensions.j != 1:
        return

    block = tiling[(0, 0)]
    # k = kwargs.get('k')
    k = 4
    if isinstance(block, PositiveClass) and k:
        bpatts = chain.from_iterable(gen_classical_binary(basis, i) for i in range(1, k + 1))
        for bpatt in bpatts:
            tilings = [Tiling({(0, 0): PositiveClass(PermSet.avoiding(basis + (bpatt,)))}),
                       tiling_from_classical_permutation(bpatt,
                                                         block.perm_class)]
            print("Found binary pattern:", bpatt)
            yield Strategy(("Placing the the classical binary pattern "
                                 "{}").format(bpatt), tilings, [False, True])

B = [Perm((0,1,2,3)), Perm((0,1,3,2)), Perm((0,2,1,3)), Perm((0,2,3,1)),
        Perm((0,3,1,2)), Perm((1,0,2,3)), Perm((1,2,0,3)), Perm((1,2,3,0)),
        Perm((2,0,1,3)), Perm((3,0,1,2))]

block = PositiveClass(PermSet.avoiding([Perm((0,1,2))]))
