//Code started by Michael Ortega for the LIG
//March 20th, 2017


//links
var global_links  = [];
var link_focus_id = null;


function create_link(js_id, src_id, dst_id, js_connection) {
    
    ws_request('get_possible_links', [src_id, dst_id], {}, function (possible_links) {
        if (possible_links.length == 0) {
            alert("These two operators cannot be linked");
            jsPlumb.detach(js_connection);
            jsPlumb.repaintEverything();
            return false;
        }
        else 
        {
            //console.log("possible links", possible_links);
            global_links.push({ id: js_id,
                        src: src_id,
                        dst: dst_id,
                        params: null});
                        
            ws_request('get_operator_instance_info', [src_id], {}, function (source_inst_info) {
                ws_request('get_operator_instance_info', [dst_id], {}, function (target_inst_info) {
                        console.log(possible_links);
                        //console.log(target_inst_info);
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
    
    var l = global_links.push({ id: js_id,
                                src: src_id,
                                dst: dst_id,
                                params: null});
    global_links[l-1].gui = gui;
    
    ws_request('get_possible_links', [src_id, dst_id], {}, function (possible_links) {
        ws_request('get_operator_instance_info', [src_id], {}, function (source_inst_info) {
            ws_request('get_operator_instance_info', [dst_id], {}, function (target_inst_info) {
                create_link_modal(  possible_links,
                                    global_links[l - 1], 
                                    instance_from_id(src_id).cl, 
                                    instance_from_id(dst_id).cl, 
                                    source_inst_info, 
                                    target_inst_info,
                                    false,
                                    out_id,
                                    in_id,
                                    hub_id);
            });
        });
    });
}

function create_params(link, out_id, in_id, link_id_from_hub) {
    
    link.params = { out_id: out_id, 
                    in_id: in_id, 
                    hub_id: link_id_from_hub};
}


function create_link_modal(p_links, link, src_cl, dst_cl, src_inst_info, dst_inst_info, open_now, out_id, in_id, hub_id) {
    
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
                            create_params(link, out_id, in_id, hub_id);
                            create_link_line(link, out_id, in_id, true);
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


function test_link(link) {
    if (typeof link == 'string') {
        link = link_from_id(link);
    }
    if (link.params == null) 
        remove_link(link)
}


function remove_link(link) {
    
    if (typeof link == 'string') {
        link = link_from_id(link);
    }
    //We first send the removing commands to the hub
    if (link.params)
        delete_link_param(link, true);
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
}


function remove_connection(hub_id) {
    var sub_array_links = sub_array_of_tuples(global_links, 2, hub_id).concat(sub_array_of_tuples(global_links, 3, hub_id));
    sub_array_links.forEach( function (item) {
        remove_link(item[0], true);
    });
}


function delete_link_param(link, and_main_link) {
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
            link.gui = null;
            
            if (and_main_link)
                remove_link(link);
        }
    });
}


function create_link_line(link, _out, _in, copy) {
    
    var svg_div = document.createElement('div');
    svg_div.id = "line_modal_link_"+link.id+"_"+_out+"_"+_in;
    svg_div.style.position = 'absolute';
    
    //Making a fake connection
    var mdiv = document.getElementById("modal_link_"+link.id+"_body");
    
    if (!copy) {
        var rect0 = document.getElementById("modal_link_"+link.id+"_dialog").getBoundingClientRect();
        var rect1 = document.getElementById("svg_modal_link_"+link.id+'_out_'+_out).getBoundingClientRect();
        var rect2 = document.getElementById("svg_modal_link_"+link.id+'_in_'+_in).getBoundingClientRect();
        
        var w = Math.abs(rect2.x-rect1.x-24+2);
        var h = Math.abs(rect2.y-rect1.y+2);
        console.log(h, rect2.y, rect1.y);
        
        svg_div.style.left = (rect1.x-rect0.x+24-1)+'px';
        
        if (parseInt(rect2.y) - parseInt(rect1.y) >= 0) {
            console.log("pass  1");
            svg_div.style.top = (rect1.y-rect0.y+12-1)+'px';
            svg_div.innerHTML= '<svg height="'+(h+20)+'" width="'+(w)+'"> \
                                    <line x1="1" y1="1" x2="'+(w-1)+'" y2="'+(h-1)+'" style="stroke:rgb(33,256,33);stroke-width:2" /> \
                                </svg> ';
        }
        else {
            console.log("pass  2");
            svg_div.style.top = (rect2.y-rect0.y+12-1)+'px';
            console.log(svg_div.style.top);
            svg_div.innerHTML= '<svg height="'+(h)+'" width="'+(w)+'"> \
                                    <line x1="1" y1="'+(h-1)+'" x2="'+(w-1)+'" y2="1" style="stroke:rgb(33,256,33);stroke-width:2" /> \
                                </svg> ';
        }
        
        link.gui = {top:        svg_div.style.top,
                    left:       svg_div.style.left,
                    innerHTML:  svg_div.innerHTML }
    }
    else {
        svg_div.style.left  = link.gui.left;
        svg_div.style.top   = link.gui.top;
        svg_div.innerHTML   = link.gui.innerHTML;
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
    global_links.forEach( function(item) {
        remove_link(item);
    });
    global_links = []
}
