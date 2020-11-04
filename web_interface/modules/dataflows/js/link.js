//Code started by Michael Ortega for the LIG
//March 20th, 2017

var link_events           = [ 'disabled', 'enabled'];


function links_deal_with_events(evt_name, args, proxy) {
    switch (evt_name) {
        case 'disabled':
            if (LOG_LINKS_EVENTS)
                console.log(evt_name, args);
            break;
        case 'enabled':
            if (LOG_LINKS_EVENTS)
                console.log(evt_name, args);
            break;
        default:
            if (LOG_LINKS_EVENTS) {
                console.log('Unknown Event', evt_name);
        }
    }
}


function create_link(js, src_id, dst_id) {
    if (LOG_LINKS_EVENTS) {console.log('CREATE LINK', js, src_id, dst_id);}
    push_request('links_list_possible');
    sakura.apis.hub.links.list_possible(src_id, dst_id).then(function (possible_links) {
        pop_request('links_list_possible');
        if (LOG_LINKS_EVENTS) {console.log('POSS LINKS', possible_links.length, possible_links);}
        if (possible_links.length == 0) {
            // alert("These two operators cannot be linked");
            main_alert("LINK", 'These two operators cannot be linked', null);
            jsPlumb.detach(js);
            jsPlumb.repaintEverything();
            return false;
        }
        else
        {
            push_request('operators_info');
            sakura.apis.hub.operators[src_id].info().then(function (source_inst_info) {
                pop_request('operators_info');
                push_request('operators_info');
                sakura.apis.hub.operators[dst_id].info().then(function (target_inst_info) {
                    pop_request('operators_info');
                    global_links.push({ id: js.id,
                                        src: src_id,
                                        dst: dst_id,
                                        params: [],
                                        jsP: js});

                    create_link_modal(  possible_links,
                                        global_links[global_links.length - 1],
                                        instance_from_id(src_id).cl,
                                        instance_from_id(dst_id).cl,
                                        source_inst_info,
                                        target_inst_info,
                                        true);
                    //js.setDetachable(false);

                    return true;
                }).catch( function(error) {
                    pop_request('operators_info');
                    if (LOG_LINKS_EVENTS) console.log('CL 3', error);
                });
            }).catch( function(error) {
                pop_request('operators_info');
                if (LOG_LINKS_EVENTS) console.log('CL 2', error);
            });
        }
    }).catch( function(error) {
        pop_request('links_list_possible');
        if (LOG_LINKS_EVENTS) console.log('CL 1', error);
    });
    js.setPaintStyle({strokeStyle: transparent_grey, radius: 6});
    jsPlumb.repaintEverything();
}


function create_link_from_hub(js, link, gui, from_shell=false) {
    if (LOG_LINKS_EVENTS) {console.log('CREATE LINK FROM HUB');}
    let l = global_links.push({ 'id': js.id,
                                'src': link.src_id,
                                'dst': link.dst_id,
                                'params': [],
                                'modal': false,
                                'jsP': js});
    //js.setDetachable(false);
    if (!link.enabled) {
        js.setPaintStyle({strokeStyle: transparent_grey, radius: 6});
        js.setHoverPaintStyle({strokeStyle: transparent_grey, radius: 6});
    }

    push_request('links_info');
    sakura.apis.hub.links.list_possible(link.src_id, link.dst_id).then(function (possible_links) {
        pop_request('links_info');
        push_request('operators_info');
        sakura.apis.hub.operators[link.src_id].info().then(function (source_inst_info) {
            pop_request('operators_info');
            push_request('operators_info');
            sakura.apis.hub.operators[link.dst_id].info().then(function (target_inst_info) {
                pop_request('operators_info');
                create_link_modal(  possible_links,
                                    global_links[l - 1],
                                    instance_from_id(link.src_id).cl,
                                    instance_from_id(link.dst_id).cl,
                                    source_inst_info,
                                    target_inst_info,
                                    false,
                                    link.src_out_id,
                                    link.dst_in_id,
                                    link.link_id,
                                    gui,
                                    from_shell);
                global_links[l - 1].modal = true;
            });
        });
    });
}


function create_link_modal( p_links,  link,
                            src_cl,   dst_cl,
                            src_inst_info, dst_inst_info,
                            open_now,
                            out_id, in_id, hub_id, gui,
                            from_shell ) {

    if (LOG_LINKS_EVENTS) {console.log('CREATING MODAL LINK');}

    //Here we automatically connect tables into the link
    // var auto_link = false;
    // if (src_inst_info['outputs'].length == 1 && dst_inst_info['inputs'].length == src_inst_info['outputs'].length) {
    //     auto_link = true;
    // }
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
            if (open_now) {
                $(modal).modal();
            }
            else if (!open_now) {
                let ij = param_exist(hub_id);
                if (!ij) {
                    link.params.push({  'out_id': out_id,
                                        'in_id': in_id,
                                        'hub_id': hub_id,
                                        'top': gui.top,
                                        'left': gui.left,
                                        'line':  gui.line});
                }
                else {
                    link.params[ij[1]].top = gui.top;
                    link.params[ij[1]].left = gui.left;
                    link.params[ij[1]].line= gui.line;
                }
                copy_link_line(link, out_id, in_id, gui);
                $("#svg_modal_link_"+link.id+'_out_'+out_id).html(svg_round_square_crossed(""));
                $("#svg_modal_link_"+link.id+'_in_'+in_id).html(svg_round_square_crossed(""));

                if (from_shell) {
                    check_operator(src_inst_info);
                    check_operator(dst_inst_info);
                }
            }
            // else if (auto_link) {  //means should be open now, but we don't because we link automatically
            //     console.log('Could think about auto link');
            //     $(modal).modal();
            // }

            $(modal).on('hidden.bs.modal', function() {
                test_link(link.id);
            });
        }
    );
}


function refresh_link_modal(link) {
    push_request('links_list_possible');
    sakura.apis.hub.links.list_possible(link.src, link.dst).then(function (p_links) {
        pop_request('links_list_possible');
        push_request('operators_info');
        sakura.apis.hub.operators[link.src].info().then(function (source_inst_info) {
            pop_request('operators_info');
            push_request('operators_info');
            sakura.apis.hub.operators[link.dst].info().then(function (target_inst_info) {
                pop_request('operators_info');
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

                check_operator(source_inst_info);
                check_operator(target_inst_info);
            });
        });
    });
}

function test_link(link, on_hub) {
    if (LOG_LINKS_EVENTS) console.log('TEST_LINK');
    if (typeof link == 'string') {
        link = link_from_id(link);
    }
    if (link && link.params.length == 0) {
        remove_link(link, on_hub);
    }
}


function remove_link(link, on_hub) {
    if (typeof link == 'string') {
        link = link_from_id(link);
    }

    if (LOG_LINKS_EVENTS) console.log('REMOVE_LINK');
    //We first send the removing commands to the hub
    if (link && link.params.length > 0)
        delete_link_params(link, true, on_hub);
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

    if (on_hub) {
        global_links.forEach( function (l) {
            refresh_link_modal(l);
        });

        push_request('operators_info');
        sakura.apis.hub.operators[link.src].info().then(function (source_inst_info) {
            pop_request('operators_info');
            push_request('operators_info');
            sakura.apis.hub.operators[link.dst].info().then(function (target_inst_info) {
                pop_request('operators_info');
                check_operator(source_inst_info);
                check_operator(target_inst_info);
            }).catch( function (res) {
                pop_request('operators_info');
                console.log('Destination does not exists anymore', res);
            });
        }).catch( function(res) {
            pop_request('operators_info');
            console.log('Source does not exists anymore', res);
        });
    }
}


function remove_connection(hub_id, on_hub) {
    if (LOG_LINKS_EVENTS) console.log('REMOVE_CONNECTION');
    global_links.forEach( function(link) {
        if (link.src == hub_id || link.dst == hub_id) {
            remove_link(link, on_hub);
        }
    });
}


function delete_link_params(link, and_main_link, on_hub) {
    if (LOG_LINKS_EVENTS) {console.log('DELETE LINK PARAMS');}

    if (typeof link == 'string') {
        link = link_from_id(link);
    }

    let mdiv    = document.getElementById("modal_link_"+link.id+"_body");
    for (let i=0; i< link.params.length; i++) {
        let para = link.params[i];
        if (on_hub) {
            if (para.hub_id) {
                push_request('links_delete');
                sakura.apis.hub.links[para.hub_id].delete().then(function (result) {
                    pop_request('links_delete');
                    if (result) {
                        console.log("Issue with 'delete_link' function from hub:", result);
                    }
                });
            }
        }
        let div_out = document.getElementById("svg_modal_link_"+link.id+"_out_"+para.out_id);
        let div_in  = document.getElementById("svg_modal_link_"+link.id+"_in_"+para.in_id);
        let line    = document.getElementById("line_modal_link_"+link.id+"_"+para.out_id+"_"+para.in_id);

        if (div_in) div_in.innerHTML = svg_round_square("");
        if (div_out) div_out.innerHTML = svg_round_square("");
        if (line) mdiv.removeChild(line);

        if (i >= link.params.length -1) {
            link.params = [];
            if (and_main_link) {
                remove_link(link, on_hub);
            }
        }
    }
}


function delete_link_param(link, side, id, on_hub = true) {
    if (LOG_LINKS_EVENTS) {console.log('DELETE LINK PARAM');}
    if (typeof link == 'string') {
        link = link_from_id(link);
    }

    let link_p = null;
    let index_p = 0;
    let mdiv    = document.getElementById("modal_link_"+link.id+"_body");
    for (let i=0; i<link.params.length; i++)
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
        if (on_hub) {
            push_request('links_delete');
            sakura.apis.hub.links[link_p.hub_id].delete().then(function (result) {
                pop_request('links_delete');
                if (result) {
                    console.log("Issue with 'delete_link' function from hub:", result);
                }
            });
        }
        let div_out = document.getElementById("svg_modal_link_"+link.id+"_out_"+link_p.out_id);
        let div_in  = document.getElementById("svg_modal_link_"+link.id+"_in_"+link_p.in_id);
        let line    = document.getElementById("line_modal_link_"+link.id+"_"+link_p.out_id+"_"+link_p.in_id);

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


function create_link_line(link_id, _out, _in) {
    let new_div = false;

    //Making a fake connection
    let mdiv = document.getElementById("modal_link_"+link_id+"_body");

    let line_id = "line_modal_link_"+link_id+"_"+_out+"_"+_in;;
    let svg_div = document.getElementById(line_id);
    if (svg_div == null) {
        new_div = true;
        svg_div = document.createElement('div');
        svg_div.id = line_id;
    }

    svg_div.style.position = 'absolute';

    let rect0 = document.getElementById("modal_link_"+link_id+"_dialog").getBoundingClientRect();
    let rect1 = document.getElementById("svg_modal_link_"+link_id+'_out_'+_out).getBoundingClientRect();
    let rect2 = document.getElementById("svg_modal_link_"+link_id+'_in_'+_in).getBoundingClientRect();

    let w = Math.abs(rect2.x-rect1.x-24+2);
    let h = Math.abs(rect2.y-rect1.y+2);

    svg_div.style.left = (rect1.x-rect0.x+24-1)+'px';
    let svg = '';
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
    if (new_div) {
        mdiv.appendChild(svg_div);
    }
    return svg;
}


function copy_link_line(link, _out, _in, gui) {
    //Making a fake connection
    let mdiv = document.getElementById("modal_link_"+link.id+"_body");
    if (mdiv) {
        let svg_div = document.createElement('div');
        svg_div.id = "line_modal_link_"+link.id+"_"+_out+"_"+_in;
        svg_div.style.position = 'absolute';

        svg_div.style.left = gui.left;
        svg_div.style.top = gui.top;
        let svg = gui.line;
        if (!svg)
            svg = "";
        svg_div.innerHTML = svg;
        mdiv.appendChild(svg_div);
        return svg;
    }
    else {
        return null;
    }
}

function open_link_params(conn_id) {
    refresh_link_modal(link_from_id(conn_id));
    $('#modal_link_'+conn_id).on('shown.bs.modal', function (e) {
        check_link_params(conn_id);
    });
    $('#modal_link_'+conn_id).modal();
    setTimeout(function() {
    }, 200);
}

function check_link_params(conn_id) {
    let link = link_from_id(conn_id);
    let para = link.params;
    for (let i = 0; i< para.length; i++) {
        if (! para[i].top) {
            let line = create_link_line(link.id, para[i].out_id, para[i].in_id);
            let svg_line = document.getElementById("line_modal_link_"+link.id+"_"+para[i].out_id+"_"+para[i].in_id);
            link.params.top   = svg_line.style.top;
            link.params.left  = svg_line.style.left;
            link.params.line  = line;
        }
    }
}

function link_from_id(id) {
    return global_links.find( function(e) {
        return e.id === id;
    });
}

function link_exist(src_id, dst_id) {
    let found = false;
    for (let i=0; i < global_links.length; i++) {
        if (global_links[i].src == src_id && global_links[i].dst == dst_id) {
            found = true;
        }
    }
    return found;
}

function param_exist(hub_id) {
    let found = null;
    for (let i=0; i < global_links.length; i++) {
        for (let j=0; j < global_links[i].params.length; j++) {
            if (global_links[i].params[j].hub_id == hub_id) {
                found = [i, j];
            }
        }
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

function remove_all_links(on_hub) {
    global_links.forEach( function(item) {
        remove_link(item, on_hub);
    });
    global_links = []
}
