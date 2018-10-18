class APIOperator:
    def __new__(cls, remote_api, dataflow, op_cls):
        info = remote_api.operators.create(dataflow.dataflow_id, op_cls.id)
        op_id = info['op_id']
        remote_obj = remote_api.operators[op_id]
        class APIOperatorImpl:
            def __init__(self, dataflow, op_cls):
                self.dataflow = dataflow
                self.op_class = op_cls
            def __getattr__(self, attr):
                if attr in info:
                    return info[attr]
                else:
                    raise AttributeError('No such attribute "%s"' % attr)
            def __repr__(self):
                return '<Sakura ' + op_cls.name + ' Operator>'
            def __del__(self):
                remote_obj.delete()
        return APIOperatorImpl(dataflow, op_cls)
