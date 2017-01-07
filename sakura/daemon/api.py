class HubToDaemonAPI(object):
    def __init__(self, engine):
        self.engine = engine
    def get_daemon_info(self):
        return self.engine.get_daemon_info_serializable()
    def create_operator_instance(self, cls_name, op_id):
        self.engine.create_operator_instance(cls_name, op_id)
