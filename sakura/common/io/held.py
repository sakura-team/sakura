import itertools, gc
from os import getpid
from sakura.common.io.debug import print_debug
from sakura.common.io.proxy import Proxy

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
        # hold obj locally then return id and origin.
        print_debug('held:', obj)
        held_id = self.__held_ids__.__next__()
        self.__objects__[held_id] = obj
        origin = getpid(), held_id
        if isinstance(obj, Proxy):
            if obj.__internals.get_origin() is not None:
                origin = obj.__internals.get_origin()
        # return held_info
        return (held_id,) + origin
    def __getitem__(self, held_id):
        return self.__objects__[held_id]
    def __delitem__(self, held_id):
        print_debug('released:', self.__objects__[held_id])
        del self.__objects__[held_id]
        gc.collect()
    @classmethod
    def get_proxy(cls, api_endpoint, held_info):
        remote_held_id, origin = held_info[0], held_info[1:]
        origin_pid, origin_held_id = origin
        if origin_pid == getpid():
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
