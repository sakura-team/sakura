class OpClassMixin:
    def pack(self):
        return dict(
            daemon = self.daemon.name,
            id = self.id,
            name = self.name,
            short_desc = self.short_desc,
            tags = tuple(self.tags),
            svg = self.icon
        )
    def on_daemon_disconnect(self):
        for op in self.op_instances:
            op.on_daemon_disconnect()
    @classmethod
    def create_or_update(cls, daemon, name, **kwargs):
        op_cls = cls.get(daemon = daemon, name = name)
        if op_cls is None:
            # create
            op_cls = cls(daemon = daemon, name = name, **kwargs)
        else:
            # update
            op_cls.set(**kwargs)
        return op_cls
    @classmethod
    def restore_op_class(cls, daemon, **cls_info):
        return cls.create_or_update(daemon, **cls_info)
