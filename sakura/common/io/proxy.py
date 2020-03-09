from sakura.common.io.tools import Internals

# note about Proxy.__internals.proxy_extend() function:
# we keep a link to our parent, otherwise it might be garbage collected
# which can cause problems in some cases, such as:
# (op_dir / 'operator.py').exists()
# here, after accessing attribute 'exists' and returning a new proxy,
# parent (result of '/' expression) would be garbage-collected, then
# trying to run its exists() function would cause an exception.
class Proxy:
    def __init__(self, manager, path=(), origin=None, delete_callback=None, parent=None):
        def proxy_extend(path_extension, **kwargs):
            new_path = path + path_extension
            if origin is None:
                new_origin = None
            else:
                new_origin = origin[0], origin[1] + path_extension
            return Proxy(manager, new_path, new_origin, parent=self)
        self.__internals = Internals(
            manager = manager,
            path = path,
            origin = origin,
            delete_callback = delete_callback,
            proxy_extend = proxy_extend,
            call_special = lambda func_name, *args, **kwargs: manager.func_call(path + (func_name,), args, kwargs),
            get_origin = lambda : origin,
            parent = parent
        )
    # attr access
    def __getattr__(self, attr):
        if attr.endswith('__internals'):
            return self.__internals     # workaround name mangling
        if attr.startswith('_'):
            return self.__internals.manager.attr_call(self.__internals.path + (attr,))
        else:
            return self.__internals.proxy_extend((attr,))
    # subscript access
    def __getitem__(self, index):
        return self.__internals.proxy_extend(((index,),))
    # function call
    def __call__(self, *args, **kwargs):
        return self.__internals.manager.func_call(self.__internals.path, args, kwargs)
    # special methods
    def __str__(self):
        return self.__internals.call_special('__str__')
    def __repr__(self):
        return 'REMOTE(' + self.__internals.call_special('__repr__') + ')'
    def __iter__(self):
        return self.__internals.call_special('__iter__')
    def __next__(self):
        return self.__internals.call_special('__next__')
    def __len__(self):
        return self.__internals.call_special('__len__')
    def __truediv__(self, other):   # handle '/' operator for remote pathlib.Path objects
        return self.__internals.call_special('__truediv__', other)
    def __lt__(self, val):
        return self.__internals.call_special('__lt__', val)
    def __le__(self, val):
        return self.__internals.call_special('__le__', val)
    def __gt__(self, val):
        return self.__internals.call_special('__gt__', val)
    def __ge__(self, val):
        return self.__internals.call_special('__ge__', val)
    def __and__(self, other):       # this is the bitwise and ("&"), logical "and" cannot be redefined
        return self.__internals.call_special('__and__', other)
    def __enter__(self):
        return self.__internals.call_special('__enter__')
    def __exit__(self, *args):
        return self.__internals.call_special('__exit__', *args)
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
