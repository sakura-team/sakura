from sakura.common.tools import SimpleAttrContainer

class OpInstance(SimpleAttrContainer):
    def __getattr__(self, attr):
        # if we cannot find the attr locally, let's look at the real operator
        # instance on the daemon side.
        return getattr(self.remote_instance, attr)

QUERY_OPINSTANCES_FROM_DAEMON = """
SELECT op.*
FROM OpClass cls, OpInstance op
WHERE cls.cls_id = op.cls_id
  AND cls.daemon_id = %d;
"""

class OpInstanceRegistry(object):
    def __init__(self, db):
        self.db = db
        self.info_per_op_id = {}
    def restore_daemon_state(self, daemon_info, op_classes):
        for row in self.db.execute(QUERY_OPINSTANCES_FROM_DAEMON % daemon_info.daemon_id):
            cls_info = op_classes[row['cls_id']]
            op_id = row['op_id']
            self.instanciate(daemon_info, cls_info, op_id)
    def create(self, daemon_info, cls_info):
        self.db.insert('OpInstance', cls_id = cls_info.cls_id)
        self.db.commit()
        op_id = self.db.lastrowid
        return self.instanciate(daemon_info, cls_info, op_id)
    def instanciate(self, daemon_info, cls_info, op_id):
        daemon_info.api.create_operator_instance(cls_info.name, op_id)
        remote_instance = daemon_info.api.op_instances[op_id]
        desc = OpInstance(  op_id = op_id,
                            daemon = daemon_info,
                            cls_info = cls_info,
                            attached_links = set(),
                            remote_instance = remote_instance,
                            gui_data = None)
        self.info_per_op_id[op_id] = desc
        return remote_instance.get_info_serializable()
    def delete(self, op_id):
        self[op_id].daemon.api.delete_operator_instance(op_id)
        del self.info_per_op_id[op_id]
        self.db.delete('OpInstance', op_id = op_id)
        self.db.commit()
    def __getitem__(self, op_id):
        return self.info_per_op_id[op_id]
    def __iter__(self):
        # iterate over op_id values
        return self.info_per_op_id.__iter__()
