class VerificationStrategy(object):

    def __init__(self, formal_step):
        if not isinstance(formal_step, str):
            raise TypeError("Formal step not a string")

        self.formal_step = formal_step
