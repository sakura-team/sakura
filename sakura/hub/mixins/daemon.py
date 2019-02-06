from sakura.hub.context import get_context
from sakura.common.errors import APIRequestErrorOfflineDaemon

class DaemonMixin:
    APIS = {}

    @property
    def api(self):
        if not self.enabled:
            raise APIRequestErrorOfflineDaemon('Daemon is offline!')
        return DaemonMixin.APIS[self.name]

    @property
    def disabled_message(self):
        if self.enabled:
            raise AttributeError
        return 'Sakura daemon "%s" is disconnected!' % self.name

    @api.setter
    def api(self, value):
        DaemonMixin.APIS[self.name] = value

    # Property 'enabled' is not stored in database.
    # It should be 'volatile'.
    # Each time the hub starts it considers all
    # daemons are disconnected (which is obviously true).
    @property
    def enabled(self):
        return self.name in DaemonMixin.APIS

    def save_api(self, api):
        self.api = api

    def on_connect(self):
        # restore according to up-to-date info from daemon
        daemon_info = self.api.get_daemon_info_serializable()
        self.restore(**daemon_info)

    def on_disconnect(self):
        # unregister api object
        del DaemonMixin.APIS[self.name]
        # notify related objects
        for op in self.op_instances:
            op.on_daemon_disconnect()
        for ds in self.datastores:
            ds.on_daemon_disconnect()

    def pack(self):
        return dict(
            name = self.name,
            datastores = self.datastores,
            **self.pack_status_info()
        )

    @classmethod
    def get_or_create(cls, name):
        daemon = cls.get(name = name)
        if daemon is None:
            daemon = cls(name = name)
            # we will need an up-to-date daemon id
            get_context().db.commit()
        return daemon

    def prefetch_code(self):
        commit_refs = set()
        for op_cls in get_context().op_classes.select():
            # code of operator instances
            for op in op_cls.op_instances:
                commit_refs.add((op_cls.code_url, op.code_ref, op.commit_hash))
            # default code ref of op_class
            commit_refs.add((op_cls.code_url, op_cls.default_code_ref, op_cls.default_commit_hash))
        # fetch all this
        for ref in commit_refs:
            self.api.prefetch_code(*ref)

    def instanciate_op_instances(self):
        # re-instanciate op instances and their parameters
        for op in self.op_instances:
            op.instanciate_on_daemon()
            # restore params
            for param in op.params:
                param.restore()
        # re-instanciate links when possible
        for op in self.op_instances:
            op.restore_links()

    def restore(self, name, origin_id, datastores, **kwargs):
        context = get_context()
        # update metadata
        self.origin_id = origin_id
        self.set(**kwargs)
        # restore datastores and related components (databases, tables, columns)
        self.datastores = set(context.datastores.restore_datastore(self, **ds) for ds in datastores)
        # ensure source code of op classes is fetched on daemon
        self.prefetch_code()
        # re-instanciate op instances and related objects (links, parameters)
        self.instanciate_op_instances()

    @classmethod
    def all_enabled(cls):
        for daemon in cls.select():
            if daemon.enabled:
                yield daemon

    @classmethod
    def any_enabled(cls):
        for daemon in cls.all_enabled():
            return daemon   # return first
