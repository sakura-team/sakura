class GuiToHubAPI(object):
    def __init__(self, context):
        self.context = context
        #MIKE START
        self.operator_instance_ids  = -1
        self.link_ids               = -1
        #MIKE SEND
    
    def list_daemons(self, *args, **kwargs):
        return self.context.list_daemons()
    
    def list_operators_classes(self):
        return self.context.list_op_classes()
    
    # instantiate an operator and return the instance id
    def create_operator_instance(self, cls_id):
        #MIKE START
        self.operator_instance_ids += 1
        return self.operator_instance_ids
        #MIKE SEND
    
    # delete operator instance and links involved
    def delete_operator_instance(self, op_id):
        #MIKE START
        if True:
            return 1
        else:
            return 0
        #MIKE SEND
    
    def get_operator_input_info(self, op_id):
        raise NotImplementedError
    
    def get_operator_output_info(self, op_id):
        raise NotImplementedError
    
    #MIKE START
    def list_operator_instances(self):
        raise NotImplementedError
    #MIKE SEND
    
    def create_link(self, src_op_id, src_out_id, dst_op_id, dst_in_id):
        #MIKE START
        self.link_ids += 1
        return self.link_ids
        #MIKE SEND
    
    def delete_link(self, link_id):
        #MIKE START
        if True:
            return 1
        else:
            return 0
        #MIKE SEND
    
    #MIKE START
    def list_links(self):
        raise NotImplementedError
    #MIKE END
    
    def get_operator_input_range(self, op_id, in_id, row_start, row_end):
        raise NotImplementedError
    
    def get_operator_output_range(self, op_id, out_id, row_start, row_end):
        raise NotImplementedError
