import sakura.daemon.conf as conf
from sakura.daemon.processing.operator import Operator
from sakura.operators.internal.fragmentsource.operator import FragmentSourceOperator

class DaemonEngine(object):
    def __init__(self, op_classes):
        self.op_classes = op_classes
        self.op_instances = {}
        self.hub = None
        self.fragment_sources = {}
    def register_hub_api(self, hub_api):
        self.hub = hub_api
    def get_daemon_info_serializable(self):
        op_classes_desc = list(
            Operator.descriptor(op_cls) for op_cls in self.op_classes.values()
        )
        return dict(name=conf.daemon_desc,
                    ext_datasets=conf.external_datasets,
                    op_classes=op_classes_desc)
    def create_operator_instance(self, cls_name, op_id):
        op_cls = self.op_classes[cls_name]
        op = op_cls(op_id)
        op.construct()
        op.auto_fill_parameters()
        self.op_instances[op_id] = op
        print("created operator %s op_id=%d" % (cls_name, op_id))
    def delete_operator_instance(self, op_id):
        print("deleting operator %s op_id=%d" % (self.op_instances[op_id].NAME, op_id))
        del self.op_instances[op_id]
    def is_foreign_operator(self, op_id):
        return op_id not in self.op_instances
    def connect_operators(self, src_op_id, src_out_id, dst_op_id, dst_in_id):
        if self.is_foreign_operator(src_op_id):
            # the source is a remote operator.
            # we replace this source operator by an internal FragmentSourceOperator
            # that will pull data from the hub and feed its unique output table.
            src_label = 'remote(op_id=%d,out%d)' % (src_op_id, src_out_id)
            src_op = FragmentSourceOperator(self.hub, src_op_id, src_out_id)
            src_op.construct()
            self.fragment_sources[(dst_op_id, dst_in_id)] = src_op
            # since src_op has been replaced (see above),
            # we will connect (src_op,0) -> (dst_op,dst_in_id)
            src_out_id = 0
        else:
            src_op = self.op_instances[src_op_id]
            src_label = '%s op_id=%d out%d' % (src_op.NAME, src_op_id, src_out_id)
        dst_op = self.op_instances[dst_op_id]
        dst_op.input_tables[dst_in_id].connect(src_op.output_tables[src_out_id])
        # auto select unselected parameters, if possible
        dst_op.auto_fill_parameters()
        print("connected %s -> %s op_id=%d in%d" % \
                (src_label, dst_op.NAME, dst_op_id, dst_in_id))
    def disconnect_operators(self, src_op_id, src_out_id, dst_op_id, dst_in_id):
        dst_op = self.op_instances[dst_op_id]
        dst_op.input_tables[dst_in_id].disconnect()
        if self.is_foreign_operator(src_op_id):
            # discard the fragment source operator
            del self.fragment_sources[(dst_op_id, dst_in_id)]
        print("disconnected [...] -> %s op_id=%d in%d" % \
                (dst_op.NAME, dst_op_id, dst_in_id))
