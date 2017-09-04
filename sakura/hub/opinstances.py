import json
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
    def get_db_params(self, op_id):
        for op_id, db_param_id, db_json_value in self.db.select('OpParam', op_id = op_id):
            yield (db_param_id, json.loads(db_json_value))
    def restore_daemon_state(self, daemon_info, op_classes):
        for row in self.db.execute(QUERY_OPINSTANCES_FROM_DAEMON % daemon_info.daemon_id):
            cls_info = op_classes[row['cls_id']]
            op_id = row['op_id']
            gui_data = row['gui_data']
            self.instanciate(daemon_info, cls_info, op_id, gui_data)
    def restore_daemon_op_params(self, daemon_info):
        for op_id in self:
            db_params = tuple(self.get_db_params(op_id))
            if len(db_params) > 0:
                num_params = self[op_id].get_num_parameters()
                for db_param_id, db_value in db_params:
                    # if the operator has been modified, it may actually
                    # have less parameters than before.
                    if db_param_id >= num_params:
                        continue
                    self[op_id].parameters[db_param_id].set_value(db_value)
    def create(self, daemon_info, cls_info):
        self.db.insert('OpInstance', cls_id = cls_info.cls_id)
        self.db.commit()
        op_id = self.db.lastrowid
        return self.instanciate(daemon_info, cls_info, op_id)
    def instanciate(self, daemon_info, cls_info, op_id,
                        gui_data = None):
        daemon_info.api.create_operator_instance(cls_info.name, op_id)
        remote_instance = daemon_info.api.op_instances[op_id]
        desc = OpInstance(  op_id = op_id,
                            daemon = daemon_info,
                            cls_info = cls_info,
                            attached_links = set(),
                            remote_instance = remote_instance,
                            gui_data = gui_data)
        self.info_per_op_id[op_id] = desc
        return remote_instance
    def pack(self, op_id):
        info = self[op_id].pack()
        info.update(cls_id = self[op_id].cls_info.cls_id)
        return info
    def delete(self, op_id):
        self[op_id].daemon.api.delete_operator_instance(op_id)
        del self.info_per_op_id[op_id]
        self.db.delete('OpInstance', op_id = op_id)
        self.db.commit()
    def set_parameter_value(self, op_id, param_id, value):
        self[op_id].parameters[param_id].set_value(value)
        self.db.insert_or_update('OpParam', ('op_id', 'param_id'),
                            param_id = param_id,
                            op_id = op_id,
                            json_value = json.dumps(value)
                        )
        self.db.commit()
    def __getitem__(self, op_id):
        return self.info_per_op_id[op_id]
    def __iter__(self):
        # iterate over op_id values
        return self.info_per_op_id.__iter__()
    def get_gui_data(self, op_id):
        return self[op_id].gui_data
    def set_gui_data(self, op_id, gui_data):
        self[op_id].gui_data = gui_data
        self.db.update('OpInstance', 'op_id',
                    op_id = op_id, gui_data = gui_data)
        self.db.commit()
