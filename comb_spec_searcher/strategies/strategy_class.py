'''
A wrapper for strategies. This covers the types Batch, Equivalence and
Decomposition. Inferral and Verification have their own classes.

You should also declare the method needed for counting. The types supported for a
strategy a -> b_1, b_2, ..., b_k are
    - disjoint union: f(a)
'''

from collections import Iterable

class Strategy(object):

    def __init__(self, formal_step, objects, workable, back_maps=None):
        if not isinstance(formal_step, str):
            raise TypeError("Formal step not a string")
        if not isinstance(objects, Iterable):
            raise TypeError("The objects give are not iterable")
        if not objects:
            raise TypeError("There are no objects, a strategy contains a list of objects")

        if not isinstance(workable, Iterable):
            raise TypeError("Workable should an iterable")
        if not objects:
            raise TypeError("There are no objects, a strategy contains a list of objects")
        if any(not isinstance(x, bool) for x in workable):
            raise TypeError("Workable should be an iterable of booleans")
        if back_maps is not None:
            if any(not isinstance(hopefully_dict, dict) for hopefully_dict in back_maps):
                raise TypeError("One of the maps is not a dictionary")
            self.back_maps = [part_map for part_map in back_maps]
        else:
            self.back_maps = None

        self.formal_step = formal_step
        self.objects = [object for object in objects]
        self.workable = [x for x in workable]

    @property
    def decomposition(self):
        return self.back_maps is not None

class StrategyPack(object):
    def __init__(self, eq_strats=None, ver_strats=None, inf_strats=None, other_strats=None, name=None, old_pack=None):
        if old_pack is not None:
            self.eq_strats = old_pack["equivalence_strategies"]
            self.ver_strats = old_pack["verification_strategies"]
            self.inf_strats = old_pack["inferral_strategies"]
            self.other_strats = [old_pack["batch_strategies"],
                                 old_pack["recursive_strategies"]]
            self.name = "No name"
        elif eq_strats is None:
            raise TypeError("Strategy pack requires a (possibly empty) list of equivalence strategies.")
        elif ver_strats is None:
            raise TypeError("Strategy pack requires a (possibly empty) list of verification strategies.")
        elif inf_strats is None:
            raise TypeError("Strategy pack requires a (possibly empty) list of inferral strategies.")
        elif other_strats is None:
            raise TypeError("Strategy pack requires a (possibly empty) list of lists of other strategies.")
        
        # TODO: Probably shouldn't do this...
        name = self
        for k, v in locals().items():
            if v is name:
                name_as_str = k

        self.name = name_as_str

        self.eq_strats = eq_strats
        self.inf_strats = inf_strats
        self.ver_strats = ver_strats
        self.other_strats = other_strats
