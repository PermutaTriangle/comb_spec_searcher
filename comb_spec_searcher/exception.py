"""Some custom errors."""


class InsaneTreeError(Exception):
    """A sanity check failed."""


class InvalidOperationError(Exception):
    """The operation used doesn't apply."""


class ObjectMappingError(Exception):
    """A problem in the bijection."""


class SpecificationNotFound(Exception):
    """A specification was not found."""


class TaylorExpansionError(Exception):
    """An error while taylor expanding."""
