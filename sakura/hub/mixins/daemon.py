from sakura.hub.context import get_context
from sakura.common.errors import APIRequestError, APIRequestErrorOfflineDaemon

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

    def save_api(self, api):
        self.api = api

    def on_connect(self):
        # restore according to up-to-date info from daemon
        daemon_info = self.api.get_daemon_info_serializable()
        self.restore(**daemon_info)

    def on_disconnect(self):
        # notify related objects
        for op in self.op_instances:
            op.on_daemon_disconnect()
        # unregister api object
        del DaemonMixin.APIS[self.name]

    def pack(self):
        return dict(
            name = self.name,
            connected = self.connected,
            datastores = self.datastores
        )

    @classmethod
    def get_or_create(cls, name):
        daemon = cls.get(name = name)
        if daemon is None:
            daemon = cls(name = name)
            # we will need an up-to-date daemon id
            get_context().db.commit()
        return daemon

    def fetch_op_classes(self):
        for op_cls in get_context().op_classes.select():
            self.api.fetch_op_class(op_cls.code_url, op_cls.static_code_ref, op_cls.code_subdir)

    def instanciate_op_instances(self):
        # re-instantiate instances on daemon
        for op in self.op_instances:
            op.instanciate_on_daemon()
        # restore links if the other end is also ok
        # caution, we should create the link only once
        # if operators on both ends belong to this daemon
        links_done = set()
        for op in self.op_instances:
            for link in set(op.uplinks) - links_done:
                if link.src_op.instanciated:
                    link.link_on_daemon()
                    links_done.add(link)
            for link in set(op.downlinks) - links_done:
                if link.dst_op.instanciated:
                    link.link_on_daemon()
                    links_done.add(link)
        # if all uplinks are ok, restore operator parameters
        for op in self.op_instances:
            if all(link.src_op.instanciated for link in op.uplinks):
                # update params in order (according to param_id)
                for param in sorted(op.params, key=lambda param: param.param_id):
                    param.update_on_daemon()

    def restore(self, name, datastores, **kwargs):
        context = get_context()
        # update metadata
        self.set(**kwargs)
        # restore datastores and related components (databases, tables, columns)
        self.datastores = set(context.datastores.restore_datastore(self, **ds) for ds in datastores)
        # ensure op classes are fetched on daemon
        self.fetch_op_classes()
        # re-instanciate op instances and related objects (links, parameters)
        self.instanciate_op_instances()

    @classmethod
    def any_connected(cls):
        for daemon in cls.select():
            if daemon.connected:
                return daemon

    @classmethod
    def list_remote_code_refs(cls, repo_url):
        daemon = cls.any_connected()
        if daemon is None:
            raise APIRequestError('Unable to proceed because no daemon is connected.')
        return daemon.api.list_remote_code_refs(repo_url)
