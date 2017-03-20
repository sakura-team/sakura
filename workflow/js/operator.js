//Code started by Michael Ortega for the LIG
//March 20th, 2017

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
                                cl          : global_ops_cl[id],
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
                            cl          : global_ops_cl[id],
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
    global_ops_inst.splice(instance_index_from_hub_id(hub_id), 1);
    
    if (on_hub)
        ws_request('delete_operator_instance', [hub_id], {}, function (result) {});
}
