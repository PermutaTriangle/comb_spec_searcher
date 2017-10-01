"""
A database for tilings found.

Contains information about if tilings have been
expanded, found by symmetries etc. It gives each tiling a unique label.
"""

# from grids import Tiling


class Info(object):
    """Information about a tiling."""

    def __init__(self,
                 tiling,
                 label,
                 expanded=0,
                 symmetry_expanded=False,
                 equivalent_expanded=False,
                 decomposition_expanded=False,
                 expanding_other_sym=False,
                 expandable=False,
                 verified=None,
                 empty=None,
                 strategy_verified=False):
        """Initialise information."""
        self.tiling = tiling
        self.label = label
        self.expanded = expanded
        self.symmetry_expanded = symmetry_expanded
        self.equivalent_expanded = equivalent_expanded
        self.expanding_other_sym = expanding_other_sym
        self.expandable = expandable
        self.verified = verified
        self.empty = empty
        self.strategy_verified = strategy_verified


class ObjectDB(object):
    """
    A database for tilings.

    Each tiling is given a unique integer label. The key to the database is
    both the unique integer label and tiling. It supports the following
    methods.
    - DB.add(tiling) will label the tiling and add it to the database.
    - DB.get_tiling(key) return the tiling with the given key.
    - DB.get_label(key) return the label of the given key.
    - DB.set_property(key) will set the property to true for key.
    - DB.is_property(key) will return True if the key has the property, False
    otherwise.
    - Sets verified tilings with explanation.
    """

    def __init__(self):
        """
        Initialise.

        Two dictionaries allow you to call database with either the tiling, or
        the unique label of the tiling. The key can therefore be either the
        label or the tiling.
        """
        self.tiling_to_info = {}
        self.label_to_info = {}

    def __iter__(self):
        """Iterator of labels."""
        for key in self.label_to_info.keys():
            yield key

    def __contains__(self, key):
        """Check for containment."""
        if isinstance(key, Tiling):
            info = self.tiling_to_info.get(key)
        if isinstance(key, int):
            info = self.label_to_info.get(key)
        return info is not None

    def add(self,
            tiling,
            symmetry_expanded=False,
            expanding_other_sym=False,
            expandable=False):
        """
        Add a tiling to the database.

        Can also set some information about the tiling on adding.
        """
        # if not isinstance(tiling, Tiling):
        #     raise TypeError("Trying to add something that isn't a tiling.")
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
        """Return Info for given key."""
        if not isinstance(key, int):
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

    def get_object(self, key):
        """Return tiling of key."""
        info = self._get_info(key)
        return info.tiling

    def get_label(self, key):
        """Return label of key."""
        info = self._get_info(key)
        return info.label

    def number_times_expanded(self, key):
        """
        Return number of times tiling corresponding to key has been expanded.

        i.e., the number of sets strategies that have been used to expanded
        the tiling corresponding to the key.
        """
        info = self._get_info(key)
        return info.expanded

    def increment_expanded(self, key):
        """Increment the counter for number times a tiling was expanded."""
        info = self._get_info(key)
        self.tiling_to_info[info.tiling].expanded += 1

    def is_expandable(self, key):
        """Return True if expandable, False otherwise."""
        info = self._get_info(key)
        return info.expandable

    def set_expandable(self, key, expandable=True):
        """Update database about tilings expandability."""
        info = self._get_info(key)
        self.tiling_to_info[info.tiling].expandable = expandable

    def is_verified(self, key):
        """
        Return True if tiling has been verified.

        Verification must have an explanation, i.e, from a strategy.
        """
        return self._get_info(key).verified is not None

    def set_verified(self, key, explanation):
        """Update database about tiling being verified, with an explanation."""
        self._get_info(key).verified = explanation

    def verification_reason(self, key):
        """Return explanation of verification, None if not verified."""
        return self._get_info(key).verified

    def is_empty(self, key):
        """Return True if tiling contains no permutation, False otherwise."""
        return self._get_info(key).empty

    def set_empty(self, key, empty=True):
        """Update database about tiling being empty."""
        self._get_info(key).empty = empty

    def verified_labels(self):
        """Yield all the labels that are verified."""
        for x in self.label_to_info:
            if self.is_verified(x):
                yield x

    def is_strategy_verified(self, key):
        """Return True if tiling verified by a strategy."""
        return self._get_info(key).strategy_verified

    def set_strategy_verified(self, key, strategy_verified=True):
        """Update database about tiling being verified by a strategy."""
        self._get_info(key).strategy_verified = strategy_verified

    def is_symmetry_expanded(self, key):
        """Return True if tiling was expanded by symmetries."""
        return self._get_info(key).symmetry_expanded

    def set_symmetry_expanded(self, key, symmetry_expanded=True):
        """Update database that tiling was symmetry expanded."""
        self._get_info(key).symmetry_expanded = symmetry_expanded

    def is_expanding_other_sym(self, key):
        """Return True if a symmetry of tiling is being expaned."""
        return self._get_info(key).expanding_other_sym

    def set_expanding_other_sym(self, key, expanding_other_sym=True):
        """Update database that a symmetry of tiling is being expanded."""
        self._get_info(key).expanding_other_sym = expanding_other_sym

    def is_equivalent_expanded(self, key):
        """Return True if tiling was equivalent expanded."""
        return self._get_info(key).equivalent_expanded

    def set_equivalent_expanded(self, key, equivalent_expanded=True):
        """Update database that tiling was equivalent expanded."""
        self._get_info(key).equivalent_expanded = equivalent_expanded
