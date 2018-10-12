class APILevel:
    def __init__(self):
        self._type = 'level'
        self._item = None    # only for tables
        self._sublevel = None
    def __getitem__(self, item):
        self._item = item
        return self._sublevel

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
            if not hasattr(self._obj, attr):
                # let's consider it is an APILevel for now
                obj = APILevel()
                setattr(self._obj, attr, obj)
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
            return orig_function(instance, *args, **kwargs)
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

