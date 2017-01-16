//Code started by Michael Ortega for the LIG
//December 06th, 2016


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
        
        global_ops_cl = JSON.parse(JSON.stringify(result));
        
        global_ops_cl.forEach( function (op) {
            op['tags'].forEach( function (tag) {
                if (tags_list.indexOf(tag) == -1) {
                        tags_list.push(tag);
                        var option = document.createElement("option");
                        option.text = tag;
                        sostl.add(option);
                }
            });
            var option = document.createElement("option");
            option.text = op['name'];
            option.value = op['id'];
            option.setAttribute("data-subtext", op['daemon']);
            sosnl.add(option);
        });
            
        $('#select_op_tags_select').selectpicker('refresh');
        $('#select_op_names_select').selectpicker('refresh');
        current_modal_id = 'modal_op_selector';
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
            global_ops_cl.forEach( function (op) {
                if (op['tags'].indexOf(ops_to[o].text) >= 0 && select_op_selected.indexOf(op['id']) == -1) {
                    select_op_divs.push(select_op_new_div(op['svg'], op['name'], op['id'], true));
                    select_op_selected.push(parseInt(op['id']));
                }
            });
        }
    }
    
    //names
    for (var o=0; o<ops_no.length; o++) {
        if (ops_no[o].selected && select_op_selected.indexOf(parseInt(ops_no[o].value)) == -1) {
            select_op_divs.push(select_op_new_div(global_ops_cl[ops_no[o].value]['svg'], global_ops_cl[ops_no[o].value]['name'], global_ops_cl[ops_no[o].value]['id'], true));
            select_op_selected.push(parseInt(global_ops_cl[ops_no[o].value]['id']));
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
                                <td align="center">'+name+' \
                        </table>';
    }
    else {
        ndiv.id = "select_op_selected_"+id+"_static";
        ndiv.setAttribute('draggable', 'true');
        ndiv.style.zIndex = '2';
        ndiv.classList.add("sakura_static_operator");
        ndiv.innerHTML = '<table> \
                            <tr> \
                                <td align="center">'+svg+ ' \
                            <tr> \
                                <td align="center">'+name+' \
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
        var op = global_ops_cl[item]
        divs.push(select_op_new_div(op['svg'], op['name'], op['id'], false));
    });
    
    var tbl = select_op_make_table(3, select_op_selected, divs);
    var tmp_el = document.createElement("div");
    tmp_el.appendChild(tbl);
    
    var acc_id = global_op_panels.length;
    global_op_panels.forEach( function (op) {
        if (op['id'] == acc_id)
            acc_id ++;
    });
    
    acc_id = "accordion_"+acc_id
    
    var new_acc = select_op_create_accordion(title, acc_id, tmp_el.innerHTML);
    var acc_div = document.getElementById('op_left_accordion');
    var butt = document.getElementById('select_op_add_button');
    
    acc_div.insertBefore(new_acc, butt);
    
    //update global variable
    global_op_panels.push([acc_id, title, select_op_selected]);
    current_modal_id = null;
    $('#modal_op_selector').modal('hide');
}


function select_op_create_accordion(title, id, ops) {
    var s = '<div id="'+id+'" class="panel panel-primary" id="div_acc_'+title+'"> \
                <div class="panel-heading"> \
                    <h6 class="panel-title"> \
                        <table width="100%"> \
                            <tr> \
                                <td> \
                                    <a data-toggle="collapse" style="color: white;" data-parent="#accordion" href="#acc_'+title+'">'+title+'</a> \
                                </td> \
                                <td align="right"> \
                                    <a><span class="glyphicon glyphicon-remove" onclick="select_op_delete_accordion(\''+id+'\');" style="color: white; cursor: pointer;"></span></a> \
                                </td> \
                            </tr> \
                        </table> \
                    </h6> \
                </div> \
                <div id="acc_'+title+'" class="panel-collapse collapse in"> \
                    <div class="panel-body">'+ops+'</div> \
                </div> \
            </div>';
    
    var wrapper= document.createElement('div');
    wrapper.innerHTML= s;
    var ndiv= wrapper.firstChild;
    return ndiv;
}

function select_op_delete_accordion(id) {
    document.getElementById('op_left_accordion').removeChild(document.getElementById(id));
}
