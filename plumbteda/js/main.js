//Code started by Michael Ortega for the LIG
//October 10th, 2016

/////////////////////////////////////////////////////////
//Globals

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



var ops = [["Data", 01], ["Select", 11], ["Mean", 10], ["New", 10]];
var ops_nb = 0;
var op_div = document.getElementById('ptda_op_div');
var main_div = document.getElementById('ptda_main_div');

var conns = []
var ops_focus = null;


/////////////////////////////////////////////////////////
//Basic Functions

function not_yet() {
    alert('Not implemented yet');
}


function new_static_operator(x, y, idn) {
    var ndiv = document.createElement("div");
    ndiv.innerHTML = "<img src='img/"+ops[idn][0]+".svg'></img>"
    ndiv.id = "static_"+idn+"_"+ops_nb;
    ndiv.classList.add("ptda_operator");
    ndiv.style.left = x;
    ndiv.style.top = y
    op_div.appendChild(ndiv);
    op_div.appendChild(create_modal(idn, ops_nb));
    ops_nb++;
    
    return ndiv;
};


function create_modal(idn, i) {
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
    not_yet();
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


/////////////////////////////////////////////////////////
//Interaction

$('#ptda_operator_contextMenu').on("click", "a", function() {
    $('#ptda_operator_contextMenu').hide();
    jsPlumb.remove(ops_focus.id);
    ops_focus = null;
});


$('#ptda_main_div').on("click", function () {
    if (ops_focus != null) {
        $('#ptda_operator_contextMenu').hide();
        ops_focus = null;
    }
});


function open_op_params() {
    var tab = this.id.split("_");
    var modal_id = "modal_"+tab[1]+"_"+tab[2];
    $('#'+modal_id).modal();
}


function open_op_menu(e) {
    $('#ptda_operator_contextMenu').css({
      display: "block",
      left: e.clientX - e.layerX + 30,
      top: e.clientY - e.layerY + 30
    });
    ops_focus = this;
    return false;
}


function drag_start_cb(e) {
    if (e.el.id.includes("static")) {
        var idn = e.el.id.split("_")[1];
        old_id = e.el.id;
        new_id = e.el.id.replace("static", "moving")
        
        //Changing the id of the dragged static element
        e.el.id = new_id;
        e.el.ondblclick = open_op_params;
        
        e.el.oncontextmenu = open_op_menu;
        jsPlumb.setIdChanged(old_id, new_id);
        
        //Create a new operator
        ndiv = new_static_operator(e.el.style.left, e.el.style.top, idn);
        jsPlumb.draggable(ndiv.id, {containment:true, start: drag_start_cb, stop: drag_stop_cb});
        
        //Updating to the dragged operator
        var anc = ops[idn][1];
        if (anc == 1 || anc == 11)
            jsPlumb.addEndpoint(e.el.id, { anchor:[ "Right"], isSource:true});
        if (anc == 10 || anc == 11)
            jsPlumb.addEndpoint(e.el.id, { anchor:[ "Left"], isTarget:true});
        e.el.style.zIndex = '2';
        
        main_div.appendChild(e.el);
    }
}


function drag_stop_cb(e) {
    if (e.el.id.includes("moving")) {
        var ot = document.getElementById("ptda_op_div");
        if (e.el.getBoundingClientRect().left < ot.getBoundingClientRect().right)
            e.el.style.left = ot.offsetWidth + 1 + "px";
    }
    
    jsPlumb.repaintEverything();        //Very Important when dragging elements manually
}

/////////////////////////////////////////////////////////
//Init Functions

//Document Initialisation
function readyCallBack() {
    for (var i=0; i<ops.length; i++){
        new_static_operator(2+ i*(35+1) +"px", 2+"px", i);
    };
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
        Container: "ptda_main_div"
    });
    
    //First operators are draggable
    var instance = jsPlumb.getInstance()
    for (var i=0; i<ops.length; i++){
        var id = "static_"+i+"_"+i;
        jsPlumb.draggable(id, {containment:true, start: drag_start_cb, stop: drag_stop_cb});
    }
    
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
