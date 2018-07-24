

class Registry:
    def register(self, container, cls, *args):
        return self.register_instance(container, cls(*args))
    def register_instance(self, container, obj):
        container.append(obj)
        return obj

