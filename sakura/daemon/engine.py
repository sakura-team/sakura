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
    def connect_operators(self, src_op_id, src_out_id, dst_op_id, dst_in_id):
        src_op = self.op_instances[src_op_id]
        dst_op = self.op_instances[dst_op_id]
        dst_op.input_tables[dst_in_id].connect(src_op.output_tables[src_out_id])
        print("connected %s op_id=%d out%d -> %s op_id=%d in%d" % \
                (src_op.NAME, src_op_id, src_out_id, dst_op.NAME, dst_op_id, dst_in_id))
    def disconnect_operators(self, dst_op_id, dst_in_id):
        dst_op = self.op_instances[dst_op_id]
        dst_op.input_tables[dst_in_id].disconnect()
        print("disconnected [...] -> %s op_id=%d in%d" % \
                (dst_op.NAME, dst_op_id, dst_in_id))
    def get_operator_instance_info_serializable(self, op_id):
        op = self.op_instances[op_id]
        return dict(
            cls_name = op.NAME,
            parameters = [ param.get_info_serializable() for param in op.parameters ],
            inputs = [ table.get_info_serializable() for table in op.input_tables ],
            outputs = [ table.get_info_serializable() for table in op.output_tables ]
        )
