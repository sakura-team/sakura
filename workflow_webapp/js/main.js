//Code started by Michael Ortega for the LIG
//October 10th, 2016

/////////////////////////////////////////////////////////
//Globals

var ops = [["Data", 01], ["Select", 11], ["Mean", 10], ["New", 10]];
var ops_nb = 0;
var left_div = document.getElementById('sakura_left_div');
var main_div = document.getElementById('sakura_main_div');

var curr_op_tags = [];
var conns = [];
var ops_focus = null;

var drag_delta = [0, 0];
var drag_current_op = null;


/////////////////////////////////////////////////////////
//Basic Functions


function not_yet() {
    alert('Not implemented yet');
}


function suppr_tag_in_templist(tagname) {
    var ostl = document.getElementById('op_selected_tags_list');
    var child_ = document.getElementById(tagname+'_button');
    ostl.removeChild(child_);
    curr_op_tags.splice(curr_op_tags.indexOf(tagname), 1);
}


function add_tag_in_templist(tagname) {
    if (curr_op_tags.indexOf(tagname) == -1) {
        var ostl = document.getElementById('op_selected_tags_list');
        ostl.innerHTML += '<button type="button" id="'+tagname+'_button" style="color: white;background-color:#008CBA;" class="btn btn-default btn-ms" onclick="suppr_tag_in_templist(\''+tagname+'\');">'+tagname+' <span class="glyphicon glyphicon-remove"></span></button>';
        curr_op_tags.push(tagname);
    }
}


function open_op_select_modal() {
    //Before opening the modal, we have to ask about the existing operators, and then make the tags list
    var tags_list = [];
    /*$.getJSON("/opclasses", function (data) {
        console.log(data);
        });
    */
    
    //var ws_echo = new WebSocket("ws:")
    
    tags_list.push("pipo1");
    tags_list.push("pipo2");
    tags_list.push("pipo3");
    
    var ostl = document.getElementById('op_selected_tags_list');
    ostl.innerHTML = '';
    $('#modal_op_selector').modal();
}
function select_operators() {
    not_yet();
}


document.addEventListener("dragstart", function ( e ) {
    var rect = e.target.parentNode.getBoundingClientRect();
    drag_current_op = e.target.parentNode;
    console.log(e.clientX, e.clientY);
    
    console.log(rect.x, rect.y);
    drag_delta = [e.clientX - rect.x, e.clientY - rect.y];
}, false);


main_div.addEventListener("dragover", function( e ) {
    e.preventDefault();
}, false);


main_div.addEventListener("drop", function( e ) {
    e.preventDefault();
    if (drag_current_op.id.includes("static")) {
        var rect = main_div.getBoundingClientRect();
        tab_name = drag_current_op.id.split("_");
        new_dynamic_operator(   e.clientX - rect.x - drag_delta[0], 
                                e.clientY - rect.y - drag_delta[1] + e.target.scrollTop, 
                                tab_name[1]);
    }
    drag_current_op = null;
}, false);


function jsp_drag_stop(e) {
    var ot = document.getElementById("sakura_main_div");
    if (e.el.getBoundingClientRect().left < ot.getBoundingClientRect().left)
        e.el.style.left = 20 + "px";
    if (e.el.getBoundingClientRect().top < ot.getBoundingClientRect().top)
        e.el.style.top = 20 + "px";
    
    jsPlumb.repaintEverything();        //Very Important when dragging elements manually
    
}


function new_dynamic_operator(x, y, idn) {
    var ndiv = document.createElement("div");
    ndiv.innerHTML = "<img src='img/"+ops[idn][0]+".svg'></img>"
    ndiv.id = "moving_"+idn+"_"+ops_nb;
    ndiv.classList.add("sakura_dynamic_operator");
    ndiv.style.left = x+"px";
    ndiv.style.top = y+"px";
    ndiv.draggable="false";
    main_div.append(ndiv);
    main_div.append(create_op_modal(idn, ops_nb));
    
    jsPlumb.draggable(ndiv.id, {stop: jsp_drag_stop});
    
    //Updating to the dragged operator
    var anc = ops[idn][1];
    if (anc == 1 || anc == 11)
        jsPlumb.addEndpoint(ndiv.id, { anchor:[ "Right"], isSource:true});
    if (anc == 10 || anc == 11)
        jsPlumb.addEndpoint(ndiv.id, { anchor:[ "Left"], isTarget:true});
    ndiv.style.zIndex = '2';
    
    //Changing the id of the dragged static element
    ndiv.ondblclick = open_op_params;    
    ndiv.oncontextmenu = open_op_menu;
    ops_nb++;
}


function new_static_operator(x, y, idn) {
    var ndiv = document.createElement("div");
    ndiv.innerHTML = "<img src='img/"+ops[idn][0]+".svg'></img>"
    ndiv.id = "static_"+idn;
    ndiv.classList.add("sakura_static_operator");
    ndiv.draggable="true";
    ops_nb++;
    return ndiv;
};


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

$('#sakura_operator_contextMenu').on("click", "a", function() {
    $('#sakura_operator_contextMenu').hide();
    tn = ops_focus.id.split("_");
    
    //remove op
    jsPlumb.remove(ops_focus.id);
    
    //remove modal
    mod = document.getElementById("modal_"+tn[1]+"_"+tn[2]);
    mod.outerHTML = "";
    delete mod;
    ops_focus = null;
});


$('#sakura_main_div').on("click", function () {
    if (ops_focus != null) {
        $('#sakura_operator_contextMenu').hide();
        ops_focus = null;
    }
});


function open_op_params() {
    var tab = this.id.split("_");
    var modal_id = "modal_"+tab[1]+"_"+tab[2];
    $('#'+modal_id).modal();
}


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
