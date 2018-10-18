def get_plug_impl_cls(remote_obj, op_id, plug_id):
    class APIOperatorPlugImpl:
        @property
        def op_id(self):
            return op_id
        @property
        def plug_id(self):
            return plug_id
        def get_range(self, row_start, row_end):
            return remote_obj.get_range(row_start, row_end)
        def __getattr__(self, attr):
            info = remote_obj.info()
            print(repr(info))
            if attr in info:
                return info[attr]
            else:
                raise AttributeError('No such attribute "%s"' % attr)
        def __repr__(self):
            return '<Sakura operator plug>'
    return APIOperatorPlugImpl

class APIOperatorInput:
    def __new__(cls, remote_api, op_id, in_id):
        remote_obj = remote_api.operators[op_id].inputs[in_id]
        plug_cls = get_plug_impl_cls(remote_obj, op_id, in_id)
        class APIOperatorInputImpl(plug_cls):
            pass
        return APIOperatorInputImpl()

class APIOperatorOutput:
    def __new__(cls, remote_api, op_id, out_id):
        remote_obj = remote_api.operators[op_id].outputs[out_id]
        plug_cls = get_plug_impl_cls(remote_obj, op_id, out_id)
        class APIOperatorOutputImpl(plug_cls):
            def connect(self, input_plug):
                remote_api.links.create(
                        self.op_id, self.plug_id, input_plug.op_id, input_plug.plug_id)
            def disconnect(self):
                link_id = remote_obj.get_link_id()
                if link_id is not None:
                    remote_api.links[link_id].delete()
        return APIOperatorOutputImpl()
