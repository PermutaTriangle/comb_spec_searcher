"""A wrapper for inferral strategies."""


from grids_two import Tiling


class InferralStrategy(object):
    """A wrapper for inferral strategies."""

    def __init__(self, formal_step, tiling):
        """
        Constructor for InferralStrategy.

        Formal step is a string explaining how it was inferred to be tiling.
        """
        if not isinstance(formal_step, str):
            raise TypeError("Formal step not a string")
        if not isinstance(tiling, Tiling):
            raise TypeError("The tiling is not a Tiling")
        self.formal_step = formal_step
        self.tiling = tiling
