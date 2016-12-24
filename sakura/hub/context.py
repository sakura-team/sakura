from sakura.hub.opclasses import OpClassRegistry

class HubContext(object):
    def __init__(self):
        self.next_daemon_id = 0
        self.daemons = {}
        self.op_classes = OpClassRegistry()
    def get_daemon_id(self):
        daemon_id = self.next_daemon_id
        self.next_daemon_id += 1
        return daemon_id
    def register_daemon(self, daemon_id, metadata):
        self.daemons[daemon_id] = metadata
    def list_daemons(self):
        return self.daemons
    def register_op_class(self, daemon_id, name, tags, icon, nb_inputs, nb_outputs):
        self.op_classes.store(daemon_id, name, tags, icon, nb_inputs, nb_outputs)
    def list_op_classes(self):
        return [ dict(
                    id = info.cls_id,
                    name = info.name,
                    daemon = self.daemons[info.daemon_id]['name'],
                    tags = info.tags,
                    svg = info.icon,
                    inputs = info.nb_inputs,
                    outputs = info.nb_outputs
                ) for info in self.op_classes.list() ]

