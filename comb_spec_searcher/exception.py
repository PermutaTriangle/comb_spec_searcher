"""Some custom errors."""


class ExceededMaxtimeError(Exception):
    """Ran out of time."""


class IncorrectGeneratingFunctionError(Exception):
    """The incorrect generating function was found."""


class InsaneTreeError(Exception):
    """A sanity check failed."""


class InvalidOperationError(Exception):
    """The operation used doesn't apply."""


class ObjectMappingError(Exception):
    """A problem in the bijection."""


class SanityCheckFailure(Exception):
    """Failed a sanity check."""


class SpecificationNotFound(Exception):
    """A specification was not found."""


class StrategyDoesNotApply(Exception):
    """A strategy does not apply to the combinatorial class."""


class NoMoreClassesToExpandError(Exception):
    """The class queue has run out of classes to try and expand."""


class TaylorExpansionError(Exception):
    """An error while taylor expanding."""
