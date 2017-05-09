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
                //Then aks for the gui
                ws_request('get_link_gui_data', [id], {}, function (gui) {
                    var jgui = eval("("+gui+")");
                    var src_inst = instance_from_id(info.src_id);
                    var dst_inst = instance_from_id(info.dst_id);
                    
                    //jsPlumb creation
                    global_project_jsFlag = false;
                    js_link = jsPlumb.connect({ uuids:[src_inst.ep.out.getUuid(),dst_inst.ep.in.getUuid()] });
                    global_project_jsFlag = true;
                    
                    //our creation
                    create_link_from_hub(js_link.id, info.link_id, info.src_id, info.dst_id, info.src_out_id, info.dst_in_id, jgui);
                });
            });
        });
    });
}

function current_project() {
    
    var starting = 0;
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
    
    //Finally, the panels and the comments
    ws_request('get_project_gui_data', [], {}, function (result) {
        if (!result)
            return
        var res = eval("(" + result + ")");
        global_op_panels = eval(res.panels);
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
            panel['selected_ops'].forEach( function(item) {
                divs.push(select_op_new_operator(item, false));
            });
            
            var tmp_el = document.createElement("div");
            tmp_el.appendChild(select_op_make_table(4, divs));
            
            panel.id = "accordion_"+index
            index++;
            
            select_op_create_accordion(panel, tmp_el.innerHTML);
        });
        
        res.comments.forEach( function(com) {
            var ncom = comment_from(com);
        });
    });
}


function load_project() {
    not_yet();
}


function save_project() {
    //The panels and the comments first
    
    var coms = [];
    global_coms.forEach( function(com) {
        coms.push(get_comment_info(com));
    });
    
    ws_request('set_project_gui_data', [JSON.stringify({'panels': global_op_panels, 'comments': coms})], {}, function(result){});
    
    //Second the operators
    global_ops_inst.forEach( function(inst) {
        var gui = {x: inst.gui.x,    y: inst.gui.y};
        ws_request('set_operator_instance_gui_data', [parseInt(inst.hub_id), JSON.stringify(gui)], {}, function(result) {});
    });
    
    //Finally the links
    global_links.forEach( function(link) {
        ws_request('set_link_gui_data', [parseInt(link.params.hub_id), JSON.stringify(link.gui)], {}, function(result) {});
    });
};


function new_project() {
    var res = confirm("Are you sure you want to erase the current project ?");
    if (!res) 
        return false;
    
    //removing links
    remove_all_links();
    
    //removing operators instances
    remove_all_operators_instances();
};


function context_new_project() {
    $('#sakura_main_div_contextMenu').css({visibility: "hidden"});
    new_project();
}