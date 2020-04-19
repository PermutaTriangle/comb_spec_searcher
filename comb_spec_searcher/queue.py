"""
A queue of labels.
"""
from collections import deque
from typing import Callable, Iterator, List, Tuple, TYPE_CHECKING
import abc


if TYPE_CHECKING:
    from comb_spec_searcher import CombinatorialClass, StrategyGenerator, StrategyPack


class CSSQueue(abc.ABC):
    """
    A queue of labels.
    """

    def __init__(self, pack: "StrategyPack"):
        self.strategy_pack = pack

    @property
    def initial_strategies(self) -> List["StrategyGenerator"]:
        """The initial strategies from the strategy pack."""
        return self.strategy_pack.initial_strats

    @property
    def expansion_strats(self) -> List["StrategyGenerator"]:
        """The expansion strategies from the strategy pack."""
        return self.strategy_pack.expansion_strats

    @property
    def inferral_strategies(self) -> List["StrategyGenerator"]:
        """The inferral strategies from the strategy pack."""
        return self.strategy_pack.inferral_strats

    @property
    def symmetries(
        self,
    ) -> List[Callable[["CombinatorialClass"], "CombinatorialClass"]]:
        """The symmetries functions for the strategy pack."""
        return self.strategy_pack.symmetries

    @abc.abstractmethod
    def add(self, label) -> None:
        """Add a label to the queue."""

    @abc.abstractmethod
    def set_not_inferrable(self, label) -> None:
        """You should avoid yielding label with an inferral strategy in future."""

    @abc.abstractmethod
    def set_verified(self, label) -> None:
        """Label was verified, how should the queue react?"""

    @abc.abstractmethod
    def set_stop_yielding(self, label) -> None:
        """You should stop yielding label. CSS indicated that this label should
        no longer be yielded, e.g., expanding another symmetry or expanding
        only children"""

    @abc.abstractmethod
    def do_level(self) -> Iterator[Tuple[int, List["StrategyGenerator"], bool]]:
        """Return a 'level'. The definition of level can be chosen by the user,
        but it determines the functionality of the do_level method in CSS."""

    @abc.abstractmethod
    def status(self) -> str:
        """Return a string that indicates that current status of the queue."""

    @abc.abstractmethod
    def __iter__(self) -> Iterator[Tuple[int, List["StrategyGenerator"], bool]]:
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


class DefaultQueue(CSSQueue):
    """
    The default queue used by CSS.
    """

    def __init__(self, pack: "StrategyPack"):
        self.working = deque()  # add to this queue for inferral and initial strategies
        self.next_level = (
            deque()
        )  # after initial, add to this one for expansion strats on the next level
        self.curr_level = (
            deque()
        )  # add back to curr level if not expanded by all expansion strats
        self.initial_expandable = set()
        self.inferral_expandable = set()
        self.expansion_expanded = [set() for _ in range(len(self.strategy_generators))]
        self.ignore = set()  # never try expand
        self.inferral_ignore = set()  # never try inferral expand
        self.levels_completed = 0
        super().__init__(pack)

    def add(self, label: int) -> None:
        if self.can_do_inferral(label) or self.can_do_initial(label):
            self.working.append(label)
        elif label not in self.ignore:
            self.next_level.append(label)

    def set_not_inferrable(self, label: int) -> None:
        if label not in self.ignore():
            self.ignore_inferral.add(label)

    def set_stop_yielding(self, label: int) -> None:
        self._add_to_ignore(label)

    def _add_to_ignore(self, label: int) -> None:
        self.ignore.add(label)
        # can remove it elsewhere to keep sets "small"
        self.initial_expandable.remove(label)
        self.inferral_expandable.remove(label)
        for s in self.expansion_expanded:
            s.remove(label)
        self.inferral_ignore.remove(label)

    def can_do_inferral(self, label: int) -> bool:
        """Return true if inferral strategies can be applied."""
        return label not in self.ignore and label not in self.inferral_ignore

    def can_do_initial(self, label: int) -> bool:
        """Return true if initial strategies can be applied."""
        return label not in self.ignore and label not in self.initial_expanded

    def can_do_expansion(self, label: int, idx: int) -> bool:
        """Return true if expansion strategies can be applied."""
        return label not in self.ignore and label not in self.expansion_strats[idx]

    def __iter__(self) -> Iterator[Tuple[int, List["StrategyGenerator"], bool]]:
        """
        Yield the next combinatorial class in current queue.

        If current queue becomes empty will change next queue to current and
        return first combinatorial class. Return None if no combinatorial
        classes to expand.
        """
        while True:
            if self.working:
                label = self.working.popleft()

                if self.can_do_inferral(label):
                    yield label, self.inferral_strategies, True
                    self.inferral_expanded.add(label)

                elif self.can_do_initial(label):
                    yield label, self.initial_strategies, False
                    self.initial_expanded.add(label)

            elif self.curr_level:
                label = self.curr_level.popleft()
                for idx, strats in self.expansion_strats:
                    if self.can_do_expansion(label, idx):
                        yield label, strats, False
                        self.expansion_strats[idx].add(label)
                        self.curr_level.append(label)
                        break
                else:
                    # finished applying all strategies to this label, ignore from now on
                    self._add_to_ignore(label)
            else:
                if not self.next_level:
                    return None
                self.levels_completed += 1
                self.curr_level = self.next_level
                self.ignore = set()
                self.next_level = deque()
                continue

    def do_level(self) -> Iterator[Tuple[int, List["StrategyGenerator"], bool]]:
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
