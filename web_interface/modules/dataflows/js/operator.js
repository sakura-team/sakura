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

function operators_deal_with_events(evt_name, args, proxy, cl_id, hub_inst_id) {
    switch (evt_name) {
        case 'altered_output':
            //console.log(evt_name, args, cl_id, hub_inst_id);
            if (!op_reloading) {
                sakura.apis.hub.operators[hub_inst_id].info().then( function(op) {
                    if (check_output(op))
                        fill_in_out('output', 'op_'+cl_id+'_'+hub_inst_id);
                });
            }
        case 'enabled':
            console.log('ENABLED OP', args, hub_inst_id);
            sakura.apis.hub.operators[hub_inst_id].info().then( function(op) {
                check_operator(op);
            });
            break;
        case 'disabled':
            console.log('DISABLED OP', args, hub_inst_id);
            sakura.apis.hub.operators[hub_inst_id].info().then( function(op) {
                check_operator(op);
            });
            break;
        // default:
        //     console.log(evt_name);
    }
}

function create_operator_instance_on_hub(drop_x, drop_y, id) {
    //We first send the creation command to the sakura hub
    sakura.apis.hub.operators.create(web_interface_current_id, parseInt(id)).then(function (result) {
        var hub_id = result.op_id;

        //Then we create the instance here
        var ndiv = document.getElementById('select_op_selected_'+id+'_static').cloneNode(true);

        //New div creation (cloning)
        ndiv.id = "op_" + id + "_" + hub_id;
        ndiv.classList.add("sakura_dynamic_operator");
        ndiv.setAttribute('draggable', 'false');
        ndiv.childNodes[1].id = ndiv.id+"_help";
        ndiv.childNodes[2].id = ndiv.id+"_warning";

        ndiv.style.left     = drop_x+"px";
        ndiv.style.top      = drop_y+"px";

        ndiv.ondblclick     = open_op_modal;
        ndiv.onclick        = op_click;
        ndiv.onmouseenter   = op_mouse_enter;
        ndiv.onmouseleave   = op_mouse_leave;

        main_div.appendChild(ndiv);

        //Plumbery: draggable + connections
        jsPlumb.draggable(ndiv.id, {start: jsp_drag_start, stop: jsp_drag_stop});

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
        create_op_modal(main_div, ndiv.id, result);

        global_ops_inst.push({  hub_id      : hub_id,
                                cl          : class_from_id(parseInt(id)),
                                ep          : {in: e_in, out: e_out},
                                gui         : {x: drop_x, y: drop_y}
                                });

        let proxy = sakura.apis.hub.operators[hub_id];
        if (proxy) {
            op_events.forEach( function(e) {
              proxy.subscribe_event(e, function(evt_name, args) {
                    operators_deal_with_events(evt_name, args, proxy, id, hub_id);
              });
          });
        }
        else {
            console.log('Cannot subscribe_event on op', info.op_id);
        }

        //Now we add the current coordinates of the operator to the hub
        save_dataflow();
        check_operator(result);
    }).catch( function (error){
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

    var e_in = null;
    var e_out = null;
    if (info.enabled) {
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
                                                    isSource: false,
                                                    paintStyle:{fillStyle:transparent_grey, radius:6},
                                                    hoverPaintStyle:{ fillStyle:transparent_grey, radius:6}
                                                    });
        create_op_modal(main_div, ndiv.id, info);
    }

    global_ops_inst.push({  hub_id      : info.op_id,
                            cl          : class_from_id(parseInt(id)),
                            ep          : {in: e_in, out: e_out},
                            gui         : {x: drop_x, y: drop_y}
                            });

    let proxy = sakura.apis.hub.operators[info.op_id];
    if (proxy) {
        op_events.forEach( function(e) {
          proxy.subscribe_event(e, function(evt_name, args) {
                operators_deal_with_events(evt_name, args, proxy, id, info.op_id);
          });
      });
    }
    else {
        console.log('Cannot subscribe_event on op', info.op_id);
    }
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
                if (inst) output_disable(inst);
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
    sakura.apis.hub.operators[hub_id].reload().then(function() {
        sakura.apis.hub.operators[hub_id].info().then(function(info) {
            let cl_id = id.split("_")[1];
            let cl = current_op_classes_list.find( function (e) {
                return e.id === parseInt(cl_id);
            });
            main_success_alert( 'Operator Reloading',
                                '<b>'+cl.name+'</b> operator reloaded',
                                null, 2);
            op_reloading = false;
            current_dataflow();
        });
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
            sakura.apis.hub.operators[hub_id].delete().then( function (result) {
                //console.log('REMOVE OP: ', result);
            }).catch( function(error) {
                console.log('ERROR REMOVING OP ', error);
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
    for (var i=0; i< global_ops_inst.length; i++)
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
    if (op.outputs) {
        let enable = false;
        op.outputs.forEach( function (o) {
            if (o.enabled) enable = true;
        });
        let inst = instance_from_id(op.op_id);
        (inst && enable) ? output_enable(inst) : output_disable(inst);
        return true;
    }
    else {
        console.log('This op has no outputs:', op);
        return false;
    }
}
