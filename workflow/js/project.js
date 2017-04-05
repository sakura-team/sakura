//Code started by Michael Ortega for the LIG
//March 9th, 2017


var global_project_jsFlag = true;

//This function is apart, because of the asynchronous aspect of ws
//links can only be recovered after recovering all operator instances
function get_project_links() {
    
    //Cleaning the gui from current links
    remove_all_links();
    
    //Recovering the links from hub
    ws_request('list_link_ids', [], {}, function (ids) {
        ids.forEach( function (id) {
            ws_request('get_link_info', [id], {}, function(info) {
                
                var src_inst = instance_from_hub_id(info.src_id);
                var dst_inst = instance_from_hub_id(info.dst_id);
                console.log(info);
                
                //jsPlumb creation
                global_project_jsFlag = false;
                js_link = jsPlumb.connect({ uuids:[src_inst.ep.out.getUuid(),dst_inst.ep.in.getUuid()] });
                global_project_jsFlag = true;
                
                //our creation
                create_link_from_hub(js_link.id, info.src_id, info.dst_id)
                
                //now params
                
            });
        });
    });
}

function current_project() {
    
    //We first clean the current gui
    while (global_ops_inst.length) {
        remove_operator_instance("op_"+global_ops_inst[0].cl.id+"_"+global_ops_inst[0].hub_id, false)
    };
    
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
                        //Then aks for the gui
                        ws_request('get_operator_instance_gui_data', [id], {}, function (gui) {
                            var jgui = eval("("+gui+")");
                            create_operator_instance_from_hub(jgui.x, jgui.y, info.cls_id, info);
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
                divs.push(select_op_new_operator(item, false));
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
    global_ops_inst.forEach( function(inst) {
        var gui = {x: inst.gui.x,    y: inst.gui.y};
        ws_request('set_operator_instance_gui_data', [parseInt(inst.hub_id), JSON.stringify(gui)], {}, function(result) {});
    });
};


function new_project() {
    var res = confirm("Are you sure you want to erase the current project ?");
    if (!res) 
        return false;
    while (global_ops_inst.length) {
        remove_operator_instance("op_"+global_ops_inst[0].cl.id+"_"+global_ops_inst[0].hub_id, true)
    };
    global_ops_inst = [];
};