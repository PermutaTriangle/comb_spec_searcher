"""THIS IMPLEMENTATION IS FROM https://www.kunxi.org/blog/2014/05/lru-cache-in-python/."""


import collections


class LRUCache:
    def __init__(self, capacity, compress=False, obj_type=None):
        self.capacity = capacity
        self.cache = collections.OrderedDict()
        self.compress = compress
        if self.compress:
            if obj_type is None:
                raise ValueError("Need to declared type for decompression")
            self.obj_type = obj_type

    def get(self, key):
        if self.compress:
            key = key.compress()
        try:
            value = self.cache.pop(key)
            self.cache[key] = value
            if self.compress:
                return self.obj_type.decompress(value)
            return value
        except KeyError:
            return None

    def pop(self, key):
        return self.cache.pop(key)

    def set(self, key, value):
        if self.compress:
            key = key.compress()
            value = value.compress()
        try:
            self.cache.pop(key)
        except KeyError:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
        self.cache[key] = value

    def __len__(self):
        return len(self.cache)

    def __contains__(self, key):
        if self.compress:
            key = key.compress()
        return key in self.cache
