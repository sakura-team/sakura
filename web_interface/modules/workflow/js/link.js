//Code started by Michael Ortega for the LIG
//March 20th, 2017


//links
var global_links  = [];
var link_focus_id = null;


function create_link(js_id, src_id, dst_id, js_connection) {
    
    sakura.common.ws_request('get_possible_links', [src_id, dst_id], {}, function (possible_links) {
        if (possible_links.length == 0) {
            alert("These two operators cannot be linked");
            jsPlumb.detach(js_connection);
            jsPlumb.repaintEverything();
            return false;
        }
        else 
        {
            global_links.push({ id: js_id,
                        src: src_id,
                        dst: dst_id,
                        params: []});
                        
            sakura.common.ws_request('get_operator_instance_info', [src_id], {}, function (source_inst_info) {
                sakura.common.ws_request('get_operator_instance_info', [dst_id], {}, function (target_inst_info) {
                        create_link_modal(  possible_links,
                                            global_links[global_links.length - 1], 
                                            instance_from_id(src_id).cl, 
                                            instance_from_id(dst_id).cl, 
                                            source_inst_info, 
                                            target_inst_info,
                                            true);
                    js_connection._jsPlumb.hoverPaintStyle = { lineWidth: 7, strokeStyle: "#333333" };
                    return true;
                });
            });
        }
    });
}


function create_link_from_hub(js_id, hub_id, src_id, dst_id, out_id, in_id, gui) {
    
    var l = global_links.push({ 'id': js_id,
                                'src': src_id,
                                'dst': dst_id,
                                'params': [],
                                'modal': false});
                                
    sakura.common.ws_request('get_possible_links', [src_id, dst_id], {}, function (possible_links) {
        sakura.common.ws_request('get_operator_instance_info', [src_id], {}, function (source_inst_info) {
            sakura.common.ws_request('get_operator_instance_info', [dst_id], {}, function (target_inst_info) {
                create_link_modal(  possible_links,
                                    global_links[l - 1], 
                                    instance_from_id(src_id).cl, 
                                    instance_from_id(dst_id).cl, 
                                    source_inst_info, 
                                    target_inst_info,
                                    false,
                                    out_id,
                                    in_id,
                                    hub_id,
                                    gui);
                global_links[l - 1].modal = true;
            });
        });
    });
}


function create_link_modal(p_links, link, src_cl, dst_cl, src_inst_info, dst_inst_info, open_now, out_id, in_id, hub_id, gui) {
    
    //Here we automatically connect tables into the link
    var auto_link = false;
    if (src_inst_info['outputs'].length == 1 && dst_inst_info['inputs'].length == src_inst_info['outputs'].length) {
        auto_link = true;
    }
    
    for (var i=0; i < src_inst_info['outputs'].length; i++) {
        var found = false;
        p_links.forEach( function(item) {
            if (item[0] == i)
                found = true;
        });
        if (found) {
            src_inst_info['outputs'][i].color   = 'black';
            src_inst_info['outputs'][i].drag    = 'true';
        }
        else {
            src_inst_info['outputs'][i].color = 'lightgrey';
            src_inst_info['outputs'][i].drag  = 'false';
        }
    };
    
    for (var i=0; i < dst_inst_info['inputs'].length; i++) {
        var found = false;
        p_links.forEach( function(item) {
            if (item[1] == i)
                found = true;
        });
        if (found) {
            dst_inst_info['inputs'][i].color   = 'black';
            dst_inst_info['inputs'][i].drag    = 'true';
        }
        else {
            dst_inst_info['inputs'][i].color = 'lightgrey';
            dst_inst_info['inputs'][i].drag  = 'false';
        }
    };
    
    var wrapper= document.createElement('div');
    load_from_template(
                    wrapper,
                    "modal-link.html",
                    {'id': link.id, 'source_cl': src_cl, 'destination_cl': dst_cl, 'tabs_src_outputs': src_inst_info['outputs'], 'tabs_dst_inputs': dst_inst_info['inputs']},
                    function () {
                        var modal = wrapper.firstChild;
                        // update the svg icon
                        $(modal).find("#td_src_svg").html(src_cl.svg);
                        $(modal).find("#td_dst_svg").html(dst_cl.svg);
                        
                        var index = 0;
                        src_inst_info['outputs'].forEach( function (item) {
                            var found = false;
                            p_links.forEach( function(item) {
                                if (item[0] == index)
                                    found = true;
                            });
                            if (found)
                                $(modal).find("#svg_modal_link_"+link.id+"_out_"+index).html(svg_round_square(""));
                            index ++;
                        });
                        
                        var index = 0;
                        dst_inst_info['inputs'].forEach( function (item) {
                            var found = false;
                            p_links.forEach( function(item) {
                                if (item[1] == index)
                                    found = true;
                            });
                            if (found)
                                $(modal).find("#svg_modal_link_"+link.id+"_in_"+index).html(svg_round_square(""));
                            index ++;
                        });
                        
                        // append to main div
                        main_div.appendChild(modal);
                        if (open_now && !auto_link)
                            $(modal).modal();
                        else if (!open_now) {
                            link.params.push({  'out_id': out_id, 
                                                'in_id': in_id, 
                                                'hub_id': hub_id,
                                                'top': gui.top,
                                                'left': gui.left,
                                                'line':  gui.line});
                            copy_link_line(link, out_id, in_id, gui);
                            $("#svg_modal_link_"+link.id+'_out_'+out_id).html(svg_round_square_crossed(""));
                            $("#svg_modal_link_"+link.id+'_in_'+in_id).html(svg_round_square_crossed(""));
                        }
                        else if (auto_link) {  //means should be open now, but we don't cause we link automatically
                            console.log('Could think about auto link');
                            $(modal).modal();
                        }
                    }
    );
}


function refresh_link_modal(link) {
    sakura.common.ws_request('get_possible_links', [link.src, link.dst], {}, function (p_links) {
        sakura.common.ws_request('get_operator_instance_info', [link.src], {}, function (source_inst_info) {
            sakura.common.ws_request('get_operator_instance_info', [link.dst], {}, function (target_inst_info) {
                //sources
                for(var i=0; i<source_inst_info.outputs.length;i++) {
                    var found = false;
                    p_links.forEach( function(item) {
                    if (item[0] == i)
                        found = true;
                    });
                    var div_name = document.getElementById('modal_link_'+link.id+'_td_out_'+i);
                    var div_square = $("#svg_modal_link_"+link.id+'_out_'+i);
                    if (found) {
                        div_name.style.color = 'black';
                        if (div_square.html().indexOf('line') == -1)
                            div_square.html(svg_round_square(""));
                        div_square.attr('draggable', 'True');
                    }
                    else {
                        div_name.style.color = 'lightgrey';
                        div_square.html("");
                        div_square.attr('draggable', 'False');
                    }
                }
                
                //destinations
                for(var i=0; i<target_inst_info.inputs.length;i++) {
                    var found = false;
                    p_links.forEach( function(item) {
                    if (item[1] == i)
                        found = true;
                    });
                    
                    var div_name = document.getElementById('modal_link_'+link.id+'_td_in_'+i);
                    var div_square = $("#svg_modal_link_"+link.id+'_in_'+i);
                    
                    if (found) {
                        div_name.style.color = 'black';
                        if (div_square.html().indexOf('line') == -1)
                            div_square.html(svg_round_square(""));
                        div_square.attr('draggable', 'True');
                    }
                    else {
                        div_name.style.color = 'lightgrey';
                        div_square.html("");
                        div_square.attr('draggable', 'False');
                    }
                }
            });
        });
    });
}

function test_link(link) {
    if (typeof link == 'string') {
        link = link_from_id(link);
    }
    if (link.params.length == 0) 
        remove_link(link)
}


function remove_link(link) {
    
    if (typeof link == 'string') {
        link = link_from_id(link);
    }
    
    //We first send the removing commands to the hub
    if (link.params.length > 0)
        delete_link_params(link, true);
    else {
        //Then to jsPlumb
        var jsPConn = null;
        jsPlumb.getConnections().forEach (function (item) {
            if (item.id == link.id)
                jsPConn = item;
        });
        
        if (jsPConn) {
            jsPlumb.detach(jsPConn);
            jsPlumb.repaintEverything();
        }
        
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
    
    global_links.forEach( function (l) {
        refresh_link_modal(l);
    });
    
}


function remove_connection(hub_id) {
    var sub_array_links = sub_array_of_tuples(global_links, 2, hub_id).concat(sub_array_of_tuples(global_links, 3, hub_id));
    sub_array_links.forEach( function (item) {
        remove_link(item[0], true);
    });
}


function delete_link_params(link, and_main_link) {
    if (typeof link == 'string') {
        link = link_from_id(link);
    }
    
    var mdiv    = document.getElementById("modal_link_"+link.id+"_body");
    for (var i=0; i< link.params.length; i++) {
        var para = link.params[i];
        sakura.common.ws_request('delete_link', [para.hub_id], {}, function (result) {
            if (result) {
                console.log("Issue with 'delete_link' function from hub:", result);
            }
        });
        var div_out = document.getElementById("svg_modal_link_"+link.id+"_out_"+para.out_id);
        var div_in  = document.getElementById("svg_modal_link_"+link.id+"_in_"+para.in_id);
        var line    = document.getElementById("line_modal_link_"+link.id+"_"+para.out_id+"_"+para.in_id);
        
        div_in.innerHTML = svg_round_square("");
        div_out.innerHTML = svg_round_square("");
        mdiv.removeChild(line);
        
        if (i >= link.params.length -1) {
            link.params = [];
            if (and_main_link) {
                remove_link(link);
            }
        }
    }
}


function delete_link_param(link, side, id) {
    
    if (typeof link == 'string') {
        link = link_from_id(link);
    }
    
    var link_p = null;
    var index_p = 0;
    var mdiv    = document.getElementById("modal_link_"+link.id+"_body");
    for (var i=0; i<link.params.length; i++)
    {
        if (side == 'in' && link.params[i].in_id == parseInt(id)) {
            link_p = link.params[i];
            index_p = i;
        }
        else if (side == 'out' && link.params[i].out_id == parseInt(id)) {
            link_p = link.params[i];
            index_p = i;
        }
    }
    if (link_p) {
        sakura.common.ws_request('delete_link', [link_p.hub_id], {}, function (result) {
            if (result) {
                console.log("Issue with 'delete_link' function from hub:", result);
            }
        });
        var div_out = document.getElementById("svg_modal_link_"+link.id+"_out_"+link_p.out_id);
        var div_in  = document.getElementById("svg_modal_link_"+link.id+"_in_"+link_p.in_id);
        var line    = document.getElementById("line_modal_link_"+link.id+"_"+link_p.out_id+"_"+link_p.in_id);
        
        div_in.innerHTML = svg_round_square("");
        div_out.innerHTML = svg_round_square("");
        link.params.splice(index_p, 1);
        mdiv.removeChild(line);
        refresh_link_modal(link);
    }
    else {
        console.log('problem with link_p in delete_link_params (link.js)');
    }
}


function create_link_line(link, _out, _in) {
    
    
    //Making a fake connection
    var mdiv = document.getElementById("modal_link_"+link.id+"_body");
    var svg_div = document.createElement('div');
    svg_div.id = "line_modal_link_"+link.id+"_"+_out+"_"+_in;
    svg_div.style.position = 'absolute';
    
    var rect0 = document.getElementById("modal_link_"+link.id+"_dialog").getBoundingClientRect();
    var rect1 = document.getElementById("svg_modal_link_"+link.id+'_out_'+_out).getBoundingClientRect();
    var rect2 = document.getElementById("svg_modal_link_"+link.id+'_in_'+_in).getBoundingClientRect();
    
    var w = Math.abs(rect2.x-rect1.x-24+2);
    var h = Math.abs(rect2.y-rect1.y+2);
    
    svg_div.style.left = (rect1.x-rect0.x+24-1)+'px';
    var svg = '';
    if (parseInt(rect2.y) - parseInt(rect1.y) >= 0) {
        svg_div.style.top = (rect1.y-rect0.y+12-1)+'px';
        svg = '<svg height="'+(h+20)+'" width="'+(w)+'"> \
                                <line x1="1" y1="1" x2="'+(w-1)+'" y2="'+(h-1)+'" style="stroke:rgb(33,256,33);stroke-width:2" /> \
                            </svg> ';
    }
    else {
        svg_div.style.top = (rect2.y-rect0.y+12-1)+'px';
        svg = '<svg height="'+(h)+'" width="'+(w)+'"> \
                                <line x1="1" y1="'+(h-1)+'" x2="'+(w-1)+'" y2="1" style="stroke:rgb(33,256,33);stroke-width:2" /> \
                            </svg> ';
    }
    
    svg_div.innerHTML = svg;
    mdiv.appendChild(svg_div);
    return svg;
}


function copy_link_line(link, _out, _in, gui) {
    //Making a fake connection
    var mdiv = document.getElementById("modal_link_"+link.id+"_body");
    var svg_div = document.createElement('div');
    svg_div.id = "line_modal_link_"+link.id+"_"+_out+"_"+_in;
    svg_div.style.position = 'absolute';
    
    svg_div.style.left = gui.left;
    svg_div.style.top = gui.top;
    svg = gui.line;
    
    svg_div.innerHTML = svg;
    mdiv.appendChild(svg_div);
    return svg;
}


function open_link_params(conn_id) {
    refresh_link_modal(link_from_id(conn_id));
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
        if (global_links[i].src == src_id && global_links[i].dst == dst_id)
            found = true;
    }
    return found;
}

function link_from_instances(src_id, dst_id) {
    for (var i=0; i<global_links.length; i++) {
        if (global_links[i].src == src_id && global_links[i].dst == dst_id)
            return global_links[i];
    }
    return null;
}


function remove_all_links() {
    global_links.forEach( function(item) {
        remove_link(item);
    });
    global_links = []
}
