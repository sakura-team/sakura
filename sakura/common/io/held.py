import itertools, gc
from sakura.common.io.debug import print_debug

class HeldObjectsStore:
    instance = None
    @staticmethod
    def get():
        if HeldObjectsStore.instance is None:
            HeldObjectsStore.instance = HeldObjectsStore()
        return HeldObjectsStore.instance
    def __init__(self):
        self.__objects__ = {}
        self.__held_ids__ = itertools.count()
    def hold(self, obj):
        # hold obj locally and return its id.
        print_debug('held:', obj)
        held_id = self.__held_ids__.__next__()
        self.__objects__[held_id] = obj
        return held_id
    def __getitem__(self, held_id):
        return self.__objects__[held_id]
    def __delitem__(self, held_id):
        del self.__objects__[held_id]
        gc.collect()
