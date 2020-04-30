"""Some custom errors."""

class ExceededMaxtimeError(Exception):
    """Ran out of time."""


class InsaneTreeError(Exception):
    """A sanity check failed."""


class InvalidOperationError(Exception):
    """The operation used doesn't apply."""


class ObjectMappingError(Exception):
    """A problem in the bijection."""


class SpecificationNotFound(Exception):
    """A specification was not found."""


class StrategyDoesNotApply(Exception):
    """A strategy does not apply to the combinatorial class."""


class TaylorExpansionError(Exception):
    """An error while taylor expanding."""
