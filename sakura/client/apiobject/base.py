import inspect

def short_repr(obj):
    if isinstance(obj, APIObjectBase):
        return obj.__repr__(level=1)
    elif isinstance(obj, list):
        return '[' + ', '.join(short_repr(elem) for elem in obj) + ']'
    else:
        res = repr(obj)
        if len(res) > 70:
            res = res[:67] + '...'
        return res

def get_attrs_desc(obj):
    attrs = {}
    # regular attributes
    if hasattr(obj, '__doc_attrs__'):
        for k, v in obj.__doc_attrs__():
            attrs[k] = v
    # properties
    for attr_name, attr_val in inspect.getmembers(obj.__class__, inspect.isdatadescriptor):
        if attr_name.startswith('_'):
            continue
        attrs[attr_name] = getattr(obj, attr_name)
    if len(attrs) == 0:
        return ''
    return '\n  attributes:\n' + '\n'.join(
            '  - self.' + str(k) + ': ' + short_repr(v) for k, v in sorted(attrs.items())) + '\n'

def get_methods_desc(obj):
    method_names = tuple(info[0] for info in inspect.getmembers(obj, inspect.ismethod) \
                        if not info[0].startswith('_'))
    res = ''
    if len(method_names) > 0:
        res += '\n  methods:\n'
        for method_name in sorted(method_names):
            method = getattr(obj.__class__, method_name)
            res += '  - self.' + method.__name__ + str(inspect.signature(method)) + \
                   ': ' + method.__doc__ + '\n'
    return res

def get_subitems_desc(obj):
    items = []
    if hasattr(obj, '__doc_subitems__'):
        items += list(obj.__doc_subitems__())
    if len(items) == 0:
        return ''
    return '\n  sub-items:\n' + '\n'.join(
        '  - self[' + str(k) + ']: ' + short_repr(v) for k, v in sorted(items)) + '\n'

class APIObjectBase:
    def __repr__(self, level=0):
        short_desc = self.__class__.__doc__
        if level == 1:
            return '<' + short_desc + '>'
        elif level == 0:
            res = '< -- ' + short_desc + ' --\n'
            res += get_attrs_desc(self)
            res += get_methods_desc(self)
            res += get_subitems_desc(self)
            res += '>'
        return res

def APIObjectRegistry(d):
    class APIObjectRegistryImpl(APIObjectBase):
        def __getitem__(self, k):
            return d[k]
        def __doc_subitems__(self):
            return d.items()
    return APIObjectRegistryImpl
