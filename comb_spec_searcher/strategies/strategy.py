'''
Wrappers for strategies.

In the future, you should also declare the method needed for counting. The
types supported for a strategy a -> b_1, b_2, ..., b_k are
    - disjoint union: f(a)
'''
from collections import Iterable
from functools import partial


class Strategy(object):
    def __init__(self, formal_step, comb_classes, inferable, possibly_empty,
                 workable, ignore_parent=False, constructor='disjoint'):
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
        if constructor not in ['disjoint', 'cartesian', 'equiv', 'other']:
            raise ValueError(("Not valid constructor. Only accepts"
                              " disjoint or cartesian."))

        self.constructor = constructor
        self.formal_step = formal_step
        self.comb_classes = [comb_class for comb_class in comb_classes]
        self.inferable = [x for x in inferable]
        self.possibly_empty = [x for x in possibly_empty]
        self.workable = [x for x in workable]
        self.ignore_parent = ignore_parent


def BatchStrategy(formal_step, comb_classes):
    """A function for batch strategies."""
    return Strategy(formal_step, comb_classes,
                    [True for _ in comb_classes],
                    [True for _ in comb_classes],
                    [True for _ in comb_classes],
                    constructor='disjoint')


def DecompositionStrategy(formal_step, comb_classes,
                          ignore_parent=True):
    """A function for decomposition strategies."""
    return Strategy(formal_step, comb_classes,
                    [False for _ in comb_classes],
                    [False for _ in comb_classes],
                    [False for _ in comb_classes],
                    ignore_parent=ignore_parent, constructor='cartesian')


def EquivalenceStrategy(formal_step, comb_class):
    """A function for equivalent strategies."""
    return Strategy(formal_step, [comb_class], [True], [False],
                    [True], constructor='equiv')


def InferralStrategy(formal_step, comb_class):
    """A function for inferral strategies."""
    return Strategy(formal_step, [comb_class], [True], [False],
                    [True], ignore_parent=True, constructor='equiv')


class VerificationStrategy(object):
    """A wrapper for verification strategies."""

    def __init__(self, formal_step):
        """
        Constructor for verification strategies.

        Formal step explains why verified.
        """
        if not isinstance(formal_step, str):
            raise TypeError("Formal step not a string")

        self.formal_step = formal_step
