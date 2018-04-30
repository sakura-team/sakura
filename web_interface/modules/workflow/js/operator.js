//Code started by Michael Ortega for the LIG
//March 20th, 2017

function create_operator_instance_on_hub(drop_x, drop_y, id) {

    //We first send the creation command to the sakura hub
    sakura.common.ws_request('create_operator_instance', [current_dataflow_id, parseInt(id)], {}, function (result) {
        var hub_id = result.op_id;

        //Then we create the instance here
        var ndiv = document.getElementById('select_op_selected_'+id+'_static').cloneNode(true);

        //New div creation (cloning)
        ndiv.id = "op_" + id + "_" + hub_id;
        ndiv.classList.add("sakura_dynamic_operator");
        ndiv.setAttribute('draggable', 'false');
        ndiv.childNodes[1].childNodes[2].id = ndiv.id+"_help";
        ndiv.childNodes[1].childNodes[2].childNodes[0].onclick = open_op_help;

        ndiv.style.left     = drop_x+"px";
        ndiv.style.top      = drop_y+"px";
        ndiv.ondblclick     = open_op_modal;
        ndiv.oncontextmenu  = open_op_menu;
        ndiv.onmouseenter   = op_mouse_enter;
        ndiv.onmouseleave   = op_mouse_leave;

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
        create_op_modal(main_div, ndiv.id, parseInt(id), result.tabs);

        global_ops_inst.push({  hub_id      : hub_id,
                                cl          : class_from_id(parseInt(id)),
                                ep          : {in: e_in, out: e_out},
                                gui         : {x: drop_x, y: drop_y}
                                });

        //Now we add the current coordinates of the operator to the hub
        save_dataflow();
    });
}


function create_operator_instance_from_hub(drop_x, drop_y, id, info) {
    var ndiv = select_op_new_operator(id, false );

    ndiv.id = "op_" + id + "_" + info.op_id;
    ndiv.classList.add("sakura_dynamic_operator");
    ndiv.setAttribute('draggable', 'false');
    ndiv.childNodes[1].childNodes[2].id = ndiv.id+"_help";
    ndiv.childNodes[1].childNodes[2].childNodes[0].onclick = open_op_help;


    ndiv.style.left     = drop_x+"px";
    ndiv.style.top      = drop_y+"px";
    ndiv.ondblclick     = open_op_modal;
    ndiv.oncontextmenu  = open_op_menu;
    ndiv.onmouseenter   = op_mouse_enter;
    ndiv.onmouseleave   = op_mouse_leave;

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
    create_op_modal(main_div, ndiv.id, parseInt(id), info.tabs);

    global_ops_inst.push({  hub_id      : info.op_id,
                            cl          : class_from_id(parseInt(id)),
                            ep          : {in: e_in, out: e_out},
                            gui         : {x: drop_x, y: drop_y}
                            });
}


function remove_operator_instance(id, on_hub) {

    tab = id.split("_");
    hub_id = parseInt(tab[2]);

    //First we remove the connections
    remove_connection(hub_id);

    //remove from jsPlumb
    jsPlumb.remove(id);
    jsPlumb.repaintEverything();

    //remove modal
    var mod = document.getElementById("modal_"+id);
    mod.outerHTML = "";
    delete mod;
    op_focus_id = null;

    //Remove from the list of instances
    global_ops_inst.splice(instance_index_from_id(hub_id), 1);

    if (on_hub)
        sakura.common.ws_request('delete_operator_instance', [hub_id], {}, function (result) {});
}

function remove_all_operators_instances() {
    var list = global_ops_inst.slice();
    list.forEach( function (item) {
        remove_operator_instance("op_"+item.cl.id+"_"+item.hub_id, true);
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


function open_op_help(e) {
    var op = class_from_id(parseInt(this.parentNode.id.split("_")[1]));
    alert("Help on operator \""+op.name +"\" is not yet implemented !");
}


function open_op_modal() {
    var modal_name = "modal_"+this.id;
    fill_all(this.id);
    if ($('#'+modal_name+"_dialog").attr('class').includes("full_width")) {
        $('#'+modal_name+"_dialog").toggleClass("full_width");
        $('#'+modal_name+"_body").css("height", "100%");
        $('#'+modal_name+"_body").children().eq(1).css("height", "100%");
        current_nb_rows = max_rows;
    }
    $('#'+modal_name).modal();
}

function class_from_id(id) {
    return global_ops_cl.find( function (e) {
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
