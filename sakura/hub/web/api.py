from sakura.hub.web.apitools import api_init, pack
from sakura.hub.code import list_code_revisions, list_operator_subdirs
from sakura.common.events import EventsAggregator

api = api_init()
EVENTS = EventsAggregator()

# Caution: this GuiToHubAPI class is instanciated once for each web connection!
@api
class GuiToHubAPI:

    def __init__(self, context):
        self.context = context

    # Events
    ########################################
    @property
    def event_listener_id(self):
        # use the web session ID to uniquely identify this event listener
        return self.context.session.id

    def events_monitor(self, obj, obj_id):
        EVENTS.monitor(self.event_listener_id, obj.all_events, obj_id)

    @api.events.unmonitor
    def events_unmonitor(self, obj_id):
        EVENTS.unmonitor(self.event_listener_id, obj_id)

    @api.events.next_events
    def events_next_events(self, timeout):
        evts = EVENTS.next_events(self.event_listener_id, timeout)
        for evt in evts:
            print('notify to GUI', *evt)
        return evts

    ########################################
    # Daemons
    @api.daemons.list
    def list_daemons(self):
        return pack(self.context.daemons)


    ########################################
    # Operator classes
    @property
    def op_classes(self):
        return self.context.op_classes.filter_for_current_user()

    @api.op_classes.list
    def list_operators_classes(self):
        return pack(self.op_classes)

    @api.op_classes.__getitem__.info
    def get_operator_class_info(self, cls_id):
        return pack(self.op_classes[cls_id])

    @api.op_classes.register
    def register_op_class(self, **cls_repo_info):
        return self.op_classes.register(self.context, **cls_repo_info)

    @api.op_classes.__getitem__.unregister
    def unregister_op_class(self, cls_id):
        return self.op_classes[cls_id].unregister()

    @api.op_classes.__getitem__.update_default_revision
    def update_op_class_default_revision(self, cls_id, code_ref, commit_hash):
        return self.op_classes[cls_id].update_default_revision(code_ref, commit_hash)

    ########################################
    # Operator instances

    # instantiate an operator and return the instance info
    @api.operators.create
    def create_operator_instance(self, dataflow_id, cls_id, local_streams=None):
        op = self.dataflows[dataflow_id].create_operator_instance(cls_id, local_streams=local_streams)
        return op.pack()

    # delete operator instance and links involved
    @api.operators.__getitem__.delete
    def delete_operator_instance(self, op_id):
        return self.context.op_instances[op_id].delete_instance()

    # returns info about operator instance: cls_name, inputs, outputs, parameters
    @api.operators.__getitem__.info
    def get_operator_instance_info(self, op_id):
        return pack(self.context.op_instances[op_id])

    @api.operators.__getitem__.monitor
    def operator_instance_monitor(self, op_id, obj_id):
        self.events_monitor(self.context.op_instances[op_id], obj_id)

    @api.operators.__getitem__.reload
    def update_op_revision(self, op_id):
        return self.context.op_instances[op_id].reload()

    @api.operators.__getitem__.update_revision
    def update_op_revision(self, op_id, code_ref, commit_hash, all_ops_of_cls=False):
        return self.context.op_instances[op_id].update_revision(code_ref, commit_hash, all_ops_of_cls)

    @api.operators.__getitem__.parameters.__getitem__.set_value
    def set_parameter_value(self, op_id, param_id, value):
        return self.context.op_params.lookup(op_id, param_id).set_value(value)

    @api.operators.__getitem__.inputs.__getitem__.info
    def get_operator_input_info(self, op_id, in_id):
        return pack(self.context.op_instances[op_id].input_plugs[in_id])

    @api.operators.__getitem__.inputs.__getitem__.get_range
    def get_operator_input_range(self, op_id, in_id, row_start, row_end):
        return pack(self.context.op_instances[op_id].input_plugs[in_id].get_range(row_start, row_end))

    @api.operators.__getitem__.inputs.__getitem__.chunks
    def get_operator_input_chunks(self, op_id, in_id, allow_approximate=False):
        yield from self.context.op_instances[op_id].input_plugs[in_id].chunks(allow_approximate=allow_approximate)

    @api.operators.__getitem__.outputs.__getitem__.info
    def get_operator_output_info(self, op_id, out_id):
        return pack(self.context.op_instances[op_id].output_plugs[out_id])

    @api.operators.__getitem__.outputs.__getitem__.get_range
    def get_operator_output_range(self, op_id, out_id, row_start, row_end):
        return pack(self.context.op_instances[op_id].output_plugs[out_id].get_range(row_start, row_end))

    @api.operators.__getitem__.outputs.__getitem__.chunks
    def get_operator_output_chunks(self, op_id, out_id, allow_approximate=False):
        yield from self.context.op_instances[op_id].output_plugs[out_id].chunks(allow_approximate=allow_approximate)

    @api.operators.__getitem__.outputs.__getitem__.get_link_id
    def get_operator_outputplug_link_id(self, op_id, out_id):
        return self.context.op_instances[op_id].get_ouputplug_link_id(out_id)

    @api.operators.__getitem__.fire_event
    def fire_operator_event(self, op_id, *args, **kwargs):
        return self.context.op_instances[op_id].sync_handle_event(*args, **kwargs)

    @api.operators.__getitem__.opengl_apps.__getitem__.info
    def get_opengl_app_info(self, op_id, ogl_id):
        return pack(self.context.op_instances[op_id].opengl_apps[ogl_id])

    @api.operators.__getitem__.opengl_apps.__getitem__.fire_event
    def fire_opengl_app_event(self, op_id, ogl_id, *args, **kwargs):
        return self.context.op_instances[op_id].opengl_apps[ogl_id].fire_event(*args, **kwargs)

    @api.operators.__getitem__.opengl_apps.__getitem__.monitor
    def opengl_app_monitor(self, op_id, ogl_id, obj_id):
        self.events_monitor(self.context.op_instances[op_id].opengl_apps[ogl_id], obj_id)

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
        return pack(self.context.links[link_id])

    @api.links.create
    def create_link(self, src_op_id, src_out_id, dst_op_id, dst_in_id):
        return self.context.create_link(src_op_id, src_out_id, dst_op_id, dst_in_id)

    @api.links.__getitem__.delete
    def delete_link(self, link_id):
        return self.context.links[link_id].delete_link()

    @api.links.__getitem__.monitor
    def link_monitor(self, link_id, obj_id):
        self.events_monitor(self.context.links[link_id], obj_id)

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
    # Datastores
    @property
    def datastores(self):
        self.context.datastores.refresh_offline_datastores()
        return self.context.datastores.filter_for_current_user()

    @api.datastores.list
    def list_datastores(self):
        return pack(self.datastores)

    @api.datastores.__getitem__.info
    def get_datastore_info(self, datastore_id):
        return self.datastores[datastore_id].get_full_info()

    @api.datastores.__getitem__.grants.request
    def request_datastore_grant(self, datastore_id, grant_name, text):
        return self.datastores[datastore_id].handle_grant_request(grant_name, text)

    @api.datastores.__getitem__.grants.deny
    def deny_datastore_grant(self, datastore_id, login):
        return self.datastores[datastore_id].deny_grant_request(login)

    @api.datastores.__getitem__.update
    def update_datastore_info(self, datastore_id, **kwargs):
        self.datastores[datastore_id].parse_and_update_attributes(**kwargs)

    @api.datastores.__getitem__.grants.update
    def update_datastore_grant(self, datastore_id, login, grant_name):
        return self.datastores[datastore_id].update_grant(login, grant_name)

    @api.datastores.__getitem__.list_expected_columns_tags
    def list_expected_columns_tags(self, datastore_id):
        return self.datastores[datastore_id].list_expected_columns_tags()

    ########################################
    # Databases
    @property
    def databases(self):
        self.context.datastores.refresh_offline_datastores()
        return self.context.databases.filter_for_current_user()

    @api.databases.list
    def list_databases(self):
        return pack(self.databases)

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

    @api.databases.__getitem__.grants.deny
    def deny_database_grant(self, database_id, login):
        return self.databases[database_id].deny_grant_request(login)

    @api.databases.__getitem__.delete
    def delete_database(self, database_id):
        return self.context.databases[database_id].delete_database()

    ########################################
    # Tables
    @api.tables.__getitem__.info
    def get_table_info(self, table_id):
        return pack(self.context.tables[table_id])

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
        return pack(self.context.tables[table_id].get_range(row_start, row_end))

    @api.tables.__getitem__.chunks
    def get_chunks_from_table(self, table_id, allow_approximate=False):
        yield from self.context.tables[table_id].chunks(allow_approximate=allow_approximate)

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

    @api.dataflows.__getitem__.monitor
    def dataflow_monitor(self, dataflow_id, obj_id):
        self.events_monitor(self.context.dataflows[dataflow_id], obj_id)

    @api.dataflows.__getitem__.update
    def update_dataflow_info(self, dataflow_id, **kwargs):
        self.dataflows[dataflow_id].parse_and_update_attributes(**kwargs)

    @api.dataflows.__getitem__.grants.update
    def update_dataflow_grant(self, dataflow_id, login, grant_name):
        return self.dataflows[dataflow_id].update_grant(login, grant_name)

    @api.dataflows.__getitem__.grants.request
    def request_dataflow_grant(self, dataflow_id, grant_name, text):
        return self.dataflows[dataflow_id].handle_grant_request(grant_name, text)

    @api.dataflows.__getitem__.grants.deny
    def deny_dataflow_grant(self, dataflow_id, login):
        return self.dataflows[dataflow_id].deny_grant_request(login)

    @api.dataflows.__getitem__.set_gui_data
    def set_dataflow_gui_data(self, dataflow_id, gui_data):
        self.dataflows[dataflow_id].gui_data = gui_data

    @api.dataflows.__getitem__.get_gui_data
    def get_dataflow_gui_data(self, dataflow_id):
        return self.dataflows[dataflow_id].gui_data

    @api.dataflows.__getitem__.delete
    def delete_dataflow(self, dataflow_id):
        return self.dataflows[dataflow_id].delete_dataflow()

    ########################################
    # Project
    @property
    def projects(self):
        return self.context.projects.filter_for_current_user()

    @api.projects.__getitem__.info
    def get_project_info(self, project_id):
        return self.projects[project_id].get_full_info()

    @api.projects.list
    def list_projects(self):
        return self.projects.pack()

    @api.projects.create
    def new_project(self, name, **kwargs):
        return self.projects.create_project(name = name, **kwargs)

    @api.projects.__getitem__.update
    def update_project_info(self, project_id, **kwargs):
        self.projects[project_id].parse_and_update_attributes(**kwargs)

    @api.projects.__getitem__.grants.update
    def update_project_grant(self, project_id, login, grant_name):
        return self.projects[project_id].update_grant(login, grant_name)

    @api.projects.__getitem__.grants.request
    def request_project_grant(self, project_id, grant_name, text):
        return self.projects[project_id].handle_grant_request(grant_name, text)

    @api.projects.__getitem__.grants.deny
    def deny_project_grant(self, project_id, login):
        return self.projects[project_id].deny_grant_request(login)

    @api.projects.__getitem__.delete
    def delete_project(self, project_id):
        return self.projects[project_id].delete_project()

    ########################################
    # Project pages
    @property
    def pages(self):
        return self.context.pages.filter_for_current_user()

    @api.pages.create
    def create_project_page(self, project_id, page_name):
        return self.projects[project_id].create_page(page_name)

    @api.pages.__getitem__.info
    def get_project_page_info(self, page_id):
        return self.pages[page_id].pack()

    @api.pages.__getitem__.update
    def update_project_page(self, page_id, page_name=None, page_content=None):
        return self.pages[page_id].update_page(page_name=page_name, page_content=page_content)

    @api.pages.__getitem__.delete
    def delete_project_page(self, page_id):
        return self.pages[page_id].delete_page()

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
        return self.context.login(login_or_email, password)

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

    # Note: you can use 'api.users.current' as a shortcut to 'api.users[<current_login>]'
    #       in the following API calls.

    @api.users.__getitem__.info
    def get_user_info(self, login):
        return self.context.users[login].get_full_info()

    @api.users.__getitem__.update
    def update_user_info(self, login, **kwargs):
        return self.context.users[login].update_attributes(**kwargs)

    @api.users.__getitem__.privileges.request
    def request_user_privilege(self, login, privilege):
        return self.context.users[login].request_privilege(privilege)

    @api.users.__getitem__.privileges.add
    def add_user_privilege(self, login, privilege):
        return self.context.users[login].add_privilege(privilege)

    @api.users.__getitem__.privileges.remove
    def remove_user_privilege(self, login, privilege):
        return self.context.users[login].remove_privilege(privilege)

    @api.users.__getitem__.privileges.deny
    def deny_user_privilege(self, login, privilege):
        return self.context.users[login].deny_privilege(privilege)

    @api.users.list
    def list_all_users(self):
        return tuple(u.pack() for u in self.context.users.select())

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

    # Misc features
    ###############
    @api.misc.list_code_revisions
    def list_code_revisions(self, repo_url, **opts):
        return list_code_revisions(repo_url, **opts)

    @api.misc.list_operator_subdirs
    def list_operator_subdirs(self, repo_url, code_ref):
        return list_operator_subdirs(repo_url, code_ref)

    # Global features
    #################
    @api.monitor
    def global_monitor(self, obj_id):
        self.events_monitor(self.context, obj_id)
