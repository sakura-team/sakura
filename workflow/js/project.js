//Code started by Michael Ortega for the LIG
//March 9th, 2017

function current_project() {
    
    //We first clean the current gui
    while (global_ops_inst.length) {
        remove_operator_instance(global_ops_inst[0], false)
    };
    
    global_ops_inst_gui = [];
    
    //Now we ask for the operator classes
    ws_request('list_operators_classes', [], {}, function (result) {
        global_ops_cl = JSON.parse(JSON.stringify(result));
        //Then we ask for the instance ids
        ws_request('list_operators_instance_ids', [], {}, function (ids) {
            ids.forEach( function(id) {
                //Then ask for the infos
                ws_request('get_operator_instance_info', [id], {}, function (info) {
                    var cl_id = index_in_array_of_tuples(global_ops_cl, 'name', info.cls_name);
                    //Then aks for the gui
                    ws_request('get_operator_instance_gui_data', [id], {}, function (gui) {
                        var jgui = eval("("+gui+")");
                        create_operator_instance_from_hub(jgui.x, jgui.y, cl_id, info);
                    });
                });
            });
        });
    });
    
    //Then the panels
    ws_request('get_project_gui_data', [], {}, function (result) {
        global_op_panels = eval(result);
        if (! global_op_panels) {
            global_op_panels = []
            return;
        }
        
        var index = 0;
        global_op_panels.forEach( function (panel) {
            console.log(panel);
            
            var divs = []
            panel[2].forEach( function(item) {
                var op = global_ops_cl[item]
                divs.push(select_op_new_operator(op['svg'], op['name'], op['id'], false));
            });
            
            var tbl = select_op_make_table(3, panel[2], divs);
            console.log(tbl);
            var tmp_el = document.createElement("div");
            tmp_el.appendChild(tbl);
            
            acc_id = "accordion_"+index
            
            var new_acc = select_op_create_accordion(panel[1], acc_id, tmp_el.innerHTML);
            var acc_div = document.getElementById('op_left_accordion');
            
            //Empty accordion
            //console.log(acc_div);
            //console.log(acc_div.firstChild);
                
            var butt = document.getElementById('select_op_add_button');
            
            acc_div.insertBefore(new_acc, butt);
            
            index++;
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
    while (global_ops_inst.length) {
        remove_operator_instance(global_ops_inst[0], true)
    };
    global_ops_inst = [];
};