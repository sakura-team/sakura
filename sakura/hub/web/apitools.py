import pony.orm
import numpy as np
from sakura.common.errors import APIInvalidRequest

def pack(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, type) and hasattr(obj, 'select'):    # for pony entities
        return tuple(o.pack() for o in obj.select())
    elif hasattr(obj, 'pack'):
        return obj.pack()
    elif hasattr(obj, '_asdict'):
        return obj._asdict()
    elif hasattr(obj, '__iter__'):
        return tuple(pack(o) for o in obj)
    elif hasattr(obj, 'item'):
        return obj.item()   # convert numpy scalar to native
    else:
        return obj

class APILevel:
    def __init__(self):
        self._type = 'level'
        self._item = None    # only for tables
        self._sublevel = None
        self._properties = set()
    def __getitem__(self, item):
        self._item = item
        return self._sublevel
    def _define_attr(self, attr, value):
        self._properties.add(attr)
        setattr(self, attr, value)
    def _attr_is_defined(self, attr):
        return attr in self._properties
    def __getattr__(self, attr):
        if self._type == 'table':
            # in javascript, obj['attr'] and obj.attr are the same,
            # so if GUI code wants to access obj['attr'], we may actually get
            # a path like ('obj', 'attr') instead of ('obj', ['attr']).
            # calling __getitem__ here when attribute is not found should
            # fix this.
            return self.__getitem__(attr)
        else:
            raise AttributeError('No such attribute "%s"' % attr)

class APIStructureBuilder:
    def __init__(self, parent = None, attr_name = None, obj = None):
        self._parent = parent
        self._attr_name = attr_name
        if obj is None:
            self._obj = APILevel()
        else:
            self._obj = obj
    def __getattr__(self, attr):
        if attr == '__getitem__':
            if self._obj._type == 'level':
                # this is a table
                self._obj._type = 'table'
                self._obj._sublevel = APILevel()
            return APIStructureBuilder(self, attr, self._obj._sublevel)
        else:
            if not self._obj._attr_is_defined(attr):
                # let's consider it is an APILevel for now
                obj = APILevel()
                self._obj._define_attr(attr, obj)
            return APIStructureBuilder(self, attr, getattr(self._obj, attr))
    def __call__(self, f_or_cls):
        if self._parent is None:
            # top level decorator call
            return self.wrap(f_or_cls)
        else:
            # api function detected
            # replace APILevel created in parent by a function
            setattr(self._parent._obj, self._attr_name, f_or_cls)
            return f_or_cls
    def wrap(self, cls):
        api_desc = self.describe_entries()
        def wrapped(*args, **kwargs):
            instance = cls(*args, **kwargs)
            obj = self.wrap_instance(instance)
            obj.describe = lambda : api_desc
            return obj
        return wrapped
    def wrap_instance(self, instance, api_obj = None, instance_api_table_path = ()):
        if api_obj is None:
            api_obj = self._obj
        instance_api_obj = APILevel()
        instance_api_obj._type = api_obj._type
        for name, value in api_obj.__dict__.items():
            if value is None:
                continue
            if name != '_sublevel' and name.startswith('_'):
                continue
            if isinstance(value, APILevel):
                path = instance_api_table_path
                if name == '_sublevel':
                    path += (instance_api_obj,)
                new_val = self.wrap_instance(instance, value, path)
            else:   # value is a member function
                new_val = self.patch_function(instance, instance_api_table_path, value)
            setattr(instance_api_obj, name, new_val)
        return instance_api_obj
    def patch_function(self, instance, instance_api_table_path, orig_function):
        def patched_function(*args, **kwargs):
            args = [ api_table._item for api_table in instance_api_table_path ] + list(args)
            try:
                return orig_function(instance, *args, **kwargs)
            except pony.orm.ObjectNotFound as e:
                raise APIInvalidRequest('No such object: ' + str(e))
        return patched_function
    def describe_entries(self, api_obj = None):
        if api_obj is None:
            api_obj = self._obj
        sub_items = {}
        for name, value in api_obj.__dict__.items():
            if name.startswith('_'):
                continue
            if isinstance(value, APILevel):
                desc = { 'type': value._type, 'entries': self.describe_entries(value) }
                if value._type == 'table':
                    # add sublevel
                    desc.update({ 'sublevel': self.describe_entries(value._sublevel) })
            else:   # member function
                desc = { 'type': 'func', 'backend_name': value.__name__ }
            sub_items[name] = desc
        return sub_items

api_init = APIStructureBuilder

