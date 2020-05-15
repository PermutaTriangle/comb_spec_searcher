"""
A queue of labels.
"""
import abc
from collections import Counter, deque
from typing import Counter as CounterType
from typing import Deque, Iterator, List, NamedTuple, Set, Tuple

from .strategies.strategy import CSSstrategy
from .strategies.strategy_pack import StrategyPack


class WorkPacket(NamedTuple):
    label: int
    strategies: Tuple[CSSstrategy, ...]
    inferral: bool


class CSSQueue(abc.ABC):
    """
    A queue of labels.
    """

    def __init__(self, pack: StrategyPack):
        self.inferral_strategies = tuple(pack.inferral_strats)
        self.initial_strategies = tuple(pack.initial_strats)
        self.expansion_strats = tuple(tuple(x) for x in pack.expansion_strats)

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
        self.curr_level: Deque[int] = deque()
        self.inferral_expanded: Set[int] = set()
        self.initial_expanded: Set[int] = set()
        self.expansion_expanded: List[Set[int]] = [
            set() for _ in range(len(self.expansion_strats))
        ]
        self.ignore: Set[int] = set()
        self.inferral_ignore: Set[int] = set()
        self.queue_sizes: List[int] = []
        self.staging: Deque[WorkPacket] = deque([])

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
        if label not in self.ignore:
            self.inferral_expanded.add(label)

    def set_stop_yielding(self, label: int) -> None:
        self._add_to_ignore(label)

    def _add_to_ignore(self, label: int) -> None:
        self.ignore.add(label)
        # can remove it elsewhere to keep sets "small"
        self.inferral_ignore.discard(label)
        self.inferral_expanded.discard(label)
        self.initial_expanded.discard(label)
        for s in self.expansion_expanded:
            s.discard(label)
        self.next_level.pop(label, None)

    def can_do_inferral(self, label: int) -> bool:
        """Return true if inferral strategies can be applied."""
        return bool(self.inferral_strategies and label not in self.inferral_ignore)

    def can_do_initial(self, label: int) -> bool:
        """Return true if initial strategies can be applied."""
        return bool(self.initial_strategies and label not in self.initial_expanded)

    def can_do_expansion(self, label: int, idx: int) -> bool:
        """Return true if expansion strategies can be applied."""
        return label not in self.expansion_expanded[idx]

    def _populate_staging(self) -> None:
        """
        Populate the staging queue that is used by next to return WorkPacket.
        """
        if not self.staging and self.working:
            self.staging.extend(self._iter_helper_working())
        if not self.staging:
            if not self.curr_level:
                self._change_level()
            if self.curr_level:
                self.staging.extend(self._iter_helper_curr())
        if not self.staging:
            raise StopIteration("No more classes to expand")

    def _change_level(self) -> None:
        self.curr_level = deque(
            label
            for label, _ in sorted(self.next_level.items(), key=lambda x: -x[1])
            if self.expansion_strats and self.can_do_expansion(label, 0)
        )
        self.queue_sizes.append(len(self.curr_level))
        self.next_level = Counter()

    def _iter_helper_curr(self) -> Iterator[WorkPacket]:
        label = self.curr_level.popleft()
        for idx, strats in enumerate(self.expansion_strats):
            if self.can_do_expansion(label, idx):
                for strat in strats:
                    yield WorkPacket(label, (strat,), False)
                self.expansion_expanded[idx].add(label)
                if idx + 1 < len(self.expansion_strats) and (
                    self.can_do_expansion(label, idx + 1)
                ):
                    self.curr_level.append(label)
                break
        else:
            # finished applying all strategies to this label, ignore from now on
            self._add_to_ignore(label)

    def _iter_helper_working(self) -> Iterator[WorkPacket]:
        label = self.working.popleft()
        if self.can_do_inferral(label):
            yield WorkPacket(label, self.inferral_strategies, True)
            self.inferral_expanded.add(label)
        if self.can_do_initial(label):
            for strat in self.initial_strategies:
                yield WorkPacket(label, (strat,), False)
            self.initial_expanded.add(label)
        self.next_level.update((label,))

    def __next__(self) -> WorkPacket:
        while self.staging:
            wp = self.staging.popleft()
            if wp.label not in self.ignore:
                return wp
        self._populate_staging()
        return next(self)

    def do_level(self) -> Iterator[WorkPacket]:
        """
        An iterator of all combinatorial classes in the current queue.

        Will swap next queue to current after iteration.
        """
        curr_level = self.levels_completed
        while curr_level == self.levels_completed:
            try:
                yield next(self)
            except StopIteration:
                return

    def status(self) -> str:
        status = "Queue status:\n"
        status += "\tCurrently on 'level' {}\n".format(self.levels_completed)
        status += "\tThe size of the working queue is {}\n".format(len(self.working))
        status += "\tThe size of the current queue is {}\n".format(len(self.curr_level))
        status += "\tThe size of the next queue is {}\n".format(len(self.next_level))
        status += "\tThe number of times added to the next queue is {}\n".format(
            sum(self.next_level.values())
        )
        status += "\tThe size of the current queues at each level: {}".format(
            ", ".join(str(i) for i in self.queue_sizes)
        )
        return status
