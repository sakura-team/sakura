//Code started by Michael Ortega for the LIG
//December 06th, 2016


var select_op_ops       = []
var select_op_divs      = []
var select_op_selected  = []
var nb_cols_in_displayed_table = 4

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


function select_op_make_table(nb_cols, ids, divs) {
    
    //table creation
    var tbl = document.createElement('table');
    var tbdy = document.createElement('tbody');
    var nb_rows = Math.ceil(ids.length/nb_cols);
    
    tbl.style.width = '100%';
    
    var index = 0;
    for (var i=0; i< nb_rows; i++) {
        var tr = document.createElement('tr');
        for (var j=0; j<nb_cols; j++) {
            if (ids[index] != null) {
                var td = document.createElement('td');
                td.setAttribute('align', 'center');
                td.style.width = '20px';
                td.appendChild(divs[index]);
                tr.appendChild(td);
                index = index + 1;
            }
        }
        tbdy.appendChild(tr);
    }
    tbl.appendChild(tbdy);
    return tbl;
}


function select_op_on_change(from) {
    //'from' is in ['tags, 'names'], not used for now ....
    
    var ops_to = document.getElementById("select_op_tags_select").options;
    var ops_no = document.getElementById("select_op_names_select").options;
    
    //cleaning
    var pdiv = document.getElementById('select_op_panel');
    select_op_selected = []
    select_op_divs = []
    
    //tags
    for (var o=0; o<ops_to.length; o++) {
        if (ops_to[o].selected) {
            select_op_ops.forEach( function (item) {
                if (item[3].indexOf(ops_to[o].text) >= 0 && select_op_selected.indexOf(item[0]) == -1) {
                    select_op_divs.push(select_op_new_div(item[4], item[1], item[0], true));
                    select_op_selected.push(parseInt(item[0]));
                }
            });
        }
    }
    
    console.log(select_op_selected);
    
    //names
    for (var o=0; o<ops_no.length; o++) {
        if (ops_no[o].selected && select_op_selected.indexOf(parseInt(ops_no[o].value)) == -1) {
            select_op_divs.push(select_op_new_div(select_op_ops[ops_no[o].value][4], select_op_ops[ops_no[o].value][1], select_op_ops[ops_no[o].value][0], true));
            select_op_selected.push(parseInt(select_op_ops[ops_no[o].value][0]));
        }
    }
    
    //Cleaning
    while(pdiv.firstChild){
        pdiv.removeChild(pdiv.firstChild);
    }
    pdiv.appendChild(select_op_make_table(nb_cols_in_displayed_table, select_op_selected, select_op_divs));
}


function select_op_new_div(svg, name, id, removable) {
    var ndiv = document.createElement('div');
    if (removable) {
        ndiv.id = "select_op_selected_"+id+'rem';
        ndiv.innerHTML = '<table> \
                            <tr> \
                                <td align="center">'+svg+ ' \
                                <td valign="top"> <span class="glyphicon glyphicon-remove" onclick="select_op_delete_op(\''+id+'\');" style="cursor: pointer;"/> \
                            <tr> \
                                <td align="center" style="padding: 1px;">'+name+' \
                        </table>';
    }
    else {
        ndiv.id = "select_op_selected_"+id;
        ndiv.innerHTML = '<table> \
                            <tr> \
                                <td align="center">'+svg+ ' \
                            <tr> \
                                <td align="center" style="padding: 1px;">'+name+' \
                        </table>';
    }
    return (ndiv);
}


function select_op_delete_op(id) {
    
    var index = select_op_selected.indexOf(parseInt(id));
    
    select_op_selected.splice(index, 1);
    select_op_divs.splice(index, 1);
    
    var pdiv = document.getElementById('select_op_panel');
    //Cleaning
    while(pdiv.firstChild){
        pdiv.removeChild(pdiv.firstChild);
    }
    pdiv.appendChild(select_op_make_table(nb_cols_in_displayed_table, select_op_selected, select_op_divs));
}


function select_op_add_panel() {
    
    var title = document.getElementById('select_op_panel_title').value;
    if (title == '') {
        alert("Need a title for your operators panel");
        return;
    }
    
    title = title.replace(" ", "_");
    
    var divs = []
    select_op_selected.forEach( function(item) {
        var op = select_op_ops[item]
        divs.push(select_op_new_div(op[4], op[1], op[0], false));
    });
    
    var tbl = select_op_make_table(3, select_op_selected, divs);
    var tmp_el = document.createElement("div");
    tmp_el.appendChild(tbl);
    
    var new_acc = select_op_create_accordion(title, tmp_el.innerHTML);
    var acc_div = document.getElementById('op_left_accordion');
    acc_div.appendChild(new_acc);
    
    $('#modal_op_selector').modal('hide');
}


function select_op_create_accordion(title, ops) {
    var s = '<div class="panel panel-primary" id="div_acc_'+title+'"> \
                <div class="panel-heading"> \
                    <h6 class="panel-title"> \
                        <table width="100%"> \
                            <tr> \
                                <td> \
                                    <a data-toggle="collapse" style="color: white;" data-parent="#accordion" href="#acc_'+title+'">'+title+'</a> \
                                </td> \
                                <td align="right"> \
                                    <a><span class="glyphicon glyphicon-remove" onclick="not_yet();" style="color: white; cursor: pointer;"></span></a> \
                                </td> \
                            </tr> \
                        </table> \
                    </h6> \
                </div> \
                <div id="acc_'+title+'" class="panel-collapse collapse"> \
                    <div class="panel-body">'+ops+'</div> \
                </div> \
            </div>';
    
    var wrapper= document.createElement('div');
    wrapper.innerHTML= s;
    var ndiv= wrapper.firstChild;
    return ndiv;
}
