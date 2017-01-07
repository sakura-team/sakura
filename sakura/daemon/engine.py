import sakura.daemon.conf as conf
from sakura.daemon.processing.operator import Operator

class DaemonEngine(object):
    def __init__(self, op_classes):
        self.op_classes = op_classes
        self.op_instances = {}
    def get_daemon_info_serializable(self):
        op_classes_desc = list(
            Operator.descriptor(op_cls) for op_cls in self.op_classes.values()
        )
        return dict(name=conf.daemon_desc,
                    ext_datasets=conf.external_datasets,
                    op_classes=op_classes_desc)
    def create_operator_instance(self, cls_name, op_id):
        op_cls = self.op_classes[cls_name]
        op = op_cls()
        op.construct()
        self.op_instances[op_id] = op
        print("created operator %s op_id=%d" % (cls_name, op_id))
    def delete_operator_instance(self, op_id):
        print("deleting operator %s op_id=%d" % (self.op_instances[op_id].NAME, op_id))
        del self.op_instances[op_id]
