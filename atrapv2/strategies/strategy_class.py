'''
A wrapper for strategies. This covers the types Batch, Equivalence and Recursion.
Inferral and Verification have their own classes.
'''

from collections import Iterable
from grids import Tiling

class Strategy(object):

    def __init__(self, formal_step, tilings, workable, back_maps=None):
        if not isinstance(formal_step, str):
            raise TypeError("Formal step not a string")
        if not isinstance(tilings, Iterable):
            raise TypeError("Tilings not iterable")
        if not tilings:
            raise TypeError("There are no tilings, a strategy contains a list of tilings")
        if any( not isinstance(tiling, Tiling) for tiling in tilings ):
            raise TypeError("A strategy takes a list of tilings")
        if not isinstance(workable, Iterable):
            raise TypeError("Workable should an iterable")
            raise TypeError("There are no tilings, a strategy contains a list of tilings")
        if any( not isinstance(x, bool) for x in workable ):
            raise TypeError("Workable should be an iterable of booleans")
        if back_maps is not None:
            if any(not isinstance(hopefully_dict, dict) for hopefully_dict in back_maps):
                raise TypeError("One of the maps is not a dictionary")
            self.back_maps = [part_map for part_map in back_maps]
        else:
            self.back_maps = None

        self.formal_step = formal_step
        self.tilings = [tiling for tiling in tilings]
        self.workable = [x for x in workable]
