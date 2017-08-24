from collections import Iterable
from grids import Tiling

class BatchStrategy(object):

    def __init__(self, formal_step, tilings):
        if not isinstance(formal_step, str):
            raise TypeError("Formal step not a string")
        if not isinstance(tilings, Iterable):
            raise TypeError("Tilings not iterable")
        if not tilings:
            raise TypeError("There are no tilings, a batch strategy contains a list with more than one tilings")
        elif len(tilings) == 1:
            raise TypeError("There is one tiling, this should be an equivalence strategy")
        if any( not isinstance(tiling, Tiling) for tiling in tilings ):
            raise TypeError("A batch strategy takes a list of tilings")

        self.formal_step = formal_step
        self.tilings = [ tiling for tiling in tilings ]
