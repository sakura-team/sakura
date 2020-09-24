var current_op_classes_list = null;
var current_project         = null;
var current_page            = null;
var web_interface_current_object_info = null;
var web_interface_current_object_type = '';
var web_interface_current_id          = -1;  //database or dataflow id

var pages_init_text = '<span style="color:grey">*Empty ! Edit by clicking on the eye*</span>';

var logo_size = 'big';

var web_interface_mouse               = {'x': 0, 'y': 0};
var web_interface_projects_div_moving = false;

var projects_all_objects_list = 'empty';

var current_simpleMDE = null;

var current_operator_revision = null;
var current_revised_op        = null;
var current_revisions         = null;
var current_code_url          = null;

//list of hub requests sent
var requests_sent = [];

//Dataflow Globals
var jsPlumbLoaded         = false;
var global_op_panels      = [];
var global_ops_inst       = [];
var global_coms           = []
var op_focus_id           = null;
var panel_focus_id        = null;
var dataflows_open_modal  = null;

//links
var global_links  = [];
var link_focus_id = null;

var op_reloading = false;
