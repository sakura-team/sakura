from collections import namedtuple

OpDesc = namedtuple('OpDesc', ['cls_id', 'daemon_id', 'name', 'tags', 'icon', 'nb_inputs', 'nb_outputs'])

class OpClassRegistry(object):
    def __init__(self):
        self.info_per_cls_id = {}
        self.info_per_daemon_and_name = {}
    def store(self, daemon_id, name, tags, icon, nb_inputs, nb_outputs):
        if (daemon_id, name) in self.info_per_daemon_and_name:
            cls_id = self.info_per_daemon_and_name[(daemon_id, name)][0]
        else:
            cls_id = len(self.info_per_cls_id)
        desc = OpDesc(cls_id, daemon_id, name, tags, icon, nb_inputs, nb_outputs)
        self.info_per_cls_id[cls_id] = desc
        self.info_per_daemon_and_name[(daemon_id, name)] = desc
    def list(self):
        return self.info_per_cls_id.values()

