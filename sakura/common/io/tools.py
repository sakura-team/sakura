import contextlib

@contextlib.contextmanager
def void_context_manager():
    yield

def traverse(obj, path):
    for attr in path:
        if isinstance(attr, str):
            obj = getattr(obj, attr)
        else:
            obj = obj[attr[0]]  # getitem
    return obj

class Internals:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

