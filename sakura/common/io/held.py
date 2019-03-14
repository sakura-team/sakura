import itertools, gc
from random import getrandbits
from sakura.common.io.debug import print_debug
from sakura.common.io.proxy import Proxy

# uniquely identify this process among all sakura processes
# in the network (os.getpid() might generate duplicate values
# since processes are running on different machines).
ORIGIN_ID = getrandbits(32)

class HeldObjectsStore:
    instance = None
    @staticmethod
    def get():
        if HeldObjectsStore.instance is None:
            HeldObjectsStore.instance = HeldObjectsStore()
        return HeldObjectsStore.instance
    def __init__(self):
        self.__objects_per_id__ = {}
        self.__ids_per_object__ = {}
        self.__refcount_per_id__ = {}
        self.__held_ids__ = itertools.count()
    def hold(self, obj):
        # hold obj locally then return id and origin.
        print_debug('held:', obj)
        # check if this object is already held
        held_id = self.__ids_per_object__.get(obj, None)
        if held_id is None:
            held_id = self.__held_ids__.__next__()
            self.__objects_per_id__[held_id] = obj
            self.__ids_per_object__[obj] = held_id
            self.__refcount_per_id__[held_id] = 1
        else:
            self.__refcount_per_id__[held_id] += 1
        origin = ORIGIN_ID, held_id
        if isinstance(obj, Proxy):
            if obj.__internals.get_origin() is not None:
                origin = obj.__internals.get_origin()
        # return held_info
        return (held_id,) + origin
    def __getitem__(self, held_id):
        return self.__objects_per_id__[held_id]
    def __delitem__(self, held_id):
        if self.__refcount_per_id__[held_id] == 1:
            obj = self.__objects_per_id__[held_id]
            print_debug('released:', obj)
            del self.__objects_per_id__[held_id]
            del self.__ids_per_object__[obj]
            del self.__refcount_per_id__[held_id]
            gc.collect()
        else:
            self.__refcount_per_id__[held_id] -= 1
    @classmethod
    def get_proxy(cls, api_endpoint, held_info):
        remote_held_id, origin = held_info[0], held_info[1:]
        origin_id, origin_held_id = origin
        if origin_id == ORIGIN_ID:
            # the object is actually a local object!
            # (may occur in case of several bounces)
            # we can short out those bounces and use the object directly.
            # first, retrieve a reference to this object
            obj = cls.get()[origin_held_id]
            print_debug('shortcut:', obj, 'is actually local.')
            # tell the remote end it can release it
            api_endpoint.delete_remotely_held(remote_held_id)
            # return the object
            return obj
        remote_held_path = ('held_objects', (remote_held_id,))
        return Proxy(api_endpoint, remote_held_path, origin,
                delete_callback=lambda : api_endpoint.delete_remotely_held(remote_held_id))
