from sakura.client.apiobject.base import APIObjectBase

# factorize here what's common to input and output plugs
def get_plug_impl_cls(remote_obj, op_id, plug_id):
    class APIOperatorPlugImpl(APIObjectBase):
        @property
        def _op_id(self):
            return op_id
        @property
        def _plug_id(self):
            return plug_id
        def get_range(self, row_start, row_end):
            """Query a range of records"""
            return remote_obj.get_range(row_start, row_end)
        def __get_remote_info__(self):
            return remote_obj.info()
    return APIOperatorPlugImpl

class APIOperatorInput:
    def __new__(cls, remote_api, op_id, in_id, in_info):
        remote_obj = remote_api.operators[op_id].inputs[in_id]
        plug_cls = get_plug_impl_cls(remote_obj, op_id, in_id)
        class APIOperatorInputImpl(plug_cls):
            __doc__ = """Sakura plug: """ + in_info['label']
        return APIOperatorInputImpl()

class APIOperatorOutput:
    def __new__(cls, remote_api, op_id, out_id, out_info):
        remote_obj = remote_api.operators[op_id].outputs[out_id]
        plug_cls = get_plug_impl_cls(remote_obj, op_id, out_id)
        class APIOperatorOutputImpl(plug_cls):
            __doc__ = """Sakura plug: """ + out_info['label']
            def connect(self, input_plug):
                """Connect to the input plug of another operator"""
                remote_api.links.create(
                        self._op_id, self._plug_id, input_plug._op_id, input_plug._plug_id)
            def disconnect(self):
                """Disconnect this output plug"""
                link_id = remote_obj.get_link_id()
                if link_id is not None:
                    remote_api.links[link_id].delete()
        return APIOperatorOutputImpl()
