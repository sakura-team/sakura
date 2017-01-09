/*Code started by Michael Ortega for the LIG*/
/*November 14th, 2016*/

/////////////////////////////////////////////////////////
//Globals

//operators
var global_op_panels    = [];
var global_ops_cl       = [];
var global_ops_inst     = [];
var ops_focus           = null;

//links
var global_link_panels  = [];
var global_links        = [];

//interaction
var drag_delta = [0, 0];
var currently_dragged = null;

//main
var main_div = document.getElementById('sakura_main_div');


//send the index of the row where arr[col] == e
function index_in_array_of_tuples(arr, col, e) {
    for (var i = 0; i< arr.length; i++)
        if (arr[i][col] == e)
            return i;
    return -1;
}

function svg_round_square(id) {
    return '<svg width="24" height="24" viewBox="0 0 24 24" id="'+id+'" name="'+id+'"> \
                <rect x="2" y="2" width="20" height="20" rx="4" ry="4" \
                    style="fill: grey; stroke: black; stroke-width: 2"/> \
            </svg>';
}

