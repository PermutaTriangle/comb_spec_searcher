"""
A queue of objects.
"""
from queue import Queue
import sys

class ObjectQueue(object):
    """
    The Queue determines the order that objects are expanded by the tilescope.
    """
    def __init__(self):
        self.working = Queue()
        self.curr_level = Queue()
        self.next_level = Queue()
        self.levels_completed = 0

    def add_to_working(self, obj):
        self.working.put(obj)

    def add_to_next(self, obj):
        self.next_level.put(obj)

    def add_to_curr(self, obj):
        self.curr_level.put(obj)

    def next(self):
        if not self.working.empty():
            return self.working.get()
        elif not self.curr_level.empty():
            return self.curr_level.get()
        else:
            if self.next_level.empty():
                print("No more objects to expand!", file=sys.stderr)
                return None
            self.levels_completed += 1
            # print("++++Changing next to curr.++++",self.levels_completed, file=sys.stderr)
            self.curr_level = self.next_level
            self.next_level = Queue()
            return self.next()

    def do_level(self, cap=None):
        # if cap, return first "cap" many objects.
        if cap is not None:
            if isinstance(cap, int):
                i = 0
            else:
                raise TypeError("The cap must be an integer.")

            while i < cap:
                if not self.working.empty():
                    yield self.working.get()
                    i += 1
                elif not self.curr_level.empty():
                    yield self.curr_level.get()
                    i += 1
                else:
                    if self.next_level.empty():
                        print("No more objects to expand!", file=sys.stderr)
                        i = cap

                    self.levels_completed += 1
                    self.curr_level = self.next_level
                    self.next_level = Queue()

        # if no cap, then do exactly one level.
        else:
            while not self.working.empty() or not self.curr_level.empty():
                while not self.working.empty():
                    yield self.working.get()
                if not self.curr_level.empty():
                    yield self.curr_level.get()
            self.levels_completed += 1
            self.curr_level = self.next_level
            self.next_level = Queue()
