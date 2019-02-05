from sakura.hub.context import get_context

class OpInstanceMixin:
    INSTANCIATED = set()
    @property
    def daemon_api(self):
        return self.daemon.api
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

    def iterate_all_ops_of_cls(self):
        """Iterates over all operators of this class the current user has."""
        for op in self.op_class.op_instances:
            if op.dataflow.owner == self.dataflow.owner:
                yield op

    @property
    def num_ops_of_cls(self):
        """Indicates how many instances of this class the user has."""
        return len(tuple(self.iterate_all_ops_of_cls()))

    def pack(self):
        res = dict(
            op_id = self.id,
            cls_id = self.op_class.id,
            cls_name = self.op_class.metadata['name'],
            code_ref = self.code_ref,
            commit_hash = self.commit_hash,
            online = self.instanciated,
            gui_data = self.gui_data,
            num_ops_of_cls = self.num_ops_of_cls
        )
        if self.instanciated:
           res.update(**self.remote_instance.pack())
        return res

    @property
    def revision(self):
        return self.code_ref, self.commit_hash

    def update_revision(self, code_ref, commit_hash, all_ops_of_cls=False):
        if all_ops_of_cls:
            ops = self.iterate_all_ops_of_cls()
        else:
            ops = [ self ]
        for op in ops:
            old_revision = op.code_ref, op.commit_hash
            op.code_ref, op.commit_hash = code_ref, commit_hash
            try:
                op.reload_on_daemon()
            except:
                # failed, restore
                op.code_ref, op.commit_hash = old_revision
                op.reload_on_daemon()
                raise

    def instanciate_on_daemon(self):
        self.daemon_api.create_operator_instance(
            self.id,
            self.op_class.code_url,
            self.code_ref,
            self.commit_hash,
            self.op_class.code_subdir
        )
        self.instanciated = True
        return self.remote_instance
    def delete_on_daemon(self):
        self.instanciated = False
        self.daemon_api.delete_operator_instance(self.id)
    def reload_on_daemon(self):
        self.daemon_api.reload_operator_instance(
            self.id,
            self.op_class.code_url,
            self.code_ref,
            self.commit_hash,
            self.op_class.code_subdir
        )
    def on_daemon_disconnect(self):
        # daemon stopped
        self.instanciated = False
    @classmethod
    def create_instance(cls, daemon, dataflow, op_cls_id, revision):
        context = get_context()
        # if not provided, select a revision (commit hash) appropriate for this user:
        # - if he has already instanciated operators of this class, and all of them
        #   are linked to the same revision, re-use this revision
        # - otherwise use the default revision defined for this class of operators
        if revision is None:
            revisions = set()
            for op in cls.select():
                if op.op_class.id == op_cls_id and op.dataflow.owner == context.user.login:
                    revisions.add(op.revision)
            if len(revisions) == 1:
                revision = revisions.pop()
            else:
                revision = context.op_classes[op_cls_id].default_revision
        code_ref, commit_hash = revision
        # create in local db
        op = cls(daemon = daemon, dataflow = dataflow, op_class = op_cls_id,
                 code_ref = code_ref, commit_hash = commit_hash)
        # refresh op id
        context.db.commit()
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
    def get_ouputplug_link_id(self, out_id):
        for l in self.downlinks:
            if l.src_out_id == out_id:
                return l.id
        return None     # not connected
