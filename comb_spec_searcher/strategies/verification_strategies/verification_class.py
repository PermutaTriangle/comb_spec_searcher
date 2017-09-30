"""A wrapper for verification strategies."""


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
