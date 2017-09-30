"A strategy for placing a pattern that is binary under the given basis."

import sys
from permuta import *
from grids import Tiling, PositiveClass, Block
from comb_spec_searcher import BatchStrategy
from comb_spec_searcher import Strategy
from itertools import chain
from .util import *
from .coincidence_classification import *

coincidence_classification = {
    Perm((0, 1, 2)) : coincclass012[0],
    Perm((0, 2, 1)) : coincclass021[0],
    Perm((1, 0, 2)) : coincclass102[0],
    Perm((1, 2, 0)) : coincclass120[0],
    Perm((2, 0, 1)) : coincclass201[0],
    Perm((2, 1, 0)) : coincclass210[0]
}

def binary_pattern_classical_class(tiling, basis, **kwargs):
    """Produces a binary pattern strategy from a tiling containing a single
    block of PositiveClass.

    Searches through the coincidence class of the classical patterns of up to
    length k, which is given as a keyword argument. Takes the maximal ones and
    places them in the grid.

    Currently only the classical patterns 012 and 021 are considered.
    """
    if tiling.dimensions.i != 1 or tiling.dimensions.j != 1:
        return

    block = tiling[(0, 0)]
    # Should be k = kwargs.get('k') for the general case
    k = 3
    if isinstance(block, PositiveClass) and k:
        for patt in PermSet.avoiding(basis).of_length(k):
            # if patt != Perm((0, 1, 2)):
                # continue
            cclass = list(map(lambda m: MeshPatt.unrank(patt, m), coincidence_classification[patt]))
            maximal = list()
            last = None

            for cur in sorted(cclass):
                if cur == last:
                    continue
                add = True
                for other in cclass:
                    if cur < other:
                        add = False
                if add:
                    maximal.append(cur)
                last = cur

            maxibin = filter(lambda x: is_binary(x, basis), maximal)

            # When printing out, the lazy iterator has to materialized
            # maxibin = list(filter(lambda x: is_binary(x, basis), maximal))
            # print("Length of maximal: ", len(maxibin), file=sys.stderr)

            for mpatt in maxibin:
                # print(mpatt, file=sys.stderr)
                # print(None, file=sys.stderr)
                # print(tiling_from_mesh_pattern(mpatt, block.perm_class), file=sys.stderr)
                # print(patt, file=sys.stderr)
                tilings = [Tiling({(0, 0): PositiveClass(PermSet.avoiding(basis + (patt,)))}),
                        tiling_from_mesh_pattern(mpatt, block.perm_class)]
                yield Strategy(("Placing the binary pattern \n"
                                     "{}").format(mpatt), tilings, [False, True])
