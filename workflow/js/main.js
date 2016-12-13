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
    
    main_div.append(ndiv);
    
    //Plumbery: draggable + connections
    jsPlumb.draggable(ndiv.id, {stop: jsp_drag_stop});
    var nb_o = global_ops_cl[id_index]['outputs'];
    
    if ( global_ops_cl[id_index]['inputs'] > 0)
        jsPlumb.addEndpoint(ndiv.id, { anchor:[ "Left"], isTarget:true});
    if (global_ops_cl[id_index]['outputs'] > 0)
        jsPlumb.addEndpoint(ndiv.id, { anchor:[ "Right"], isSource:true});
}


function jsp_drag_stop(e) {
    var ot = document.getElementById("sakura_main_div");
    if (e.el.getBoundingClientRect().left < ot.getBoundingClientRect().left)
        e.el.style.left = 20 + "px";
    if (e.el.getBoundingClientRect().top < ot.getBoundingClientRect().top)
        e.el.style.top = 20 + "px";
    
    jsPlumb.repaintEverything();        //Very Important when dragging elements manually
}


function create_simple_modal (id, title, main_html) {
    var m_1 = '<div class="modal fade" id="';
    //here the modal id
    var m_2 = '" tabindex="-1" role="dialog" aria-labelledby="';
    //here the label id
    var m_3 = '" aria-hidden="true"> \
                    <div class="modal-dialog modal-lg" role="document"> \
                        <div class="modal-content"> \
                            <div class="modal-header"> \
                                <button type="button" class="close" data-dismiss="modal" aria-label="Close"> <span aria-hidden="true">&times;</span> </button> \
                                <h4 class="modal-title"><b>';
    //here the label
    var m_4 = '</b></h4> \
              </div> \
              <div class="modal-body"> ';
    //here the blabla
    var m_5 = '</div> \
            </div> \
          </div> \
        </div> ';
    var s = m_1+id;
    s = s + m_2+id+title;
    s = s + m_3+title;
    s = s + m_4+main_html;
    s = s + m_5;
    
    var wrapper= document.createElement('div');
    wrapper.innerHTML= s;
    var ndiv= wrapper.firstChild;
    return ndiv;
}

function create_op_modal(idn, i) {
    var modal_1 = '<div class="modal fade" id="';
    //here the modal id
    var modal_2 = '" tabindex="-1" role="dialog" aria-labelledby="';
    //here the label id
    var modal_3 = '" aria-hidden="true"> \
                        <div class="modal-dialog" role="document"> \
                            <div class="modal-content"> \
                                <div class="modal-header"> \
                                    <button type="button" class="close" data-dismiss="modal" aria-label="Close"> \
                                        <span aria-hidden="true">&times;</span> \
                                            </button> \
                                                <table><tr><td><img src="img/';
    //here the svg image
    var modal_4 = '.svg"/></td><td><h4 class="modal-title" id="';
    //here the label id
    var modal_5 = '"><b>&nbsp;&nbsp;';
    //here the label
    var modal_6 = '</b></h4></td></table> \
                  </div> \
                  <div class="modal-body"> ';
    //here the blabla
    var modal_7 = '</div> \
                </div> \
              </div> \
            </div> ';
    
    var s = modal_1+"modal_"+idn+"_"+i;
    s = s + modal_2+"modal_label_"+idn+"_"+i;
    s = s + modal_3+ops[idn][0]; 
    s = s + modal_4+"modal_label_"+idn+"_"+i;
    s = s + modal_5+ops[idn][0];
    s = s + modal_6+"<br>Here is where we'll put the operators parameters. <br>Soon :)";
    s = s + modal_7;
    
    var wrapper= document.createElement('div');
    wrapper.innerHTML= s;
    var ndiv= wrapper.firstChild;
    return ndiv;
}


function load_project() {
    not_yet();
}


function save_project() {
    //not_yet();
    
    //sandbox/begin
    
     ws_request('operator_input_info', [0], {}, function (result) {
        var res = JSON.parse(JSON.stringify(result));
        console.log(res);
    });
    //sansbox/end
};


function new_project() {
    var res = confirm("Are you sure you want to erase the current project ?");
    if (!res) 
        return false;
    
    //we remove all the nodes but the last created, so the node with "moving" in their id
    for (i=0; i<ops.length; i++)
        for (j=0; j<ops_nb; j++) {
            var tmp = document.getElementById("moving_"+i+"_"+j);
            if (tmp != null) {
                jsPlumb.remove(tmp.id);
            }
        }
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
