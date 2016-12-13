$('#sakura_operator_contextMenu').on("click", "a", function() {
    $('#sakura_operator_contextMenu').hide();
    console.log(ops_focus);
    jsPlumb.remove(ops_focus.id);
    
    //remove modal
    var mod = document.getElementById("modal_"+ops_focus.id);
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
    var modal_name = "modal_"+this.id;
    $('#'+modal_name).modal();
}
