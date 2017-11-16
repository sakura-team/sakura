class OpParamMixin:
    @property
    def remote_param(self):
        return self.op.remote_instance.parameters[self.param_id]
    def udpate_on_daemon(self):
        # if the operator has been modified, it may actually
        # have less parameters than before.
        num_params = self.op.remote_instance.get_num_parameters()
        if self.param_id < num_params:
            self.remote_param.set_value(self.value)
        else:
            self.delete()
    def set_value(self, value):
        # on remote instance
        self.remote_param.set_value(value)
        # on local db
        self.value = value
    @classmethod
    def lookup(cls, op, param_id):
        param = cls.get(op = op, param_id = param_id)
        if param is None:
            param = cls(op = op, param_id = param_id)
        return param
