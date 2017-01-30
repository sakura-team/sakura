//Code started by Michael Ortega for the LIG
//Started on: January 30th, 2017

function not_yet(s) {
    alert("Not implemented yet !", s);
}

function show_div(id) {
    //Hide all
    maindivs_array.forEach( function(item) {
        document.getElementById(item).style.visibility='hidden';
    });
    //Show the one
    document.getElementById(maindivs_array[id]).style.visibility='visible';
    
    var d = document.getElementById("navbar_ul");
    for (var i=0; i< d.children.length; i++)
        d.children[i].className = "";
    d.children[id].className = "active";
}