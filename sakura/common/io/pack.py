import numpy as np

# obtain a serializable description of an object
def pack(obj):
    # some classes can pass unchanged
    if isinstance(obj, str) or isinstance(obj, bytes) or \
            isinstance(obj, np.ndarray):
        return obj
    # with other objects, try to be smart
    if isinstance(obj, dict):
        return { k: pack(v) for k, v in obj.items() }
    elif isinstance(obj, type) and hasattr(obj, 'select'):    # for pony entities
        return tuple(pack(o) for o in obj.select())
    elif hasattr(obj, 'pack'):
        return pack(obj.pack())
    elif hasattr(obj, '_asdict'):
        return pack(obj._asdict())
    elif isinstance(obj, list) or isinstance(obj, tuple) or \
                hasattr(obj, '__iter__'):
        return tuple(pack(o) for o in obj)
    # object is probably a native type
    return obj
