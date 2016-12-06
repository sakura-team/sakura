//Code started by Michael Ortega for the LIG
//October 10th, 2016


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

function op_on_change_tag() {
    var ops = document.getElementById("op_tags_select").options;
    for (var i=0;i<ops.length;i++) {
        console.log(ops[i].selected);
    }
}


function open_op_select_modal() {
    //Before opening the modal, we have to ask about the existing operators, and then make the tags list
    /*$.getJSON("/opclasses", function (data) {
        console.log(data);
        });
    */
    
    //var ws_echo = new WebSocket("ws:")
    
    var ostl = document.getElementById('op_tags_select');
    console.log(ostl);
    var option1 = document.createElement("option");
    option1.text = "Tag1";
    ostl.add(option1);
    
    var option2 = document.createElement("option");
    option2.text = "Tag2";
    ostl.add(option2);
    
    var option3 = document.createElement("option");
    option3.text = "Tag3";
    ostl.add(option3);
    
    var option4 = document.createElement("option");
    option4.text = "Tag4";
    ostl.add(option4);
    
    $('#op_tags_select').selectpicker('refresh');
    $('#modal_op_selector').modal();
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


function add_accordion() {
    
    var ops = document.getElementById("op_tags_select").options;
    var n_tag = '';
    var nb_tags = 0;
    for (var i=0;i<ops.length;i++) {
        if (ops[i].selected)
            n_tag += ops[i].text + '_';
            nb_tags++;
    }
    
    if (nb_tags > 0) {
        var new_acc = create_accordion(n_tag, "titi");
        var acc_div = document.getElementById('op_left_accordion');
        acc_div.appendChild(new_acc);
    }
}

function create_accordion(title, ops) {
    var s = '<div class="panel panel-primary" id="div_acc_'+title+'"> \
                <div class="panel-heading"> \
                    <h6 class="panel-title"> \
                        <table width="100%"> \
                            <tr> \
                                <td> \
                                    <a data-toggle="collapse" style="color: white;" data-parent="#accordion" href="#acc_'+title+'">'+title+'</a> \
                                </td> \
                                <td align="right"> \
                                    <a><span class="glyphicon glyphicon-remove" onclick="not_yet();" style="color: white; cursor: pointer;"></span></a> \
                                </td> \
                            </tr> \
                        </table> \
                    </h6> \
                </div> \
                <div id="acc_'+title+'" class="panel-collapse collapse"> \
                    <div class="panel-body">'+ops+'</div> \
                </div> \
            </div>';
    
    var wrapper= document.createElement('div');
    wrapper.innerHTML= s;
    var ndiv= wrapper.firstChild;
    return ndiv;
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
    ws_request('list_daemons', [], {}, function (result) {
        console.log(JSON.stringify(result));
    });
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
