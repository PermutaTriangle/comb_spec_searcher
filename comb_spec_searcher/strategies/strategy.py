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
    def __init__(self, formal_step, comb_classes, inferable, workable,
                 ignore_parent=False, constructor='disjoint'):
        if not isinstance(formal_step, str):
            raise TypeError("Formal step not a string")
        if not isinstance(comb_classes, Iterable):
            raise TypeError("The combinatorial classes are not iterable")
        if not comb_classes:
            raise TypeError(("There are no combinatorial classes, a strategy"
                             " contains a list of combinatorial classes"))

        if not isinstance(workable, Iterable):
            raise TypeError("Workable should an iterable")
        if not comb_classes:
            raise TypeError(("There are no combinatorial classes, a strategy"
                             " contains a list of combinatorial classes"))
        if any(not isinstance(x, bool) for x in workable):
            raise TypeError("Workable should be an iterable of booleans")
        if any(not isinstance(x, bool) for x in inferable):
            raise TypeError("Inferable should be an iterable of booleans")
        if constructor not in ['disjoint', 'cartesian', 'equiv']:
            raise ValueError(("Not valid constructor. Only accepts"
                              " disjoint or cartesian."))

        self.constructor = constructor
        self.formal_step = formal_step
        self.comb_classes = [comb_class for comb_class in comb_classes]
        self.workable = [x for x in workable]
        self.inferable = [x for x in inferable]
        self.ignore_parent = ignore_parent
