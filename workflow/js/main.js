//Code started by Michael Ortega for the LIG
//October 10th, 2016


/////////////////////////////////////////////////////////
//Basic Functions


function not_yet() {
    alert('Not implemented yet');
}

function create_operator_instance(x, y, idiv_id) {
    
    var id_index = idiv_id.split("_").slice(-2)[0];
    
    //We first create send the creation command to the sakura hub
    ws_request('create_operator_instance', [id_index], {}, function (result) {
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
        main_div.append(ndiv);
        
        //Plumbery: draggable + connections
        jsPlumb.draggable(ndiv.id, {stop: jsp_drag_stop});
        var nb_o = global_ops_cl[id_index]['outputs'];
        
        if ( global_ops_cl[id_index]['inputs'] > 0)
            jsPlumb.addEndpoint(ndiv.id, { anchor:[ "Left"], isTarget:true});
        if (global_ops_cl[id_index]['outputs'] > 0)
            jsPlumb.addEndpoint(ndiv.id, { anchor:[ "Right"], isSource:true});
        
        //Now the modal for parameters/creation/visu/...
        main_div.append(create_op_modal(ndiv.id, global_ops_cl[id_index]['name'], global_ops_cl[id_index]['svg']));
    });
}


function remove_operator_instance(id) {
    
    tab = id.split("_");
    op_inst = tab[2];
    
    //First we send the command to the hub
    ws_request('delete_operator_instance', [op_inst], {}, function (result) {
        if (result) {
            //Then remove form the list of instances
            var index = global_ops_inst.indexOf(id);
            global_ops_inst.splice(index, 1);
            
            //remove from jsPlumb
            jsPlumb.remove(id);
            
            //remove modal
            var mod = document.getElementById("modal_"+id);
            mod.outerHTML = "";
            delete mod;
            ops_focus = null;
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
                        <br>Here the operators parameters. <br>Soon :) \
                    </div> \
                </div> \
              </div> \
            </div> ';
    
    var wrapper= document.createElement('div');
    wrapper.innerHTML= s;
    var ndiv= wrapper.firstChild;
    return ndiv;
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
    ops_focus = this;
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
    
    // setup some defaults for jsPlumb.
    jsPlumb.importDefaults({
        PaintStyle : { lineWidth : 1, strokeStyle : "#333333" },
        MaxConnections : 100,
        Endpoint : ["Dot", {radius:6}],
        EndpointStyle : { fillStyle:"#000000" },
        Container: "sakura_main_div"
    });
    
    
    //This piece of code is for preventing two or more identical connections
    jsPlumb.bind("beforeDrop", function(params) {
        var found = false;
        for (i=0; i<conns.length; i++) {
            if (conns[i][0] == params.sourceId && conns[i][1] == params.targetId)
                found = true;
        }
        
        if (found == true) {
            console.log("Connection already exists !");
            return false;
        }
        
        conns.push([params.sourceId, params.targetId])
        return true;
        
    });
});
