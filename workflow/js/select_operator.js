//Code started by Michael Ortega for the LIG
//December 06th, 2016


select_op_ops = []
//This function ask about all the operators, and then update the "operators selection" modal
function select_op_open_modal() {
    
    //cleaning
    $('#select_op_tags_select').empty();
    $('#select_op_names_select').empty();
    document.getElementById('select_op_panel_title').value = '';
    
    //Before opening the modal, we have to ask about the existing operators, and then make the tags list
    ws_request('list_operators_classes', [], {}, function (result) {
        var tags_list = [];
        var sostl = document.getElementById('select_op_tags_select');
        var sosnl = document.getElementById('select_op_names_select');
        
        var div = document.getElementById('select_op_panel');
        while(div.firstChild){
            div.removeChild(div.firstChild);
        }
        
        select_op_ops = JSON.parse(JSON.stringify(result));
        for (var i=0; i<select_op_ops.length; i++) {
            select_op_ops[i][3].forEach( function (item) {
                    if (tags_list.indexOf(item) == -1) {
                        tags_list.push(item);
                        var option = document.createElement("option");
                        option.text = item;
                        sostl.add(option);
                    }
                });
            var option = document.createElement("option");
            option.text = select_op_ops[i][1];
            option.value = select_op_ops[i][0];
            option.setAttribute("data-subtext", select_op_ops[i][2]);
            sosnl.add(option);
        }
        $('#select_op_tags_select').selectpicker('refresh');
        $('#select_op_names_select').selectpicker('refresh');
        $('#modal_op_selector').modal();
    });
}


function select_op_on_change() {
    var ops_t = document.getElementById("select_op_tags_select").options;
    var ops_n = document.getElementById("select_op_names_select").options;
    
    //cleaning
    var pdiv = document.getElementById('select_op_panel');
    while(pdiv.firstChild){
        pdiv.removeChild(pdiv.firstChild);
    }
    displayed = [];
    
    //tags
    for (var o=0; o<ops_t.length; o++) {
        if (ops_t[o].selected) {
            select_op_ops.forEach( function (item) {
                if (item[3].indexOf(ops_t[o].text) >= 0 && displayed.indexOf(item[0]) == -1) {
                    select_op_new_div(item[4], item[1], pdiv);
                    displayed.push(parseInt(item[0]));
                }
            });
        }
    }
    
    //names
    for (var o=0; o<ops_n.length; o++) {
        if (ops_n[o].selected && displayed.indexOf(parseInt(ops_n[o].value)) == -1) {
            var ndiv = select_op_new_div(select_op_ops[ops_n[o].value][4], select_op_ops[ops_n[o].value][1] , pdiv);
            displayed.push(select_op_ops[ops_n[o].value][0]);
        }
    }
}


function select_op_new_div(svg, name, div) {
    var ndiv = document.createElement('div');
    ndiv.innerHTML = '<table> \
                        <tr> \
                            <td align="center">'+svg+ ' \
                            <td valign="top"> <span class="glyphicon glyphicon-remove" onclick="not_yet();" style="cursor: pointer;"/> \
                        <tr> \
                            <td align="center" colspan="2"> \
                                <div class="panel panel-default"> \
                                    <div class="panel-body-sm"> \
                                        <table width="100%"> \
                                            <tr> \
                                                <td align="center" style="padding: 1px;">&nbsp;'+name+' &nbsp;\
                                        </table> \
                                    </div> \
                                </div> \
                            </table>';
    ndiv.id = "select_op_icon_"+name;
    div.appendChild(ndiv);
    
    //var tab = document.getElementById('select_op_panel_table');
    //console.log(tab);
    
}