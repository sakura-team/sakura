class GuiToHubAPI(object):
    def __init__(self, context):
        self.context = context
        self.project_id = 0     # for now
        
    
    ########################################
    # Daemons
    def list_daemons(self):
        return self.context.daemons
    
    ########################################
    # Operators
    
    def list_operators_classes(self):
        return self.context.op_classes
    
    def list_operators_instance_ids(self):
        return tuple(op.id for op in self.context.op_instances.select())
    
    # instantiate an operator and return the instance info
    def create_operator_instance(self, cls_id):
        return self.context.op_instances.create_instance(self.context, cls_id)
    
    # delete operator instance and links involved
    def delete_operator_instance(self, op_id):
        return self.context.op_instances[op_id].delete_instance()
    
    # returns info about operator instance: cls_name, inputs, outputs, parameters
    def get_operator_instance_info(self, op_id):
        return self.context.op_instances[op_id]
    
    def set_parameter_value(self, op_id, param_id, value):
        return self.context.op_params.lookup(op_id, param_id).set_value(value)
    
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
        return tuple(l.id for l in self.context.links.select())
    
    def get_link_info(self, link_id):
        return self.context.links[link_id]
    
    def create_link(self, src_op_id, src_out_id, dst_op_id, dst_in_id):
        return self.context.create_link(src_op_id, src_out_id, dst_op_id, dst_in_id)
    
    def delete_link(self, link_id):
        return self.context.links[link_id].delete_link()

    def get_possible_links(self, src_op_id, dst_op_id):
        return self.context.get_possible_links(src_op_id, dst_op_id)
    
    ########################################
    # Gui
    def set_operator_instance_gui_data(self, op_id, gui_data):
        self.context.op_instances[op_id].gui_data = gui_data

    def get_operator_instance_gui_data(self, op_id):
        return self.context.op_instances[op_id].gui_data

    def set_project_gui_data(self, project_gui_data):
        self.context.projects.set_gui_data(self.project_id, project_gui_data)
    
    def get_project_gui_data(self):
        return self.context.projects.get_gui_data(self.project_id)
    
    def set_link_gui_data(self, link_id, gui_data):
        self.context.links[link_id].gui_data = gui_data

    def get_link_gui_data(self, link_id):
        return self.context.links[link_id].gui_data

    ########################################
    # Databases
    def list_datastores(self):
        return self.context.datastores
    
    def list_databases(self):
        return self.context.databases
    
    def get_database_info(self, database_id):
        return self.context.databases[database_id].get_full_info(self.context)

    def new_database(self, datastore_id, name, **kwargs):
        # optional arguments of kwargs: short_desc, creation_date, tags, contacts
        # returns the database_id
        datastore = self.context.datastores[datastore_id]
        return self.context.databases.create_db(
                        self.context, datastore, name, **kwargs)

    def update_database_info(self, database_id, **kwargs):
        # optional arguments of kwargs: name, short_desc, creation_date, tags, contacts
        self.context.databases[database_id].update_metadata(self.context, **kwargs)

    def list_expected_columns_tags(self, datastore_id):
        # il y a les tags standards auxquels on ajoute
        # les tags deja rencontres sur ce datastore
        return (
            ("statistics", ("qualitative", "quantitative", "textual")),
            ("processing", ("sorted_asc", "sorted_desc", "unique")),
            ("others", ("longitude", "latitude"))
        )

    def get_table_info(self, table_id):
        return self.context.tables[table_id]

    def new_table(self, database_id, name, columns, **kwargs):
        # optional arguments of kwargs: short_desc, creation_date
        # returns the table_id
        database = self.context.databases[database_id]
        return self.context.tables.create_table(
                        self.context, database, name, columns, **kwargs)

    def update_table_info(self, table_id, **kwargs):
        # optional arguments of kwargs: name, description, creation_date
        self.context.tables[table_id].set(**kwargs)

    def add_rows_into_table(self, table_id, data, date_formats):
        print(data)
        print(date_formats)
        return True
    
    def get_rows_from_table(self, table_id, row_start, row_end):
        import numpy as np
        
        print('Asking for rows of table:', table_id )
        rows = np.arange(200).reshape((200, 1))
        print('Sending', rows[row_start: row_end])
        
        return rows[row_start: row_end]

    # User Management
    ########################################
    def set_user_account(self, userAccountValues):
        print(userAccountValues)
        sampleDBDict = {
        'ritesh': {'signUpEmail': 'ritesh.shah@imag.fr', 'signUpPassword': 'a', 'signUpConfirmPassword': 'a', 'signUpFirstName': 'aa', 'signUpLastName': 'a', 'gender': 'M', 'signUpCountry': 'a', 'signUpInstitution': 'a', 'signUpStatus': '', 'signUpDomain': '', 'signInCGU': 'cguNotRead'},

        'mike': {'signUpEmail': 'Michael.Ortega@imag.fr', 'signUpPassword': 'a', 'signUpConfirmPassword': 'a', 'signUpFirstName': 'aa', 'signUpLastName': 'a', 'gender': 'M', 'signUpCountry': 'a', 'signUpInstitution': 'a', 'signUpStatus': '', 'signUpDomain': '', 'signInCGU': 'cguNotRead'},

        'etienne': {'signUpEmail': 'etienne.duble@imag.fr', 'signUpPassword': 'a', 'signUpConfirmPassword': 'a', 'signUpFirstName': 'aa', 'signUpLastName': 'a', 'gender': 'M', 'signUpCountry': 'a', 'signUpInstitution': 'a', 'signUpStatus': '', 'signUpDomain': '', 'signInCGU': 'cguNotRead'}
        }
        if userAccountValues:
            if userAccountValues["loginName"] in sampleDBDict.keys():
                print ("loginName matches in DB")
                return False
            for existingLoginName in sampleDBDict.keys():
                print ("looking at sampleDBDict info entries")
                if sampleDBDict[existingLoginName]["signUpEmail"] == userAccountValues["signUpEmail"]:
                    print ("email matches in DB")
                    return False;
            # none of the entries contain the new email so add the information
            sampleDBDict[userAccountValues.pop("loginName")] = userAccountValues #adding a new user to sampleDB
            print ("user information added")
            return True;
