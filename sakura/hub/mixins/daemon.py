from sakura.hub.context import get_context
from sakura.common.errors import APIRequestErrorOfflineDaemon

class DaemonMixin:
    APIS = {}

    @property
    def api(self):
        if not self.connected:
            raise APIRequestErrorOfflineDaemon('Daemon is offline!')
        return DaemonMixin.APIS[self.name]

    @api.setter
    def api(self, value):
        DaemonMixin.APIS[self.name] = value

    # Property 'connected' is not stored in database.
    # It should be 'volatile'.
    # Each time the hub starts it considers all
    # daemons are disconnected (which is obviously true).
    @property
    def connected(self):
        return self.name in DaemonMixin.APIS

    def disconnect(self):
        del DaemonMixin.APIS[self.name]

    def pack(self):
        return dict(
            name = self.name,
            connected = self.connected,
            datastores = self.datastores,
            op_classes = self.op_classes
        )

    @classmethod
    def create_or_update(cls, name, **kwargs):
        daemon = cls.get(name = name)
        if daemon is None:
            daemon = cls(name = name, **kwargs)
        else:
            daemon.set(name = name, **kwargs)
        return daemon

    @classmethod
    def restore_daemon(cls, api, name, datastores, op_classes, **kwargs):
        context = get_context()
        # create or update existing daemon of db
        daemon = cls.create_or_update(name, **kwargs)
        # we will need an up-to-date daemon id
        context.db.commit()
        # save api
        daemon.api = api
        # restore datastores and related components (databases, tables, columns)
        daemon.datastores = set(context.datastores.restore_datastore(daemon, **ds) for ds in datastores)
        # restore op classes and re-instanciate related objects (instances, links, parameters)
        daemon.op_classes = set(context.op_classes.restore_op_class(daemon, **cls) for cls in op_classes)
        return daemon
