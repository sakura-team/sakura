

class Registry:
    def register(self, container, cls, *args, **kwargs):
        return self.register_instance(container, cls(*args, **kwargs))
    def register_instance(self, container, obj):
        container.append(obj)
        return obj

