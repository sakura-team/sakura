/*Code started by Michael Ortega for the LIG*/
/*November 14th, 2016*/

var sakura_web_site = 'http://localhost/~ortega/panteda/sakura';


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
