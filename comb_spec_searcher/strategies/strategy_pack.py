"""
Base class for strategy packs.
"""


class StrategyPack(object):
    def __init__(self, eq_strats=None, ver_strats=None, inf_strats=None,
                 other_strats=None, name=None, old_pack=None):
        if old_pack is not None:
            self.eq_strats = old_pack["equivalence_strategies"]
            self.ver_strats = old_pack["verification_strategies"]
            self.inf_strats = old_pack["inferral_strategies"]
            self.other_strats = [old_pack["batch_strategies"],
                                 old_pack["recursive_strategies"]]
            self.name = "No name"
        elif eq_strats is None:
            raise TypeError(("Strategy pack requires a (possibly empty) list "
                             "of equivalence strategies."))
        elif ver_strats is None:
            raise TypeError(("Strategy pack requires a (possibly empty) list "
                             "of verification strategies."))
        elif inf_strats is None:
            raise TypeError(("Strategy pack requires a (possibly empty) list "
                             "of inferral strategies."))
        elif other_strats is None:
            raise TypeError(("Strategy pack requires a (possibly empty) list "
                             "of lists of other strategies."))
        self.name = name
        self.eq_strats = eq_strats
        self.inf_strats = inf_strats
        self.ver_strats = ver_strats
        self.other_strats = other_strats
