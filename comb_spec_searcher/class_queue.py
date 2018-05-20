"""
A queue of labels.
"""
from collections import deque

import sys


class ClassQueue(object):
    """
    The Queue determines the order that classes are expanded.
    """
    def __init__(self):
        """Initialise a ClassQueue."""
        self.working = deque()
        self.curr_level = deque()
        self.next_level = deque()
        self.levels_completed = 0
        self.ignore = set()

    def to_dict(self):
        """Return dictionary object of self."""
        return {
            'working': list(self.working),
            'curr_level': list(self.curr_level),
            'next_level': list(self.next_level),
            'levels_completed': self.levels_completed,
            'ignore': self.ignore,
        }

    @classmethod
    def from_dict(cls, dict):
        """Return ClassQueue from dictionary object."""
        queue = cls()
        queue.working = deque(dict['working'])
        queue.curr_level = deque(dict['curr_level'])
        queue.next_level = deque(dict['next_level'])
        queue.levels_completed = dict['levels_completed']
        queue.ignore = dict['ignore']
        return queue

    def add_to_working(self, comb_class):
        """Add combinatorial class to working queue."""
        self.working.append(comb_class)

    def add_to_next(self, comb_class):
        """Add combinatorial class to next queue."""
        self.next_level.append(comb_class)

    def add_to_curr(self, comb_class):
        """Add combinatorial class to current queue."""
        self.curr_level.append(comb_class)

    def next(self):
        """
        Return next combinatorial class in current queue.

        If current queue becomes empty will change next queue to current and
        return first combinatorial class. Return None if no combinatorial
        classes to expand.
        """
        if self.working:
            n = self.working.popleft()
        elif self.curr_level:
            n = self.curr_level.popleft()
        else:
            if not self.next_level:
                return None
            self.levels_completed += 1
            self.curr_level = self.next_level
            self.ignore = set()
            self.next_level = deque()
            n = self.next()
        if n in self.ignore:
            return self.next()
        else:
            return n

    def do_level(self):
        """
        An iterator of all combinatorial classes in the current queue.

        Will swap next queue to current after iteration. Yields None if no
        combinatorial class to expand.
        """
        curr_level = self.levels_completed
        while curr_level == self.levels_completed:
            n = self.next()
            yield n
            if n is None:
                return None
