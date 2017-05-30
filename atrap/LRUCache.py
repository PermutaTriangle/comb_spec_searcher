"""THIS IMPLEMENTATION IS FROM https://www.kunxi.org/blog/2014/05/lru-cache-in-python/."""


import collections


class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = collections.OrderedDict()

    def get(self, key):
        try:
            value = self.cache.pop(key)
            self.cache[key] = value
            return value
        except KeyError:
            return None

    def pop(self, key):
        return self.cache.pop(key)

    def set(self, key, value):
        try:
            self.cache.pop(key)
        except KeyError:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
        self.cache[key] = value

    def __len__(self):
        return len(self.cache)

    def __contains__(self, key):
        return key in self.cache
