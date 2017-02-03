//Code started by Michael Ortega for the LIG
//October 10th, 2016


/////////////////////////////////////////////////////////
//Basic Functions


function not_yet(s = '') {
    if (s == '')
        alert('Not implemented yet');
    else
        alert('Not implemented yet: '+ s);
}

function create_operator_instance(x, y, idiv_id) {
    
    var id_index = idiv_id.split("_").slice(-2)[0];
    
    //We first create send the creation command to the sakura hub
    ws_request('create_operator_instance', [parseInt(id_index)], {}, function (result) {
        var instance_id = result;
        
        //Then we create the instance here
        var idiv = document.getElementById(idiv_id);
        
        //New div creation (cloning)
        var ndiv = idiv.cloneNode(true);
        ndiv.id = "op_" + id_index + "_" + instance_id;
        ndiv.classList.add("sakura_dynamic_operator");
        ndiv.style.left = x+"px";
        ndiv.style.top = y+"px";
        ndiv.setAttribute('draggable', 'false');
        ndiv.ondblclick = open_op_params;    
        ndiv.oncontextmenu = open_op_menu;
        
        global_ops_inst.push(ndiv.id);
        main_div.appendChild(ndiv);
        
        //Plumbery: draggable + connections
        jsPlumb.draggable(ndiv.id, {stop: jsp_drag_stop});
        var nb_o = global_ops_cl[id_index]['outputs'];
        
        if ( global_ops_cl[id_index]['inputs'] > 0)
            jsPlumb.addEndpoint(ndiv.id, { anchor:[ "Left"], isTarget:true});
        if (global_ops_cl[id_index]['outputs'] > 0)
            jsPlumb.addEndpoint(ndiv.id, { anchor:[ "Right"], isSource:true});
        
        //Now the modal for parameters/creation/visu/...
        main_div.appendChild(create_op_modal(ndiv.id, global_ops_cl[parseInt(id_index)]['name'], global_ops_cl[id_index]['svg']));
    });
}


function remove_operator_instance(id) {
    
    tab = id.split("_");
    op_inst = parseInt(tab[2]);
    
    //First we remove the connections
    var sub_array_links = sub_array_of_tuples(global_links, 2, op_inst).concat(sub_array_of_tuples(global_links, 3, op_inst));
    sub_array_links.forEach( function (item) {
        remove_link(item[0]);
    });
    
    //First we send the command to the hub
    ws_request('delete_operator_instance', [op_inst], {}, function (result) {
        if (!result) {
            
            //Then remove from the list of instances
            var index = index_in_array_of_tuples(global_ops_inst, 2, op_inst);
            global_ops_inst.splice(index, 1);
            
            //remove from jsPlumb
            jsPlumb.remove(id);
            jsPlumb.repaintEverything();
            
            //remove modal
            var mod = document.getElementById("modal_"+id);
            mod.outerHTML = "";
            delete mod;
            op_focus_id = null;
            
            console.log(global_links);
            console.log(global_ops_inst);
        }
    });
}


function create_op_modal(id, name, svg) {
    
    var s = '<div class="modal fade" name="modal_'+id+'" id="modal_'+id+'" tabindex="-1" role="dialog" aria-hidden="true"> \
                <div class="modal-dialog" role="document"> \
                    <div class="modal-content"> \
                        <div class="modal-header"> \
                            <button type="button" class="close" data-dismiss="modal" aria-label="Close"> \
                                <span aria-hidden="true">&times;</span> \
                            </button> \
                            <table> \
                                <tr> \
                                <td>'+svg+'</td> \
                                <td><h4 class="modal-title"><b>&nbsp;&nbsp;'+name+'</b></h4></td> \
                            </table> \
                        </div> \
                        <div class="modal-body"> \
                            <ul class="nav nav-tabs"> \
                                <li class="active"> \
                                    <a data-toggle="tab" href="#modal_'+id+'_tab_inputs">Inputs</a></li> \
                                <li><a data-toggle="tab" href="#modal_'+id+'_tab_params">Params</a></li> \
                                <li><a data-toggle="tab" href="#modal_'+id+'_tab_outputs">Outputs</a></li> \
                                <li class="disabled"><a data-toggle="tab" href="#modal_'+id+'_tab_code">Code</a></li> \
                            </ul> \
                            <div class="tab-content"> \
                                <div id="modal_'+id+'_tab_inputs" class="tab-pane fade in active"> \
                                </div> \
                                <div id="modal_'+id+'_tab_params" class="tab-pane fade"> \
                                </div> \
                                <div id="modal_'+id+'_tab_outputs" class="tab-pane fade"> \
                                </div> \
                                <div id="modal_'+id+'_tab_code" class="tab-pane fade"> \
                                </div> \
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
