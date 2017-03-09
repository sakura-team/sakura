//Code started by Michael Ortega for the LIG
//March 9th, 2017

function current_project() {
    //We first ask for the operator classes
    ws_request('list_operators_classes', [], {}, function (result) {
        global_ops_cl = JSON.parse(JSON.stringify(result));
        //Then we ask for the instance ids
        ws_request('list_operators_instance_ids', [], {}, function (ids) {
            ids.forEach( function(id) {
                //Then ask for the infos
                ws_request('get_operator_instance_info', [id], {}, function (info) {
                    cl_id = index_in_array_of_tuples(global_ops_cl, 'name', info.cls_name);
                    //Then aks for the gui
                    ws_request('get_operator_instance_gui_data', [id], {}, function (gui) {
                        jgui = eval("("+gui+")");
                        create_operator_instance_from_hub(jgui.x, jgui.y, cl_id, info);
                    });
                });
            });
        });
    });
}


function load_project() {
    not_yet();
}


function save_project() {
    not_yet();
};


function new_project() {
    var res = confirm("Are you sure you want to erase the current project ?");
    if (!res) 
        return false;
    global_ops_inst.forEach( function (id) {
        remove_operator_instance(id)
    });
    global_ops_inst = [];
};