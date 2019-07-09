from sakura.client.opskeleton.plug import generate_input_plugs, generate_output_plugs
from sakura.client.opskeleton.param import generate_params
from sakura.client.opskeleton.tab import generate_tabs

class SkeletonInfo:
    def __init__(self, op_name, num_inputs, num_outputs, param_classes, num_tabs):
        self.op_name = op_name
        if op_name.endswith('Op'):
            self.op_cls_name = op_name[:-2] + 'Operator'
        elif op_name.endswith('Operator'):
            self.op_cls_name = op_name
        else:
            self.op_cls_name = op_name + 'Operator'
        self.param_classes = param_classes
        self.num_tabs = num_tabs
        self.inputs = generate_input_plugs(num_inputs)
        self.params = generate_params(param_classes, self.inputs)
        self.outputs = generate_output_plugs(num_outputs, self.inputs, self.params)
        self.tabs = generate_tabs(num_tabs, self.inputs, self.params)
