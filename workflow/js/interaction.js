document.addEventListener("dragstart", function ( e ) {
    e.dataTransfer.setData('text/plain', null);
    var rect = e.target.getBoundingClientRect();
    currently_dragged = e.target;
    
    if (currently_dragged.id.includes("svg_modal_link")) {
        //currently_dragged.innerHTML = svg_round_square("");
        var modal_id = currently_dragged.id.split("_")[3];
        var bdiv = document.getElementById("modal_link_"+modal_id+"_body");
    }
    drag_delta = [e.clientX - rect.left, e.clientY - rect.top];
}, false);


main_div.addEventListener("dragover", function( e ) {
    e.preventDefault();
}, false);


main_div.addEventListener("drop", function( e ) {
    e.preventDefault();
    //Operators
    if (currently_dragged.id.includes("static")) {
        var rect = main_div.getBoundingClientRect();
        create_operator_instance(   e.clientX - rect.left - drag_delta[0], 
                                    e.clientY - rect.top - drag_delta[1] + e.target.scrollTop, 
                                    currently_dragged.id);
    }
    
    //Link params
    else if (currently_dragged.id.includes("svg_modal_link") && e.target.parentElement.parentElement.id.includes("svg_modal_link")) {
        var param_out = currently_dragged;
        var param_in = e.target.parentElement.parentElement;
        
        //Make sure the two links are from two objects
        if (    (param_out.id.includes("_in_") && param_in.id.includes("_in_")) ||
                (param_out.id.includes("_out_") && param_in.id.includes("_out_")) ) {
            return ;
        }
        //Make sure out is from object out
        else if (param_out.id.includes("_in_") && param_out.id.includes("_in_")) {
            param_in = currently_dragged;
            param_out = e.target.parentElement.parentElement;
        }
        
        var tab1 = param_out.id.split("_");
        var modal_id = parseInt(tab1[3]);
        var _out_id = parseInt(tab1[5]);
        var _in_id = parseInt(param_in.id.split("_")[5]);
        
        var params_for_this_modal = sub_array_of_tuples(global_links_params, 0, modal_id);
        
        //if (tuple_in_array_of_tuples(global_links_params, [modal_id, _out_id, _in_id]) == -1) {
        if (index_in_array_of_tuples(params_for_this_modal, 1, _out_id) == -1 &&
            index_in_array_of_tuples(params_for_this_modal, 2, _in_id) == -1 ) {
            
            //we first retrieve the objects instance ids
            var index = index_in_array_of_tuples(global_links, 0, modal_id)
            var src_op_id = global_links[index][2];
            var dst_op_id = global_links[index][3];
            
            //src_op_id, src_out_id, dst_op_id, dst_in_id):
            ws_request('create_link', [src_op_id, _out_id, dst_op_id, _in_id], {}, function (link_id_from_hub) {
                
                //local creation
                create_link_line(modal_id, _out_id, _in_id);
                global_links_params.push([modal_id, _out_id, _in_id, parseInt(link_id_from_hub)]);
                
                //changing svgs
                var div_out = document.getElementById(param_out.id)
                var div_in  = document.getElementById(param_in.id);
                div_in.innerHTML = svg_round_square_crossed("");
                div_out.innerHTML = svg_round_square_crossed("");
                
                currently_dragged = null;
            });
        }
        else {
            console.log("Already exists !!");
            currently_dragged = null;
        }
    }
    else {
        console.log("Unknown Drop !!!");
        currently_dragged = null;
    }
}, false);


$(window).bind('keypress', function(e){
    if ( $("#modal_op_selector").is(':visible') && (e.keyCode == 13 || e.which == 13))
        select_op_add_panel();
});


$('#sakura_operator_contextMenu').on("click", "a", function() {
    $('#sakura_operator_contextMenu').hide();
    remove_operator_instance(op_focus_id);
});

$('#sakura_link_contextMenu').on("click", "a", function() {
    $('#sakura_link_contextMenu').hide();
    remove_link(link_focus_id);
});


$('#sakura_main_div').on("click", function () {
    if (op_focus_id != null) {
        $('#sakura_operator_contextMenu').hide();
        op_focus_id = null;
    }
    else if (link_focus_id != null) {
        $('#sakura_link_contextMenu').hide();
        op_focus_id = null;
    }
});


function open_op_modal() {
    var modal_name = "modal_"+this.id;
    current_modal_id = "modal_"+this.id;
    fill_all(this.id);
    $('#'+modal_name).modal();
}


function jsp_drag_stop(e) {
    var ot = document.getElementById("sakura_main_div");
    if (e.el.getBoundingClientRect().left < ot.getBoundingClientRect().left)
        e.el.style.left = 20 + "px";
    if (e.el.getBoundingClientRect().top < ot.getBoundingClientRect().top)
        e.el.style.top = 20 + "px";
    
    jsPlumb.repaintEverything();        //Very Important when dragging elements manually
}


function delete_link_param(id) {
    console.log(id);
    var tab         = id.split("_");
    var modal_id    = parseInt(tab[2]);
    var div_type    = tab[3];
    var param_id    = parseInt(tab[4]);
    
    var col = 1;
    if (div_type == "in") {
        col = 2;
    }
        
    var indexes = [];
    for (var i = 0; i < global_links_params.length; i++) {
        if (global_links_params[i][0] == modal_id && global_links_params[i][col] == param_id) {
            indexes.push(i);
            
            //console.log("Delete link param:", global_links_params[i]);
            
            var mdiv = document.getElementById("modal_link_"+modal_id+"_body");
            var line = "";
            var div_out = "";
            var div_in = "";
            
            if (div_type == "out") {
                div_out = document.getElementById("svg_"+id);
                div_in  = document.getElementById("svg_modal_link_"+modal_id+"_in_"+global_links_params[i][2]);                
                line = document.getElementById("line_modal_link_"+modal_id+"_"+param_id+"_"+global_links_params[i][2]);
            }
            else {
                div_out  = document.getElementById("svg_modal_link_"+modal_id+"_out_"+global_links_params[i][1]);
                div_in = document.getElementById("svg_"+id);
                line = document.getElementById("line_modal_link_"+modal_id+"_"+global_links_params[i][1]+"_"+param_id);
            }
            
            //change the svgs
            div_in.innerHTML = svg_round_square("");
            div_out.innerHTML = svg_round_square("");
            
            //delete the line
            mdiv.removeChild(line);
            
            //delete from hub side
            var hub_link_id = global_links_params[i][3];
            ws_request('delete_link', [hub_link_id], {}, function (result) {
                if (result) {
                    console.log("Issue with 'delete_link' function from hub:", result);
                }
            });
        }
    }
    
    for (var i = indexes.length-1; i >= 0; i--) {
        global_links_params.splice(indexes[i], 1);
    }
}

function create_link_line(id, _out, _in) {
    var rect0 = document.getElementById("modal_link_"+id+"_dialog").getBoundingClientRect();
    var rect1 = document.getElementById("svg_modal_link_"+id+'_out_'+_out).getBoundingClientRect();
    var rect2 = document.getElementById("svg_modal_link_"+id+'_in_'+_in).getBoundingClientRect();
    
    var w = Math.abs(rect2.x-rect1.x-24+2);
    var h = Math.abs(rect2.y-rect1.y+2);
    
    //Making a fake connection
    var mdiv = document.getElementById("modal_link_"+id+"_body");
    
    var svg_div = document.createElement('div');
    svg_div.id = "line_modal_link_"+id+"_"+_out+"_"+_in;
    //console.log("line id", svg_div.id);
    
    svg_div.style.position = 'absolute';
    
    svg_div.style.left = (rect1.x-rect0.x+24-1)+'px';
    if (rect2.y >= rect1.y) {
        svg_div.style.top = (rect1.y-rect0.y+12-1)+'px';
        svg_div.innerHTML= '<svg height="'+(h+20)+'" width="'+(w)+'"> \
                                <line x1="1" y1="1" x2="'+(w-1)+'" y2="'+(h-1)+'" style="stroke:rgb(33,256,33);stroke-width:2" /> \
                            </svg> ';
    }
    else {
        svg_div.style.top = (rect2.y-rect0.y+12-1)+'px';
        svg_div.innerHTML= '<svg height="'+(h)+'" width="'+(w)+'"> \
                                <line x1="1" y1="'+(h-1)+'" x2="'+(w-1)+'" y2="1" style="stroke:rgb(33,256,33);stroke-width:2" /> \
                            </svg> ';
    }
    mdiv.appendChild(svg_div);
}