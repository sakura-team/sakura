from collections import namedtuple

OpClsInfo = namedtuple('OpClsInfo',
        ['cls_id', 'daemon_id', 'name', 'short_desc', 'tags', 'icon', 'nb_inputs', 'nb_outputs'])

class OpClassRegistry(object):
    def __init__(self):
        self.next_cls_id = 0
        self.info_per_cls_id = {}
        self.info_per_daemon_and_name = {}
    def store(self, daemon_id, name, *args):
        if (daemon_id, name) in self.info_per_daemon_and_name:
            cls_id = self.info_per_daemon_and_name[(daemon_id, name)][0]
        else:
            cls_id = self.next_cls_id
            self.next_cls_id += 1
        desc = OpClsInfo(cls_id, daemon_id, name, *args)
        self.info_per_cls_id[cls_id] = desc
        self.info_per_daemon_and_name[(daemon_id, name)] = desc
    def list(self):
        return self.info_per_cls_id.values()
    def get_cls_info(self, cls_id):
        return self.info_per_cls_id[cls_id]

