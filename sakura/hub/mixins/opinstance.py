from sakura.hub.context import get_context
from sakura.hub.mixins.bases import BaseMixin
from sakura.common.errors import APIOperatorError

class OpInstanceMixin(BaseMixin):
    INSTANCIATED = set()
    MOVING = set()
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
    def enabled(self):
        return self.id in OpInstanceMixin.INSTANCIATED
    @enabled.setter
    def enabled(self, boolean):
        if boolean:
            self.push_event('enabled')
            OpInstanceMixin.INSTANCIATED.add(self.id)
        else:
            self.push_event('disabled')
            OpInstanceMixin.INSTANCIATED.discard(self.id)
    @property
    def moving(self):
        return self.id in OpInstanceMixin.MOVING
    @moving.setter
    def moving(self, boolean):
        if boolean:
            OpInstanceMixin.MOVING.add(self.id)
        else:
            OpInstanceMixin.MOVING.discard(self.id)
    @property
    def disabled_message(self):
        return self.op_class.daemon.disabled_message
    def __getattr__(self, attr):
        # find other attributes at the real operator
        # instance on the daemon side.
        if attr != 'warning_message' and not 'internal' in attr:
            return getattr(self.remote_instance, attr)
        raise AttributeError

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
            gui_data = self.gui_data,
            num_ops_of_cls = self.num_ops_of_cls,
            **self.pack_status_info()
        )
        if self.enabled:
           res.update(**self.remote_instance.pack())
        return res
    def recheck_params(self):
        # recheck params in order (according to param_id)
        for param in sorted(self.params, key=lambda param: param.param_id):
            param.recheck()

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
        self.resync_params()
        # we have it instanciated
        self.enabled = True
    def resync_params(self):
        # resync number of parameters with what the daemon reports (possible source code change)
        local_ids = set(param.param_id for param in self.params)
        remote_ids = set(range(self.remote_instance.get_num_parameters()))
        for param in self.params:
            if param.param_id not in remote_ids:
                param.delete()
        context = get_context()
        for param_id in (remote_ids - local_ids):
            param = context.op_params(op = self, param_id = param_id) # instanciate in local db
            context.db.commit()
        # send previously recorded param value, subscribe to remote events
        for param in self.params:
            param.setup()
    def delete_on_daemon(self):
        self.enabled = False
        self.daemon_api.delete_operator_instance(self.id)
    def disable_downlinks(self):
        for link in self.downlinks:
            link.disable()
            link.dst_op.disable_downlinks()
    def reload_on_daemon(self):
        self.daemon_api.reload_operator_instance(
            self.id,
            self.op_class.code_url,
            self.code_ref,
            self.commit_hash,
            self.op_class.code_subdir
        )
        self.resync_params()
    def on_daemon_disconnect(self):
        # daemon stopped
        for link in self.uplinks:
            link.disable()
        self.disable_downlinks()
        self.enabled = False
    def ready(self):
        if not self.enabled:
            return False
        for link in self.uplinks:
            if not link.enabled:
                return False
        for param in self.params:
            if not param.is_valid:
                return False
        return True
    @classmethod
    def create_instance(cls, dataflow, op_cls_id, revision):
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
        op = cls(daemon = None, dataflow = dataflow, op_class = op_cls_id,
                 code_ref = code_ref, commit_hash = commit_hash)
        # refresh op id
        context.db.commit()
        # run on most appropriate daemon
        try:
            op.move()
        except:
            op.delete()
            raise
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
        if self.enabled:
            self.delete_on_daemon()
        # delete instance in local db
        self.delete()
        get_context().db.commit()
    def check_move(self):
        if self.moving:     # discard if already moving
            return
        if self.remote_instance.pop_pending_move_check():
            self.move()
    def move(self):
        print('MOVE')
        self.moving = True
        affinities = {}
        # list available daemons, current first
        # (if self.daemon already has a value)
        daemons = sorted(get_context().daemons.all_enabled(),
                         key = lambda daemon: daemon != self.daemon)
        # try available daemons
        for daemon in daemons:
            if daemon != self.daemon:   # if not already current
                self.move_out()
                try:
                    self.move_in(daemon)
                except: # not compatible
                    continue
            affinities[daemon] = self.env_affinity()
        # check that we can move somewhere
        if len(affinities) == 0:
            self.moving = False
            raise APIOperatorError('This operator is not compatible with available daemons!')
        # check best affinity
        best = (None, -1)
        for daemon, score in affinities.items():
            if score > best[1]:
                best = (daemon, score)
        # migrate to best match
        if self.daemon != best[0]:
            daemon = best[0]
            self.move_out()
            self.move_in(daemon)
        self.moving = False
    def move_out(self):
        if self.enabled:
            # disable links
            for link in self.uplinks:
                link.disable()
            self.disable_downlinks()
            # drop op
            self.delete_on_daemon()
    def move_in(self, daemon):
        # associate
        self.daemon = daemon
        # recreate op
        self.restore()
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
    def restore(self):
        self.instanciate_on_daemon()
        self.restore_links()
