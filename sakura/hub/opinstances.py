from collections import namedtuple

OpInstanceInfo = namedtuple('OpInstanceInfo',
                ['op_id','daemon','cls_info','attached_links','remote_instance'])

class OpInstance(OpInstanceInfo):
    def __getattr__(self, attr):
        # if we cannot find the attr locally, let's look at the real operator
        # instance on the daemon side.
        return getattr(self.remote_instance, attr)

class OpInstanceRegistry(object):
    def __init__(self):
        self.next_op_id = 0
        self.info_per_op_id = {}
    def create(self, daemon_info, cls_info):
        op_id = self.next_op_id
        self.next_op_id += 1
        daemon_info.api.create_operator_instance(cls_info.name, op_id)
        remote_instance = daemon_info.api.op_instances[op_id]
        desc = OpInstance(op_id, daemon_info, cls_info, set(), remote_instance)
        self.info_per_op_id[op_id] = desc
        return remote_instance.get_info_serializable()
    def delete(self, op_id):
        self[op_id].daemon.api.delete_operator_instance(op_id)
        del self.info_per_op_id[op_id]
    def __getitem__(self, op_id):
        return self.info_per_op_id[op_id]
    def __iter__(self):
        # iterate over op_id values
        return self.info_per_op_id.__iter__()
