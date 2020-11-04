//Code started by Michael Ortega for the LIG
//December 06th, 2016


var select_op_divs      = []
var select_op_selected  = []
var nb_cols_in_displayed_table = 4
var svg_up_div  = null;

//This function ask about all the operators, and then update the "operators selection" modal
function select_op_new_modal() {

    //cleaning
    $('#select_op_tags_select').empty();
    $('#select_op_names_select').empty();
    document.getElementById('select_op_panel_title').value = '';

    $("#select_op_make_button").removeClass('btn btn-secondary').addClass('btn btn-primary');
    $("#select_op_update_button").hide();

    //Before opening the modal, we have to ask about the existing operators, and then make the tags list
    push_request('op_classes_list');
    sakura.apis.hub.op_classes.list().then(function (result) {
        pop_request('op_classes_list');
        let tags_list = [];
        let sostl = document.getElementById('select_op_tags_select');
        let sosnl = document.getElementById('select_op_names_select');

        let div = document.getElementById('select_op_panel');
        while(div.firstChild){
            div.removeChild(div.firstChild);
        }

        current_op_classes_list = JSON.parse(JSON.stringify(result));
        current_op_classes_list.forEach( function (op) {
            op['tags'].forEach( function (tag) {
                if (tags_list.indexOf(tag) == -1) {
                        tags_list.push(tag);
                        let option = document.createElement("option");
                        option.text = tag;
                        sostl.add(option);
                }
            });
            let option = document.createElement("option");
            option.text = op['name'];
            option.value = op['id'];
            sosnl.add(option);
        });

        $('#select_op_tags_select').selectpicker('refresh');
        $('#select_op_names_select').selectpicker('refresh');
        $('#modal_op_selector').modal();
    });
}


function select_op_reopen_modal(id) {
    panel = panel_from_id(id);
    panel_focus_id = id;

    $('#select_op_tags_select').empty();
    $('#select_op_names_select').empty();
    document.getElementById('select_op_panel_title').value = '';

    $("#select_op_make_button").removeClass('btn btn-primary').addClass('btn btn-secondary');
    $("#select_op_update_button").show();

    //Before opening the modal, we have to ask about the existing operators, and then make the tags list
    push_request('op_classes_list');
    sakura.apis.hub.op_classes.list().then(function (result) {
        pop_request('op_classes_list');
        let tags_list = [];
        let sostl = document.getElementById('select_op_tags_select');
        let sosnl = document.getElementById('select_op_names_select');

        let div = document.getElementById('select_op_panel');
        while(div.firstChild){
            div.removeChild(div.firstChild);
        }

        current_op_classes_list = JSON.parse(JSON.stringify(result));
        current_op_classes_list.forEach( function (op) {
            op['tags'].forEach( function (tag) {
                if (tags_list.indexOf(tag) == -1) {
                        tags_list.push(tag);
                        let option = document.createElement("option");
                        option.text = tag;
                        panel.selected_ops.forEach( function (id) {
                            if (op['id'] == id)
                                option.selected = true
                        });
                        sostl.add(option);
                }
            });
            let option      = document.createElement("option");
            option.text     = op['name'];
            option.value    = op['id'];
            option.selected = false;
            panel.selected_ops.forEach( function (id) {
                if (op['id'] == id)
                    option.selected = true
            });
            sosnl.add(option);
        });

        document.getElementById('select_op_panel_title').value = panel.title;

        select_op_on_change();

        //Cleaning
        while(div.firstChild){
            div.removeChild(div.firstChild);
        }

        let divs = [];
        panel.selected_ops.forEach( function(op) {
            divs.push(select_op_new_operator(op, true));
        });

        let pdiv = document.getElementById('select_op_panel');
        pdiv.appendChild(select_op_make_table(nb_cols_in_displayed_table, divs));

        $('#select_op_tags_select').selectpicker('refresh');
        $('#select_op_names_select').selectpicker('refresh');

        $('#modal_op_selector').modal();
    });
}


function select_op_make_table(nb_cols, divs) {

    //table creation
    let tbl = document.createElement('table');
    let tbdy = document.createElement('tbody');
    let nb_rows = Math.ceil(divs.length/nb_cols);

    tbl.style.width = '100%';

    let index = 0;
    for (let i=0; i< nb_rows; i++) {
        let tr = document.createElement('tr');
        for (let j=0; j<nb_cols; j++) {
            if (divs[index] != null) {
                let td = document.createElement('td');
                td.setAttribute('align', 'center');
                td.style.width = '20px';
                td.appendChild(divs[index]);
                tr.appendChild(td);
                index = index + 1;
            }
            else {
                let td = document.createElement('td');
                td.setAttribute('align', 'center');
                td.style.width = '20px';
                tr.appendChild(td);
                index = index + 1;
            }
        }
        tbdy.appendChild(tr);
    }
    tbl.appendChild(tbdy);
    return tbl;
}


function select_op_on_change() {

    let ops_to = document.getElementById("select_op_tags_select").options;
    let ops_no = document.getElementById("select_op_names_select").options;

    //cleaning
    let pdiv = document.getElementById('select_op_panel');
    select_op_selected = []
    select_op_divs = []

    //tags
    for (let o=0; o<ops_to.length; o++) {
        if (ops_to[o].selected) {
            current_op_classes_list.forEach( function (op) {
                if (op['tags'].indexOf(ops_to[o].text) >= 0 && select_op_selected.indexOf(op['id']) == -1) {
                    select_op_divs.push(select_op_new_operator(parseInt(op['id']), true));
                    select_op_selected.push(parseInt(op['id']));
                }
            });
        }
    }

    //names
    for (let o=0; o<ops_no.length; o++) {
        if (ops_no[o].selected && select_op_selected.indexOf(parseInt(ops_no[o].value)) == -1) {
            select_op_divs.push(select_op_new_operator(parseInt(ops_no[o].value), true));
            select_op_selected.push(parseInt(ops_no[o].value));
        }
    }

    //Cleaning
    while(pdiv.firstChild){
        pdiv.removeChild(pdiv.firstChild);
    }
    pdiv.appendChild(select_op_make_table(nb_cols_in_displayed_table, select_op_divs));
}

function dragging_svg(event, id) {
    svg_up_div = document.getElementById(id);
}

function select_op_new_operator(id, removable) {
    let cl = class_from_id(id);
    let ndiv = document.createElement('div');
    let s = '';
    let svg = cl.svg;

    // if (!cl.enabled) {
    //     svg = disable_op_svg(svg);
    // }

    ndiv.id = "select_op_selected_"+cl.id+"_static";
    if (removable) {
        ndiv.id = "select_op_selected_"+cl.id+'_rem';
    }

    //Main div with svg
    let div1  = $('<div>');
    let table = $('<table>');
    let tr    = $('<tr>');
    if (removable) {
        console.log('Here');
        let td1 = $('<td>', {align: "center"});
        let td2 = $('<td>', {valign: "top"});
        let td_span = $('<span>', {class: "glyphicon glyphicon-remove", onclick: "select_op_delete_op(\'"+cl.id+"\');", style: "cursor: pointer;"});
        td1.html(svg);
        table.append(tr.append([td1, td2.append(td_span)]));
    }
    else {
      let td = $('<td>');
      let svg_div = $('<div>', {class: 'op_svg_'+cl.id,
                                height: "38px",
                                draggable:"true",
                                ondragstart:"dragging_svg(event,\'"+ndiv.id+"\')"});
      svg_div.html(svg);
      table.append(tr.append(td.append(svg_div)));
    }

    let l = cl.name.length;
    let fname = cl.name;
    if (l > 7) {
        fname = cl.name.substring(0,7)+'.';
    }
    let tr2 = $('<tr>');
    let td3 = $('<td>', {align: "center", height: '14px'});
    td3.html('<p style="line-height:13px; margin-bottom: 0px;"><font size="1">'+fname+'</font></p>');
    table.append(tr2.append(td3));

    $(ndiv).append(div1.append(table));

    //exclamation
    let excl_div = $('<div>', {style: "position: absolute; top:8px; left: 13px;visibility: hidden;"});
    let excl_span = $('<span>', {class: "glyphicon glyphicon-exclamation-sign", style: "cursor: pointer;"});
    excl_div.append(excl_span);

    //list button
    if (!removable) {
      let list_div = $('<div>', {style: "position: absolute; font-size: 1.2em; top:-5px; left: 32px; visibility: hidden;"});
      let list_span = $('<span>', {class: "glyphicon glyphicon-menu-hamburger", style:"cursor: pointer;"});
      $(ndiv).append(list_div.append(list_span));
    }
    $(ndiv).append(excl_div);

    return (ndiv);
}


function select_op_delete_op(id) {

    let index = select_op_selected.indexOf(parseInt(id));

    select_op_selected.splice(index, 1);
    select_op_divs.splice(index, 1);

    let pdiv = document.getElementById('select_op_panel');

    //Cleaning div
    while(pdiv.firstChild){
        pdiv.removeChild(pdiv.firstChild);
    }
    pdiv.appendChild(select_op_make_table(nb_cols_in_displayed_table, select_op_divs));

    //Cleaning name selection
    let options = document.getElementById("select_op_names_select").options;
    for (let i=0; i<options.length;i++) {
        options[i].selected = false;
        select_op_divs.forEach( function(op) {
            let val = op.id.split('_')[3];
            if (val == options[i].value)
                options[i].selected = true;
        });
    }
    $('#select_op_names_select').selectpicker('refresh');
}


function select_op_add_panel() {
    let title = document.getElementById('select_op_panel_title').value;

    //Here we manage a panel title by default
    if (title == '') {
        title  = "Panel 0";
        let cpt = 0;
        global_op_panels.forEach( function (p) {
            if (p['title'] == title) {
                 cpt += 1;
            }
        title = "Panel "+cpt;
        });
    }

    let divs = []
    select_op_selected.forEach( function(item) {
        divs.push(select_op_new_operator(item, false));
    });

    let tbl = select_op_make_table(nb_cols_in_displayed_table, divs);
    let tmp_el = document.createElement("div");
    tmp_el.appendChild(tbl);

    let acc_id = global_op_panels.length;
    global_op_panels.forEach( function (op) {
        if (op['id'] == acc_id)
            acc_id ++;
    });

    let names = []
    let options = document.getElementById("select_op_names_select").options;
    for (let i=0; i<options.length;i++) {
        names.push(options[i].selected);
    }

    let tags = []
    options = document.getElementById("select_op_tags_select").options;
    for (let i=0; i<options.length;i++) {
        tags.push(options[i].selected);
    }

    let panel = {'id': acc_id, 'title': title, 'selected_ops': select_op_selected, gui: {'opened': true}, 'names': names, 'tags': tags}
    panel.id = "accordion_"+acc_id;

    global_op_panels.push(panel);

    select_op_create_accordion(panel, tmp_el.innerHTML);

    //update global variable
    $('#modal_op_selector').modal('hide');

    //Send the the current global var to the hub
    save_dataflow();
}


function select_op_update_panel() {
    select_op_delete_accordion(panel_focus_id);
    select_op_add_panel();
}


function change_chevron(a, panel_id) {

    let panel = panel_from_id(panel_id);
    let span_class = a.find('span').attr('class');

    if (span_class == "glyphicon glyphicon-chevron-up") {
        a.find('span').removeClass('glyphicon glyphicon-chevron-up').addClass('glyphicon glyphicon-chevron-down');
        panel.gui.opened = false;
    }
    else {
        a.find('span').removeClass('glyphicon glyphicon-chevron-down').addClass('glyphicon glyphicon-chevron-up');
        panel.gui.opened = true;
    }

    save_dataflow();
}


function select_op_create_accordion(panel, ops) {

    let wrapper= document.createElement('div');
    load_from_template(
                    wrapper,
                    "panel.html",
                    {'id': panel.id, 'title': panel.title, 'title_escaped': panel.title.replace(' ', '_')},
                    function () {
                        let modal = wrapper.firstChild;
                        $(modal).find("#panel_"+panel.id+"_body").html(ops);
                        let acc_div = document.getElementById('op_left_accordion');
                        let butt = document.getElementById('select_op_add_button');

                        acc_div.insertBefore(wrapper.firstChild, butt);

                        if (!panel.gui.opened)
                            $('#panel_'+panel.title.replace(' ', '_')+'_chevron').trigger('click');
                    });
}


function select_op_delete_accordion(id) {
    let panel = panel_from_id(id);
    let acc = document.getElementById(panel.id);
    document.getElementById('op_left_accordion').removeChild(acc);

    let index = panel_index_from_id(panel.id);
    global_op_panels.splice(index,1);

    save_dataflow();
}


function panel_from_id(id) {
    return global_op_panels.find( function (e) {
        return e['id'] === id;
    });
}

function panel_index_from_id(id) {
    for (let i=0; i< global_op_panels.length; i++)
        if (global_op_panels[i]['id'] == id)
            return i;
    return -1
}
