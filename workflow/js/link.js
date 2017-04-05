//Code started by Michael Ortega for the LIG
//March 20th, 2017


//links
var global_links  = []; //[local_id, jsPlumb_id, src_inst_id (from hub), dst_inst_id (from hub)]
var link_focus_id = null;


function create_link(js_id, src_id, dst_id) {
    
    global_links.push({ id: js_id,
                        src: src_id,
                        dst: dst_id,
                        params: null});
    //modal creation
    ws_request('get_operator_instance_info', [src_id], {}, function (source_inst_info) {
        ws_request('get_operator_instance_info', [dst_id], {}, function (target_inst_info) {
            var ndiv = create_link_modal(   global_links[global_links.length - 1], 
                                            instance_from_id(src_id).cl, 
                                            instance_from_id(dst_id).cl, 
                                            source_inst_info, 
                                            target_inst_info);
            main_div.append(ndiv);
            $('#modal_link_'+js_id).modal();
        });
    });
}


function create_link_from_hub(js_id, hub_id, src_id, dst_id, out_id, in_id) {
    
    //global_links.push([global_links_inc, js_id, src_id, dst_id]);
    var l = global_links.push({ id: js_id,
                                src: src_id,
                                dst: dst_id,
                                params: null});
    
    ws_request('get_operator_instance_info', [src_id], {}, function (source_inst_info) {
        ws_request('get_operator_instance_info', [dst_id], {}, function (target_inst_info) {
            main_div.append( create_link_modal(   global_links[l - 1], 
                                            instance_from_id(src_id).cl, 
                                            instance_from_id(dst_id).cl, 
                                            source_inst_info, 
                                            target_inst_info) );
                                            
            create_params(global_links[l - 1], out_id, in_id, hub_id);
            create_link_line(global_links[l - 1], out_id, in_id);
            
            document.getElementById("svg_modal_link_"+global_links[l - 1].id+'_out_'+out_id).innerHTML = svg_round_square_crossed("");
            document.getElementById("svg_modal_link_"+global_links[l - 1].id+'_in_'+in_id).innerHTML = svg_round_square_crossed("");
        });
    });
}

function create_params(link, out_id, in_id, link_id_from_hub) {
    
    link.params = { out_id: out_id, 
                    in_id: in_id, 
                    hub_id: link_id_from_hub};
}


function create_link_modal(link, source_cl, destination_cl, source_inst_info, target_inst_info) {
    
    var modal_id = "modal_link_"+link.id;
    
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
                                                <tr><td align="center">'+ source_cl['svg']+'</td> \
                                                <tr><td align="center">'+ source_cl['name']+ '</td> \
                                            </table> \
                                        </div> \
                                        <div class="panel-body" name="'+modal_id+'_body" id="'+modal_id+'_body"> \
                                            <table align="right"> \
                                                <tr><td> \
                                                    <table> ';
    for (var i = 0; i < source_inst_info['outputs'].length; i++) {
        s += '                                          <tr><td valign="middle"> '+source_inst_info['outputs'][i]['label']+' </td> \
                                                            <td title="Drag me to another box, or click to delete my links" onclick="delete_link_param(\''+link.id+'\');" name="'+modal_id+"_out_"+i+'" id="'+modal_id+"_out_"+i+'" align="right" valign="middle" width="40px"> \
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
                                                <tr><td align="center">'+ destination_cl['svg']+'</td> \
                                                <tr><td align="center">'+ destination_cl['name']+ '</td> \
                                            </table> \
                                        </div> \
                                        <div class="panel-body"> \
                                            <table align="left"> \
                                                <tr><td> \
                                                    <table>';
    for (var i = 0; i < target_inst_info['inputs'].length; i++)
        s += '                                          <tr><td title="Drag me to another box, or click to delete my links" onclick="delete_link_param(\''+link.id+'\');" name="'+modal_id+"_in_"+i+'" id="'+modal_id+"_in_"+i+'" align="left" valign="middle" width="40px"> \
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
                            <button type="button" class="btn btn-secondary" data-dismiss="modal" onclick="remove_link(\''+link.id+'\');">Delete Link</button> \
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


function remove_link(link) {

    //We first send the removing commands to the hub
    if (link.params)
        delete_link_param(link);
    
    //Then to jsPlumb
    var jsPConn = null;
    jsPlumb.getConnections().forEach (function (item) {
        if (item.id == link.id)
            jsPConn = item;
    });
    
    jsPlumb.detach(jsPConn);
    jsPlumb.repaintEverything();
    
    //remove modal
    var mod = document.getElementById("modal_link_"+link.id);
    mod.outerHTML = "";
    delete mod;
    link_focus_id = null;
    
    //Then to us :) (removing the modal and the link)
    var index = global_links.findIndex( function (e) {
        return e.id === link.id;
    });
    global_links.splice(index, 1);
}


function remove_connection(hub_id) {
    var sub_array_links = sub_array_of_tuples(global_links, 2, hub_id).concat(sub_array_of_tuples(global_links, 3, hub_id));
    sub_array_links.forEach( function (item) {
        remove_link(item[0], true);
    });
}


function delete_link_param(link) {
    if (typeof link == 'string') {
        link = link_from_id(link);
    }
    
    ws_request('delete_link', [link.params.hub_id], {}, function (result) {
        if (result) {
            console.log("Issue with 'delete_link' function from hub:", result);
        }
        else {
            var mdiv    = document.getElementById("modal_link_"+link.id+"_body");
            var div_out = document.getElementById("svg_modal_link_"+link.id+"_out_"+link.params.out_id);
            var div_in  = document.getElementById("svg_modal_link_"+link.id+"_in_"+link.params.in_id);
            var line    = document.getElementById("line_modal_link_"+link.id+"_"+link.params.out_id+"_"+link.params.in_id);
            
            div_in.innerHTML = svg_round_square("");
            div_out.innerHTML = svg_round_square("");
            mdiv.removeChild(line);
            
            link.params = null;
        }
    });
}


function create_link_line(link, _out, _in) {
    var rect0 = document.getElementById("modal_link_"+link.id+"_dialog").getBoundingClientRect();
    var rect1 = document.getElementById("svg_modal_link_"+link.id+'_out_'+_out).getBoundingClientRect();
    var rect2 = document.getElementById("svg_modal_link_"+link.id+'_in_'+_in).getBoundingClientRect();
    
    var w = Math.abs(rect2.x-rect1.x-24+2);
    var h = Math.abs(rect2.y-rect1.y+2);
    
    //Making a fake connection
    var mdiv = document.getElementById("modal_link_"+link.id+"_body");
    
    var svg_div = document.createElement('div');
    svg_div.id = "line_modal_link_"+link.id+"_"+_out+"_"+_in;
    
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


function open_link_params(conn_id) {    
    $('#modal_link_'+conn_id).modal();
    setTimeout(function() {
    }, 200);
}


function link_from_id(id) {
    return global_links.find( function(e) {
        return e.id === id;
    });
}


function link_exist(src_id, dst_id) {
    var found = false;
    for (var i=0; i<global_links.length; i++) {
        if (global_links[i][2] == src_id && global_links[i][3] == dst_id)
            found = true;
    }
    return found;
}


function remove_all_links() {
    while (global_links.length)
        remove_link(global_links[0]);
}
