//Code started by Michael Ortega for the LIG
//March 9th, 2017

//This function is apart, because of the asynchronous aspect of ws
//links can only be recovered after recovering all operator instances
function get_project_links() {
    
    //Cleaning the gui from current links
    while (global_links.length)
        remove_link(global_links[0][0]);
    
    //Recovering the links from hub
    ws_request('list_link_ids', [], {}, function (ids) {
        ids.forEach( function (id) {
            ws_request('get_link_info', [id], {}, function(info) {
                console.log(info);
                 //First we send the link creation command to the hub
                
                //global_links.push([global_links_inc, params.connection.id, source_inst_id, target_inst_id]);
                
                /*//modal creation
                ws_request('get_operator_instance_info', [source_inst_id], {}, function (source_inst_info) {
                    ws_request('get_operator_instance_info', [target_inst_id], {}, function (target_inst_info) {
                        var ndiv = create_link_modal("link_"+global_links_inc, source_cl_id, target_cl_id, source_inst_info, target_inst_info);
                        main_div.append(ndiv);
                        $('#modal_link_'+global_links_inc).modal();
                        global_links_inc++;
                    });
                });
                */
            });
        });
    });
}

function current_project() {
    
    //We first clean the current gui
    while (global_ops_inst.length) {
        remove_operator_instance(global_ops_inst[0], false)
    };
    
    global_ops_inst_gui = [];
    
    var starting = null;
    var nb_ops = -1;
    
    //Now we ask for the operator classes
    ws_request('list_operators_classes', [], {}, function (result) {
        global_ops_cl = JSON.parse(JSON.stringify(result));
        //Then we ask for the instance ids
        ws_request('list_operators_instance_ids', [], {}, function (ids) {
            nb_ops = ids.length;
            if (ids.length == 0) {
                starting = 0;
            }
            else {
                ids.forEach( function(id) {
                    //Then ask for the infos
                    ws_request('get_operator_instance_info', [id], {}, function (info) {
                        var cl_id = index_in_array_of_tuples(global_ops_cl, 'name', info.cls_name);
                        //Then aks for the gui
                        ws_request('get_operator_instance_gui_data', [id], {}, function (gui) {
                            var jgui = eval("("+gui+")");
                            create_operator_instance_from_hub(jgui.x, jgui.y, cl_id, info);
                            starting++;
                            if (nb_ops == starting) {
                                get_project_links();
                            }
                        });
                    });
                });
            }
        });
    });
    
    //Finally, he panels
    ws_request('get_project_gui_data', [], {}, function (result) {
        global_op_panels = eval(result);
        if (! global_op_panels) {
            global_op_panels = []
            return;
        }
        
        //Emptying current accordion
        var acc_div = document.getElementById('op_left_accordion');
        var butt = document.getElementById('select_op_add_button').cloneNode(true);
        while(acc_div.firstChild){
            acc_div.removeChild(acc_div.firstChild);
        }
        acc_div.appendChild(butt);
        
        //Filling accordion with panels
        var index = 0;
        global_op_panels.forEach( function (panel) {
            
            var divs = []
            panel[2].forEach( function(item) {
                var op = global_ops_cl[item]
                divs.push(select_op_new_operator(op['svg'], op['name'], op['id'], false));
            });
            
            var tmp_el = document.createElement("div");
            tmp_el.appendChild(select_op_make_table(3, panel[2], divs));
            
            acc_id = "accordion_"+index
            index++;
            
            var new_acc = select_op_create_accordion(panel[1], acc_id, tmp_el.innerHTML);
            acc_div.insertBefore(new_acc, butt);
        });
    });
}


function load_project() {
    not_yet();
}


function save_project() {
    //The panels first
    var gui = JSON.stringify(global_op_panels);
    ws_request('set_project_gui_data', [gui], {}, function(result){});
    
    
    //Then the operators
    global_ops_inst.forEach( function(id) {
        var op = document.getElementById(id);
        var tab = id.split("_");
        var hub_id = tab[2];
        
        drop_x = parseInt(op.style.left.split('px')[0]);
        drop_y = parseInt(op.style.top.split('px')[0]);
        var gui = {x: drop_x,    y: drop_y};
        ws_request('set_operator_instance_gui_data', [parseInt(hub_id), JSON.stringify(gui)], {}, function(result) {});
    });
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