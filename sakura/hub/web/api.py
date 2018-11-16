from sakura.hub.web.apitools import api_init

api = api_init()

@api
class GuiToHubAPI:
    def __init__(self, context):
        self.context = context

    ########################################
    # Daemons
    @api.daemons.list
    def list_daemons(self):
        return self.context.daemons

    ########################################
    # Datastores
    @api.datastores.__getitem__.grants.request
    def request_datastore_grant(self, datastore_id, grant_name, text):
        return self.datastores[datastore_id].handle_grant_request(grant_name, text)

    ########################################
    # Operators
    @api.op_classes.list
    def list_operators_classes(self):
        return self.context.op_classes

    @api.op_classes.__getitem__.info
    def get_operator_class_info(self, cls_id):
        return self.context.op_classes[cls_id]

    # instantiate an operator and return the instance info
    @api.operators.create
    def create_operator_instance(self, dataflow_id, cls_id):
        return self.dataflows[dataflow_id].create_operator_instance(cls_id)

    # delete operator instance and links involved
    @api.operators.__getitem__.delete
    def delete_operator_instance(self, op_id):
        return self.context.op_instances[op_id].delete_instance()

    # returns info about operator instance: cls_name, inputs, outputs, parameters
    @api.operators.__getitem__.info
    def get_operator_instance_info(self, op_id):
        return self.context.op_instances[op_id]

    @api.operators.__getitem__.parameters.__getitem__.set_value
    def set_parameter_value(self, op_id, param_id, value):
        return self.context.op_params.lookup(op_id, param_id).set_value(value)

    @api.operators.__getitem__.inputs.__getitem__.info
    def get_operator_input_info(self, op_id, in_id):
        return self.context.op_instances[op_id].input_plugs[in_id]

    @api.operators.__getitem__.inputs.__getitem__.get_range
    def get_operator_input_range(self, op_id, in_id, row_start, row_end):
        return self.context.op_instances[op_id].input_plugs[in_id].get_range(row_start, row_end)

    @api.operators.__getitem__.outputs.__getitem__.info
    def get_operator_output_info(self, op_id, out_id):
        return self.context.op_instances[op_id].output_plugs[out_id]

    @api.operators.__getitem__.outputs.__getitem__.get_range
    def get_operator_output_range(self, op_id, out_id, row_start, row_end):
        return self.context.op_instances[op_id].output_plugs[out_id].get_range(row_start, row_end)

    @api.operators.__getitem__.outputs.__getitem__.get_link_id
    def get_operator_outputplug_link_id(self, op_id, out_id):
        return self.context.op_instances[op_id].get_ouputplug_link_id(out_id)

    @api.operators.__getitem__.internals.__getitem__.get_range
    def get_operator_internal_range(self, op_id, intern_id, row_start, row_end):
        return self.context.op_instances[op_id].internal_plugs[intern_id].get_range(row_start, row_end)

    @api.operators.__getitem__.fire_event
    def fire_operator_event(self, op_id, *args, **kwargs):
        return self.context.op_instances[op_id].sync_handle_event(*args, **kwargs)

    ########################################
    # Operator files

    @api.operators.__getitem__.get_file_content
    def get_operator_file_content(self, op_id, file_path):
        return self.context.op_instances[op_id].get_file_content(file_path)

    @api.operators.__getitem__.get_file_tree
    def get_operator_file_tree(self, op_id):
        return self.context.op_instances[op_id].get_file_tree()

    @api.operators.__getitem__.save_file_content
    def save_operator_file_content(self, op_id, file_path, file_content):
        return self.context.op_instances[op_id].save_file_content(file_path, file_content)

    @api.operators.__getitem__.create_file
    def new_operator_file(self, op_id, file_path, file_content):
        return self.context.op_instances[op_id].new_file(file_path, file_content)

    @api.operators.__getitem__.create_directory
    def new_operator_directory(self, op_id, dir_path):
        return self.context.op_instances[op_id].new_directory(dir_path)

    @api.operators.__getitem__.move_file
    def move_operator_file(self, op_id, file_src, file_dst):
        return self.context.op_instances[op_id].move_file(file_src, file_dst)

    @api.operators.__getitem__.delete_file
    def delete_operator_file(self, op_id, file_path):
        return self.context.op_instances[op_id].delete_file(file_path)

    ########################################
    # Links
    @api.links.__getitem__.info
    def get_link_info(self, link_id):
        return self.context.links[link_id]

    @api.links.create
    def create_link(self, src_op_id, src_out_id, dst_op_id, dst_in_id):
        return self.context.create_link(src_op_id, src_out_id, dst_op_id, dst_in_id)

    @api.links.__getitem__.delete
    def delete_link(self, link_id):
        return self.context.links[link_id].delete_link()

    @api.links.list_possible
    def get_possible_links(self, src_op_id, dst_op_id):
        return self.context.get_possible_links(src_op_id, dst_op_id)

    ########################################
    # Gui
    @api.operators.__getitem__.set_gui_data
    def set_operator_instance_gui_data(self, op_id, gui_data):
        self.context.op_instances[op_id].gui_data = gui_data

    @api.operators.__getitem__.get_gui_data
    def get_operator_instance_gui_data(self, op_id):
        return self.context.op_instances[op_id].gui_data

    @api.links.__getitem__.set_gui_data
    def set_link_gui_data(self, link_id, gui_data):
        self.context.links[link_id].gui_data = gui_data

    @api.links.__getitem__.get_gui_data
    def get_link_gui_data(self, link_id):
        return self.context.links[link_id].gui_data

    ########################################
    # Databases
    @property
    def datastores(self):
        return self.context.datastores.filter_for_current_user()

    @property
    def databases(self):
        return self.context.databases.filter_for_current_user()

    @api.datastores.list
    def list_datastores(self):
        return self.datastores

    @api.datastores.__getitem__.update
    def update_datastore_info(self, datastore_id, **kwargs):
        self.datastores[datastore_id].parse_and_update_attributes(**kwargs)

    @api.datastores.__getitem__.grants.update
    def update_datastore_grant(self, datastore_id, login, grant_name):
        return self.datastores[datastore_id].update_grant(login, grant_name)

    @api.databases.list
    def list_databases(self):
        return self.databases

    @api.databases.__getitem__.info
    def get_database_info(self, database_id):
        return self.databases[database_id].get_full_info()

    @api.databases.create
    def new_database(self, datastore_id, name, **kwargs):
        # optional arguments of kwargs: short_desc, creation_date, tags, contacts
        # returns the database_id
        datastore = self.datastores[datastore_id]
        return self.databases.create_db(datastore, name, **kwargs)

    @api.databases.__getitem__.update
    def update_database_info(self, database_id, **kwargs):
        # optional arguments of kwargs: name, short_desc, creation_date, tags, contacts
        self.databases[database_id].parse_and_update_attributes(**kwargs)

    @api.databases.__getitem__.grants.update
    def update_database_grant(self, database_id, login, grant_name):
        self.databases[database_id].update_grant(login, grant_name)

    @api.databases.__getitem__.grants.request
    def request_database_grant(self, database_id, grant_name, text):
        return self.databases[database_id].handle_grant_request(grant_name, text)

    @api.databases.__getitem__.delete
    def delete_database(self, database_id):
        return self.context.databases[database_id].delete_database()

    @api.datastores.__getitem__.list_expected_columns_tags
    def list_expected_columns_tags(self, datastore_id):
        return self.datastores[datastore_id].list_expected_columns_tags()

    @api.tables.__getitem__.info
    def get_table_info(self, table_id):
        return self.context.tables[table_id]

    @api.tables.create
    def new_table(self, database_id, name, columns, **kwargs):
        # optional arguments of kwargs: short_desc, creation_date
        # returns the table_id
        database = self.databases[database_id]
        return self.context.tables.create_table(
                        database, name, columns, **kwargs)

    @api.tables.__getitem__.update
    def update_table_info(self, table_id, **kwargs):
        # optional arguments of kwargs: name, description, creation_date
        self.context.tables[table_id].set(**kwargs)

    @api.tables.__getitem__.add_rows
    def add_rows_into_table(self, table_id, data):
        return self.context.tables[table_id].add_rows(data)

    @api.tables.__getitem__.get_rows
    def get_rows_from_table(self, table_id, row_start, row_end):
        return self.context.tables[table_id].get_range(row_start, row_end)

    @api.tables.__getitem__.delete
    def delete_table(self, table_id):
        return self.context.tables[table_id].delete_table()

    ########################################
    # Dataflow
    @property
    def dataflows(self):
        return self.context.dataflows.filter_for_current_user()

    @api.dataflows.__getitem__.info
    def get_dataflow_info(self, dataflow_id):
        return self.dataflows[dataflow_id].get_full_info()

    @api.dataflows.list
    def list_dataflows(self):
        return self.dataflows.pack()

    @api.dataflows.create
    def new_dataflow(self, name, **kwargs):
        return self.dataflows.create_dataflow(name = name, **kwargs)

    @api.dataflows.__getitem__.update
    def update_dataflow_info(self, dataflow_id, **kwargs):
        self.dataflows[dataflow_id].parse_and_update_attributes(**kwargs)

    @api.dataflows.__getitem__.grants.update
    def update_dataflow_grant(self, dataflow_id, login, grant_name):
        return self.dataflows[dataflow_id].update_grant(login, grant_name)

    @api.dataflows.__getitem__.grants.request
    def request_dataflow_grant(self, dataflow_id, grant_name, text):
        return self.dataflows[dataflow_id].handle_grant_request(grant_name, text)

    @api.dataflows.__getitem__.set_gui_data
    def set_dataflow_gui_data(self, dataflow_id, gui_data):
        self.dataflows[dataflow_id].gui_data = gui_data

    @api.dataflows.__getitem__.get_gui_data
    def get_dataflow_gui_data(self, dataflow_id):
        return self.dataflows[dataflow_id].gui_data

    @api.dataflows.__getitem__.delete
    def delete_dataflow(self, dataflow_id):
        return self.dataflows[dataflow_id].delete_dataflow()

    # Session management
    ####################
    @api.renew_session
    def renew_session(self):
        return self.context.session.renew()

    # User management
    #################
    @api.users.create
    def new_user(self, **user_info):
        return self.context.users.new_user(**user_info)

    @api.login
    def login(self, login_or_email, password):
        self.context.session.user = self.context.users.from_credentials(login_or_email, password)
        return self.context.session.user.login

    @api.logout
    def logout(self):
        self.context.session.user = None

    @api.recover_password
    def recover_password(self, login_or_email):
        self.context.users.recover_password(login_or_email)

    @api.change_passord
    def change_password(self, login_or_email, current_password_or_rec_token, new_password):
        self.context.users.change_password(
                login_or_email, current_password_or_rec_token, new_password)

    @api.users.current.info
    def get_current_login_name(self):
        return None if self.context.user is None else self.context.user

    @api.users.list
    def list_all_users(self):
        return tuple(u.login for u in self.context.users.select())

    # Transfers management
    ######################
    @api.transfers.start
    def start_transfer(self):
        return self.context.start_transfer() # return transfer_id

    @api.transfers.__getitem__.get_status
    def get_transfer_status(self, transfer_id):
        return self.context.get_transfer_status(transfer_id)

    @api.transfers.__getitem__.abort
    def abort_transfer(self, transfer_id):
        return self.context.abort_transfer(transfer_id)
