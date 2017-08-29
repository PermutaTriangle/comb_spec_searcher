"""
A queue of tilings.
"""
from queue import Queue

class TilingQueue(object):
    """
    The Queue determines the order that tilings are expanded by the tilescope.
    """
    def __init__(self):
        self.working = Queue()
        self.curr_level = Queue()
        self.next_level = Queue()
        self.levels_completed = 0

    def add_to_working(self, tiling):
        self.working.put(tiling)

    def add_to_next(self, tiling):
        self.next_level.put(tiling)

    def do_level(self, cap=None):
        # if cap, return first "cap" many tilings.
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
                        print("No more tilings to expand!")
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
