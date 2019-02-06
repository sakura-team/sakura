class OpParamMixin:
    @property
    def remote_param(self):
        return self.op.remote_instance.parameters[self.param_id]
    def update_on_daemon(self):
        # if the operator has been modified, it may actually
        # have less parameters than before.
        num_params = self.op.remote_instance.get_num_parameters()
        if self.param_id < num_params:
            self.remote_param.set_value(self.value)
        else:
            self.delete()
    def set_value(self, value):
        # on local db
        self.value = value
        self._database_.commit()
        # on remote instance
        self.update_on_daemon()
        # refresh any other parameter linked to this one
        self.op.remote_instance.auto_fill_parameters()
        # if needed, try to relocate the operator
        if self.op._trigger_env_affinity_update():
            self.op.move()
    @classmethod
    def lookup(cls, op, param_id):
        param = cls.get(op = op, param_id = param_id)
        if param is None:
            param = cls(op = op, param_id = param_id)
        return param
