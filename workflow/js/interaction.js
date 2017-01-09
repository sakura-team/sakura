document.addEventListener("dragstart", function ( e ) {
    e.dataTransfer.setData('text/plain', null);
    var rect = e.target.getBoundingClientRect();
    currently_dragged = e.target;
    drag_delta = [e.clientX - rect.left, e.clientY - rect.top];
}, false);


main_div.addEventListener("dragover", function( e ) {
    e.preventDefault();
}, false);


main_div.addEventListener("drop", function( e ) {
    e.preventDefault();
    if (currently_dragged.id.includes("static")) {
        var rect = main_div.getBoundingClientRect();
        create_operator_instance(   e.clientX - rect.left - drag_delta[0], 
                                    e.clientY - rect.top - drag_delta[1] + e.target.scrollTop, 
                                    currently_dragged.id);
    }
    else if (currently_dragged.id.includes("svg_modal_link") && e.target.parentElement.parentElement.id.includes("svg_modal_link")) {
        console.log("HERE");
    }
    else
        console.log("NOT HERE");
    currently_dragged = null;
}, false);


$('#sakura_operator_contextMenu').on("click", "a", function() {
    $('#sakura_operator_contextMenu').hide();
    remove_operator_instance(ops_focus.id);
});


$('#sakura_main_div').on("click", function () {
    if (ops_focus != null) {
        $('#sakura_operator_contextMenu').hide();
        ops_focus = null;
    }
});


function open_op_params() {
    var modal_name = "modal_"+this.id;
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
