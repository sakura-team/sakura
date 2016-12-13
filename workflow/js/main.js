//Code started by Michael Ortega for the LIG
//October 10th, 2016


/////////////////////////////////////////////////////////
//Basic Functions


function not_yet() {
    alert('Not implemented yet');
}


document.addEventListener("dragstart", function ( e ) {
    e.dataTransfer.setData('text/plain', null);
    var rect = e.target.getBoundingClientRect();
    drag_current_op = e.target;
    drag_delta = [e.clientX - rect.left, e.clientY - rect.top];
}, false);


main_div.addEventListener("dragover", function( e ) {
    e.preventDefault();
}, false);


main_div.addEventListener("drop", function( e ) {
    e.preventDefault();
    if (drag_current_op.id.includes("static")) {
        var rect = main_div.getBoundingClientRect();
        new_dynamic_operator(   e.clientX - rect.left - drag_delta[0], 
                                e.clientY - rect.top - drag_delta[1] + e.target.scrollTop, 
                                drag_current_op.id);
    }
    drag_current_op = null;
}, false);


function new_dynamic_operator(x, y, idiv_id) {
    var id_index = idiv_id.split("_").slice(-2)[0];
    var idiv = document.getElementById(idiv_id);
    
    //New div creation (cloning)
    var ndiv = idiv.cloneNode(true);
    ndiv.id = "op_" + id_index + "_" + global_ops_inst.length
    ndiv.classList.add("sakura_dynamic_operator");
    ndiv.style.left = x+"px";
    ndiv.style.top = y+"px";
    ndiv.setAttribute('draggable', 'false');
    //ndiv.style.zIndex = '2';
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
}


function jsp_drag_stop(e) {
    var ot = document.getElementById("sakura_main_div");
    if (e.el.getBoundingClientRect().left < ot.getBoundingClientRect().left)
        e.el.style.left = 20 + "px";
    if (e.el.getBoundingClientRect().top < ot.getBoundingClientRect().top)
        e.el.style.top = 20 + "px";
    
    jsPlumb.repaintEverything();        //Very Important when dragging elements manually
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
    
    //sandbox/begin
    //sansbox/end
};


function new_project() {
    var res = confirm("Are you sure you want to erase the current project ?");
    if (!res) 
        return false;
    global_ops_inst.forEach( function (id) {
        jsPlumb.remove(id);
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
    /*for (var i=0; i<ops.length; i++){
        $('#sakura_left_div').append(new_static_operator(0, i, i));
    };
    */
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
