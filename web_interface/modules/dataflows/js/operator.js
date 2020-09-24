//Code started by Michael Ortega for the LIG
//March 20th, 2017

var op_events = [ 'disabled',
                  'altered_input',
                  'altered_output',
                  'altered_set_of_inputs',
                  'altered_set_of_outputs',
                  'altered_set_of_parameters',
                  'altered_set_of_parameters',
                  'altered_set_of_tabs',
                  'enabled',
                  'altered_parameter' ]

var transparent_grey = 'rgba(200, 200, 200, 1)';

var dataflows_operators_debug = false;

function operators_deal_with_events(evt_name, args, proxy, hub_inst_id) {
    switch (evt_name) {
        case 'altered_output':
            if (! op_reloading) {
                push_request('operators_info');
                sakura.apis.hub.operators[hub_inst_id].info().then( function(op) {
                    pop_request('operators_info');
                    if (check_output(op)) {
                        fill_in_out('output', 'op_'+op.cls_id+'_'+hub_inst_id);
                    }
                }).catch ( function (error) {
                    console.log('OPERATORS.js: error 1', error);
                });
            }
            break;
        case 'enabled':
            if (LOG_OPERATORS_EVENTS) { console.log('ENABLED OP', args, hub_inst_id); }

            let inst_index = -1;
            for (let i=0; i< instances_waiting_for_creation.length; i++) {
                if  (instances_waiting_for_creation[i].id == hub_inst_id) {
                    inst_index = i;
                }
            };
            console.log('INST', instances_waiting_for_creation[inst_index]);
            if ( inst_index != -1) {
                let proxy = sakura.apis.hub.operators[hub_inst_id];
                let g = { x: instances_waiting_for_creation[inst_index].gui.x,
                          y: instances_waiting_for_creation[inst_index].gui.y
                        }
                push_request('operators_set_gui_data');
                proxy.set_gui_data(JSON.stringify(g)).then( function() {
                    pop_request('operators_set_gui_data');
                    push_request('operators_info');
                    proxy.info().then( function (opi) {
                        pop_request('operators_info');
                        create_operator_instance_from_hub(g.x,
                                                          g.y,
                                                          opi.cls_id, opi);
                        check_operator(opi);
                    }).catch ( function (error) {
                        pop_request('operators_info');
                        console.log('OPERATORS.js: error 2', error);
                    });
                }).catch ( function (error) {
                    pop_request('operators_set_gui_data');
                    console.log('OPERATORS.js: error 3', error);
                });

                //remove from waiting list
                instances_waiting_for_creation.pop(inst_index);
            }
            else {
                console.log('SHOULD NOT CREATE OP');
            }
            break;
        case 'disabled':
            if (LOG_OPERATORS_EVENTS) { console.log('DISABLED OP', args, proxy, hub_inst_id);}
            break;
        default:
            let en = evt_name;
            if (LOG_OPERATORS_EVENTS) { console.log('OP EVENT', evt_name, args, proxy, hub_inst_id);}
            push_request('operators_info');
            sakura.apis.hub.operators[hub_inst_id].info().then( function(op) {
                pop_request('operators_info');
                check_operator(op);
            }).catch ( function (error) {
                pop_request('operators_info');
                console.log('OPERATORS.js: error 4, event: ', en, ', ', error);
            });
    }
}

function create_operator_instance_on_hub(drop_x, drop_y, id) {
    waiting_gui = {x: drop_x, y: drop_y}
    //We first send the creation command to the sakura hub
    push_request('operators_create');
    sakura.apis.hub.operators.create(web_interface_current_id, parseInt(id)).then(function (result) {
        pop_request('operators_create');
    }).catch( function (error){
        pop_request('operators_create');
        console.log('Error 7:', error)
    });
}


function create_operator_instance_from_hub(drop_x, drop_y, id, info) {
    var ndiv = select_op_new_operator(id, false );

    ndiv.id = "op_" + id + "_" + info.op_id;
    ndiv.classList.add("sakura_dynamic_operator");
    ndiv.setAttribute('draggable', 'false');
    ndiv.childNodes[1].id = ndiv.id+"_help";
    ndiv.childNodes[2].id = ndiv.id+"_warning";

    ndiv.style.left     = drop_x+"px";
    ndiv.style.top      = drop_y+"px";
    if (info['enabled']) {
        ndiv.ondblclick     = open_op_modal;
    }
    ndiv.onclick        = op_click;
    ndiv.onmouseenter   = op_mouse_enter;
    ndiv.onmouseleave   = op_mouse_leave;

    main_div.appendChild(ndiv);

    //Plumbery: draggable + connections
    jsPlumb.draggable(ndiv.id, {start: jsp_drag_start, stop: jsp_drag_stop});

    let e_in = null;
    let e_out = null;
    global_ops_inst.push({  hub_id      : info.op_id,
                            cl          : class_from_id(parseInt(id)),
                            ep          : {in: e_in, out: e_out},
                            gui         : {x: drop_x, y: drop_y}
                            });

    if (info.enabled) {
        create_op_outputs(info, ndiv);
        create_op_modal(ndiv.id, info);
    }

    let proxy = sakura.apis.hub.operators[info.op_id];
    if (proxy) {
        op_events.forEach( function(e) {
          proxy.subscribe_event(e, function(evt_name, args) {
                operators_deal_with_events(evt_name, args, proxy, info.op_id);
          });
          // .catch ( function (error) {
          //     console.log('OPERATORS.js: error 5', error);
          // });
      });
    }
    else {
        console.log('Cannot subscribe_event on op', info.op_id);
    }
}


function create_op_outputs(info, ndiv) {
    let inst = instance_from_id(info.op_id);
    inst.ep.in = null;
    inst.ep.out = null;
    if ( info.inputs.length > 0) {
        inst.ep.in = jsPlumb.addEndpoint(ndiv.id, {   anchor:[ "Left"],
                                                isTarget:true,
                                                uuid:"ep_"+ndiv.id+"_in",
                                                cssClass:"sakura_endPoint",
                                                paintStyle:{fillStyle:"black", radius:6},
                                                hoverPaintStyle:{ fillStyle:"black", radius:10}
                                                });
    }
    if (info.outputs.length > 0)
        inst.ep.out = jsPlumb.addEndpoint(ndiv.id, {  anchor:[ "Right"],
                                                isSource:true,
                                                uuid:"ep_"+ndiv.id+"_out",
                                                cssClass:"sakura_endPoint",
                                                isSource: false,
                                                paintStyle:{fillStyle:transparent_grey, radius:6},
                                                hoverPaintStyle:{ fillStyle:transparent_grey, radius:6}
                                                });
}

function check_operator(op) {
    var disabled  = false;
    var warning   = false;
    var d_message = '';
    var w_message = '';

    if (op.enabled) {

        function check_elt(elt) {
          if (!elt.enabled) {
              disabled = true;
              d_message = elt.disabled_message;
          }
          else if (elt.warning_message) {
              warning = true;
              w_message = elt.warning_message;
          }
        }

        op.inputs.forEach( function(inp) { check_elt(inp); });
        op.parameters.forEach( function(param) { check_elt(param); });

        let inst = instance_from_id(op.op_id);
        if (inst) {
            var id = 'op_'+inst.cl.id+'_'+inst.hub_id;
            w_div = document.getElementById(id+"_warning");

            if (disabled) {
                w_div.style.color       = 'red';
                w_div.title             = d_message;
                w_div.style.visibility  = "visible";
                if (inst && inst.outputs) { output_disable(inst); }
            }
            else if (warning) {
                w_div.style.color       = 'orange';
                w_div.title             = w_message;
                w_div.style.visibility  = "visible";
                check_output(op);
            }
            else {
                w_div.style.visibility  = "hidden";
                check_output(op);
            }
        }
    }
}

function reload_operator_instance(id, hub_id) {
    op_reloading = true
    if (!hub_id) {
        let tab = id.split("_");
        hub_id = parseInt(tab[2]);
    }
    push_request('operators_reload');
    sakura.apis.hub.operators[hub_id].reload().then(function() {
        pop_request('operators_reload');
        push_request('operators_info');
        sakura.apis.hub.operators[hub_id].info().then(function(info) {
            pop_request('operators_info');
            let cl_id = id.split("_")[1];
            let cl = current_op_classes_list.find( function (e) {
                return e.id === parseInt(cl_id);
            });
            main_success_alert( 'Operator Reloading',
                                '<b>'+cl.name+'</b> operator reloaded',
                                null, 2);
            op_reloading = false;
            current_dataflow();
        }).catch ( function (error) {
            pop_request('operators_info');
            console.log('OPERATORS.js: error 6', error);
        });
    }).catch ( function (error) {
        pop_request('operators_reload');
        console.log('OPERATORS.js: error 7', error);
    });
}

function remove_operator_instance(id, on_hub) {
    if (id) {
        tab = id.split("_");
        hub_id = parseInt(tab[2]);

        //First we remove the connections
        remove_connection(hub_id, on_hub);

        //remove from jsPlumb
        jsPlumb.remove(id);
        jsPlumb.repaintEverything();

        //remove modal
        var mod = document.getElementById("modal_"+id);
        if (mod) {
            mod.outerHTML = "";
            delete mod;
        }
        op_focus_id = null;

        //Remove from the list of instances
        global_ops_inst.splice(instance_index_from_id(hub_id), 1);

        if (id && on_hub) {
            //console.log(hub_id);
            push_request('operators_delete');
            sakura.apis.hub.operators[hub_id].delete().then( function (result) {
                pop_request('operators_delete');
            }).catch ( function (error) {
                pop_request('operators_delete');
                console.log('OPERATORS.js: error 8', error);
            });
        }
    }
}

function remove_all_operators_instances(on_hub) {
    var list = global_ops_inst.slice();
    list.forEach( function (item) {
        remove_operator_instance("op_"+item.cl.id+"_"+item.hub_id, on_hub);
    });
}

//Interactions
function op_mouse_enter(e) {
    h_div = document.getElementById(this.id+"_help");
    h_div.style.visibility = "visible";
}


function op_mouse_leave(e) {
    h_div = document.getElementById(this.id+"_help");
    h_div.style.visibility = "hidden";
}


function open_op_menu(e) {
    e.preventDefault();
    $('#sakura_operator_contextMenu').css({
      display: "block",
      left: e.clientX,
      top: e.clientY
    });
    op_focus_id = this.id;
    return false;
}

function op_click(e) {
    if (e.target.parentNode.id.indexOf('_help') != -1) {
      e.preventDefault();
      e.stopPropagation();
      $('#sakura_operator_contextMenu').css({
        display: "block",
        left: e.clientX,
        top: e.clientY
      });
      op_focus_id = e.target.parentNode.parentNode.id;
      return false;
    }
}


function open_op_help(e) {
    var op = class_from_id(parseInt(this.parentNode.id.split("_")[1]));
    alert("Help on operator \""+op.name +"\" is not yet implemented !");
}


function open_op_modal() {
    current_op_instance_id = this.id;
    let modal_id = "modal_"+current_op_instance_id;
    dataflows_open_modal = modal_id;
    fill_all(current_op_instance_id);
    if ($('#'+modal_id+"_dialog").attr('class').includes("full_width")) {
        $('#'+modal_id+"_dialog").toggleClass("full_width");
        $('#'+modal_id+"_body").css("height", "100%");
        $('#'+modal_id+"_body").children().eq(1).css("height", "100%");
        current_nb_rows = max_rows;
    }
    $('#'+modal_id).modal();
    // add on-close handler
    $('#'+modal_id).on('hide.bs.modal', function () {
        release_all(current_op_instance_id).then(function(){

            }).catch( function (error){
                console.log('Error 6:', error)
        });
    });
}

function class_from_id(id) {
    return current_op_classes_list.find( function (e) {
        return e.id === id;
    });
}

function instance_from_id(id) {
    return global_ops_inst.find( function (e) {
        return e.hub_id === id;
    });
}


function instance_index_from_id(hid) {
    for (let i = 0; i< global_ops_inst.length; i++)
        if (global_ops_inst[i].hub_id == hid)
            return i;
    return -1
}

function output_enable(inst) {
    inst.ep.out.isSource = true;
    inst.ep.out.setPaintStyle({fillStyle: 'black', radius: 6});
    inst.ep.out.setHoverPaintStyle({fillStyle: 'black', radius: 10});

    for (let i=0;i<global_links.length;i++) {
        if (global_links[i].src == inst.hub_id) {
            global_links[i].jsP.setPaintStyle({strokeStyle: 'black',
                                              lineWidth: 3});
            global_links[i].jsP.setHoverPaintStyle({strokeStyle: 'black',
                                                    lineWidth: 7});
        }
    }

    jsPlumb.repaintEverything();
}

function output_disable(inst) {
    inst.ep.out.isSource = false;
    inst.ep.out.setPaintStyle({fillStyle: transparent_grey, radius: 6});
    inst.ep.out.setHoverPaintStyle({fillStyle: transparent_grey, radius: 6});

    for (let i=0;i<global_links.length;i++) {
        if (global_links[i].src == inst.hub_id) {
            global_links[i].jsP.setPaintStyle({strokeStyle: transparent_grey,
                                              lineWidth: 3});
            global_links[i].jsP.setHoverPaintStyle({strokeStyle: transparent_grey,
                                                    lineWidth: 4});
        }
    }

    jsPlumb.repaintEverything();
}

function check_output(op) {
    if (op.outputs && op.outputs.length) {
        let enable = false;
        let inst = instance_from_id(op.op_id);

        op.outputs.forEach( function (o) {
            if (o.enabled) enable = true;
        });
        (inst && enable) ? output_enable(inst) : output_disable(inst);
        return true;
    }
    else {
        if (dataflows_operators_debug) {
            console.log('This op has no outputs:', op);
        }
        return false;
    }
}
