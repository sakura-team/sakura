from sakura.common.io.tools import Internals

class Proxy:
    def __init__(self, manager, path=(), origin=None, delete_callback=None):
        self.__internals = Internals(
            manager = manager,
            path = path,
            origin = origin,
            delete_callback = delete_callback,
            proxy_at = lambda new_path: Proxy(manager, new_path, origin),
            call_special = lambda func_name: manager.func_call(path + (func_name,)),
            get_origin = lambda : origin
        )
    # attr access
    def __getattr__(self, attr):
        if attr.endswith('__internals'):
            return self.__internals     # workaround name mangling
        path = self.__internals.path + (attr,)
        if attr.startswith('_'):
            return self.__internals.manager.attr_call(path)
        else:
            return self.__internals.proxy_at(path)
    # subscript access
    def __getitem__(self, index):
        path = self.__internals.path + ((index,),)
        return self.__internals.proxy_at(path)
    # function call
    def __call__(self, *args, **kwargs):
        return self.__internals.manager.func_call(self.__internals.path, args, kwargs)
    # special methods
    def __str__(self):
        return 'REMOTE(' + self.__internals.call_special('__str__') + ')'
    def __repr__(self):
        return 'REMOTE(' + self.__internals.call_special('__repr__') + ')'
    def __iter__(self):
        return self.__internals.call_special('__iter__')
    def __next__(self):
        return self.__internals.call_special('__next__')
    def __len__(self):
        return self.__internals.call_special('__len__')
    # optional deletion callback management
    def __del__(self):
        if self.__internals.delete_callback is not None:
            self.__internals.delete_callback()
    def __eq__(self, other):
        if not isinstance(other, Proxy):
            return False
        return  self.__internals.path == other.__internals.path and \
                self.__internals.origin == other.__internals.origin
    def __hash__(self):
        return hash((self.__internals.path, self.__internals.origin))
