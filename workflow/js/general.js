/*Code started by Michael Ortega for the LIG*/
/*November 14th, 2016*/

var sakura_web_site = 'http://localhost/~ortega/panteda/sakura';


/////////////////////////////////////////////////////////
//Globals


//id, title, liste of operators ids
var global_op_panels    = [];
var global_ops_cl       = [];
var global_ops_inst     = [];

var main_div = document.getElementById('sakura_main_div');

var conns = [];
var ops_focus = null;

var drag_delta = [0, 0];
var drag_current_op = null;
