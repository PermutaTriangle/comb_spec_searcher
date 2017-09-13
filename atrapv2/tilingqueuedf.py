"""
A queue of tilings.
"""
from queue import Queue
import tqdm
import sys

class TilingQueueDF(object):
    """
    The Queue determines the order that tilings are expanded by the tilescope.
    """
    def __init__(self, rules_dict=None, root=None, equivalent_set=None, is_verified=None):
        self.working = Queue()
        self.curr_level = Queue()
        self.next_level = Queue()
        self.levels_completed = 0
        if rules_dict is None:
            raise TypeError("TilingQueueDF requires a rules dict.")
        if root is None:
            raise TypeError("Root must be given.")
        if equivalent_set is None:
            raise TypeError("TilingQueueDF requires a function that returns equivalent set.")
        self.equivalent_set = equivalent_set
        self.rules_dict = rules_dict
        self.is_verified = is_verified
        self.root = root
        self.iter = None

    def add_to_working(self, tiling):
        pass

    def add_to_next(self, tiling):
        pass

    def add_to_curr(self, tiling):
        pass

    def do_level(self):
        self.iter = self.do_level_iter(self.root, 0, self.levels_completed + 1)
        for t in self.iter:
            yield t

    def next(self):
        if self.iter is None:
            self.iter = self.do_level_iter(self.root, 0, self.levels_completed + 1)
            return self.root
        try:
            return next(self.iter)
        except StopIteration:
            print("Finished depth", self.levels_completed)
            self.levels_completed += 1
            self.iter = self.do_level_iter(self.root, 0, self.levels_completed + 1)
            try:
                return next(self.iter)
            except StopIteration:
                print("No more tilings to expand!", file=sys.stderr)
                return None


    def do_level_iter(self, root, current_depth, max_depth):
        if current_depth < max_depth:
            for eq_label in self.equivalent_set(root):
                yield eq_label
                rules = self.rules_dict[eq_label]
                # print(rules)
                for rule in rules:
                    # if self.is_verified is not None:
                    #     previous = None
                    for child_label in rule:
                        # if self.is_verified is not None:
                        #     if previous is None:
                        #         previous = child_label
                        #     else:
                        #         if not self.is_verified(previous):
                        #             break
                        for label in self.do_level_iter(child_label, current_depth + 1, max_depth):
                            yield label
