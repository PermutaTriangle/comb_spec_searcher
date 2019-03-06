"""
Base class for strategy packs.
"""
from ..utils import get_func_name


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
        self.symmetries = kwargs.get('symmetries', [])
        self.forward_equivalence = kwargs.get('forward_equivalence', False)
        self.iterative = kwargs.get('iterative', False)

    def __str__(self):
        string = ("Looking for {} combinatorial specification"
                  " with the strategies:\n").format(
                        'iterative' if self.iterative else 'recursive')
        initial_strats = ", ".join(get_func_name(f)
                                   for f in self.initial_strats)
        infer_strats = ", ".join(get_func_name(f)
                                 for f in self.inferral_strats)
        verif_strats = ", ".join(get_func_name(f)
                                 for f in self.ver_strats)
        string += "Inferral: {}\n".format(infer_strats)
        string += "Initial: {}\n".format(initial_strats)
        string += "Verification: {}\n".format(verif_strats)
        if self.forward_equivalence:
            string += "Using forward equivalence only.\n"
        if self.symmetries:
            symme_strats = ", ".join(get_func_name(f)
                                     for f in self.symmetries)
            string += "Symmetries: {}\n".format(symme_strats)
        for i, strategies in enumerate(self.expansion_strats):
            strats = ", ".join(get_func_name(f) for f in strategies)
            string += "Set {}: {}\n".format(str(i+1), strats)
        return string
