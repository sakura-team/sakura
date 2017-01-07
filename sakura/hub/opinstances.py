from collections import namedtuple

OpInstanceInfo = namedtuple('OpInstanceInfo', ['op_id','daemon_info','cls_info','attached_links'])

class OpInstanceRegistry(object):
    def __init__(self):
        self.next_op_id = 0
        self.info_per_op_id = {}
    def create(self, daemon_info, cls_info):
        op_id = self.next_op_id
        self.next_op_id += 1
        daemon_info.api.create_operator_instance(cls_info.name, op_id)
        desc = OpInstanceInfo(op_id, daemon_info, cls_info, set())
        self.info_per_op_id[op_id] = desc
        return op_id
    def delete(self, op_id):
        op_info = self.info_per_op_id[op_id]
        op_info.daemon_info.api.delete_operator_instance(op_id)
        del self.info_per_op_id[op_id]
    def __getitem__(self, op_id):
        return self.info_per_op_id[op_id]
