"""A strategy for placing a classical pattern that is binary under the given
basis."""

import sys

from permuta import PermSet, Perm
from grids import Tiling, PositiveClass, Block
from comb_spec_searcher import BatchStrategy
from itertools import chain
from .util import *


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
        bpatts = list(chain.from_iterable(gen_classical_binary(basis, i) for i in range(1, k + 1)))
        print("Number of classical binary patterns ", len(bpatts), file=sys.stderr)
        for bpatt in bpatts:
            tilings = [Tiling({(0, 0): PositiveClass(PermSet.avoiding(basis + (bpatt,)))}),
                       tiling_from_classical_permutation(bpatt,
                                                         block.perm_class)]
            print("Found binary pattern:", bpatt, file=sys.sderr)
            yield Strategy(("Placing the the classical binary pattern "
                                 "{}").format(bpatt), tilings, [False, True])
