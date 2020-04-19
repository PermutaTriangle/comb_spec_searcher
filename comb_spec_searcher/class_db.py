"""
A database for combinatorial class found.

Contains information about if combinatorial classes have been expanded, found
by symmetries etc. It gives each combinatorial class a unique label.
"""

from base64 import b64decode, b64encode

from logzero import logger

from .combinatorial_class import CombinatorialClass


class Info:
    """Information about a combinatorial class."""

    def __init__(self, comb_class, label, **kwargs):
        """Initialise information."""
        self.comb_class = comb_class
        self.label = label
        self.strategy_verified = kwargs.get("strategy_verified", None)
        self.symmetry_expanded = kwargs.get("symmetry_expanded", False)
        self.empty = kwargs.get("empty", None)

    def to_dict(self):
        """Return dictionary object of self that is JSON serializable."""
        try:
            return {
                "comb_class": b64encode(self.comb_class).decode(),
                "label": self.label,
                "strategy_verified": self.strategy_verified,
                "symmetry_expanded": self.symmetry_expanded,
                "empty": self.empty,
            }
        except TypeError as e:
            logger.warning(
                "Lost information about combinatorial class with "
                "encoding as:\n%s\n%s",
                self.comb_class,
                e,
            )
            return None

    @classmethod
    def from_dict(cls, dict_):
        """Return Info object from dictionary."""
        return cls(
            comb_class=b64decode(dict_["comb_class"].encode()),
            label=int(dict_["label"]),
            symmetry_expanded=dict_.get("symmetry_expanded", False),
            strategy_verified=dict_.get("strategy_verified", None),
            empty=dict_.get("empty", None),
        )

    def __eq__(self, other):
        """Equal if all parameters are equal."""
        return (
            self.comb_class == self.comb_class
            and self.label == self.label
            and self.symmetry_expanded == other.symmetry_expanded
            and self.empty == self.empty
            and self.strategy_verified == self.strategy_verified
        )


class ClassDB:
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
        for key in self.label_to_info:
            yield key

    def __contains__(self, key):
        """Check for containment."""
        if isinstance(key, CombinatorialClass):
            comb_class = self._compress(key)
            info = self.class_to_info.get(comb_class)
        if isinstance(key, int):
            info = self.label_to_info.get(key)
        return info is not None

    def __eq__(self, other):
        """Equal if all information stored is the same."""
        return (
            self.class_to_info == other.class_to_info
            and self.label_to_info == other.label_to_info
        )

    def to_dict(self):
        """Return dictionary object of self."""
        return {label: info.to_dict() for label, info in self.label_to_info.items()}

    @classmethod
    def from_dict(cls, dict_, combinatorial_class):
        """Return ClassDB for dictionary object."""
        classdb = cls(combinatorial_class)
        for label, info in dict_.items():
            info = Info.from_dict(info)
            label = info.label
            comb_class = info.comb_class
            classdb.label_to_info[label] = info
            classdb.class_to_info[comb_class] = info
        return classdb

    def add(
        self, comb_class, symmetry_expanded=False, compressed=False,
    ):
        """
        Add a combinatorial class to the database.

        Can also set some information about the combinatorial class on adding.
        """
        if not compressed and not isinstance(comb_class, CombinatorialClass):
            raise TypeError(
                ("Trying to add something that isn't a" "CombinatorialClass.")
            )
        if not compressed:
            compressed_class = self._compress(comb_class)
        else:
            compressed_class = comb_class
        if compressed_class not in self.class_to_info:
            label = len(self.class_to_info)
            info = Info(compressed_class, label, symmetry_expanded=symmetry_expanded,)
            self.class_to_info[compressed_class] = info
            self.label_to_info[label] = info
        else:
            label = self.class_to_info[compressed_class].label
            if symmetry_expanded:
                self.set_symmetry_expanded(label)

    def _get_info(self, key):
        """Return Info for given key."""
        if isinstance(key, CombinatorialClass):
            key = self._compress(key)
            info = self.class_to_info.get(key)
            if info is None:
                self.add(key, compressed=True)
                info = self.class_to_info[key]
        elif isinstance(key, int):
            info = self.label_to_info.get(key)
            if info is None:
                raise KeyError("Key not in ClassDB.")
        else:
            raise TypeError(
                "ClassDB only accepts"
                "CombinatorialClass and will decompress with"
                "{}.".format(self.combinatorial_class)
            )
        return info

    def _compress(self, key):
        """Return compressed version of combinatorial class."""
        try:
            return key.compress()
        except AttributeError:
            raise AttributeError(
                ("The class {} needs a compress function" ".").format(
                    self.combinatorial_class
                )
            )

    def _decompress(self, key):
        """Return decompressed version of compressed combinatorial class."""
        try:
            return self.combinatorial_class.decompress(key)
        except AttributeError:
            raise AttributeError(
                ("The class {} needs a compress function" ".").format(
                    self.combinatorial_class
                )
            )

    def get_class(self, key):
        """Return combinatorial class of key."""
        info = self._get_info(key)
        return self._decompress(info.comb_class)

    def get_label(self, key):
        """Return label of key."""
        info = self._get_info(key)
        return info.label

    def is_empty(self, comb_class, label=None):
        """Return True if combinatorial class is empty set, False if not.
        Return None if status not set."""
        if label is None:
            info = self._get_info(comb_class)
            label = info.label
        else:
            info = self._get_info(label)
        empty = info.empty
        if empty is None:
            if not isinstance(comb_class, CombinatorialClass):
                comb_class = self.get_class(comb_class)
            empty = comb_class.is_empty()
            self.set_empty(label)
        return empty

    def set_empty(self, key, empty=True):
        """Update database about comb class being empty."""
        info = self._get_info(key)
        info.empty = empty or bool(info.empty)

    def is_strategy_verified(self, key):
        """Return True if combinatorial class verified by a strategy.
        Returns None if never updated."""
        return self._get_info(key).strategy_verified

    def set_strategy_verified(self, key, strategy_verified=True):
        """Update database combinatorial class is verified by a strategy."""
        info = self._get_info(key)
        info.strategy_verified = strategy_verified or bool(info.strategy_verified)

    def is_symmetry_expanded(self, key):
        """Return True if combinatorial class was expanded by symmetries."""
        return self._get_info(key).symmetry_expanded

    def set_symmetry_expanded(self, key, symmetry_expanded=True):
        """Update database that combinatorial class was symmetry expanded."""
        info = self._get_info(key)
        info.symmetry_expanded = symmetry_expanded or bool(info.symmetry_expanded)
