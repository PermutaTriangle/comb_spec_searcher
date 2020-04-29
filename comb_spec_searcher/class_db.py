"""
A database for combinatorial class found. It gives each combinatorial class
a unique label. Each combinatorial class object is compressed, and decompressed
using the CombinatorialClass 'to_bytes' and 'from_bytes' method if these are
implemented.

Contains information about if combinatorial classes have been found by
if is_empty has been checked.
"""

from collections import defaultdict
from typing import Iterator, Optional, Type, TYPE_CHECKING, Union

from .combinatorial_class import CombinatorialClass
from .utils import cssmethodtimer

ClassKey = Union[bytes, CombinatorialClass]
Key = Union[CombinatorialClass, int]

if TYPE_CHECKING:
    from typing import Dict


class Info:
    """
    Information about a combinatorial class.
        - the class,
        - the label,
        - is it empty?
    """

    def __init__(
        self, comb_class: ClassKey, label: int, empty: Optional[bool] = None,
    ):
        self.comb_class = comb_class
        self.label = label
        self.empty = empty

    def __eq__(self, other) -> bool:
        return (
            self.comb_class == self.comb_class
            and self.label == self.label
            and self.empty == self.empty
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
    - DB.set_empty(key) will set empty to be true for key.
    - DB.is_empty(key) will return True if the key is empty, False
    otherwise.
    """

    def __init__(self, combinatorial_class: Type[CombinatorialClass]):
        self.class_to_info = {}  # type: Dict[ClassKey, Info]
        self.label_to_info = {}  # type: Dict[int, Info]
        self.combinatorial_class = combinatorial_class
        self.func_calls = defaultdict(int)  # type: Dict[str, int]
        self.func_times = defaultdict(float)  # type: Dict[str, float]

    def __iter__(self) -> Iterator[int]:
        """
        Iterator of labels.
        """
        for key in self.label_to_info:
            yield key

    def __contains__(self, key: Key):
        """
        Return true if the the key is already in the database.
        """
        if isinstance(key, CombinatorialClass):
            comb_class = self._compress(key)
            info = self.class_to_info.get(comb_class)
        if isinstance(key, int):
            info = self.label_to_info.get(key)
        return info is not None

    def __eq__(self, other) -> bool:
        return bool(
            self.class_to_info == other.class_to_info
            and self.label_to_info == other.label_to_info
        )

    def add(
        self, comb_class: CombinatorialClass, compressed: bool = False,
    ):
        """
        Add a combinatorial class to the database.
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
            info = Info(compressed_class, label)
            self.class_to_info[compressed_class] = info
            self.label_to_info[label] = info
        else:
            label = self.class_to_info[compressed_class].label

    def _get_info(self, key: Key) -> Info:
        """
        Return Info for given key.
        """
        if isinstance(key, CombinatorialClass):
            compressed_key = self._compress(key)
            info = self.class_to_info.get(compressed_key)
            f = self._compress
            reveal_locals()
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

    @cssmethodtimer("compress")
    def _compress(self, key: CombinatorialClass) -> Union[bytes, CombinatorialClass]:
        """
        Return compressed version of combinatorial class.
        """
        try:
            return key.to_bytes()
        except NotImplementedError:
            # to use compression you should implement a 'to_bytes' function.
            return key

    @cssmethodtimer("decompress")
    def _decompress(self, key: Union[bytes, CombinatorialClass]) -> CombinatorialClass:
        """
        Return decompressed version of compressed combinatorial class.
        """
        try:
            assert isinstance(key, bytes)
            return self.combinatorial_class.from_bytes(key)
        except (AssertionError, NotImplementedError):
            # to use compression you should implement a 'from_bytes' function.
            assert isinstance(
                key, CombinatorialClass
            ), "you must implement a 'from_bytes' function to use compression"
            return key

    @cssmethodtimer("get class")
    def get_class(self, key: Key) -> CombinatorialClass:
        """
        Return combinatorial class of key.
        """
        info = self._get_info(key)
        c = info.comb_class
        d = self._decompress(info.comb_class)
        f = self._decompress
        reveal_locals()
        return self._decompress(info.comb_class)

    @cssmethodtimer("get label")
    def get_label(self, key: Key) -> int:
        """
        Return label of key.
        """
        info = self._get_info(key)
        return info.label

    def is_empty(
        self, comb_class: CombinatorialClass, label: Optional[int] = None
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
            if not isinstance(comb_class, CombinatorialClass):
                comb_class = self.get_class(comb_class)
            empty = self._is_empty(comb_class)
            self.set_empty(label, empty)
        return bool(empty)

    @cssmethodtimer("is empty")
    def _is_empty(self, comb_class: CombinatorialClass) -> bool:
        if not isinstance(comb_class, CombinatorialClass):
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
        status += "\tTotal number of combinatorial classes found is {}\n".format(
            len(self.label_to_info)
        )
        for explanation in self.func_calls:
            count = self.func_calls[explanation]
            time_spent = self.func_times[explanation]
            status += "\tApplied {} {} times. Time spent is {} seconds.\n".format(
                explanation, count, round(time_spent, 2)
            )
        # TODO: empty classes?
        status = status[:-2]
        return status
