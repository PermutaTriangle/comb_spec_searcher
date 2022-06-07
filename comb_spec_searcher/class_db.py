"""
A database for combinatorial class found. It gives each combinatorial class
a unique label. Each combinatorial class object is compressed, and decompressed
using the CombinatorialClass 'to_bytes' and 'from_bytes' method if these are
implemented.

Contains information about if combinatorial classes have been found by
if is_empty has been checked.
"""

import time
import zlib
from datetime import timedelta
from typing import (
    Dict,
    Generic,
    Iterator,
    List,
    MutableMapping,
    NamedTuple,
    Optional,
    Type,
    cast,
)

from comb_spec_searcher.typing import ClassKey, CombinatorialClassType, Key


class Info(NamedTuple):
    comb_class: ClassKey
    label: int
    empty: Optional[bool] = None


class LabelToInfo(MutableMapping[int, Optional[Info]]):
    def __init__(
        self,
        comb_class_list: List[ClassKey],
        label_dict: Dict[ClassKey, int],
        empty_list: List[Optional[bool]],
    ):
        self.comb_class_list = comb_class_list
        self.label_dict = label_dict
        self.empty_list = empty_list

    def __getitem__(self, label: int) -> Optional[Info]:
        try:
            return Info(self.comb_class_list[label], label, self.empty_list[label])
        except KeyError:
            return None

    def __setitem__(self, key: int, value: Optional[Info]) -> None:
        raise NotImplementedError

    def __delitem__(self, key: int) -> None:
        raise NotImplementedError

    def __iter__(self) -> Iterator:
        for label in self.label_dict.values():
            yield label

    def __len__(self) -> int:
        return len(self.empty_list)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LabelToInfo):
            return NotImplemented
        return (
            self.comb_class_list == other.comb_class_list
            and self.label_dict == other.label_dict
            and self.empty_list == other.empty_list
        )


class ClassToInfo(MutableMapping[ClassKey, Optional[Info]]):
    def __init__(
        self,
        comb_class_list: List[ClassKey],
        label_dict: Dict[ClassKey, int],
        empty_list: List[Optional[bool]],
    ):
        self.comb_class_list = comb_class_list
        self.label_dict = label_dict
        self.empty_list = empty_list

    def __getitem__(self, class_key: ClassKey) -> Optional[Info]:
        try:
            label = self.label_dict[class_key]
            return Info(self.comb_class_list[label], label, self.empty_list[label])
        except KeyError:
            return None

    def __setitem__(self, key: ClassKey, value: Optional[Info]) -> None:
        raise NotImplementedError

    def __delitem__(self, key: ClassKey) -> None:
        raise NotImplementedError

    def __iter__(self) -> Iterator:
        raise NotImplementedError

    def __len__(self) -> int:
        return len(self.empty_list)

    def __contains__(self, class_key: ClassKey) -> bool:
        return class_key in self.label_dict

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ClassToInfo):
            return NotImplemented
        return (
            self.comb_class_list == other.comb_class_list
            and self.label_dict == other.label_dict
            and self.empty_list == other.empty_list
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
        self.comb_class_list: List[ClassKey] = []
        self.label_dict: Dict[ClassKey, int] = {}
        self.empty_list: List[Optional[bool]] = []
        self.class_to_info: ClassToInfo = ClassToInfo(
            self.comb_class_list, self.label_dict, self.empty_list
        )
        self.label_to_info: LabelToInfo = LabelToInfo(
            self.comb_class_list, self.label_dict, self.empty_list
        )
        self.combinatorial_class = combinatorial_class
        self._empty_time = 0.0
        self._empty_num_application = 0

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
            self.comb_class_list.append(compressed_class)
            self.label_dict[compressed_class] = label
            self.empty_list.append(None)

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
                f"{self.combinatorial_class}."
            )
        return cast(Info, info)

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
        """
        if label is None:
            label = self.label_dict[self._compress(comb_class)]

        empty = self.empty_list[label]
        if empty is None:
            if not isinstance(comb_class, self.combinatorial_class):
                comb_class = self.get_class(comb_class)
            empty = self._is_empty(comb_class)
            self.set_empty(label, empty)
        return bool(empty)

    def _is_empty(self, comb_class: CombinatorialClassType) -> bool:
        if not isinstance(comb_class, self.combinatorial_class):
            comb_class = self.get_class(comb_class)
        self._empty_num_application += 1
        start = time.time()
        is_empty = comb_class.is_empty()
        self._empty_time += time.time() - start
        return is_empty

    def set_empty(self, key: Key, empty: bool = True) -> None:
        """
        Update database about comb class being empty.
        """
        self.empty_list[self.get_label(key)] = empty

    def status(self) -> str:
        """
        Return a string with the current status of the run.
        """
        status = "ClassDB status:\n"
        status += "\tTotal number of combinatorial classes found is"
        status += f" {len(self.label_to_info):,d}\n"
        status += f"\tis_empty check applied {self._empty_num_application} time. "
        status += f"Time spent: {timedelta(seconds=int(self._empty_time))}"
        return status
