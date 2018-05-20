"""
A database for combinatorial class found.

Contains information about if combinatorial classes have been expanded, found
by symmetries etc. It gives each combinatorial class a unique label.
"""

from .combinatorial_class import CombinatorialClass


class Info(object):
    """Information about a combinatorial class."""
    def __init__(self, comb_class, label, **kwargs):
        """Initialise information."""
        self.comb_class = comb_class
        self.label = label
        self.expanded = kwargs.get('expanded', 0)
        self.symmetry_expanded = kwargs.get('symmetry_expanded', False)
        self.initial_expanded = kwargs.get('initial_expanded', False)
        self.expanding_children_only = kwargs.get('expanding_children_only',
                                                  False)
        self.expanding_other_sym = kwargs.get('expanding_other_sym', False)
        self.expandable = kwargs.get('expandable', False)
        self.inferral_expanded = kwargs.get('inferral_expanded', False)
        self.verified = kwargs.get('verified', None)
        self.empty = kwargs.get('empty', None)
        self.strategy_verified = kwargs.get('strategy_verified', None)

    def to_dict(self):
        """Return dictionary object of self that is JSON serializable."""
        return {
            'comb_class': self.comb_class.decode("utf-8"),
            'label': self.label,
            'expanded': self.expanded,
            'symmetry_expanded': self.symmetry_expanded,
            'initial_expanded': self.initial_expanded,
            'expanding_children_only': self.expanding_children_only,
            'expanding_other_sym': self.expanding_other_sym,
            'expandable': self.expandable,
            'inferral_expanded': self.inferral_expanded,
            'verified': self.verified,
            'empty': self.empty,
            'strategy_verified': self.strategy_verified,
        }

    @classmethod
    def from_dict(cls, dict):
        """Return Info object from dictionary."""
        return cls(
            comb_class=dict['comb_class'].encode("utf-8"),
            label=int(dict['label']),
            expanded=int(dict.get('expanded', 0)),
            symmetry_expanded=dict.get('symmetry_expanded', False),
            initial_expanded=dict.get('initial_expanded', False),
            expanding_children_only=dict.get('expanding_children_only', False),
            expanding_other_sym=dict.get('expanding_other_sym', False),
            expandable=dict.get('expandable', False),
            inferral_expanded=dict.get('inferral_expanded', False),
            verified=dict.get('verified', None),
            empty=dict.get('empty', None),
            strategy_verified=dict.get('strategy_verified', False),
        )

    def __eq__(self, other):
        """Equal if all parameters are equal."""
        return (
            self.comb_class == self.comb_class and
            self.label == self.label and
            self.expanded == self.expanded and
            self.symmetry_expanded == self.symmetry_expanded and
            self.initial_expanded == self.initial_expanded and
            self.expanding_children_only == self.expanding_children_only and
            self.expanding_other_sym == self.expanding_other_sym and
            self.expandable == self.expandable and
            self.inferral_expanded == self.inferral_expanded and
            self.verified == self.verified and
            self.empty == self.empty and
            self.strategy_verified == self.strategy_verified
        )


class ClassDB(object):
    """
    A database for combinatorial classes.

    Each class is given a unique integer label. The key to the database is
    both the unique integer label and the ckass. It supports the following
    methods.
    - DB.add(class) will label the class and add it to the database.
    - DB.get_class(key) return the class with the given key.
    - DB.get_label(key) return the label of the given key.
    - DB.set_property(key) will set the property to true for key.
    - DB.is_property(key) will return True if the key has the property, False
    otherwise.
    - Sets verified classes with explanation.
    """

    def __init__(self, combinatorial_class):
        """
        Initialise.

        Two dictionaries allow you to call database with either the
        combinatorial class, or the unique label of the combinatorial class.
        The key can therefore be either the label or the combinatorial class.
        """
        self.class_to_info = {}
        self.label_to_info = {}
        if combinatorial_class is None:
            raise TypeError("Need to declare type of combinatorial class.")
        self.combinatorial_class = combinatorial_class

    def __iter__(self):
        """Iterator of labels."""
        for key in self.label_to_info.keys():
            yield key

    def __contains__(self, key):
        """Check for containment."""
        if isinstance(key, CombinatorialClass):
            self._compress(key)
            info = self.class_to_info.get(key)
        if isinstance(key, int):
            info = self.label_to_info.get(key)
        return info is not None

    def __eq__(self, other):
        """Equal if all information stored is the same."""
        return (self.class_to_info == other.class_to_info and
                self.label_to_info == other.label_to_info)

    def to_dict(self):
        """Return dictionary object of self."""
        return {label: info.to_dict()
                for label, info in self.label_to_info.items()}

    @classmethod
    def from_dict(cls, dict, combinatorial_class):
        """Return ClassDB for dictionary object."""
        classdb = cls(combinatorial_class)
        for label, info in dict.items():
            info = Info.from_dict(info)
            label = info.label
            comb_class = info.comb_class
            classdb.label_to_info[label] = info
            classdb.class_to_info[comb_class] = info
        return classdb

    def add(self,
            comb_class,
            symmetry_expanded=False,
            expanding_other_sym=False,
            expandable=False):
        """
        Add a combinatorial class to the database.

        Can also set some information about the combinatorial class on adding.
        """
        if not isinstance(comb_class, CombinatorialClass):
            raise TypeError(("Trying to add something that isn't a"
                            "CombinatorialClass."))
        compressed_class = self._compress(comb_class)
        if compressed_class not in self.class_to_info:
            label = len(self.class_to_info)
            info = Info(compressed_class,
                        label,
                        symmetry_expanded=symmetry_expanded,
                        expanding_other_sym=expanding_other_sym,
                        expandable=expandable)
            self.class_to_info[compressed_class] = info
            self.label_to_info[label] = info
        else:
            if expandable:
                self.set_expandable(comb_class)
            if expanding_other_sym:
                self.set_expanding_other_sym(comb_class)
            if symmetry_expanded:
                self.set_symmetry_expanded(comb_class)

    def _get_info(self, key):
        """Return Info for given key."""
        if isinstance(key, CombinatorialClass):
            key = self._compress(key)
            info = self.class_to_info.get(key)
            if info is None:
                label = len(self.class_to_info)
                info = Info(key, len(self.class_to_info))
                self.class_to_info[key] = info
                self.label_to_info[label] = info
        elif isinstance(key, int):
            info = self.label_to_info.get(key)
            if info is None:
                raise KeyError("Key not in ClassDB.")
        else:
            raise TypeError('ClassDB only accepts'
                            'CombinatorialClass and will decompress with'
                            '{}.'.format(self.combinatorial_class))
        return info

    def _compress(self, key):
        """Return compressed version of combinatorial class."""
        try:
            return key.compress()
        except AttributeError:
            raise AttributeError(("The class {} needs a compress function"
                                  ".").format(self.combinatorial_class))

    def _decompress(self, key):
        """Return decompressed version of compressed combinatorial class."""
        try:
            return self.combinatorial_class.decompress(key)
        except AttributeError:
            raise AttributeError(("The class {} needs a compress function"
                                  ".").format(self.combinatorial_class))

    def get_class(self, key):
        """Return combinatorial class of key."""
        info = self._get_info(key)
        return self._decompress(info.comb_class)

    def get_label(self, key):
        """Return label of key."""
        info = self._get_info(key)
        return info.label

    def number_times_expanded(self, key):
        """
        Return number of times combinatorial class has been expanded.

        i.e., the number of sets strategies that have been used to expanded
        the combinatorial class corresponding to the key.
        """
        info = self._get_info(key)
        return info.expanded

    def increment_expanded(self, key):
        """Increment counter for times combinatorial class was expanded."""
        info = self._get_info(key)
        self.class_to_info[info.comb_class].expanded += 1

    def is_expandable(self, key):
        """Return True if expandable, False otherwise."""
        info = self._get_info(key)
        return info.expandable

    def set_expandable(self, key, expandable=True):
        """Update database about combinatorial class expandability."""
        info = self._get_info(key)
        self.class_to_info[info.comb_class].expandable = expandable

    def is_verified(self, key):
        """
        Return True if combinatorial class has been verified.

        Verification must have an explanation, i.e, from a strategy.
        """
        return self._get_info(key).verified is not None

    def set_verified(self, key, explanation):
        """
        Update database about combinatorial class being verified

        An explanation should be provided.
        """
        self._get_info(key).verified = explanation

    def verification_reason(self, key):
        """Return explanation of verification, None if not verified."""
        return self._get_info(key).verified

    def is_empty(self, key):
        """Return True if combinatorial class is empty set, False otherwise."""
        return self._get_info(key).empty

    def set_empty(self, key, empty=True):
        """Update database about comb class being empty."""
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
        """Return True if combinatorial class verified by a strategy.
        Returns None if never updated."""
        return self._get_info(key).strategy_verified

    def set_strategy_verified(self, key, strategy_verified=True):
        """Update database combinatorial class is verified by a strategy."""
        self._get_info(key).strategy_verified = strategy_verified

    def is_symmetry_expanded(self, key):
        """Return True if combinatorial class was expanded by symmetries."""
        return self._get_info(key).symmetry_expanded

    def set_symmetry_expanded(self, key, symmetry_expanded=True):
        """Update database that combinatorial class was symmetry expanded."""
        self._get_info(key).symmetry_expanded = symmetry_expanded

    def is_expanding_children_only(self, key):
        """Return True if not expanding as expanding other children only."""
        return self._get_info(key).expanding_children_only

    def set_expanding_children_only(self, key, expanding_children_only=True):
        """Update database if expanding childern_only."""
        self._get_info(key).expanding_children_only = expanding_children_only

    def is_expanding_other_sym(self, key):
        """Return True if symmetry of combinatorial class is being expaned."""
        return self._get_info(key).expanding_other_sym

    def set_expanding_other_sym(self, key, expanding_other_sym=True):
        """Update database symmetry of combinatorial class is being
        expanded."""
        self._get_info(key).expanding_other_sym = expanding_other_sym

    def is_initial_expanded(self, key):
        """Return True if combinatorial class was initial expanded."""
        return self._get_info(key).initial_expanded

    def set_initial_expanded(self, key, initial_expanded=True):
        """Update database that combinatorial class was initial expanded."""
        self._get_info(key).initial_expanded = initial_expanded

    def is_inferral_expanded(self, key):
        """Return True if combinatorial class was inferral expanded."""
        return self._get_info(key).inferral_expanded

    def set_inferral_expanded(self, key, inferral_expanded=True):
        """Update database that combinatorial class was inferral expanded."""
        self._get_info(key).inferral_expanded = inferral_expanded
