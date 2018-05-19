"""
Base class for strategy packs.
"""


class StrategyPack(object):
    def __init__(self, initial_strats, inferral_strats, expansion_strats,
                 ver_strats, name, **kwargs):
        if initial_strats is None:
            raise TypeError(("Strategy pack requires a (possibly empty) list "
                             "of equivalence strategies."))
        elif ver_strats is None:
            raise TypeError(("Strategy pack requires a (possibly empty) list "
                             "of verification strategies."))
        elif inferral_strats is None:
            raise TypeError(("Strategy pack requires a (possibly empty) list "
                             "of inferral strategies."))
        elif expansion_strats is None:
            raise TypeError(("Strategy pack requires a (possibly empty) list "
                             "of lists of other strategies."))
        self.name = name
        self.initial_strats = initial_strats
        self.inferral_strats = inferral_strats
        self.ver_strats = ver_strats
        self.expansion_strats = expansion_strats
        self.symmetries = kwargs.get('symmetries', None)
        self.forward_equivalence = kwargs.get('forward_equivalence', False)
        self.iterative = kwargs.get('iterative', False)
