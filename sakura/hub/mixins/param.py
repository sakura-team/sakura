class OpParamMixin:
    @property
    def remote_param(self):
        return self.op.remote_instance.parameters[self.param_id]
    def setup(self):
        self.remote_param.setup(self.value, self.retrieve_auto_filled)
    def set_value(self, gui_value):
        self.remote_param.set_requested_gui_value(gui_value)
        self.value = self.remote_param.recheck()
        self.op.check_move()
    def retrieve_auto_filled(self):
        print('retrieve_auto_filled')
        if self.value is None:
            value = self.remote_param.get_value()
            if value is not None:
                self.value = value
                # the parameter auto-selected a default value,
                # record it to be able to restore it later
                self.remote_param.set_requested_value(self.value)
    def recheck(self):
        return self.remote_param.recheck()
    @property
    def is_valid(self):
        return self.remote_param.selected()
    @classmethod
    def lookup(cls, op, param_id):
        param = cls.get(op = op, param_id = param_id)
        if param is None:
            param = cls(op = op, param_id = param_id)
        return param
