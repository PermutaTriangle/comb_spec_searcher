"A strategy for placing a pattern that is binary under the given basis."

from permuta import PermSet, MeshPatt, Perm
# from grids import Tiling, PositiveClass, Block
from grids_two import Tiling
from tilescopetwo.strategies import Strategy
from .util import is_binary
from .coincidence_classification import (coincclass012,
                                         coincclass021,
                                         coincclass102,
                                         coincclass120,
                                         coincclass201,
                                         coincclass210)

coincidence_classification = {
    Perm((0, 1, 2)): coincclass012[0],
    Perm((0, 2, 1)): coincclass021[0],
    Perm((1, 0, 2)): coincclass102[0],
    Perm((1, 2, 0)): coincclass120[0],
    Perm((2, 0, 1)): coincclass201[0],
    Perm((2, 1, 0)): coincclass210[0]
}


def binary_pattern_classical_class(tiling, basis, **kwargs):
    """Produces a binary pattern strategy from a single cell tiling containing
    a positive cell.

    Searches through the coincidence class of the classical patterns of up to
    length k, which is given as a keyword argument. Takes the maximal ones and
    places them in the grid.
    """
    if tiling.dimensions != (1, 1):
        return

    block = tiling[(0, 0)]
    # Should be k = kwargs.get('k') for the general case
    k = 3
    if (0, 0) in tiling.positive_cells and k:
        for patt in PermSet.avoiding(basis).of_length(k):
            # if patt != Perm((0, 1, 2)):
                # continue
            cclass = list(map(lambda m: MeshPatt.unrank(patt, m),
                              coincidence_classification[patt]))
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
            # maxibin = list(maxibin)
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
