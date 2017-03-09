//Code started by Michael Ortega for the LIG
//October 10th, 2016


/////////////////////////////////////////////////////////
//Basic Functions

function create_operator_instance_on_hub(drop_x, drop_y, id) {
    
    //We first send the creation command to the sakura hub
    ws_request('create_operator_instance', [parseInt(id)], {}, function (result) {
        var instance_id = result.op_id;
        
        //Then we create the instance here
        var ndiv = document.getElementById('select_op_selected_'+id+'_static').cloneNode(true);
        
        //New div creation (cloning)
        ndiv.id = "op_" + id + "_" + instance_id;
        ndiv.classList.add("sakura_dynamic_operator");
        ndiv.style.left = drop_x+"px";
        ndiv.style.top = drop_y+"px";
        ndiv.setAttribute('draggable', 'false');
        ndiv.ondblclick = open_op_modal;    
        ndiv.oncontextmenu = open_op_menu;
        
        global_ops_inst.push(ndiv.id);
        main_div.appendChild(ndiv);
        
        //Plumbery: draggable + connections
        jsPlumb.draggable(ndiv.id, {stop: jsp_drag_stop});
        
        if ( result.inputs.length > 0)
            jsPlumb.addEndpoint(ndiv.id, { anchor:[ "Left"], isTarget:true});
        if (result.outputs.length > 0)
            jsPlumb.addEndpoint(ndiv.id, { anchor:[ "Right"], isSource:true});
        
        
        //Now the modal for parameters/creation/visu/...
        main_div.appendChild(create_op_modal(ndiv.id, id, result.tabs));
        
        //Now we add the current coordinates of the operator to the hub
        var gui = {x: drop_x,    y: drop_y};
        global_ops_inst_gui.push(gui);
        
        ws_request('set_operator_instance_gui_data', [instance_id, JSON.stringify(gui)], {}, function(result) {
            console.log("Set GUI result:", result);
        });
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
        
    global_ops_inst.push(ndiv.id);
    main_div.appendChild(ndiv);
    
    //Plumbery: draggable + connections
    jsPlumb.draggable(ndiv.id, {stop: jsp_drag_stop});
    
    if ( info.inputs.length > 0)
        jsPlumb.addEndpoint(ndiv.id, { anchor:[ "Left"], isTarget:true});
    if (info.outputs.length > 0)
        jsPlumb.addEndpoint(ndiv.id, { anchor:[ "Right"], isSource:true});
    
    //Now the modal for parameters/creation/visu/...
    main_div.appendChild(create_op_modal(ndiv.id, id, info.tabs));
    
    //Now we add the current coordinates of the operator to the hub
    var gui = {x: drop_x,    y: drop_y};
    global_ops_inst_gui.push(gui);
}


function remove_operator_instance(id, on_hub) {
    
    tab = id.split("_");
    op_inst = parseInt(tab[2]);
    
    //First we remove the connections
    var sub_array_links = sub_array_of_tuples(global_links, 2, op_inst).concat(sub_array_of_tuples(global_links, 3, op_inst));
    sub_array_links.forEach( function (item) {
        remove_link(item[0]);
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
    var index = global_ops_inst.indexOf(id);
    global_ops_inst.splice(index, 1);
    
    if (on_hub)
        ws_request('delete_operator_instance', [op_inst], {}, function (result) {});
}


function full_width(elt) {
    $('#'+elt+"_dialog").toggleClass('full_width');
    if ($('#'+elt+"_dialog").attr('class').includes("full_width")) {
        var h = ($(window).height()-$('#'+elt+"_header").height()-80);
        $('#'+elt+"_body").css("height", h+"px");
        $('#'+elt+"_body").children().eq(1).css("height", (h-60)+"px");
    }
    else {
        $('#'+elt+"_body").css("height", "100%");
        $('#'+elt+"_body").children().eq(1).css("height", "100%");
    }
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
                                                            <td title="Drag me to another box, or click to delete my links" onclick="delete_link_param(\''+modal_id+"_out_"+i+'\');" name="'+modal_id+"_out_"+i+'" id="'+modal_id+"_out_"+i+'" align="right" valign="middle" width="40px"> \
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
        s += '                                          <tr><td title="Drag me to another box, or click to delete my links" onclick="delete_link_param(\''+modal_id+"_in_"+i+'\');" name="'+modal_id+"_in_"+i+'" id="'+modal_id+"_in_"+i+'" align="left" valign="middle" width="40px"> \
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
                            <button type="button" class="btn btn-secondary" data-dismiss="modal" onclick="remove_link(\''+id.split("_")[1]+'\');">Delete Link</button> \
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


function remove_link(nid) {
    var link_index = index_in_array_of_tuples(global_links, 0, parseInt(nid));
    var modal_id = "modal_link_"+nid;
    
    //Now we send the removing commands to the hub, for each params
    var sub_params = sub_array_of_tuples(global_links_params, 0, nid);
    sub_params.forEach( function(row) {
        delete_link_param(modal_id+"_out_"+row[1]);
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
        Endpoint : ["Dot", {radius:6}],
        EndpointStyle : { fillStyle:"#000000" },
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
