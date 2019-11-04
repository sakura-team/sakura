import socket, inspect

def short_repr(obj):
    if isinstance(obj, APIObjectBase):
        return obj.__repr__(level=1)
    elif isinstance(obj, list):
        return '[' + ', '.join(short_repr(elem) for elem in obj) + ']'
    elif isinstance(obj, Exception):
        return '<' + str(obj) + '>'
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
        try:
            attrs[attr_name] = getattr(obj, attr_name)
        except socket.error:
            raise   # probably a connection error with hub
        except Exception as e:
            attrs[attr_name] = e
    if len(attrs) == 0:
        return (), ''
    return attrs.keys(), '\n  attributes:\n' + '\n'.join(
        '  - self.' + str(k) + ': ' + short_repr(v) for k, v in sorted(attrs.items())) + '\n'

def get_methods_desc(obj, excluded_attrs):
    # we cannot directly use inspect.getmembers(obj, inspect.ismethod)
    # because it would cause evaluation of properties, and evaluation of properties
    # may throw exceptions.
    method_names = []
    for attr in obj.__dir__():
        if attr.startswith('_') or attr in excluded_attrs:
            continue
        val = getattr(obj, attr)
        if inspect.ismethod(val):
            method_names.append(attr)
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
        '  - self[' + repr(k) + ']: ' + short_repr(v) for k, v in sorted(items)) + '\n'

class APIObjectBase:
    def __repr__(self, level=0):
        short_desc = self.__class__.__doc__
        if hasattr(self.__class__, '__len__'):
            short_desc += ' (%d items)' % len(self)
        if level == 1:
            return '<' + short_desc + '>'
        elif level == 0:
            attr_names, attr_desc = get_attrs_desc(self)
            res = '< -- ' + short_desc + ' --\n'
            res += attr_desc
            res += get_methods_desc(self, excluded_attrs = attr_names)
            res += get_subitems_desc(self)
            res += '>'
        return res

def APIObjectRegistryClass(d, doc=None):
    class APIObjectRegistryImpl(APIObjectBase):
        __doc__ = doc
        def __getitem__(self, k):
            try:
                return d[k]
            except KeyError:
                pass
            raise KeyError('Sorry, no object at key "%s"' % str(k))
        def __doc_subitems__(self):
            return d.items()
        def __iter__(self):
            return iter(d)
        def items(self):
            "Iterate over key & value pairs this registry contains"
            return d.items()
        def keys(self):
            "Iterate over keys this registry contains"
            return d.keys()
        def values(self):
            "Iterate over values this registry contains"
            return d.values()
        def __len__(self):
            "Indicate how many items this registry contains"
            return len(d)
    return APIObjectRegistryImpl

def APIObjectRegistry(*args):
    cls = APIObjectRegistryClass(*args)
    return cls()    # instanciate
