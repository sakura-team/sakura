class GuiToHubAPI(object):
    def __init__(self, context):
        self.context = context
    
    def list_daemons(self):
        return list(self.context.list_daemons_serializable())

    def list_operators_classes(self):
        return self.context.list_op_classes_serializable()

    # instantiate an operator and return the instance id
    def create_operator_instance(self, cls_id):
        return self.context.create_operator_instance(cls_id)
    
    # delete operator instance and links involved
    def delete_operator_instance(self, op_id):
        return self.context.delete_operator_instance(op_id)
    
    # returns info about operator instance: cls_name, inputs, outputs & parameters
    def get_operator_instance_info(self, op_id):
        return self.context.op_instances.get_info_serializable(op_id)
    
    def set_parameter_value(self, op_id, param_id, value):
        return self.context.op_instances.set_parameter_value(op_id, param_id, value)

    #MIKE START
    def list_operator_instances(self):
        raise NotImplementedError
    #MIKE SEND
    
    def create_link(self, src_op_id, src_out_id, dst_op_id, dst_in_id):
        return self.context.create_link(src_op_id, src_out_id, dst_op_id, dst_in_id)
    
    def delete_link(self, link_id):
        return self.context.delete_link(link_id)
    
    #MIKE START
    def list_links(self):
        raise NotImplementedError
    #MIKE END
    
    def get_operator_input_range(self, op_id, in_id, row_start, row_end):
        raise NotImplementedError
    
    def get_operator_output_range(self, op_id, out_id, row_start, row_end):
        raise NotImplementedError
