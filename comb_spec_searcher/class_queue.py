"""
A queue of labels.
"""
import abc
import multiprocessing
import os
from collections import Counter, defaultdict, deque
from email.policy import default
from typing import Counter as CounterType
from typing import (
    Deque,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Set,
    Tuple,
)

import tabulate

from comb_spec_searcher.class_db import WorkerClassDB
from comb_spec_searcher.exception import NoMoreClassesToExpandError
from comb_spec_searcher.strategies.rule import AbstractRule
from comb_spec_searcher.strategies.strategy_pack import StrategyPack
from comb_spec_searcher.typing import CombinatorialClassType, CSSstrategy, WorkPacket


class CSSQueue(abc.ABC):
    """
    A queue of labels.
    """

    def __init__(self, pack: StrategyPack):
        self.inferral_strategies = tuple(pack.inferral_strats)
        self.initial_strategies = tuple(pack.initial_strats)
        self.expansion_strats = tuple(tuple(x) for x in pack.expansion_strats)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CSSQueue):
            return NotImplemented
        return self.__class__ == other.__class__ and self.__dict__ == other.__dict__

    @abc.abstractmethod
    def add(self, label: int) -> None:
        """Add a label to the queue."""

    @abc.abstractmethod
    def set_not_inferrable(self, label: int) -> None:
        """You should avoid yielding label with an inferral strategy in future."""

    @abc.abstractmethod
    def set_verified(self, label: int) -> None:
        """Label was verified, how should the queue react?"""

    @abc.abstractmethod
    def set_stop_yielding(self, label: int) -> None:
        """You should stop yielding label. CSS indicated that this label should
        no longer be yielded, e.g., expanding another symmetry or expanding
        only children"""

    @abc.abstractmethod
    def do_level(self) -> Iterator[WorkPacket]:
        """Return a 'level'. The definition of level can be chosen by the user,
        but it determines the functionality of the do_level method in CSS."""

    @abc.abstractmethod
    def status(self) -> str:
        """Return a string that indicates that current status of the queue."""

    def __iter__(self) -> Iterator[WorkPacket]:
        return self

    @abc.abstractmethod
    def __next__(self) -> WorkPacket:
        """
        Yield the combinatorial classes in queue.
        It should yield triples (label, strategies, inferral)
        - label is the next thing to be expanded
        - strategies is the list of strategies to expand label with
        - inferral boolean tells the CSS if it is a inferral strategies. With
        inferral set to True, CSS will only apply the next in the list to the
        children, and assume you are ignore the parent from now on. The
        strategies will be applied cyclically until no change.
        """
        raise NotImplementedError


class DefaultQueue(CSSQueue):
    """
    The default queue used by CSS.
    """

    def __init__(self, pack: StrategyPack):
        super().__init__(pack)
        self.working: Deque[int] = deque()
        self.next_level: CounterType[int] = Counter()
        self.curr_level: Tuple[Deque[int], ...] = tuple(
            deque() for _ in self.expansion_strats
        )
        # One extra deque to be able to set ignore
        self.curr_level = self.curr_level + (deque(),)
        self._inferral_expanded: Set[int] = set()
        self._initial_expanded: Set[int] = set()
        self.ignore: Set[int] = set()
        self.queue_sizes: List[int] = []
        self.staging: Deque[WorkPacket] = deque([])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DefaultQueue):
            return NotImplemented
        return self.__class__ == other.__class__ and self.__dict__ == other.__dict__

    @property
    def levels_completed(self):
        """Return the number of times swapped from curr to next."""
        return len(self.queue_sizes)

    def add(self, label: int) -> None:
        if self.can_do_inferral(label) or self.can_do_initial(label):
            self.working.append(label)
        elif label not in self.ignore:
            self.next_level.update((label,))

    def set_verified(self, label) -> None:
        self.set_stop_yielding(label)

    def set_not_inferrable(self, label: int) -> None:
        """Mark the label such that it's not expanded with inferral anymore"""
        if label not in self.ignore:
            self._inferral_expanded.add(label)

    def set_not_initial(self, label: int) -> None:
        """Mark the label such that it's not expanded with initial anymore"""
        if label not in self.ignore:
            self._initial_expanded.add(label)

    def set_stop_yielding(self, label: int) -> None:
        self.ignore.add(label)
        # can remove it elsewhere to keep sets "small"
        self._inferral_expanded.discard(label)
        self._initial_expanded.discard(label)
        self.next_level.pop(label, None)

    def can_do_inferral(self, label: int) -> bool:
        """Return true if inferral strategies can be applied."""
        return bool(self.inferral_strategies) and label not in self._inferral_expanded

    def can_do_initial(self, label: int) -> bool:
        """Return true if initial strategies can be applied."""
        return bool(self.initial_strategies) and label not in self._initial_expanded

    def can_do_expansion(self, label: int, idx: int) -> bool:
        """Return true if expansion strategies can be applied."""
        return label not in self.ignore and idx < len(self.expansion_strats)

    def _populate_staging(self) -> None:
        """
        Populate the staging queue that is used by next to return WorkPacket.
        """
        while not self.staging and self.working:
            self.staging.extend(self._iter_helper_working())
        while not self.staging:
            if not any(self.curr_level):
                self._change_level()
            self.staging.extend(self._iter_helper_curr())

    def _change_level(self) -> None:
        assert not self.staging, "Can't change level is staging is not empty"
        assert not self.working, "Can't change level is working is not empty"
        assert not any(self.curr_level), "Can't change level is curr_level is not empty"
        self.curr_level[0].extend(
            label for label, _ in sorted(self.next_level.items(), key=lambda x: -x[1])
        )
        if not any(self.curr_level):
            raise StopIteration
        self.queue_sizes.append(len(self.curr_level[0]))
        self.next_level = Counter()

    def _iter_helper_curr(self) -> Iterator[WorkPacket]:
        assert any(self.curr_level), "The current queue is empty"
        # pylint: disable=stop-iteration-return
        idx, label = next(
            (
                (idx, queue.popleft())
                for idx, queue in enumerate(self.curr_level)
                if queue
            )
        )
        if idx == len(self.expansion_strats):
            self.set_stop_yielding(label)
            return
        for strat in self.expansion_strats[idx]:
            yield WorkPacket(label, (strat,), False)
        self.curr_level[idx + 1].append(label)

    def _iter_helper_working(self) -> Iterator[WorkPacket]:
        label = self.working.popleft()
        if self.can_do_inferral(label):
            yield WorkPacket(label, self.inferral_strategies, True)
            self.set_not_inferrable(label)
        if self.can_do_initial(label):
            for strat in self.initial_strategies:
                yield WorkPacket(label, (strat,), False)
            self.set_not_initial(label)
        self.next_level.update((label,))

    def __next__(self) -> WorkPacket:
        while True:
            while self.staging:
                wp = self.staging.popleft()
                if wp.label not in self.ignore:
                    return wp
            self._populate_staging()

    def do_level(self) -> Iterator[WorkPacket]:
        """
        An iterator of all combinatorial classes in the current queue.

        Will swap next queue to current after iteration.
        """
        curr_level = self.levels_completed
        while curr_level == self.levels_completed:
            try:
                yield next(self)
            except StopIteration as e:
                if curr_level == self.levels_completed:
                    raise NoMoreClassesToExpandError from e
                return

    def status(self) -> str:
        status = f"Queue status (currently on level {self.levels_completed}):\n"
        table: List[Tuple[str, str]] = []
        table.append(("working", f"{len(self.working):,d}"))
        for idx, queue in enumerate(self.curr_level[:-1]):
            table.append((f"current (set {idx+1})", f"{len(queue):,d}"))
        table.append(("next", f"{len(self.next_level):,d}"))
        status += "    "
        headers = ("Queue", "Size")
        colalign = ("left", "right")
        status += (
            tabulate.tabulate(table, headers=headers, colalign=colalign).replace(
                "\n", "\n    "
            )
            + "\n"
        )
        status += "\tThe size of the current queues at each level: "
        status += ", ".join(map(str, self.queue_sizes))
        return status


class ParallelWorkPacket(NamedTuple):
    label: int
    strategy_index: int


class TrackedDefaultQueue(DefaultQueue):
    def __init__(self, pack: StrategyPack):
        super().__init__(pack)
        self.next_curr_level: Optional[Tuple[Deque[int], ...]] = None

    def is_empty(self) -> bool:
        return bool(
            not self.working and not self.next_level and not any(self.curr_level)
        )

    def set_next_curr_level(self, other: "TrackedDefaultQueue"):
        self.next_curr_level = other.curr_level

    def set_tracked_queue(self, tracked_queue: "TrackedQueue") -> None:
        self._inferral_expanded = tracked_queue.inferral_expanded
        self._initial_expanded = tracked_queue.initial_expanded
        self.ignore = tracked_queue.ignore

    def _change_level(self) -> None:
        assert not self.staging, "Can't change level is staging is not empty"
        assert not self.working, "Can't change level is working is not empty"
        assert not any(self.curr_level), "Can't change level is curr_level is not empty"
        assert self.next_curr_level is not None, "not set the next curr queue"
        if any(self.next_curr_level):
            # this ensures we only change level when the next curr queue is empty
            # and therefore makes sure we never expand a label with the same strategy
            # twice
            raise StopIteration
        self.next_curr_level[0].extend(
            label
            for label, _ in sorted(self.next_level.items(), key=lambda x: -x[1])
            if label not in self.ignore
        )
        self.next_level: CounterType[int] = Counter()
        self.next_curr_level = self.curr_level
        if not any(self.curr_level):
            raise StopIteration

    def _iter_helper_curr(self) -> Iterator[WorkPacket]:
        assert any(self.curr_level), "The current queue is empty"
        # pylint: disable=stop-iteration-return
        idx, label = next(
            (
                (idx, queue.popleft())
                for idx, queue in enumerate(self.curr_level)
                if queue
            )
        )
        if idx == len(self.expansion_strats):
            self.set_stop_yielding(label)
            return
        yield ParallelWorkPacket(label, idx + 2)
        self.curr_level[idx + 1].append(label)

    def _iter_helper_working(self) -> Iterator[WorkPacket]:
        label = self.working.popleft()
        if self.can_do_inferral(label):
            yield ParallelWorkPacket(label, 0)
            self.set_not_inferrable(label)
        if self.can_do_initial(label):
            yield ParallelWorkPacket(label, 1)
            self.set_not_initial(label)
        self.next_level.update((label,))


class TrackedQueue(CSSQueue):
    def __init__(self, pack: StrategyPack):
        self.pack = pack
        self._level_first_found: Dict[int, int] = {}
        self.inferral_expanded: Set[int] = set()
        self.initial_expanded: Set[int] = set()
        self.ignore: Set[int] = set()
        first_queue = TrackedDefaultQueue(pack)
        first_queue.set_tracked_queue(self)
        self.queues = [first_queue]
        self._all_labels_per_level = defaultdict(int)
        self.add_new_queue()

        super().__init__(pack)

    @property
    def levels_completed(self):
        return len(self.queues) - 2

    def add_new_queue(self) -> None:
        last_queue = self.queues[-1]
        new_queue = TrackedDefaultQueue(self.pack)
        new_queue.set_tracked_queue(self)
        last_queue.set_next_curr_level(new_queue)
        self.queues.append(new_queue)

    def level_first_found(self, label: int) -> int:
        """Return the level that the label was first found at."""
        level = self._level_first_found.get(label)
        if label == -1:
            return -1
        if level is None:
            level = len(self.queues) - 2
            self._level_first_found[label] = level
            self._all_labels_per_level[level] += 1
        return level

    def add_to_level_plus_one(
        self, label: int, parent_label: int, underlying_label: int, initial: bool
    ):
        if label in self.ignore:
            return
        level = min(
            self.level_first_found(parent_label), self.level_first_found(parent_label)
        )
        if not initial:
            level += 1
        if label not in self._level_first_found:
            self._all_labels_per_level[level] += 1
            self._level_first_found[label] = level
        else:
            self._level_first_found[label] = min(self._level_first_found[label], level)
        self.queues[level].add(label)

    def add(self, label: int) -> None:
        if label in self.ignore:
            return
        self.queues[self.level_first_found(label)].add(label)

    def set_not_inferrable(self, label: int) -> None:
        self.queues[self.level_first_found(label)].set_not_inferrable(label)

    def set_verified(self, label: int) -> None:
        self.queues[self.level_first_found(label)].set_verified(label)

    def set_stop_yielding(self, label: int) -> None:
        self.queues[self.level_first_found(label)].set_stop_yielding(label)

    def do_level(self) -> Iterator[WorkPacket]:
        raise NotImplementedError

    def status(self) -> str:
        status = f"Queue status (currently on level {self.levels_completed}):\n"
        table: List[Tuple[str, ...]] = []
        working = ("working",) + tuple(
            f"{len(queue.working):,d}" for queue in self.queues
        )
        table.append(working)
        for idx in range(len(self.pack.expansion_strats)):
            current = (f"current (set {idx+1})",) + tuple(
                f"{len(queue.curr_level[idx]):,d}" for queue in self.queues
            )
            table.append(current)
        nxt = ("next",) + tuple(f"{len(queue.next_level):,d}" for queue in self.queues)
        table.append(nxt)
        all_labels = ("all labels",) + tuple(
            self._all_labels_per_level[level] for level in range(len(self.queues))
        )
        table.append(all_labels)
        status += "    "
        headers = ("Size",) + tuple(f"Queue {idx}" for idx in range(len(self.queues)))
        table = [headers] + table
        table = list(zip(*table))
        headers = table[0]
        table = table[1:]
        colalign = ("left",) + tuple("right" for _ in headers[1:])
        status += (
            tabulate.tabulate(table, headers=headers, colalign=colalign).replace(
                "\n", "\n    "
            )
            + "\n"
        )
        return status

    def __next__(self) -> WorkPacket:
        for idx, queue in enumerate(self.queues):
            if idx == len(self.queues) - 1:
                if queue.is_empty():
                    raise StopIteration
                self.add_new_queue()
            try:
                return next(queue)
            except StopIteration:
                continue


class WorkerParallelQueue(Generic[CombinatorialClassType]):
    def __init__(self, conn: "multiprocessing.connection.Connection") -> None:
        super().__init__()
        self.conn = conn

    def add_to_queue(
        self,
        new_labels: Iterable[
            Tuple[int, int, Tuple[int, ...], bool, bool, bool]
        ],  # parent, underlying, children, inferrable, ignore_parent, initial
    ) -> None:
        self.conn.send(tuple(new_labels))

    def set_not_inferrable(self, label: int) -> None:
        self.conn.send(label)  # do this with an iterable?

    def set_verified(self, labels: Iterable[int]) -> None:
        self.conn.send(tuple(labels))

    def get_work_packet(self):
        self.conn.send(None)
        return self.conn.recv()

    def status(self):
        self.conn.send("status")
        return self.conn.recv()


class ParallelQueue(Generic[CombinatorialClassType]):
    def __init__(self, pack: StrategyPack) -> None:
        super().__init__()
        self.connections: List["multiprocessing.connection.Connection"] = []
        self.queue = TrackedQueue(pack)

    def spawn_worker(self) -> "WorkerParallelQueue[CombinatorialClassType]":
        master_conn, worker_conn = multiprocessing.Pipe()
        self.connections.append(master_conn)
        return WorkerParallelQueue(worker_conn)

    def monitor_connection(self) -> None:
        print("parallel queue", os.getpid())
        waiting: List["multiprocessing.connection.Connection"] = []
        while True:
            while waiting:
                conn = waiting.pop()
                try:
                    conn.send(next(self.queue))
                except StopIteration:
                    waiting.append(conn)
                    break
            ready_connections = multiprocessing.connection.wait(self.connections)

            for conn in ready_connections:

                assert isinstance(conn, multiprocessing.connection.Connection)
                message = conn.recv()
                if isinstance(message, tuple):
                    if all(isinstance(label, int) for label in message):
                        for label in message:
                            self.queue.set_stop_yielding(label)
                    else:
                        for (
                            parent,
                            underlying,
                            children,
                            inferrable,
                            ignore_parent,
                            initial,
                        ) in message:
                            self.add_to_queue(
                                parent,
                                underlying,
                                children,
                                inferrable,
                                ignore_parent,
                                initial,
                            )

                elif isinstance(message, int):
                    self.queue.set_not_inferrable(message)
                elif message is None:
                    try:
                        conn.send(next(self.queue))
                    except StopIteration:
                        waiting.append(conn)
                elif message == "status":
                    conn.send(self.queue.status())
                else:
                    raise ValueError("Unexpected message")

    def add_to_queue(
        self,
        parent: int,
        underlying: int,
        children: Tuple[int, ...],
        inferrable: bool,
        ignore_parent: bool,
        initial: bool,
    ) -> None:
        if ignore_parent:
            self.queue.set_stop_yielding(parent)
        for child in children:
            if not inferrable:
                self.queue.set_not_inferrable(child)
            self.queue.add_to_level_plus_one(child, parent, underlying, initial)
