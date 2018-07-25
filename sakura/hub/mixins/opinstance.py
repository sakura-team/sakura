from sakura.hub.context import get_context

class OpInstanceMixin:
    INSTANCIATED = set()
    @property
    def daemon_api(self):
        return self.op_class.daemon.api
    @property
    def remote_instance(self):
        # note: the following shortcut will become valid only after
        # the operator has been instanciated with function
        # instanciate_on_daemon() below.
        return self.daemon_api.op_instances[self.id]
    @property
    def instanciated(self):
        return self.id in OpInstanceMixin.INSTANCIATED
    @instanciated.setter
    def instanciated(self, boolean):
        if boolean:
            OpInstanceMixin.INSTANCIATED.add(self.id)
        else:
            OpInstanceMixin.INSTANCIATED.discard(self.id)
    def __getattr__(self, attr):
        # if we cannot find the attr,
        # let's look at the real operator
        # instance on the daemon side.
        return getattr(self.remote_instance, attr)
    def pack(self):
        res = dict(
            op_id = self.id,
            cls_id = self.op_class.id,
            online = self.instanciated,
            gui_data = self.gui_data
        )
        if self.instanciated:
           res.update(**self.remote_instance.pack())
        return res
    def instanciate_on_daemon(self):
        self.daemon_api.create_operator_instance(self.op_class.name, self.id)
        self.instanciated = True
        return self.remote_instance
    def delete_on_daemon(self):
        self.instanciated = False
        self.daemon_api.delete_operator_instance(self.id)
    def on_daemon_disconnect(self):
        # daemon stopped
        self.instanciated = False
    @classmethod
    def create_instance(cls, dataflow, op_cls_id):
        # create in local db
        op = cls(dataflow = dataflow, op_class = op_cls_id)
        # refresh op id
        get_context().db.commit()
        # create remotely
        return op.instanciate_on_daemon()
    def delete_instance(self):
        # delete connected links
        for l in self.uplinks:
            l.delete_link()
        for l in self.downlinks:
            l.delete_link()
        # delete instance remotely
        self.delete_on_daemon()
        # delete instance in local db
        self.delete()
