

from grids import Tiling

class InferralStrategy(object):

    def __init__(self, formal_step, tiling):
        if not isinstance(formal_step, str):
            raise TypeError("Formal step not a string")
        if not isinstance(tiling, Tiling):
            raise TypeError("The tiling is not a Tiling")
        self.formal_step = formal_step
        self.tiling = tiling
