from sakura.hub.context import get_context
from sakura.common.errors import APIRequestErrorOfflineDaemon
from sakura.common.errors import APIOperatorError

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
        get_context().op_classes.prefetch_code(self.api)

    def restore_op_instances(self):
        for op in self.op_instances:
            try:
                op.restore()
            except APIOperatorError as e:
                print('Could not restore an operator instance:', str(e))
                op.delete_instance()
                print('Operator instance was deleted.')

    def restore(self, name, origin_id, datastores, **kwargs):
        context = get_context()
        # update metadata
        self.origin_id = origin_id
        self.set(**kwargs)
        # restore datastores and related components (databases, tables, columns)
        self.datastores = set(context.datastores.restore_datastore(self, **ds) for ds in datastores)
        self.restore_col_tags()
        # ensure source code of op classes is fetched on daemon
        self.prefetch_code()
        # re-instanciate op instances and related objects (links, parameters)
        self.restore_op_instances()

    def restore_col_tags(self):
        daemon_col_tags = {}
        for ds in self.datastores:
            ds_col_tags = ds.describe_col_tags()
            if len(ds_col_tags) > 0:
                daemon_col_tags[(ds.host, ds.driver_label)] = ds_col_tags
        if len(daemon_col_tags) > 0:
            self.api.set_col_tags(daemon_col_tags)

    @classmethod
    def all_enabled(cls):
        for daemon in cls.select():
            if daemon.enabled:
                yield daemon

    @classmethod
    def any_enabled(cls):
        for daemon in cls.all_enabled():
            return daemon   # return first
