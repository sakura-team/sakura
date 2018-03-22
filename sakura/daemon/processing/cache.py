import bisect, weakref
from time import time

# This is the minimum cache resilience value.
CACHE_MIN_DELAY = 5.0   # seconds

class Cache:
    instances = weakref.WeakSet()
    def __init__(self, size):
        self.size = size
        self.per_item = {}
        self.per_key = {}
        self.per_date = []
        Cache.instances.add(self)
    def get(self, key):
        if key in self.per_key:
            #print('cache.get match')
            return self.per_key[key]
        return None, None
    def forget(self, item):
        #print(time(), 'cache.forget', item)
        expiry_time, key = self.per_item[item]
        self.per_date.remove((expiry_time, item))
        del self.per_item[item]
        del self.per_key[key]
    def save(self, item, expiry_delay, key, context_info=None):
        # ensure we keep in cache for at least CACHE_MIN_DELAY
        expiry_time = time() + max(CACHE_MIN_DELAY, expiry_delay)
        #print(time(), 'cache.save', item, expiry_time, key)
        if item in self.per_item:
            # remove previous key about item
            old_expiry_time, old_key = self.per_item[item]
            del self.per_key[old_key]
            # remove item from per_date, it
            # will be appended below
            self.per_date.remove((old_expiry_time, item))
        if key in self.per_key:
            # remove previous item linked to key
            old_item, old_ctx_info = self.per_key[key]
            old_expiry_time, old_key = self.per_item[old_item]
            del self.per_item[old_item]
            self.per_date.remove((old_expiry_time, old_item))
        if len(self.per_date) == self.size:
            # cache is full, drop oldest entry
            oldest_expiry_time, oldest_item = self.per_date[0]
            oldest_expiry_time, oldest_key = self.per_item[oldest_item]
            assert oldest_key in self.per_key, \
                        '********* cache coherency issue.'
            del self.per_item[oldest_item]
            del self.per_key[oldest_key]
            self.per_date = self.per_date[1:]
        # record entry for this item
        self.per_item[item] = (expiry_time, key)
        self.per_key[key] = (item, context_info)
        # update item position in self.per_date
        bisect.insort(self.per_date, (expiry_time, item))
        assert len(self.per_item) == len(self.per_key), \
                        '********* cache len issue.'
    def cleanup(self):
        #print(time(), 'cache.cleanup')
        while len(self.per_date) > 0 and self.per_date[0][0] < time():
            expiry_time, item = self.per_date[0]
            self.per_date = self.per_date[1:]
            expiry_time, key = self.per_item[item]
            del self.per_item[item]
            del self.per_key[key]
    @staticmethod
    def cleanup_all():
        for cache in Cache.instances:
            cache.cleanup()
    @staticmethod
    def plan_cleanup(planner):
        planner.plan(CACHE_MIN_DELAY/2, Cache.cleanup_all)
