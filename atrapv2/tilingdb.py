"""
A database for tilings found. Contains information about if tilings have been
expanded, found by symmetries etc. It gives each tiling a unique label.
"""

from grids import Tiling

class Info(object):
    '''
    Information about a tiling.
    '''
    def __init__(self,
                 tiling,
                 label,
                 expanded=False,
                 symmetry_expanded=False,
                 equivalent_expanded=False,
                 decomposition_expanded=False,
                 expanding_other_sym=False,
                 expandable=False,
                 verified=None,
                 empty=None,
                 strategy_verified=False):
        self.tiling = tiling
        self.label = label
        self.expanded = expanded
        self.symmetry_expanded = symmetry_expanded
        self.equivalent_expanded = equivalent_expanded
        self.decomposition_expanded = decomposition_expanded
        self.expanding_other_sym = expanding_other_sym
        self.expandable = expandable
        self.verified = verified
        self.empty = empty
        self.strategy_verified = strategy_verified

class TilingDB(object):
    """
    A database for tilings. Each tiling is given a unique integer label. The
    key to the database is both the unique integer label and tiling.

    It supports the following methods.

    - DB.add(tiling) will label the tiling and add it to the database.

    - DB.get_tiling(key) return the tiling with the given key.

    - DB.get_label(key) return the label of the given key.

    - DB.set_property(key) will set the property to true for key.

    - DB.is_property(key) will return True if the key has the property, False
    otherwise.

    - Sets verified tilings with explanation.
    """
    def __init__(self):
        self.tiling_to_info = {}
        self.label_to_info = {}

    def __iter__(self):
        for key in self.label_to_info.keys():
            yield key

    def __contains__(self, key):
        if isinstance(key, Tiling):
            info = self.tiling_to_info.get(key)
        if isinstance(key, int):
            info = self.label_to_info.get(key)
        return info is not None

    def add(self, tiling, symmetry_expanded=False, expanding_other_sym=False, expandable=False):
        if not isinstance(tiling, Tiling):
            raise TypeError("Trying to add something that isn't a tiling.")
        if tiling not in self.tiling_to_info:
            label = len(self.tiling_to_info)
            info = Info(tiling,
                        label,
                        symmetry_expanded=symmetry_expanded,
                        expanding_other_sym=expanding_other_sym,
                        expandable=expandable)
            self.tiling_to_info[tiling] = info
            self.label_to_info[label] = info
        else:
            if expandable:
                self.set_expandable(tiling)
            if expanding_other_sym:
                self.set_expanding_other_sym(tiling)
            if symmetry_expanded:
                self.set_symmetry_expanded(tiling)


    def _get_info(self, key):
        if isinstance(key, Tiling):
            info = self.tiling_to_info.get(key)
            if info is None:
                label = len(self.tiling_to_info)
                info = Info(key, len(self.tiling_to_info))
                self.tiling_to_info[key] = info
                self.label_to_info[label] = info

        elif isinstance(key, int):
            info = self.label_to_info.get(key)
            if info is None:
                raise KeyError("Key not in TilingDB.")
        return info

    def get_tiling(self, key):
        info = self._get_info(key)
        return info.tiling

    def get_label(self,key):
        info = self._get_info(key)
        return info.label

    def is_expanded(self, key):
        info = self._get_info(key)
        return info.expanded

    def set_expanded(self, key, expanded=True):
        info = self._get_info(key)
        self.tiling_to_info[info.tiling].expanded = expanded
        assert self.tiling_to_info[info.tiling].expanded == self.label_to_info[info.label].expanded
        # Do I need this line, testing with assert
        self.label_to_info[info.label].expanded = expanded

    def is_expandable(self,key):
        info = self._get_info(key)
        return info.expandable

    def set_expandable(self, key, expandable=True):
        info = self._get_info(key)
        self.tiling_to_info[info.tiling].expandable = expandable
        assert self.tiling_to_info[info.tiling].expandable == self.label_to_info[info.label].expandable
        # Do I need this line, testing with assert
        self.label_to_info[info.label].expandable = expandable

    def is_verified(self, key):
        return self._get_info(key).verified is not None

    def set_verified(self, key, explanation):
        self._get_info(key).verified = explanation

    def is_empty(self, key):
        return self._get_info(key).empty

    def set_empty(self, key, empty=True):
        self._get_info(key).empty = empty

    def verified_labels(self):
        for x in self.label_to_info:
            if self.is_verified(x):
                yield x

    def is_strategy_verified(self, key):
        return self._get_info(key).strategy_verified

    def set_strategy_verified(self, key, strategy_verified=True):
        self._get_info(key).strategy_verified = strategy_verified

    def is_symmetry_expanded(self, key):
        return self._get_info(key).symmetry_expanded

    def set_symmetry_expanded(self, key, symmetry_expanded=True):
        self._get_info(key).symmetry_expanded = symmetry_expanded

    def is_expanding_other_sym(self, key):
        return self._get_info(key).expanding_other_sym

    def set_expanding_other_sym(self, key, expanding_other_sym=True):
        self._get_info(key).expanding_other_sym = expanding_other_sym

    def is_equivalent_expanded(self, key):
        return self._get_info(key).equivalent_expanded

    def set_equivalent_expanded(self, key, equivalent_expanded=True):
        self._get_info(key).equivalent_expanded = equivalent_expanded

    def is_decomposition_expanded(self, key):
        return self._get_info(key).decomposition_expanded

    def set_decomposition_expanded(self, key, decomposition_expanded=True):
        self._get_info(key).decomposition_expanded = decomposition_expanded
