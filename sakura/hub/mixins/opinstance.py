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
        if self.op_class.enabled:
            return 'Daemon running this operator was just stopped.'
        else:
            return self.op_class.disabled_message
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

    def pack_repo_info(self, **flags):
        info = self.op_class.pack_repo_info(revision_prefix='', **flags)
        if info['repo_type'] == 'git':
            info.update(
                code_ref = self.revision['code_ref'],
                commit_hash = self.revision['commit_hash']
            )
        return info

    def pack(self):
        res = dict(
            op_id = self.id,
            cls_id = self.op_class.id,
            cls_name = self.op_class.metadata['name'],
            gui_data = self.gui_data,
            num_ops_of_cls = self.num_ops_of_cls,
            **self.pack_repo_info(),
            **self.pack_status_info()
        )
        if self.enabled:
           res.update(**self.remote_instance.pack())
        return res

    @property
    def sorted_params(self):
        # sort params according to param_id
        yield from sorted(self.params, key=lambda param: param.param_id)

    def recheck_params(self):
        # recheck params in order
        for param in self.sorted_params:
            param.recheck()

    def update_revision(self, code_ref, commit_hash, all_ops_of_cls=False):
        if all_ops_of_cls:
            ops = self.iterate_all_ops_of_cls()
        else:
            ops = [ self ]
        for op in ops:
            old_revision = op.revision
            op.revision = dict(code_ref = code_ref, commit_hash = commit_hash)
            try:
                op.reload_on_daemon()
            except:
                # failed, restore
                op.revision = old_revision
                op.reload_on_daemon()
                raise

    def instanciate_on_daemon(self):
        self.daemon_api.create_operator_instance(
            self.id,
            **self.pack_repo_info(include_sandbox_attrs=True)
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
        # setup parameters with remote daemon
        for param in self.sorted_params:
            param.setup()
        # discard any move request queued during the process
        self.remote_instance.pop_pending_move_check()
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
            **self.pack_repo_info(include_sandbox_attrs=True)
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
    def create_instance(cls, dataflow, op_cls_id, **revision_kwargs):
        context = get_context()
        # create in local db
        op = cls(daemon = None, dataflow = dataflow, op_class = op_cls_id, **revision_kwargs)
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
        # discard any move request queued during the process
        self.remote_instance.pop_pending_move_check()
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
            if self.ready():
                for link in self.downlinks:
                    link.dst_op.restore_links()
    def restore(self):
        self.instanciate_on_daemon()
        self.restore_links()
