class GuiToHubAPI(object):
    def __init__(self, context, session):
        self.context = context
        self.project_id = 0     # for now
        self.session_id = session.id

    # We cannot simply keep the session object we got
    # at __init__() call, because it is a pony db object
    # thus its scope is limited to a db session.
    # And for each call, we get a different db session.
    # Thus we use a property below, in order to get
    # an object valid for the current db session.
    @property
    def session(self):
        return self.context.sessions[self.session_id]

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
        self.context.databases[database_id].update_attributes(self.context, **kwargs)

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
    
    def delete_table(self, table_id):
        return None
    
    def update_table_info(self, table_id, **kwargs):
        # optional arguments of kwargs: name, description, creation_date
        self.context.tables[table_id].set(**kwargs)

    def add_rows_into_table(self, table_id, data):
        return self.context.tables[table_id].add_rows(data)

    def get_rows_from_table(self, table_id, row_start, row_end):
        return self.context.tables[table_id].get_range(row_start, row_end)

    def delete_table(self, table_id):
        return self.context.tables[table_id].delete_table()

    ########################################
    # Analysis
    def get_analysis_info(self, analysis_id):
        return {'name': 'texting name', 'short_desc': 'testing short description'}
    
    def list_analyses(self):
        return None
    
    # Session management
    ####################
    def renew_session(self):
        return self.session.renew()

    def generate_session_secret(self):
        return self.context.session_secrets.generate_secret(self.session)

    # User management
    #################
    def new_user(self, **user_info):
        return self.context.users.new_user(self.context, **user_info)

    def login(self, login_or_email, password):
        self.session.user = self.context.users.from_credentials(self.context, login_or_email, password)
        return self.session.user.login

    def logout(self):
        self.session.user = None

    def recover_password(self, login_or_email):
        self.context.users.recover_password(self.context, login_or_email)

    def change_password(self, login_or_email, current_password_or_rec_token, new_password):
        self.context.users.change_password(self.context,
                login_or_email, current_password_or_rec_token, new_password)
