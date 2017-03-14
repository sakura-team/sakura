//Code started by Michael Ortega for the LIG
//November 14th, 2016

/////////////////////////////////////////////////////////
//Globals

//operators
var global_op_panels    = [];
var global_ops_cl       = [];
var global_ops_inst     = [];
var op_focus_id         = null;
var link_focus_id       = null;

//links
var global_links        = []; //[local_id, jsPlumb_id, src_inst_id (from hub), dst_inst_id (from hub)]
var global_links_params = []; //[local_id, src_param_id, dst_param_id, hub_link_id]
var global_links_inc    = 0;  // for the links' local ids

//interaction
var drag_delta          = [0, 0];
var currently_dragged   = null;
var current_modal_id    = null;

//main
var main_div = document.getElementById('sakura_main_div');


function not_yet(s = '') {
    if (s == '')
        alert('Not implemented yet');
    else
        alert('Not implemented yet: '+ s);
}


function instance_index_from_hub_id(hid) {
    for (var i=0; i< global_ops_inst.length; i++)
        if (global_ops_inst[i].hub_id == hid)
            return i;
    return -1
}


function instance_from_hub_id(hid) {
    for (var i=0; i< global_ops_inst.length; i++)
        if (global_ops_inst[i].hub_id == hid)
            return global_ops_inst[i];
    return null;
}


//send the index of the row where arr[row][col] == e
function index_in_array_of_tuples(arr, col, e) {
    for (var i = 0; i< arr.length; i++)
        if (arr[i][col] == e)
            return i;
    return -1;
}


function tuple_in_array_of_tuples(arr, tuple) {
    for (var i = 0; i< arr.length; i++) {
        
        var is_the_one = true;
        for (var j = 0; j< tuple.length; j++)
            if (arr[i][j] != tuple[j])
                is_the_one = false;
        
        if (is_the_one)
            return i;
    } 
    return -1;
}


//returns a sub-array in which arr[row][col] == e for each row
function sub_array_of_tuples(arr, col, e) {
    var result = [];
    for (var i = 0; i< arr.length; i++) {
        if (arr[i][col] == e)
            result.push(arr[i]);
    }
    return result;
}


function svg_round_square(id) {
    return '<svg width="24" height="24" viewBox="0 0 24 24" id="'+id+'" name="'+id+'"> \
                <rect x="2" y="2" width="20" height="20" rx="4" ry="4" \
                    style="fill: grey; stroke: black; stroke-width: 2"/> \
            </svg>';
}


function svg_round_square_crossed(id) {
    return '<svg width="24" height="24" viewBox="0 0 24 24" id="'+id+'" name="'+id+'"> \
                <rect x="2" y="2" width="20" height="20" rx="4" ry="4" \
                    style="fill: grey; stroke: black; stroke-width: 2"/> \
                <line x1="3" y1="3" x2="21" y2="21" \
                    style="fill: grey; stroke: black; stroke-width: 2"/> \
                <line x1="3" y1="21" x2="21" y2="3" \
                    style="fill: grey; stroke: black; stroke-width: 2"/> \
            </svg>';
}


function escapeHtml(text) {
    return text.replace(/[\"&<>]/g, function (a) {
        return { '"': '&quot;', '&': '&amp;', '<': '&lt;', '>': '&gt;' }[a];
    });
}

