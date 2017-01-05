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
var drag_current_op = null;

//main
var main_div = document.getElementById('sakura_main_div');


function index_in_array_of_tuples(arr, col, e) {
    for (var i = 0; i< arr.length; i++)
        if (arr[i][col] == e)
            return i;
    return -1;
}

