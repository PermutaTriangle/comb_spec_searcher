"""
A database for combinatorial class found. It gives each combinatorial class
a unique label. Each combinatorial class object is compressed, and decompressed
using the CombinatorialClass 'to_bytes' and 'from_bytes' method if these are
implemented.

Contains information about if combinatorial classes have been found by
if is_empty has been checked.
"""

import zlib
from typing import Dict, Generic, Iterator, Optional, Type, cast

from comb_spec_searcher.typing import ClassKey, CombinatorialClassType, Key


class Info:
    """
    Information about a combinatorial class.
        - the class,
        - the label,
        - is it empty?
    """

    def __init__(self, comb_class: ClassKey, label: int, empty: Optional[bool] = None):
        self.comb_class = comb_class
        self.label = label
        self.empty = empty

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Info):
            return NotImplemented
        return (
            self.comb_class == self.comb_class
            and self.label == self.label
            and self.empty == self.empty
        )


class ClassDB(Generic[CombinatorialClassType]):
    """
    A database for combinatorial classes.

    Each class is given a unique integer label. The key to the database is
    both the unique integer label and the ckass. It supports the following
    methods.
    - DB.add(class) will label the class and add it to the database.
    - DB.get_class(key) return the class with the given key.
    - DB.get_label(key) return the label of the given key.
    - DB.set_empty(key) will set empty to be true for key.
    - DB.is_empty(key) will return True if the key is empty, False
    otherwise.
    """

    def __init__(self, combinatorial_class: Type[CombinatorialClassType]):
        self.class_to_info: Dict[ClassKey, Info] = {}
        self.label_to_info: Dict[int, Info] = {}
        self.combinatorial_class = combinatorial_class

    def __iter__(self) -> Iterator[int]:
        """
        Iterator of labels.
        """
        for key in self.label_to_info:
            yield key

    def __contains__(self, key: Key) -> bool:
        """
        Return true if the the key is already in the database.
        """
        if isinstance(key, self.combinatorial_class):
            comb_class = self._compress(key)
            info = self.class_to_info.get(comb_class)
        elif isinstance(key, int):
            info = self.label_to_info.get(key)
        else:
            raise ValueError("Invalid key")
        return info is not None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ClassDB):
            return NotImplemented
        return bool(
            self.class_to_info == other.class_to_info
            and self.label_to_info == other.label_to_info
        )

    def add(self, comb_class: ClassKey, compressed: bool = False) -> None:
        """
        Add a combinatorial class to the database.
        """
        if not compressed and not isinstance(comb_class, self.combinatorial_class):
            raise TypeError(
                ("Trying to add something that isn't a" "CombinatorialClass.")
            )
        if not compressed:
            assert isinstance(
                comb_class, self.combinatorial_class
            ), "trying to add non combinatorial class to database"
            compressed_class = self._compress(comb_class)
        else:
            compressed_class = comb_class
        if compressed_class not in self.class_to_info:
            label = len(self.class_to_info)
            info = Info(compressed_class, label)
            self.class_to_info[compressed_class] = info
            self.label_to_info[label] = info
        else:
            label = self.class_to_info[compressed_class].label

    def _get_info(self, key: Key) -> Info:
        """
        Return Info for given key.
        """
        if isinstance(key, self.combinatorial_class):
            compressed_key = self._compress(key)
            info = self.class_to_info.get(compressed_key)
            if info is None:
                self.add(compressed_key, compressed=True)
                info = self.class_to_info[compressed_key]
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

    def _compress(self, key: CombinatorialClassType) -> ClassKey:
        """
        Return compressed version of combinatorial class.
        """
        # pylint: disable=no-self-use
        try:
            return zlib.compress(key.to_bytes(), 9)
        except NotImplementedError:
            # to use compression you should implement a 'to_bytes' function.
            return key

    def _decompress(self, key: ClassKey) -> CombinatorialClassType:
        """
        Return decompressed version of compressed combinatorial class.
        """
        try:
            assert isinstance(key, bytes)
            return cast(
                CombinatorialClassType,
                self.combinatorial_class.from_bytes(zlib.decompress(key)),
            )
        except (AssertionError, NotImplementedError):
            # to use compression you should implement a 'from_bytes' function.
            assert isinstance(
                key, self.combinatorial_class
            ), "you must implement a 'from_bytes' function to use compression"
            return key

    def get_class(self, key: Key) -> CombinatorialClassType:
        """
        Return combinatorial class of key.
        """
        info = self._get_info(key)
        return self._decompress(info.comb_class)

    def get_label(self, key: Key) -> int:
        """
        Return label of key.
        """
        info = self._get_info(key)
        return info.label

    def is_empty(
        self, comb_class: CombinatorialClassType, label: Optional[int] = None
    ) -> bool:
        """
        Return True if combinatorial class is empty set, False if not.
        Return None if status not set.
        """
        if label is None:
            info = self._get_info(comb_class)
            label = info.label
        else:
            info = self._get_info(label)
        empty = info.empty
        if empty is None:
            if not isinstance(comb_class, self.combinatorial_class):
                comb_class = self.get_class(comb_class)
            empty = self._is_empty(comb_class)
            self.set_empty(label, empty)
        return bool(empty)

    def _is_empty(self, comb_class: CombinatorialClassType) -> bool:
        if not isinstance(comb_class, self.combinatorial_class):
            comb_class = self.get_class(comb_class)
        return comb_class.is_empty()

    def set_empty(self, key: Key, empty: bool = True) -> None:
        """
        Update database about comb class being empty.
        """
        info = self._get_info(key)
        info.empty = empty

    def status(self) -> str:
        """
        Return a string with the current status of the run.
        """
        status = "ClassDB status:\n"
        status += "\tTotal number of combinatorial classes found is"
        status += f" {len(self.label_to_info):,d}"
        return status
