

class Registry(object):
    def register(self, container, cls, *args):
        obj = cls(*args)
        container.append(obj)
        return obj

