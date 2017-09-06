"A strategy for placing a pattern that is binary under the given basis."

import sys
from permuta import *
from grids import Tiling, PositiveClass, Block
from .batch_class import BatchStrategy
from atrapv2.strategies import Strategy
from itertools import chain
from .util import *
from .coincidence_classification_012 import coincidence_classification as coincclass012
from .coincidence_classification_021 import coincidence_classification as coincclass021

def binary_pattern(tiling, basis, **kwargs):
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
            if patt != Perm((0, 1, 2)):
                continue
            inferred_patt = infer_empty_boxes(patt, basis)
            inferred_patt_bin = shad_to_binary(inferred_patt.shading, len(inferred_patt) + 1)
            print(inferred_patt)
            print(inferred_patt_bin)
            cclass = chain.from_iterable(clas for clas in coincclass012 if any(is_subset(c, inferred_patt_bin) for c in clas))
            # cclass = chain.from_iterable(clas for clas in coincclass012 if any(is_subset(c, inferred_patt_bin) for c in clas))
            maxibin = filter(lambda x: is_binary(MeshPatt.unrank(patt, x), basis), filter_maximal(cclass))
            # maxibin = list(filter(lambda x: is_binary(x, basis), filter_maximal(cclass)))
            # print(list(cclass))

            # cclass = list(map(lambda m: MeshPatt.unrank(patt, m), coincidence_classification[patt]))
            # maximal = list()
            # last = None

            # for cur in sorted(cclass):
                # if cur == last:
                    # continue
                # add = True
                # for other in cclass:
                    # if cur < other:
                        # add = False
                # if add:
                    # maximal.append(cur)
                # last = cur

            # maxibin = filter(lambda x: is_binary(x, basis), maximal)

            # When printing out, the lazy iterator has to materialized
            # maxibin = list(filter(lambda x: is_binary(x, basis), maximal))
            # print("Length of maximal: ", len(maxibin), file=sys.stderr)
            # continue

            for mpatt_bin in maxibin:
                # print(mpatt, file=sys.stderr)
                # print(None, file=sys.stderr)
                # print(tiling_from_mesh_pattern(mpatt, block.perm_class), file=sys.stderr)
                # print(patt, file=sys.stderr)
                mpatt = MeshPatt.unrank(patt, mpatt_bin)
                tilings = [Tiling({(0, 0): PositiveClass(PermSet.avoiding(basis + (patt,)))}),
                        tiling_from_mesh_pattern(mpatt, block.perm_class)]
                yield Strategy(("Placing the binary pattern "
                                     "{}").format(mpatt), tilings, [False, True])
                break
            break
