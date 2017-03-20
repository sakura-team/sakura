//Code started by Michael Ortega for the LIG
//October 10th, 2016


/////////////////////////////////////////////////////////
//Basic Functions

function create_operator_instance_on_hub(drop_x, drop_y, id) {
    
    //We first send the creation command to the sakura hub
    ws_request('create_operator_instance', [parseInt(id)], {}, function (result) {
        var hub_id = result.op_id;
        
        //Then we create the instance here
        var ndiv = document.getElementById('select_op_selected_'+id+'_static').cloneNode(true);
        
        //New div creation (cloning)
        ndiv.id = "op_" + id + "_" + hub_id;
        ndiv.classList.add("sakura_dynamic_operator");
        ndiv.style.left = drop_x+"px";
        ndiv.style.top = drop_y+"px";
        ndiv.setAttribute('draggable', 'false');
        ndiv.ondblclick = open_op_modal;    
        ndiv.oncontextmenu = open_op_menu;
        
        main_div.appendChild(ndiv);
        
        //Plumbery: draggable + connections
        jsPlumb.draggable(ndiv.id, {stop: jsp_drag_stop});
        
        var e_in = null;
        var e_out = null;
        if ( result.inputs.length > 0)
            e_in = jsPlumb.addEndpoint(ndiv.id, {   anchor:[ "Left"], 
                                                    isTarget:true,
                                                    cssClass:"sakura_endPoint",
                                                    paintStyle:{fillStyle:"black", radius:6},
                                                    hoverPaintStyle:{ fillStyle:"black", radius:10}
                                                    });
        if (result.outputs.length > 0)
            e_out = jsPlumb.addEndpoint(ndiv.id, {  anchor:[ "Right"], 
                                                    isSource:true,
                                                    cssClass:"sakura_endPoint",
                                                    paintStyle:{fillStyle:"black", radius:6},
                                                    hoverPaintStyle:{ fillStyle:"black", radius:10}
                                                    });
        
        
        //Now the modal for parameters/creation/visu/...
        main_div.appendChild(create_op_modal(ndiv.id, id, result.tabs));
        
        
        global_ops_inst.push({  hub_id      : hub_id,
                                class_id    : id,
                                ep          : {in: e_in, out: e_out},
                                gui         : {x: drop_x, y: drop_y}
                                });
        
        //Now we add the current coordinates of the operator to the hub
        save_project();
    });
}


function create_operator_instance_from_hub(drop_x, drop_y, id, info) {
    var ndiv = select_op_new_operator(  global_ops_cl[id]['svg'],
                                        global_ops_cl[id]['name'],
                                        global_ops_cl[id]['id'],
                                        false );
    
    ndiv.id = "op_" + id + "_" + info.op_id;
    ndiv.classList.add("sakura_dynamic_operator");
    ndiv.style.left = drop_x+"px";
    ndiv.style.top = drop_y+"px";
    ndiv.setAttribute('draggable', 'false');
    ndiv.ondblclick = open_op_modal;    
    ndiv.oncontextmenu = open_op_menu;
    
    main_div.appendChild(ndiv);
    
    //Plumbery: draggable + connections
    jsPlumb.draggable(ndiv.id, {stop: jsp_drag_stop});
    
    var e_in = null;
    var e_out = null;
    if ( info.inputs.length > 0) {
        e_in = jsPlumb.addEndpoint(ndiv.id, {   anchor:[ "Left"], 
                                                isTarget:true, 
                                                uuid:"ep_"+ndiv.id+"_in",
                                                cssClass:"sakura_endPoint",
                                                paintStyle:{fillStyle:"black", radius:6},
                                                hoverPaintStyle:{ fillStyle:"black", radius:10}
                                                });
    }
    if (info.outputs.length > 0)
        e_out = jsPlumb.addEndpoint(ndiv.id, {  anchor:[ "Right"], 
                                                isSource:true, 
                                                uuid:"ep_"+ndiv.id+"_out",
                                                cssClass:"sakura_endPoint",
                                                paintStyle:{fillStyle:"black", radius:6},
                                                hoverPaintStyle:{ fillStyle:"black", radius:10}
                                                });
    
    //Now the modal for parameters/creation/visu/...
    main_div.appendChild(create_op_modal(ndiv.id, id, info.tabs));
    
    global_ops_inst.push({  hub_id      : info.op_id,
                            class_id    : id,
                            ep          : {in: e_in, out: e_out},
                            gui         : {x: drop_x, y: drop_y} 
                            });
}


function remove_operator_instance(id, on_hub) {
    
    tab = id.split("_");
    hub_id = parseInt(tab[2]);
    
    //First we remove the connections
    var sub_array_links = sub_array_of_tuples(global_links, 2, hub_id).concat(sub_array_of_tuples(global_links, 3, hub_id));
    sub_array_links.forEach( function (item) {
        remove_link(item[0], true);
    });
    
    //remove from jsPlumb
    jsPlumb.remove(id);
    jsPlumb.repaintEverything();
    
    //remove modal
    var mod = document.getElementById("modal_"+id);
    mod.outerHTML = "";
    delete mod;
    op_focus_id = null;
    
    //Remove from the list of instances
    global_ops_inst.splice(instance_index_from_hub_id(hub_id), 1);
    
    if (on_hub)
        ws_request('delete_operator_instance', [hub_id], {}, function (result) {});
}


function create_op_modal(id, id_index, tabs) {
    var name    = global_ops_cl[id_index].name;
    var svg     = global_ops_cl[id_index].svg;
    var desc    = global_ops_cl[id_index].short_desc;
    var daemon  = global_ops_cl[id_index].daemon;
    
    var s = '<div class="modal fade" name="modal_'+id+'" id="modal_'+id+'" tabindex="-1" role="dialog" aria-hidden="true"> \
                <div class="modal-dialog" role="document" id="modal_'+id+'_dialog"> \
                    <div class="modal-content"> \
                        <div class="modal-header" id="modal_'+id+'_header"> \
                            <table width="100%"> \
                                <tr> \
                                <td width="38px">'+svg+'</td> \
                                <td class="modal-title" align="left"><b><font size=4>&nbsp;&nbsp;'+name+'&nbsp;&nbsp;</font></b><font size="2" color="grey">'+daemon+'</font></td> \
                                <td align="right"> \
                                    <table> \
                                        <tr> \
                                            <td> \
                                                <button type="button" class="btn btn-xs" style="background-color: transparent; border-color: transparent;" onclick="full_width(\'modal_'+id+'\');"> \
                                                    <span class="glyphicon glyphicon-resize-full"></span>\
                                                </button> \
                                            <td> \
                                                <button type="button" class="btn btn-xs" style="background-color: transparent; border-color: transparent;" data-dismiss="modal" aria-label="Close"> \
                                                    <span class="glyphicon glyphicon-remove"></span>\
                                                </button> \
                                    </table> \
                                </td> \
                                <tr><td colspan="3"><font size="2">'+desc+'</font></td> \
                            </table> \
                        </div> \
                        <div class="modal-body" id="modal_'+id+'_body"> \
                            <ul class="nav nav-tabs"> \
                                <li class="active"> \
                                    <a style="padding-top: 0px; padding-bottom: 0px;" class="a_tabs" data-toggle="tab" href="#modal_'+id+'_tab_inputs">Inputs</a></li> \
                                <li><a style="padding-top: 0px; padding-bottom: 0px;" class="a_tabs" data-toggle="tab" href="#modal_'+id+'_tab_params">Params</a></li> \
                                <li><a style="padding-top: 0px; padding-bottom: 0px;" class="a_tabs" data-toggle="tab" href="#modal_'+id+'_tab_outputs">Outputs</a></li> \
                                <li class="disabled"><a style="padding-top: 0px; padding-bottom: 0px;" class="a_tabs" data-toggle="tab" href="#modal_'+id+'_tab_code">Code</a></li>';
    tabs.forEach( function (tab) {
        s += '<li><a style="padding-top: 0px; padding-bottom: 0px;" class="a_tabs" data-toggle="tab" href="#modal_'+id+'_tab_'+tab.label+'">'+tab.label+'</a></li>';
    });
    s += '                  </ul> \
                            <div class="tab-content" style="width:100%; height:100%;"> \
                                <div id="modal_'+id+'_tab_inputs" class="tab-pane fade in active"></div> \
                                <div id="modal_'+id+'_tab_params" class="tab-pane fade"></div> \
                                <div id="modal_'+id+'_tab_outputs" class="tab-pane fade"></div>';
    tabs.forEach( function (tab) {
        s += '<iframe frameborder="0" style="margin-top:10px; margin-bottom:10px; width:100%; height:100%;" id="modal_'+id+'_tab_'+tab.label+'" class="tab-pane fade" sandbox="allow-scripts"></iframe>';
    });
    s += '                      <div id="modal_'+id+'_tab_code" class="tab-pane fade"></div> \
                            </div> \
                        </div> \
                    </div> \
                </div> \
            </div>';
    
    var wrapper= document.createElement('div');
    wrapper.innerHTML= s;
    var ndiv= wrapper.firstChild;
    return ndiv;
}


function create_link_modal(id, source_cl_id, target_cl_id, source_inst_info, target_inst_info) {
    var source = global_ops_cl[source_cl_id];
    var target = global_ops_cl[target_cl_id];
    
    var modal_id = "modal_"+id;
    
    //we ask for instances info
    var s = '<div class="modal fade" name="'+modal_id+'" id="'+modal_id+'" tabindex="-1" role="dialog" aria-hidden="true"> \
                <div class="modal-dialog" role="document" name="'+modal_id+'_dialog" id="'+modal_id+'_dialog"> \
                    <div class="modal-content"> \
                        <div class="modal-body"> \
                            <table width="100%"> \
                                <tr><td width="45%" valign="top"> \
                                    <div class="panel panel-default" name="'+modal_id+'_panel" id="'+modal_id+'_panel"> \
                                         <div class="panel-heading"> \
                                            <table width="100%"> \
                                                <tr><td align="center">'+ source['svg']+'</td> \
                                                <tr><td align="center">'+ source['name']+ '</td> \
                                            </table> \
                                        </div> \
                                        <div class="panel-body" name="'+modal_id+'_body" id="'+modal_id+'_body"> \
                                            <table align="right"> \
                                                <tr><td> \
                                                    <table> ';
    for (var i = 0; i < source_inst_info['outputs'].length; i++) {
        s += '                                          <tr><td valign="middle"> '+source_inst_info['outputs'][i]['label']+' </td> \
                                                            <td title="Drag me to another box, or click to delete my links" onclick="delete_link_param(\''+modal_id+"_out_"+i+'\', true);" name="'+modal_id+"_out_"+i+'" id="'+modal_id+"_out_"+i+'" align="right" valign="middle" width="40px"> \
                                                                <div style="width: 24px; height: 24px;" draggable="true" id="svg_'+modal_id+'_out_'+i+'">'+svg_round_square("")+' \
                                                                </div></td>';
    }
    s += '                                          </table> \
                                                </td> \
                                            </table> \
                                        </div> \
                                    </div> \
                                <td width="10%"> \
                                <td width="45%" valign="top"> \
                                    <div class="panel panel-default"> \
                                        <div class="panel-heading"> \
                                            <table width="100%"> \
                                                <tr><td align="center">'+ target['svg']+'</td> \
                                                <tr><td align="center">'+ target['name']+ '</td> \
                                            </table> \
                                        </div> \
                                        <div class="panel-body"> \
                                            <table align="left"> \
                                                <tr><td> \
                                                    <table>';
    for (var i = 0; i < target_inst_info['inputs'].length; i++)
        s += '                                          <tr><td title="Drag me to another box, or click to delete my links" onclick="delete_link_param(\''+modal_id+"_in_"+i+'\', true);" name="'+modal_id+"_in_"+i+'" id="'+modal_id+"_in_"+i+'" align="left" valign="middle" width="40px"> \
                                                                <div style="width: 24px; height: 24px;" draggable="true" id="svg_'+modal_id+'_in_'+i+'">'+svg_round_square("")+' \
                                                                </div></td> \
                                                            <td valign="middle"> '+target_inst_info['inputs'][i]['label']+' </td>';
    s += '                                          </table> </td>\
                                                </td>\
                                            </table> \
                                        </div> \
                                    </div> \
                            </table> \
                        </div> \
                        <div class="modal-footer"> \
                            <button type="button" class="btn btn-secondary" data-dismiss="modal" onclick="remove_link(\''+id.split("_")[1]+'\', true);">Delete Link</button> \
                            <button type="button" class="btn btn-primary" data-dismiss="modal">Close</button> \
                        </div> \
                    </div> \
                </div> \
            </div>';
    
    //Here we automatically connect tables into the link
    if (source_inst_info['outputs'].length == 1 && target_inst_info['inputs'].length == source_inst_info['outputs'].length) {
        console.log("Could be Automatically connected");
    }
    
    var wrapper= document.createElement('div');
    wrapper.innerHTML= s;
    var ndiv= wrapper.firstChild;
    return ndiv;
}


function remove_link(nid, on_hub) {
    var link_index = index_in_array_of_tuples(global_links, 0, parseInt(nid));
    var modal_id = "modal_link_"+nid;
    
    //Now we send the removing commands to the hub, for each params
    var sub_params = sub_array_of_tuples(global_links_params, 0, nid);
    sub_params.forEach( function(row) {
        delete_link_param(modal_id+"_out_"+row[1], on_hub);
    });
    
    //Then to jsPlumb
    var jsPConn = null;
    jsPlumb.getConnections().forEach (function (item) {
        if (item.id == global_links[link_index][1])
            jsPConn = item;
    });
    
    jsPlumb.detach(jsPConn);
    jsPlumb.repaintEverything();
    
    //Then to us :) (removing the modal and the link)
    global_links.splice(link_index, 1)
    
    //remove modal
    var mod = document.getElementById(modal_id);
    mod.outerHTML = "";
    delete mod;
    link_focus_id = null;
}


function delete_link_param(id, on_hub) {
    var tab         = id.split("_");
    var modal_id    = parseInt(tab[2]);
    var div_type    = tab[3];
    var param_id    = parseInt(tab[4]);
    
    var col = 1;
    if (div_type == "in") {
        col = 2;
    }
        
    var indexes = [];
    for (var i = 0; i < global_links_params.length; i++) {
        if (global_links_params[i][0] == modal_id && global_links_params[i][col] == param_id) {
            indexes.push(i);
            
            
            var mdiv = document.getElementById("modal_link_"+modal_id+"_body");
            var line = "";
            var div_out = "";
            var div_in = "";
            
            if (div_type == "out") {
                div_out = document.getElementById("svg_"+id);
                div_in  = document.getElementById("svg_modal_link_"+modal_id+"_in_"+global_links_params[i][2]);                
                line = document.getElementById("line_modal_link_"+modal_id+"_"+param_id+"_"+global_links_params[i][2]);
            }
            else {
                div_out  = document.getElementById("svg_modal_link_"+modal_id+"_out_"+global_links_params[i][1]);
                div_in = document.getElementById("svg_"+id);
                line = document.getElementById("line_modal_link_"+modal_id+"_"+global_links_params[i][1]+"_"+param_id);
            }
            
            //change the svgs
            div_in.innerHTML = svg_round_square("");
            div_out.innerHTML = svg_round_square("");
            
            //delete the line
            mdiv.removeChild(line);
            
            //delete from hub side
            if (on_hub) {
                var hub_link_id = global_links_params[i][3];
                ws_request('delete_link', [hub_link_id], {}, function (result) {
                    if (result) {
                        console.log("Issue with 'delete_link' function from hub:", result);
                    }
                });
            }
        }
    }
    
    for (var i = indexes.length-1; i >= 0; i--) {
        global_links_params.splice(indexes[i], 1);
    }
}


function create_link_line(id, _out, _in) {
    var rect0 = document.getElementById("modal_link_"+id+"_dialog").getBoundingClientRect();
    var rect1 = document.getElementById("svg_modal_link_"+id+'_out_'+_out).getBoundingClientRect();
    var rect2 = document.getElementById("svg_modal_link_"+id+'_in_'+_in).getBoundingClientRect();
    
    var w = Math.abs(rect2.x-rect1.x-24+2);
    var h = Math.abs(rect2.y-rect1.y+2);
    
    //Making a fake connection
    var mdiv = document.getElementById("modal_link_"+id+"_body");
    
    var svg_div = document.createElement('div');
    svg_div.id = "line_modal_link_"+id+"_"+_out+"_"+_in;
    
    svg_div.style.position = 'absolute';
    
    svg_div.style.left = (rect1.x-rect0.x+24-1)+'px';
    if (rect2.y >= rect1.y) {
        svg_div.style.top = (rect1.y-rect0.y+12-1)+'px';
        svg_div.innerHTML= '<svg height="'+(h+20)+'" width="'+(w)+'"> \
                                <line x1="1" y1="1" x2="'+(w-1)+'" y2="'+(h-1)+'" style="stroke:rgb(33,256,33);stroke-width:2" /> \
                            </svg> ';
    }
    else {
        svg_div.style.top = (rect2.y-rect0.y+12-1)+'px';
        svg_div.innerHTML= '<svg height="'+(h)+'" width="'+(w)+'"> \
                                <line x1="1" y1="'+(h-1)+'" x2="'+(w-1)+'" y2="1" style="stroke:rgb(33,256,33);stroke-width:2" /> \
                            </svg> ';
    }
    mdiv.appendChild(svg_div);
}


function open_op_menu(e) {
    $('#sakura_operator_contextMenu').css({
      display: "block",
      left: e.clientX - e.layerX + 30,
      top: e.clientY - e.layerY + 30
    });
    op_focus_id = this.id;
    return false;
}


/////////////////////////////////////////////////////////
//Init Functions

//Document Initialisation
function readyCallBack() {
};

$(document).ready(readyCallBack);

//jsPlumb initialisation
$( window ).load(function() {
    
    ///////////////DEFAULTS
    jsPlumb.importDefaults({
        PaintStyle : { lineWidth : 4, strokeStyle : "#333333" },
        MaxConnections : 100,
        Endpoint : ["Dot", {radius:6, zindex:20}],
        EndpointStyle : { fillStyle:"black" },
        Container: "sakura_main_div"
    });
    
    
    ///////////////LINKS EVENTS
    //This piece of code is for preventing two or more identical links
    jsPlumb.bind("beforeDrop", function(params) {
        var found = false;
        for (i=0; i<global_links.length; i++) {
            if (global_links[i][2] == params.sourceId && global_links[i][3] == params.targetId)
                found = true;
        }
        
        //we test the link existence from our side
        if (found == true) {
            console.log("link already exists !");
            return false;
        }
        
        //here we validate the jsPlumb link creation
        return true;
    });
    
    //A connection is established
    jsPlumb.bind("connection", function(params) {
        params.connection._jsPlumb.hoverPaintStyle = { lineWidth: 7, strokeStyle: "#333333" };
        //First we send the link creation command to the hub
        var source_inst_id = parseInt(params.sourceId.split("_")[2]);
        var target_inst_id = parseInt(params.targetId.split("_")[2]);
        var source_cl_id = params.sourceId.split("_")[1];
        var target_cl_id = params.targetId.split("_")[1];
        
        global_links.push([global_links_inc, params.connection.id, source_inst_id, target_inst_id]);
        
        //modal creation
        ws_request('get_operator_instance_info', [source_inst_id], {}, function (source_inst_info) {
            ws_request('get_operator_instance_info', [target_inst_id], {}, function (target_inst_info) {
                var ndiv = create_link_modal("link_"+global_links_inc, source_cl_id, target_cl_id, source_inst_info, target_inst_info);
                main_div.append(ndiv);
                $('#modal_link_'+global_links_inc).modal();
                global_links_inc++;
            });
        });
    });
    
    //When the target of a link changes
    jsPlumb.bind("connectionMoved", function(params) {
        not_yet('connectionMoved Event');
    });
    
    //On double click we open the link parameters
    jsPlumb.bind("dblclick", function(connection) {
        var index = index_in_array_of_tuples(global_links, 1, connection.id);
        var id = global_links[index][0];
        current_modal_id = 'modal_link_'+id;
        $('#modal_link_'+id).modal();
        
        setTimeout(function() {
        }, 200);
    });
    
    //Context Menu is one of the ways for deleting the link
    jsPlumb.bind("contextmenu", function(params, e) {
        e.preventDefault();
        $('#sakura_link_contextMenu').css({
            display: "block",
            left: e.clientX - e.layerX + 30,
            top: e.clientY - e.layerY + 30
        });
        var index = index_in_array_of_tuples(global_links, 1, params.id);
        link_focus_id = global_links[index][0];
    });
});
