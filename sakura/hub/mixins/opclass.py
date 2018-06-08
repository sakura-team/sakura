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
        op_cls = cls.create_or_update(daemon, **cls_info)
        # re-instantiate related instances on daemon
        for op in op_cls.op_instances:
            op.instanciate_on_daemon()
        # restore links if the other end is also ok
        for op in op_cls.op_instances:
            for link in op.uplinks:
                if link.src_op.instanciated:
                    link.link_on_daemon()
            for link in op.downlinks:
                if link.dst_op.instanciated:
                    link.link_on_daemon()
        # if all uplinks are ok, restore operator parameters
        for op in op_cls.op_instances:
            if all(link.src_op.instanciated \
                    for link in op.uplinks):
                # update params in order (according to param_id)
                for param in sorted(op.params, key=lambda param: param.param_id):
                    param.update_on_daemon()
        return op_cls
