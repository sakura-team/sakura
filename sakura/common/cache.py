import bisect, weakref
from time import time
from sakura.common.actor import actor

# This is the minimum cache resilience value.
CACHE_MIN_DELAY = 5.0   # seconds
DEBUG = False

@actor
class Cache:
    instances = weakref.WeakSet()
    def __init__(self, size = None):
        self.size = size
        self.per_key = {}   # <key> -> (<expiry_time, <item>)
        self.per_date = []  # list of (<expiry_time, <key>)
        Cache.instances.add(self)
    def resize(self, size):
        self.size = size
    def in_cache(self, key, check_expiry=False):
        if key not in self.per_key:
            return False
        if not check_expiry:
            return True
        expiry_time, item = self.per_key[key]
        if expiry_time < time():    # expired!
            return False
        return True
    def get(self, key, check_expiry=False, default=None):
        if not self.in_cache(key, check_expiry):
            return default
        return self.per_key[key][1]
    def forget(self, key):
        if key in self.per_key:
            if DEBUG:
                print(id(self), time(), 'cache.forget', key)
            expiry_time, item = self.per_key[key]
            self.per_date.remove((expiry_time, key))
            del self.per_key[key]
    def pop(self, key, check_expiry=False, default=None):
        result = self.get(key, check_expiry, default)
        self.forget(key)
        return result
    def save(self, key, item, expiry_delay):
        # ensure we keep in cache for at least CACHE_MIN_DELAY
        expiry_time = time() + max(CACHE_MIN_DELAY, expiry_delay)
        if DEBUG:
            print(id(self), time(), 'cache.save', key, item, expiry_time)
        # remove any previous info linked to key
        self.forget(key)
        while self.size is not None and len(self.per_date) >= self.size:
            # cache is full, drop oldest entry
            oldest_expiry_time, oldest_key = self.per_date[0]
            assert oldest_key in self.per_key, \
                        '********* cache coherency issue.'
            del self.per_key[oldest_key]
            self.per_date = self.per_date[1:]
        # record entry for this item
        self.per_key[key] = (expiry_time, item)
        # update item position in self.per_date
        bisect.insort(self.per_date, (expiry_time, key))
        assert len(self.per_date) == len(self.per_key), \
                        '********* cache len issue.'
    def cleanup(self):
        if DEBUG:
            if len(self.per_date) > 0 and self.per_date[0][0] < time():
                print(id(self), time(), 'cache.cleanup')
        while len(self.per_date) > 0 and self.per_date[0][0] < time():
            self.cleanup_oldest()
    def cleanup_oldest(self):
        expiry_time, key = self.per_date[0]
        self.per_date = self.per_date[1:]
        del self.per_key[key]
    def __del__(self):
        while len(self.per_date) > 0:
            self.cleanup_oldest()
    @staticmethod
    def cleanup_all():
        for cache in Cache.instances:
            cache.cleanup()
    @staticmethod
    def plan_cleanup(planner):
        planner.plan(CACHE_MIN_DELAY/2, Cache.cleanup_all)

result_cache = Cache()
def cache_result(delay):
    """
    cache_result is a decorator you can use like this:

    @cache_result(10)
    def long_function(i):
       [...long computation...]
       return <res>

    If long_function is called repeatedly with the same
    arguments and within a 10s time window, the result
    will be found in cache and returned immediately,
    instead of executing the function again.
    This can also be used on class methods.
    """
    def wrapper(func):
        def cached_func(*args, **kwargs):
            key = (func, args, tuple(kwargs.items()))
            # check if we have the result of the same call in cache
            in_cache = result_cache.in_cache(key, check_expiry=True)
            # if yes, return it
            if in_cache:
                return result_cache.get(key)
            # otherwise, call func
            result = func(*args, **kwargs)
            # save for next time
            result_cache.save(key, result, delay)
            # return result of this call
            return result
        return cached_func
    return wrapper

def test(delay):
    class C:
        @cache_result(delay)
        def print(self, i):
            print('working', self, i)
    return C
