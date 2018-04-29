'''
A wrapper for strategies. This covers the types Batch, Equivalence and
Decomposition. Inferral and Verification have their own classes.

In the future, you should also declare the method needed for counting. The
types supported for a strategy a -> b_1, b_2, ..., b_k are
    - disjoint union: f(a)
'''
from collections import Iterable
from functools import partial


class Strategy(object):
    def __init__(self, formal_step, objects, inferable, workable,
                 ignore_parent=False, back_maps=None):
        if not isinstance(formal_step, str):
            raise TypeError("Formal step not a string")
        if not isinstance(objects, Iterable):
            raise TypeError("The objects give are not iterable")
        if not objects:
            raise TypeError(("There are no objects, a strategy contains a list"
                             " of objects"))

        if not isinstance(workable, Iterable):
            raise TypeError("Workable should an iterable")
        if not objects:
            raise TypeError(("There are no objects, a strategy contains a list"
                             " of objects"))
        if any(not isinstance(x, bool) for x in workable):
            raise TypeError("Workable should be an iterable of booleans")
        if any(not isinstance(x, bool) for x in inferable):
            raise TypeError("Inferable should be an iterable of booleans")
        if back_maps is not None:
            if any(not isinstance(bm, dict) and not isinstance(bm, partial)
                   for bm in back_maps):
                raise TypeError("One of the maps is not a dictionary")
            self.back_maps = [part_map for part_map in back_maps]
        else:
            self.back_maps = None

        self.formal_step = formal_step
        self.objects = [object for object in objects]
        self.workable = [x for x in workable]
        self.inferable = [x for x in inferable]
        self.ignore_parent = ignore_parent

    @property
    def decomposition(self):
        return self.back_maps is not None
