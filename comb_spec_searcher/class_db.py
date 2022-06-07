"""
A database for combinatorial class found. It gives each combinatorial class
a unique label. Each combinatorial class object is compressed, and decompressed
using the CombinatorialClass 'to_bytes' and 'from_bytes' method if these are
implemented.

Contains information about if combinatorial classes have been found by
if is_empty has been checked.
"""

import abc
import multiprocessing
import multiprocessing.connection
import os
import time
import zlib
from collections import defaultdict
from datetime import timedelta
from typing import (
    Any,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
    Union,
    cast,
)

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


class AbstractClassDB(Generic[CombinatorialClassType]):
    def __init__(self, combinatorial_class: Type[CombinatorialClassType]):
        self.combinatorial_class = combinatorial_class

    @abc.abstractmethod
    def _get_info(self, key: Key) -> Info:
        """
        Return Info for given key.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _set_info(self, key: Key, info: Info) -> None:
        """
        Return Info for given key.
        """
        raise NotImplementedError

    def get_class(self, key: Key) -> CombinatorialClassType:
        """
        Return combinatorial class of key.
        """
        info = self._get_info(key)
        return self._decompress(info.comb_class)

    def is_empty(
        self, comb_class: CombinatorialClassType, label: Optional[int] = None
    ) -> bool:
        """
        Return True if combinatorial class is empty set, False if not.
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
        return comb_class.is_empty()

    def get_label(self, key: Key) -> int:
        """
        Return label of key.
        """
        info = self._get_info(key)
        return info.label

    def set_empty(self, key: Key, empty: bool = True) -> None:
        """
        Update database about comb class being empty.
        """
        info = self._get_info(key)
        info.empty = empty
        self._set_info(key, info)

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

    def status(self) -> str:
        return f"Status update for class {self.__class__} is not implemented."


class ClassDB(AbstractClassDB[CombinatorialClassType]):
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
        super().__init__(combinatorial_class)
        self.class_to_info: Dict[ClassKey, Info] = {}
        self.label_to_info: Dict[int, Info] = {}
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
                f"{self.combinatorial_class}."
            )
        return info

    def _set_info(self, key: Key, info: Info):
        self.label_to_info[info.label] = info
        self.class_to_info[info.comb_class] = info

    def get_class(self, key: Key) -> CombinatorialClassType:
        """
        Return combinatorial class of key.
        """
        info = self._get_info(key)
        return self._decompress(info.comb_class)

    def _is_empty(self, comb_class: CombinatorialClassType) -> bool:
        self._empty_num_application += 1
        start = time.time()
        is_empty = super()._is_empty(comb_class)
        self._empty_time += time.time() - start
        return is_empty

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


class WorkerClassDB(AbstractClassDB[CombinatorialClassType]):
    def __init__(
        self,
        combinatorial_class: Type[CombinatorialClassType],
        conn: "multiprocessing.connection.Connection",
    ) -> None:
        super().__init__(combinatorial_class)
        self.conn = conn
        self.waiting_time = 0.0

    def _get_info(self, key: Key) -> Info:
        """
        Return Info for given key.
        """
        if isinstance(key, self.combinatorial_class):
            message: ClassKey = self._compress(key)
        elif isinstance(key, int):
            message = key
        else:
            raise TypeError(
                "ClassDB only accepts"
                "CombinatorialClass and will decompress with"
                f"{self.combinatorial_class}."
            )
        wait_time = time.time()
        self.conn.send(message)
        info = self.conn.recv()
        self.waiting_time += time.time() - wait_time
        assert isinstance(info, Info)
        return info

    def _get_infos(self, keys: Iterable[Key]) -> Tuple[Info]:
        """
        Return Info for given key.
        """
        messages = []
        for key in keys:
            if isinstance(key, self.combinatorial_class):
                message: ClassKey = self._compress(key)
            elif isinstance(key, int):
                message = key
            else:
                raise TypeError(
                    "ClassDB only accepts"
                    "CombinatorialClass and will decompress with"
                    f"{self.combinatorial_class}."
                )
            messages.append(message)
        wait_time = time.time()
        self.conn.send(tuple(messages))
        infos = self.conn.recv()
        self.waiting_time += time.time() - wait_time
        return infos

    def get_labels(self, keys: Iterable[Key]) -> Tuple[int, ...]:
        """
        Return label of key.
        """
        infos = self._get_infos(keys)
        return tuple(info.label for info in infos)

    def _set_info(self, key: Key, info: Info) -> None:
        """
        Return Info for given key.
        """
        self.conn.send(info)

    def status(self) -> str:
        self.conn.send("status")
        return self.conn.recv()


class PrimaryClassDB(Generic[CombinatorialClassType]):
    def __init__(
        self,
        combinatorial_class: Type[CombinatorialClassType],
    ) -> None:
        self.combinatorial_class = combinatorial_class
        self.class_to_info: Dict[bytes, Info] = {}
        self.label_to_info: Dict[int, Info] = {}
        self.connections: List["multiprocessing.connection.Connection"] = []

    def spawn_workerdb(self) -> WorkerClassDB[CombinatorialClassType]:
        primary_conn, worker_conn = multiprocessing.Pipe()
        self.connections.append(primary_conn)
        return WorkerClassDB(self.combinatorial_class, worker_conn)

    def add(self, compressed_class: bytes) -> Info:
        assert compressed_class not in self.class_to_info
        label = len(self.class_to_info)
        info = Info(compressed_class, label)
        self.class_to_info[compressed_class] = info
        self.label_to_info[label] = info
        return info

    def monitor_connection(self) -> None:
        print("classdb", os.getpid())
        times = defaultdict(float)
        num_waiting = defaultdict(int)
        while True:
            waiting_time = time.time()
            ready_connections = multiprocessing.connection.wait(self.connections)
            times["waiting_time"] += time.time() - waiting_time

            num_waiting[len(ready_connections)] += 1
            for conn in ready_connections:
                assert isinstance(conn, multiprocessing.connection.Connection)

                rcv_time = time.time()
                message = conn.recv()
                rcv_time = time.time() - rcv_time
                if isinstance(message, tuple):
                    conn.send(
                        tuple(
                            self.handle_message(
                                msg, times, rcv_time / len(message), num_waiting
                            )
                            for msg in message
                        )
                    )
                else:
                    res = self.handle_message(message, times, rcv_time, num_waiting)
                    if res is not None:
                        conn.send(res)

    def handle_message(
        self, message: Union[Info, bytes, int, str], times, rcv_time, num_waiting
    ) -> Optional[Any]:
        if isinstance(message, Info):
            times["rcv_Info"] += rcv_time
            self.label_to_info[message.label] = message
            self.class_to_info[message.comb_class] = message
        elif isinstance(message, bytes):
            times["rcv_bytes"] += rcv_time
            info = self.class_to_info.get(message)
            if info is None:
                info = self.add(message)
            return info

        elif isinstance(message, int):
            times["rcv_int"] += rcv_time
            info = self.label_to_info[message]
            if info is None:
                raise KeyError("Missing class")
            return info
        elif message == "status":
            times["rcv_status"] += rcv_time
            print("\n\n" + "=" * 50)
            for k, v in times.items():
                print(f"{k} {round(v,4)}")
            print(num_waiting)
            return self.status()
        else:
            print(message)
            raise ValueError("Unexpected message")

    def status(self) -> str:
        """
        Return a string with the current status of the run.
        """
        status = "ClassDB status:\n"
        status += "\tTotal number of combinatorial classes found is"
        status += f" {len(self.label_to_info):,d}\n"
        return status
