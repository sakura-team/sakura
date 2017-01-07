class HubToDaemonAPI(object):
    def __init__(self, engine):
        self.engine = engine
    def get_daemon_info(self):
        return self.engine.get_daemon_info_serializable()
    def create_operator_instance(self, cls_name, op_id):
        self.engine.create_operator_instance(cls_name, op_id)
    def delete_operator_instance(self, op_id):
        self.engine.delete_operator_instance(op_id)
    def connect_operators(self, src_op_id, src_out_id, dst_op_id, dst_in_id):
        self.engine.connect_operators(src_op_id, src_out_id, dst_op_id, dst_in_id)
    def disconnect_operators(self, dst_op_id, dst_in_id):
        self.engine.disconnect_operators(dst_op_id, dst_in_id)
