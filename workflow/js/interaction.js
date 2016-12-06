$('#sakura_operator_contextMenu').on("click", "a", function() {
    $('#sakura_operator_contextMenu').hide();
    tn = ops_focus.id.split("_");
    
    //remove op
    jsPlumb.remove(ops_focus.id);
    
    //remove modal
    mod = document.getElementById("modal_"+tn[1]+"_"+tn[2]);
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
    var tab = this.id.split("_");
    var modal_id = "modal_"+tab[1]+"_"+tab[2];
    $('#'+modal_id).modal();
}
