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
    def recheck_params(self):
        # recheck params in order (according to param_id)
        for param in sorted(self.params, key=lambda param: param.param_id):
            param.recheck()
    def instanciate_on_daemon(self):
        self.daemon_api.create_operator_instance(self.op_class.name, self.id)
        # recheck number of parameters with what the daemon reports (possible source code change)
        local_ids = set(param.param_id for param in self.params)
        remote_ids = set(range(self.remote_instance.get_num_parameters()))
        for param in self.params:
            if param.param_id not in remote_ids:
                param.delete()
        context = get_context()
        for param_id in (remote_ids - local_ids):
            param = context.op_params(op = self, param_id = param_id) # instanciate in local db
            context.db.commit()
        for param in self.params:
            param.setup()
        # we have it instanciated
        self.instanciated = True
    def delete_on_daemon(self):
        self.instanciated = False
        self.daemon_api.delete_operator_instance(self.id)
    def disable_downlinks(self):
        for link in self.downlinks:
            link.disable()
            link.dst_op.disable_downlinks()
    def on_daemon_disconnect(self):
        # daemon stopped
        for link in self.uplinks:
            link.disable()
        self.disable_downlinks()
        self.instanciated = False
    def ready(self):
        if not self.instanciated:
            return False
        for link in self.uplinks:
            if not link.enabled:
                return False
        for param in self.params:
            if not param.is_valid:
                return False
        return True
    @classmethod
    def create_instance(cls, dataflow, op_cls_id):
        # create in local db
        op = cls(dataflow = dataflow, op_class = op_cls_id)
        # refresh op id
        get_context().db.commit()
        # create remotely
        op.instanciate_on_daemon()
        # auto-set params when possible
        op.recheck_params()
        return op
    def delete_instance(self):
        # the whole down-tree will be affected
        self.disable_downlinks()
        # remove 1-hop links (since these are connected to
        # the operator instance we are removing)
        for link in self.uplinks:
            link.delete_link()
        for link in self.downlinks:
            link.delete_link()
        # delete instance remotely
        self.delete_on_daemon()
        # delete instance in local db
        self.delete()
    def get_ouputplug_link_id(self, out_id):
        for l in self.downlinks:
            if l.src_out_id == out_id:
                return l.id
        return None     # not connected
    def restore_links(self):
        # restore uplinks if src is ok
        altered = False
        for link in self.uplinks:
            if link.enabled:
                continue    # nothing to do
            if link.src_op.ready():
                # ok, restore!
                try:
                    link.enable()
                    altered = True
                except:
                    # this link is no longer valid
                    # ex: DataSource -> Map, with
                    # the table selected in DataSource no longer
                    # valid (offline datastore)
                    pass    # link is simply not enabled (for now)
        # if we just got ready, recurse with operators
        # on downlinks.
        if altered or len(self.uplinks) == 0:
            self.recheck_params()
            if self.ready():
                for link in self.downlinks:
                    link.dst_op.restore_links()
