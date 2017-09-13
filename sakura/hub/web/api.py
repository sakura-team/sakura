class GuiToHubAPI(object):
    def __init__(self, context):
        self.context = context
        self.project_id = 0     # for now
    
    ########################################
    # Daemons
    def list_daemons(self):
        return list(self.context.list_daemons_serializable())
    
    
    ########################################
    # Operators
    
    def list_operators_classes(self):
        return self.context.list_op_classes_serializable()
    
    def list_operators_instance_ids(self):
        return list(self.context.op_instances)
    
    # instantiate an operator and return the instance info
    def create_operator_instance(self, cls_id):
        return self.context.create_operator_instance(cls_id)
    
    # delete operator instance and links involved
    def delete_operator_instance(self, op_id):
        return self.context.delete_operator_instance(op_id)
    
    # returns info about operator instance: cls_name, inputs, outputs, parameters
    def get_operator_instance_info(self, op_id):
        return self.context.op_instances.pack(op_id)
    
    def set_parameter_value(self, op_id, param_id, value):
        return self.context.op_instances.set_parameter_value(op_id, param_id, value)
    
    def get_operator_input_range(self, op_id, in_id, row_start, row_end):
        return self.context.op_instances[op_id].input_streams[in_id].get_range(row_start, row_end)
    
    def get_operator_output_range(self, op_id, out_id, row_start, row_end):
        if not self.context.op_instances[op_id].is_ready():
            return None
        return self.context.op_instances[op_id].output_streams[out_id].get_range(row_start, row_end)
    
    def get_operator_internal_range(self, op_id, intern_id, row_start, row_end):
        return self.context.op_instances[op_id].internal_streams[intern_id].get_range(row_start, row_end)
    
    def fire_operator_event(self, op_id, event):
        return self.context.op_instances[op_id].sync_handle_event(event)
    
    ########################################
    # Operator files

    def get_operator_file_content(self, op_id, file_path):
        return self.context.op_instances[op_id].get_file_content(file_path)

    def get_operator_file_tree(self, op_id):
        return self.context.op_instances[op_id].get_file_tree()

    def save_operator_file_content(self, op_id, file_path, file_content):
        return self.context.op_instances[op_id].save_file_content(file_path, file_content)

    def new_operator_file(self, op_id, file_path, file_content):
        return self.context.op_instances[op_id].new_file(file_path, file_content)

    def new_operator_directory(self, op_id, dir_path):
        return self.context.op_instances[op_id].new_directory(dir_path)

    def move_operator_file(self, op_id, file_src, file_dst):
        return self.context.op_instances[op_id].move_file(file_src, file_dst)

    def delete_operator_file(self, op_id, file_path):
        return self.context.op_instances[op_id].delete_file(file_path)
    
    ########################################
    # Links
    def list_link_ids(self):
        return list(self.context.links)
    
    def get_link_info(self, link_id):
        return self.context.links[link_id]
    
    def create_link(self, src_op_id, src_out_id, dst_op_id, dst_in_id):
        return self.context.create_link(src_op_id, src_out_id, dst_op_id, dst_in_id)
    
    def delete_link(self, link_id):
        return self.context.delete_link(link_id)

    def get_possible_links(self, src_op_id, dst_op_id):
        return self.context.get_possible_links(src_op_id, dst_op_id)
    
    ########################################
    # Gui
    def set_operator_instance_gui_data(self, op_id, gui_data):
        self.context.op_instances.set_gui_data(op_id, gui_data)
    
    def get_operator_instance_gui_data(self, op_id):
        return self.context.op_instances.get_gui_data(op_id)
    
    def set_project_gui_data(self, project_gui_data):
        self.context.set_project_gui_data(self.project_id, project_gui_data)
    
    def get_project_gui_data(self):
        return self.context.get_project_gui_data(self.project_id)

    def set_link_gui_data(self, link_id, gui_data):
        self.context.links.set_gui_data(link_id, gui_data)

    def get_link_gui_data(self, link_id):
        return self.context.links.get_gui_data(link_id)

    ########################################
    # Databases
    def list_datastores(self):
        return self.context.datastores.list()

    def list_databases(self):
        return self.context.databases.list()

    def get_database_info(self, database_id):
        return self.context.get_database_info(database_id)
