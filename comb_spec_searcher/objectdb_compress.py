"""
A database for objects found.

Contains information about if objects have been
expanded, found by symmetries etc. It gives each object a unique label.
"""

from .combinatorial_class import CombinatorialClass


class Info(object):
    """Information about a object."""
    def __init__(self,
                 obj,
                 label,
                 expanded=0,
                 symmetry_expanded=False,
                 equivalent_expanded=False,
                 decomposition_expanded=False,
                 expanding_children_only=False,
                 expanding_other_sym=False,
                 expandable=False,
                 inferral_expanded=False,
                 workably_decomposed=False,
                 verified=None,
                 empty=None,
                 strategy_verified=False):
        """Initialise information."""
        self.obj = obj
        self.label = label
        self.expanded = expanded
        self.symmetry_expanded = symmetry_expanded
        self.equivalent_expanded = equivalent_expanded
        self.expanding_children_only = expanding_children_only
        self.expanding_other_sym = expanding_other_sym
        self.expandable = expandable
        self.inferral_expanded = inferral_expanded
        self.workably_decomposed = workably_decomposed
        self.verified = verified
        self.empty = empty
        self.strategy_verified = strategy_verified


class CompressedObjectDB(object):
    """
    A database for objects.

    Each object is given a unique integer label. The key to the database is
    both the unique integer label and object. It supports the following
    methods.
    - DB.add(obj) will label the object and add it to the database.
    - DB.get_object(key) return the object with the given key.
    - DB.get_label(key) return the label of the given key.
    - DB.set_property(key) will set the property to true for key.
    - DB.is_property(key) will return True if the key has the property, False
    otherwise.
    - Sets verified objects with explanation.
    """

    def __init__(self, combinatorial_object=None):
        """
        Initialise.

        Two dictionaries allow you to call database with either the object, or
        the unique label of the object. The key can therefore be either the
        label or the object.
        """
        self.obj_to_info = {}
        self.label_to_info = {}
        if combinatorial_object is None:
            raise TypeError("Need to declare type of combinatorial object.")
        self.combinatorial_object = combinatorial_object

    def __iter__(self):
        """Iterator of labels."""
        for key in self.label_to_info.keys():
            yield key

    def __contains__(self, key):
        """Check for containment."""
        if isinstance(key, CombinatorialClass):
            self._compress(key)
            info = self.obj_to_info.get(key)
        if isinstance(key, int):
            info = self.label_to_info.get(key)
        return info is not None

    def add(self,
            obj,
            symmetry_expanded=False,
            expanding_other_sym=False,
            expandable=False):
        """
        Add a object to the database.

        Can also set some information about the object on adding.
        """
        if not isinstance(obj, CombinatorialClass):
            raise TypeError("Trying to add something that isn't a object.")
        compressed_obj = self._compress(obj)
        if compressed_obj not in self.obj_to_info:
            label = len(self.obj_to_info)
            info = Info(compressed_obj,
                        label,
                        symmetry_expanded=symmetry_expanded,
                        expanding_other_sym=expanding_other_sym,
                        expandable=expandable)
            self.obj_to_info[compressed_obj] = info
            self.label_to_info[label] = info
        else:
            if expandable:
                self.set_expandable(obj)
            if expanding_other_sym:
                self.set_expanding_other_sym(obj)
            if symmetry_expanded:
                self.set_symmetry_expanded(obj)

    def _get_info(self, key):
        """Return Info for given key."""
        if isinstance(key, CombinatorialClass):
            key = self._compress(key)
            info = self.obj_to_info.get(key)
            if info is None:
                label = len(self.obj_to_info)
                info = Info(key, len(self.obj_to_info))
                self.obj_to_info[key] = info
                self.label_to_info[label] = info
        elif isinstance(key, int):
            info = self.label_to_info.get(key)
            if info is None:
                raise KeyError("Key not in ObjectgDB.")
        else:
            raise TypeError('CompressedObjectDB only accepts'
                            'CombinatorialClass and will decompress with'
                            '{}.'.format(self.combinatorial_object))
        return info

    def _compress(self, key):
        try:
            return key.compress()
        except AttributeError:
            raise AttributeError(("The class {} needs a compress function"
                                  ".").format(self.combinatorial_object))

    def _decompress(self, key):
        try:
            return self.combinatorial_object.decompress(key)
        except AttributeError:
            raise AttributeError(("The class {} needs a compress function"
                                  ".").format(self.combinatorial_object))

    def get_object(self, key):
        """Return object of key."""
        info = self._get_info(key)
        return self._decompress(info.obj)

    def get_label(self, key):
        """Return label of key."""
        info = self._get_info(key)
        return info.label

    def number_times_expanded(self, key):
        """
        Return number of times object corresponding to key has been expanded.

        i.e., the number of sets strategies that have been used to expanded
        the object corresponding to the key.
        """
        info = self._get_info(key)
        return info.expanded

    def increment_expanded(self, key):
        """Increment the counter for number times a object was expanded."""
        info = self._get_info(key)
        self.obj_to_info[info.obj].expanded += 1

    def is_expandable(self, key):
        """Return True if expandable, False otherwise."""
        info = self._get_info(key)
        return info.expandable

    def set_expandable(self, key, expandable=True):
        """Update database about objects expandability."""
        info = self._get_info(key)
        self.obj_to_info[info.obj].expandable = expandable

    def is_verified(self, key):
        """
        Return True if object has been verified.

        Verification must have an explanation, i.e, from a strategy.
        """
        return self._get_info(key).verified is not None

    def set_verified(self, key, explanation):
        """Update database about object being verified, with an explanation."""
        self._get_info(key).verified = explanation

    def verification_reason(self, key):
        """Return explanation of verification, None if not verified."""
        return self._get_info(key).verified

    def is_empty(self, key):
        """Return True if object is empty set, False otherwise."""
        return self._get_info(key).empty

    def set_empty(self, key, empty=True):
        """Update database about object being empty."""
        self._get_info(key).empty = empty

    def verified_labels(self):
        """Yield all the labels that are verified."""
        for x in self.label_to_info:
            if self.is_verified(x):
                yield x

    def empty_labels(self):
        """Yield all the labels that are verified."""
        for x in self.label_to_info:
            if self.is_empty(x):
                yield x

    def is_strategy_verified(self, key):
        """Return True if object verified by a strategy."""
        return self._get_info(key).strategy_verified

    def set_strategy_verified(self, key, strategy_verified=True):
        """Update database about object being verified by a strategy."""
        self._get_info(key).strategy_verified = strategy_verified

    def is_symmetry_expanded(self, key):
        """Return True if object was expanded by symmetries."""
        return self._get_info(key).symmetry_expanded

    def set_symmetry_expanded(self, key, symmetry_expanded=True):
        """Update database that object was symmetry expanded."""
        self._get_info(key).symmetry_expanded = symmetry_expanded

    def is_expanding_children_only(self, key):
        """Return True if not expanding as expanding other children only."""
        return self._get_info(key).expanding_children_only

    def set_expanding_children_only(self, key, expanding_children_only=True):
        """Update database if expanding childern_only."""
        self._get_info(key).expanding_children_only = expanding_children_only

    def is_expanding_other_sym(self, key):
        """Return True if a symmetry of object is being expaned."""
        return self._get_info(key).expanding_other_sym

    def set_expanding_other_sym(self, key, expanding_other_sym=True):
        """Update database that a symmetry of object is being expanded."""
        self._get_info(key).expanding_other_sym = expanding_other_sym

    def is_equivalent_expanded(self, key):
        """Return True if object was equivalent expanded."""
        return self._get_info(key).equivalent_expanded

    def set_equivalent_expanded(self, key, equivalent_expanded=True):
        """Update database that object was equivalent expanded."""
        self._get_info(key).equivalent_expanded = equivalent_expanded

    def is_inferral_expanded(self, key):
        """Return True if object was inferral expanded."""
        return self._get_info(key).inferral_expanded

    def set_inferral_expanded(self, key, inferral_expanded=True):
        """Update database that object was inferral expanded."""
        self._get_info(key).inferral_expanded = inferral_expanded

    def is_workably_decomposed(self, key):
        """Return True if object was equivalent expanded."""
        return self._get_info(key).workably_decomposed

    def set_workably_decomposed(self, key, workably_decomposed=True):
        """Update database that object was equivalent expanded."""
        self._get_info(key).workably_decomposed = workably_decomposed
