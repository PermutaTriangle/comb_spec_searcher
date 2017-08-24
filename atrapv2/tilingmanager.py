'''
A manager for tilings. Contains information about if tilings have been expanded,
found by symmetries etc. It gives each tiling a unique label.
'''
from grids import Tiling

class Info(object):
    '''
    Information about a tiling.
    '''
    def __init__(self, tiling, label, expanded=False, expandable=False):
        self.tiling = tiling
        self.label = label
        self.expanded = expanded
        self.expandable = expandable

class TilingManager(object):
    '''
    A manager for tilings.
    '''
    def __init__(self):
        self.tiling_to_info = {}
        self.label_to_info = {}

    def get_info(self, key):
        if isinstance(key, Tiling):
            info = self.tiling_to_info.get(tiling)
        elif isinstance(key, int):
            info = self.label_to_info.get(tiling)
        if info is None:
            label = len(self.tiling_to_info)
            info = Info(tiling, len(self.tiling_to_info))
            self.tiling_to_info[tiling] = info
            self.label_to_info[label] = info
        return info

    def get_tiling(self, key):
        info = self.get_info(key)
        return info.tiling

    def get_label(self,key):
        info = self.get_info(key)
        return info.label

    def is_expanded(self, key):
        info = self.get_info(key):
        return info.expanded

    def set_expanded(self, key, expanded=True):
        info = self.get_info(key)
        self.tiling_to_info[info.tilng].expanded = expanded
        assert self.tiling_to_info[info.tiling].expanded == self.label_to_info[info.label].expanded
        # Do I need this line, testing with assert
        self.label_to_info[info.label].expanded = expanded

    def is_expandable(self,key):
        info = self.get_info(key)
        return info.expandable

    def set_expandable(self, key, expandable=True):
        info = self.get_info(key)
        self.tiling_to_info[info.tiling].expandable = expandable
        assert self.tiling_to_info[info.tiling].expandable == self.label_to_info[info.label].expandable
        # Do I need this line, testing with assert
        self.label_to_info[info.label].expandable = expandable
