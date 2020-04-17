"""
Wrappers for combinatorial rules.

In the future, you should also declare the method needed for counting. The
types supported for a rule a -> b_1, b_2, ..., b_k are
    - disjoint union: f(a) = f(b_1) + f(b_2) + ... + f(b_k)
    - cartesian product: f(a) = f(b_1) * f(b_2) * ... * f(b_k)
"""
import warnings
from collections.abc import Iterable


class Rule:
    def __init__(
        self,
        formal_step,
        comb_classes,
        inferable,
        possibly_empty,
        workable,
        ignore_parent=False,
        constructor="disjoint",
    ):
        if not isinstance(formal_step, str):
            raise TypeError("Formal step not a string")
        if not isinstance(comb_classes, Iterable):
            raise TypeError("The combinatorial classes are not iterable")
        if not comb_classes:
            raise TypeError(
                (
                    "There are no combinatorial classes, a strategy"
                    " contains a list of combinatorial classes"
                )
            )
        if not isinstance(workable, Iterable):
            raise TypeError("Workable should an iterable")
        if not comb_classes:
            raise TypeError(
                (
                    "There are no combinatorial classes, a strategy"
                    " contains a list of combinatorial classes"
                )
            )
        if any(not isinstance(x, bool) for x in workable):
            raise TypeError("Workable should be an iterable of booleans")
        if any(not isinstance(x, bool) for x in inferable):
            raise TypeError("Inferable should be an iterable of booleans")
        if constructor not in ["disjoint", "cartesian", "equiv", "other"]:
            raise ValueError(
                (
                    "Not valid constructor. Only accepts"
                    " disjoint, cartesian, equiv and other."
                )
            )

        self.constructor = constructor
        self.formal_step = formal_step
        self.comb_classes = list(comb_classes)
        self.inferable = list(inferable)
        self.possibly_empty = list(possibly_empty)
        self.workable = list(workable)
        self.ignore_parent = ignore_parent


def BatchRule(formal_step, comb_classes):
    """A function for creating rules with the disjoint union constructor."""
    return Rule(
        formal_step,
        comb_classes,
        [True for _ in comb_classes],
        [True for _ in comb_classes],
        [True for _ in comb_classes],
        constructor="disjoint",
    )


def DecompositionRule(formal_step, comb_classes, ignore_parent=True):
    """A function for creating rules with the cartesian product constructor."""
    return Rule(
        formal_step,
        comb_classes,
        [False for _ in comb_classes],
        [False for _ in comb_classes],
        [True for _ in comb_classes],
        ignore_parent=ignore_parent,
        constructor="cartesian",
    )


def EquivalenceRule(formal_step, comb_class):
    """A function for creating equivalence rules."""
    return Rule(formal_step, [comb_class], [True], [False], [True], constructor="equiv")


def InferralRule(formal_step, comb_class):
    """A function for creating inferral rules."""
    return Rule(
        formal_step,
        [comb_class],
        [True],
        [False],
        [True],
        ignore_parent=True,
        constructor="equiv",
    )


class VerificationRule:
    """A wrapper for verification rules."""

    def __init__(self, formal_step):
        """
        Constructor for verification rules.

        Formal step explains why verified.
        """
        if not isinstance(formal_step, str):
            raise TypeError("Formal step not a string")

        self.formal_step = formal_step


# Below is deprecated functions and classes for backwards compatability.


def BatchStrategy(formal_step, comb_classes):
    """A deprecated function for creating rules with the disjoint union
    constructor."""
    warnings.warn(
        ("The BatchStrategy class is deprecated." " Use BatchRule instead."),
        DeprecationWarning,
        stacklevel=2,
    )
    return BatchRule(formal_step, comb_classes)


def DecompositionStrategy(formal_step, comb_classes, ignore_parent=True):
    """A deprecated function for creating rules with the cartesian product
    constructor."""
    warnings.warn(
        (
            "The DecompositionStrategy function is deprecated."
            " Use DecompositionRule instead."
        ),
        DeprecationWarning,
        stacklevel=2,
    )
    return DecompositionRule(formal_step, comb_classes, ignore_parent)


def EquivalenceStrategy(formal_step, comb_class):
    """A deprecated function for creating equivalence rules."""
    warnings.warn(
        (
            "The EquivalenceStrategy function is deprecated."
            " Use EquivalenceRule instead."
        ),
        DeprecationWarning,
        stacklevel=2,
    )
    return EquivalenceRule(formal_step, comb_class)


def InferralStrategy(formal_step, comb_class):
    """A deprecated function for creating inferral rules."""
    warnings.warn(
        ("The InferralStrategy function is deprecated." " Use InferralRule instead."),
        DeprecationWarning,
        stacklevel=2,
    )
    return InferralRule(formal_step, comb_class)


class Strategy(Rule):
    """A deprecated class for creating rules."""

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "The Strategy class is deprecated. Use Rule instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        Rule.__init__(self, *args, **kwargs)


class VerificationStrategy(VerificationRule):
    """A deprecated wrapper for verification strategies."""

    def __init__(self, formal_step):
        """
        Constructor for verification strategies.

        Formal step explains why verified.
        """
        warnings.warn(
            (
                "The VerificationStrategy class is deprecated."
                " Use VerificationRule instead."
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        VerificationRule.__init__(self, formal_step)
