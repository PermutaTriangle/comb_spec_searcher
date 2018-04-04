"""A wrapper for inferral strategies."""

class InferralStrategy(object):
    """A wrapper for inferral strategies."""

    def __init__(self, formal_step, obj):
        """
        Constructor for InferralStrategy.

        Formal step is a string explaining how it was inferred to be object.
        """
        if not isinstance(formal_step, str):
            raise TypeError("Formal step not a string")
        self.formal_step = formal_step
        self.object = obj
