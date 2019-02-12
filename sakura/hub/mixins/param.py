class OpParamMixin:
    @property
    def remote_param(self):
        return self.op.remote_instance.parameters[self.param_id]
    def restore(self):
        if self.value is not None:
            self.remote_param.set_requested_value(self.value)
        self.resync()
    def set_value(self, value):
        # on remote instance
        self.remote_param.set_requested_value(value)
        self.remote_param.resync()
        # on local db
        self.value = value
    def resync(self):
        value = self.remote_param.resync()
        if self.value is None and value is not None:
            self.value = value
    @property
    def is_valid(self):
        return self.remote_param.selected()
    @classmethod
    def lookup(cls, op, param_id):
        param = cls.get(op = op, param_id = param_id)
        if param is None:
            param = cls(op = op, param_id = param_id)
        return param
