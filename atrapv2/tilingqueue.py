"""
A queue of tilings.
"""
from queue import Queue
import tqdm

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

    def next(self):
        if not self.working.empty():
            return self.working.get()
        elif not self.curr_level.empty():
            return self.curr_level.get()
        else:
            if self.next_level.empty():
                print("No more tilings to expand!")
                return None
            self.levels_completed += 1
            self.curr_level = self.next_level
            self.next_level = Queue()
            print("Starting level " + str(self.levels_completed + 1))
            return self.next()

    def do_level(self, cap=None):
        # if cap, return first "cap" many tilings.
        if cap is not None:
            # x = tqdm.tqdm(range(cap))
            if isinstance(cap, int):
                i = 0
            else:
                raise TypeError("The cap must be an integer.")

            while i < cap:
                if not self.working.empty():
                    yield self.working.get()
                    i += 1
                    # x.update()
                elif not self.curr_level.empty():
                    yield self.curr_level.get()
                    i += 1
                    # x.update()
                else:
                    if self.next_level.empty():
                        print("No more tilings to expand!")
                        # x.update(cap - i)
                        i = cap

                    self.levels_completed += 1
                    self.curr_level = self.next_level
                    self.next_level = Queue()
                    print("Starting level " + str(self.levels_completed + 1))

        # if no cap, then do exactly one level.
        else:
            # x = tqdm.tqdm(self.curr_level.queue)
            while not self.working.empty() or not self.curr_level.empty():
                while not self.working.empty():
                    yield self.working.get()
                if not self.curr_level.empty():
                    yield self.curr_level.get()
                    # x.update()
            self.levels_completed += 1
            self.curr_level = self.next_level
            self.next_level = Queue()
            print("Starting level " + str(self.levels_completed + 1))
