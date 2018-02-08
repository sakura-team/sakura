//Code started by Michael Ortega for the LIG
//August, 22nd, 2017


var datasets_creation_current_select    = null;
var datasets_creation_global_ids        = 0;
var datasets_creation_csv_file          = {'headers': [], 'lines': []};
var datasets_creation_first_time        = true;
var datasets_creation_pkeys             = { 'fs': {
                                                'rows': []}, 
                                            'ff': {
                                                'rows': []} };
                                                
var datasets_creation_fkeys             = { 'fs': {
                                                'rows': [], 'data': []  }, 
                                            'ff': {
                                                'rows': [], 'data': []  }   };
var error_in_fs_names       = true;
var error_in_ff_names       = true;
var fkey_matrix_disabled    = false;

/////////////////////////////////////////////////////////////////////////////////////
// CREATION

function datasets_open_creation(db_id) {
    
    if (datasets_creation_first_time) {
        $('#datasets_creation_name').val("");
        $('#datasets_creation_description').val("");
        $("#datasets_file_from_HD").val("");
        $('#datasets_creation_button').attr('onclick', 'datasets_send_new('+db_id+')');
        
        //Creating at least one row
        datasets_creation_empty_tables();
        datasets_add_a_row('datasets_creation_fs_columns');
        
        //Red frame for the new dataset name
        $($('#datasets_creation_name')[0].parentElement).addClass('has-error');
        $('#datasets_creation_name').on('keyup', function() {datasets_creation_check_name($('#datasets_creation_name'));});
        
        datasets_creation_fkeys             = { 'fs': {
                                                    'rows': [], 'data': []  }, 
                                                'ff': {
                                                    'rows': [], 'data': []  }   };
        datasets_creation_pkeys             = { 'fs': {
                                                    'rows': []}, 
                                                'ff': {
                                                    'rows': []} };
        
        datasets_creation_first_time = false;
        
        $('#datasets_creation_datetimepicker').datetimepicker();
        $('#datasets_creation_datetimepicker').data("DateTimePicker").date(new Date());
    }
    
    $('#datasets_creation_modal').modal();
}


function datasets_creation_check_name(input) {
    if (input.val().replace(/^\s+|\s+$/g, '').length != 0) {
        $(input[0].parentElement).removeClass('has-error');
        $(input[0].parentElement).addClass('has-success');
    }
    else {
        $(input[0].parentElement).removeClass('has-success');
        $(input[0].parentElement).addClass('has-error');
    }
}


function datasets_send_new(database_id) {
    
    //Reading first main elements: name and description
    var name = $('#datasets_creation_name').val();
    var desc = $('#datasets_creation_description').val();
    if ( name == "") {
        datasets_alert("Dataset Name", "We cannot create a dataset with an empty name !");
        return;
    }
    
    //Which table body ?
    var from_what = 'fs';
    var body = $('#datasets_creation_fs_columns').find('tbody');
    var cols = body.find('tr');
    var nb_cols = cols.length - 1;
    $('#datasets_creation_from_file_pan').attr("class").split(' ').forEach( function (elt) {
        if (elt == 'active') {
            from_what = 'ff';
            body = $('#datasets_creation_from_file_columns').find('tbody');
            cols = body.find('tr');
            nb_cols = cols.length
            fkey
        }
    });
    
    var columns = [];
    var labels  = [];
    
    //Data from each row
    for (var i=0; i< nb_cols; i++) {
        var inputs = $(cols[i]).find('input');
        var label = $(inputs[0]).val();
        
        var tab = $(cols[i])[0].id.split('_');
        var global_i = parseInt(tab[tab.length -1]);
        
        //Some verifications
        if (label == 'Column Name') {
            datasets_alert("Columns Name", "Each column should have an explicit name");
            return;
        }
        if (labels.indexOf(label) != -1) {
            datasets_alert("Columns Name", "Each column should have a different name: two '"+label+"' detected !");
            return;
        }
        else
            labels.push(label);
        
        //tags
        var type = $($(cols[i]).find('select')[0]).val();
        var pkey = ($('#pkey_'+from_what+'_'+global_i).attr("class").indexOf("active") != -1);
        var fkey = null;
        
        if ($('#fkey_'+from_what+'_'+global_i).attr("class").indexOf("active") != -1) {
            index = datasets_creation_fkeys[from_what].rows.indexOf(i);
            fkey = datasets_creation_fkeys[from_what].data[index];
        }
        var tags = $($(cols[i]).find('select')[1]).val();
        if (tags == null)
            tags = [];
        
        columns.push([label, type, tags, pkey, fkey]);
    };
    
    var dates = []
    var date_divs = $('*').filter(function() {
        return this.id.match(/.*datasets_date_format_fs_div_.*/);
    });
    if (from_what == 'ff') {
        date_divs = $('*').filter(function() {
            return this.id.match(/.*datasets_date_format_ff_div_.*/);
        });
    }
    date_divs.toArray().forEach( function(div) {
        var tab = div.id.split('_');
        var i = tab[tab.length-1];
        dates.push({'column_id': parseInt(i), 'column_name': columns[i][0], 'format': div.children[1].children[0].value});
    });
    
    //Sending the new dataset description
    sakura.common.ws_request('new_table', [database_id, name, columns], {'short_desc': desc, 'creation_date': ($('#datasets_creation_datetimepicker').data("DateTimePicker").date()).unix()}, function(dataset_id) {
        if (dataset_id >= 0) {
            
            //Sending file
            if (from_what == 'ff') {
                var f = $('#datasets_file_from_HD')[0].files[0];
                datasets_send_file(dataset_id, f, dates, $("#datasets_creation_modal"));
            }
            
            //Refresh dataset list
            recover_datasets();
            datasets_creation_first_time = true;
            $("#datasets_creation_modal").modal('hide');
        }
    });
}


/////////////////////////////////////////////////////////////////////////////////////
// FILE MANAGEMENT

function datasets_on_file_selected(f) {
    
    if (!datasets_extension_check(f.value, 'csv')) {
        return;
    }
    // emptying variable
    datasets_creation_csv_file.lines = [];
    datasets_creation_csv_file.headers = [];
    
    //We parse the 10 first lines only
    Papa.parse(f.files[0], {
            comments: true,
            header: true,
            skipEmptyLines: true,
            preview: 10,
            step: function(line) {
                datasets_creation_csv_file.lines.push(line.data);
                if (datasets_creation_csv_file.headers.length == 0)
                    datasets_creation_csv_file.headers = line.meta.fields;
            },
            complete: function() {
                //Reading columns and first line
                var body = $('#datasets_creation_from_file_columns').find('tbody');
                body.empty();
                
                datasets_creation_csv_file.headers.forEach( function(col, index) {
                    var new_row = $(body[0].insertRow(-1));
                    new_row.attr('id', 'datasets_ff_row_' + index);
                    new_row.load('templates/creation_dataset_row.html', function () {
                        var before_last_cel = $(new_row[0].childNodes[new_row[0].childNodes.length - 2]);
                        var inputs = new_row.find('input');
                        inputs[0].value = col;
                        
                        var select = new_row.find('select');
                        var type_select = $(select[0]);
                        var tags_select = $(select[1]);
                        
                        before_last_cel.append($('<button>', {  id: "pkey_ff_"+index,
                                                                type: "button",
                                                                class: "btn btn-xs btn-secondary",
                                                                text: "pkey",
                                                                title: "Click for defining a primary key",
                                                                onclick: "datasets_primary_key("+index+", 'ff');"
                                                                }));
                        
                        before_last_cel.append('&nbsp;')
                        before_last_cel.append($('<button>', {  id: "fkey_ff_"+index,
                                                                type:"button",
                                                                class: "btn btn-xs btn-outline btn-secondary",
                                                                text: "FKey",
                                                                title: "Click for defining a foreign key",
                                                                onclick: "datasets_foreign_key("+index+", 'ff');"
                                                            }));
                        
                        new_row.find("td:last").remove();
                        
                        type_select.attr('id', 'datasets_ff_type_select_'+index);
                        type_select.attr('onchange', "datasets_type_change("+index+", this);");
                        type_select.val(getType(datasets_creation_csv_file.lines[0][0][col]));
                        
                        tags_select.attr('id', 'datasets_ff_tags_select_'+index);
                        datasets_fill_select_tags(tags_select);
                        
                        $('#datasets_ff_type_select_'+index).selectpicker('refresh');
                        $('#datasets_ff_tags_select_'+index).selectpicker('refresh');
                        $('#datasets_ff_tags_select_'+index).change(datasets_tags_select_change);
                        $('#datasets_new_tag_select_group').selectpicker('refresh');
                        $('#datasets_new_tag_name').val("");
                    });
                });
            },
            error: function(error) {
                datasets_alert("Parsing error:", error);
            }
    });
}


/////////////////////////////////////////////////////////////////////////////////////
// ROWS 
function datasets_add_a_row(table_id) {
    
    var body = $('#'+table_id).find('tbody');
    var nb_rows = body[0].childElementCount - 1;
    var new_row = $(body[0].insertRow(nb_rows));
    new_row.attr('id', 'datasets_fs_row_' + datasets_creation_global_ids);
    
    new_row.load('templates/creation_dataset_row.html', function () {
        var col_name    = $('#datasets_creation_col_name_temp');
        var parent      = col_name.parent(0);
        parent.addClass('has-error');
        col_name.attr('id', 'datasets_creation_col_name_fs_'+datasets_creation_global_ids);
        
        col_name.attr('title', '"Column Name" is not a correct name');
        col_name.on('keyup', {'input': col_name, 'iparent': parent, 'from_what': 'fs'}, function(event) {
            datasets_creation_check_column_names(event.data.from_what);
        });
        
        var last_cel = $(new_row[0].childNodes[new_row[0].childNodes.length - 1]);
        var before_last_cel = $(new_row[0].childNodes[new_row[0].childNodes.length - 2]);
        
        $(last_cel.find('span')[0]).attr('onclick', 'datasets_remove_line('+datasets_creation_global_ids+',"fs");');
        
        var select = new_row.find('select');
        var type_select = $(select[0]);
        var tags_select = $(select[1]);
        
        $('#datasets_creation_pkey_temp').attr('onclick', 'datasets_primary_key('+datasets_creation_global_ids+', "fs");');
        $('#datasets_creation_pkey_temp').attr('id', 'datasets_creation_fs_pkey_'+datasets_creation_global_ids);
        
        type_select.attr('id', 'datasets_fs_type_select_'+datasets_creation_global_ids);
        type_select.attr('onchange', "datasets_type_change("+datasets_creation_global_ids+",this);");
        type_select.selectpicker('refresh');
        
        tags_select.attr('id', 'datasets_fs_tags_select_'+datasets_creation_global_ids);
        datasets_fill_select_tags(tags_select);
        tags_select.selectpicker('refresh');
        tags_select.change(datasets_tags_select_change);
        $('#datasets_new_tag_select_group').selectpicker('refresh');
        
        $('#datasets_new_tag_name').val("");
        
        datasets_creation_global_ids ++;
    });
    
    return new_row;
}


function datasets_creation_empty_tables() {
    var body = $('#datasets_creation_from_file_columns').find('tbody');
    body.empty();
    var trs = $('#datasets_creation_fs_columns').find('tbody').find('tr');
    for (var i=0; i< trs.length-1; i++) {
        console.log(trs[i]);
        var tab = trs[i].id.split('_');
        var row_id = parseInt(tab[tab.length -1]);
        datasets_remove_line(row_id, 'fs');
    }
}


function datasets_remove_line(row, from_what) {
    console.log(row, from_what);
    //Remove the foreign key if there is one
    datasets_creation_check_keys(row, from_what);
    //Remove the line
    $('#datasets_'+from_what+'_row_'+row).remove();
}


function datasets_creation_check_column_names(from_what) {
    var labels = [];
    
    var error = false;
    $("[id^='datasets_creation_col_name_"+from_what+"']").each(function (i, el) {
        if ($(el).val() == 'Column Name') {
            $(el.parentElement).removeClass('has-success');
            $(el.parentElement).addClass('has-error');   
            $(el).attr('title', '"Column Name" is not a correct name');
            error = true;
        }
        else {
            var label = $(el).val();
            var index = labels.indexOf(label);
            
            if ( index != -1) {
                $(el.parentElement).removeClass('has-success');
                $(el.parentElement).addClass('has-error');
                error = true;
                $(el).attr('title', 'This name is already used');
            }
            else {
                $(el.parentElement).removeClass('has-error');
                $(el.parentElement).addClass('has-success');
                $(el).attr('title', '');
            }
            labels.push(label);
        }
    });
    
    
    if (from_what == 'fs')
        error_in_fs_names = error;
    else 
        error_in_ff_names = error;
    
    datasets_creation_update_pkey(from_what);
    datasets_creation_remove_all_fkeys(from_what);
}

/////////////////////////////////////////////////////////////////////////////////////
// TAGS
function datasets_fill_select_tags(tags_select) {
    tags_select.append('<option data-hidden="true" value="Select..."></option>')
    $('#datasets_new_tag_select_group').empty();
    columns_tags_list.forEach(function (group) {
        group_elem = '<optgroup label="' + group[0] + '">';
        group[1].forEach(function (tag) {
            group_elem += '<option value="' + tag + '">' + tag + '</option>';
        });
        group_elem += '</optgroup>';
        tags_select.append(group_elem);
        $('#datasets_new_tag_select_group').append('<option value="'+group[0]+'">'+group[0]+'</option>');
    });
    tags_select.append('<option data-icon="glyphicon glyphicon-plus" value="datasets_add_tag" data-subtext="add a new tag"></option>')
}


function datasets_tags_select_change(event) {
    datasets_creation_current_select  = $(event.target);
    if (datasets_creation_current_select.val() && datasets_creation_current_select.val().indexOf("datasets_add_tag") >= 0) {
        var last_option = datasets_creation_current_select[0].options[datasets_creation_current_select[0].options.length-1];
        last_option.selected = false;
        $(datasets_creation_current_select).selectpicker('refresh');
        $('#datasets_new_tag_modal').modal();
    }
}

function datasets_new_tag() {
    var tag     = $('#datasets_new_tag_name').val();
    
    if (tag.replace(/ /g, '') == "") {
        return;
    }
    
    var selects = $('*').filter(function() {
        return this.id.match(/.*_tags_select_.*/);
    });
    var group = "others";
    $.each(selects, function(i, select) {
        var optGroups = $(select).find('optgroup');
        for (var i=0; i < optGroups.length; i++) {
            if (optGroups[i].label == group) {
                var option = $('<option/>');
                option.attr({ 'value': tag }).text(tag);
                
                //selecting the tag
                if (select.id == datasets_creation_current_select[0].id) {
                    $(option).prop('selected', true);
                }
                $(optGroups[i]).append(option);
            }
        }
        $(select).selectpicker("refresh");
    });
    
    //Global variable
    columns_tags_list.forEach( function (tags_group) {
        if (tags_group[0] == group) {
            tags_group[1].push(tag);
        }
    });
    
    $('#datasets_new_tag_name').val("");
}


/////////////////////////////////////////////////////////////////////////////////////
// CONSTRAINTS
function datasets_primary_key(row, from_what) {
    
    var butt = $('#datasets_creation_'+from_what+'_pkey_'+row);
    if (butt.attr("class").indexOf("active") == -1) {
        //Button appearance
        butt.addClass('active');
        butt.addClass('btn-primary');
        butt.html('<img src="images/key_white.png" width="13px" height="13px"/>');
        
        //Globla var
        datasets_creation_pkeys[from_what].rows.push(row);
    }
    else {
        //Button appearance
        butt.removeClass('active');
        butt.removeClass('btn-primary');
        butt.html('<img src="images/key.png" width="13px" height="13px"/>');
        
        //Globla var
        var index = datasets_creation_pkeys[from_what].rows.indexOf(row);
        datasets_creation_pkeys[from_what].rows.splice(index, 1);
    }
    
    datasets_creation_update_pkey(from_what);
}


function datasets_creation_update_pkey(from_what) {
    
    //Updating GUI text
    var s = "";
    if (datasets_creation_pkeys[from_what].rows.length != 0) {
        var index = datasets_creation_pkeys[from_what].rows[0];
        var col_name = $("#datasets_creation_col_name_"+from_what+"_"+index).val();
        
        s += "("+col_name;
        for (var i=1; i< datasets_creation_pkeys[from_what].rows.length; i++) {
            index = datasets_creation_pkeys[from_what].rows[i];
            col_name = $("#datasets_creation_col_name_"+from_what+"_"+index).val();
            s += ' , '+col_name;
        }
        s += ')';
    }
    else {
        s = 'None &nbsp;<font color="lightgrey">Click on the keys right to the column names (Warning: order is important)</font>';
    }
    
    $('#datasets_creation_'+from_what+'_pkey_input').html(s);
}

function datasets_foreign_modal(from_what) {
    
    var error = error_in_fs_names;
    if (from_what == 'ff')
        error = error_in_ff_names;
    
    if (error) {
        datasets_alert('Cannot open Foreign Key modal', 'There are errors in <b>Column Names</b>. Please check  before creating a foreign key !');
        return;
    }
    
    var select = $('#datasets_creation_fkey_modal_select_table');
    var found_at_least_one  = false
    
    var options_ds          = "";
    
    //Filling the select
    database_infos.tables.forEach( function (ds) {
        //as this table a primary key ?
        var as_a_pkey = false;
        ds.columns.forEach( function(c) {
            if (c[3] > 0) {
                as_a_pkey = true;
                found_at_least_one = true;
            }
        });
        if (as_a_pkey) {
            options_ds += '<option value='+ds.table_id+'>'+ds.name+'</option>';
        }
    });
    
    if (found_at_least_one) {
        select.empty();
        select.append(options_ds);
    }
    
    //Now we fill the matrix
    datasets_creation_fill_fkey_matrix('fs');
    $('#datasets_creation_fkey_modal_validate_button').attr('onclick', "datasets_creation_new_fkey('fs')");
    
    $('#datasets_creation_fkey_modal').modal();
}


function datasets_creation_fill_fkey_matrix(from_what) {
    
    var col_names   = [];
    var row_names       = [];
    
    database_infos.tables.forEach( function (ds) {
        if (ds.table_id == $('#datasets_creation_fkey_modal_select_table').val()) {
            ds.columns.forEach( function(c) {
                col_names.push(c[0]);
            });
        }
    });
    
    $("[id^='datasets_creation_col_name_"+from_what+"_']").each( function () {
        row_names.push($(this).val());
    });
    
    var td_class = '';
    if (row_names.length < col_names.length) {
        td_class = 'bg-danger';
        $('#datasets_creation_fkey_modal_validate_button').prop("disabled",true);
        fkey_matrix_disabled = true;
    }
    else {
        $('#datasets_creation_fkey_modal_validate_button').prop("disabled",false);
        fkey_matrix_disabled = false;
    }
    
    var body = $('#datasets_creation_fkey_modal_matrix').find('tbody');
    body.empty();
    
    var new_row = $(body[0].insertRow(-1));
    new_row.append('<td>');
    col_names.forEach( function (cn) {
        new_row.append('<td class="'+td_class+'">'+cn);
    });
    var rows = [];
    var index = 0;
    
    row_names.forEach( function(name, index) {
        var new_row = $(body[0].insertRow(-1));
        new_row.append('<td class="'+td_class+'">'+name);
        col_names.forEach(function (cn, i) {
            var td = $('<td>', {class: td_class});
            var input = $('<input>', {  type: "radio",
                                        class: "datasets_creation_"+from_what+"_radio_"+i,
                                        name: "datasets_creation_"+from_what+"_radio_"+index,
                                        onclick: "datasets_creation_check_mat(this, \'"+from_what+"\');"
                                        } );
            td.append(input)
            new_row.append(td);
        });
        index += 1;
    });
    
    datasets_creation_check_mat_filled(from_what);

}

function datasets_creation_check_mat(e, from_what) {
    $("[class^='datasets_creation_"+from_what+"_radio']").not(e).each( function() {
        if (this.className == e.className) {
            this.checked = false;
        }
    });
    datasets_creation_check_mat_filled(from_what);
}


function datasets_creation_check_mat_filled(from_what) {
    var list = $("[class^='datasets_creation_"+from_what+"_radio']");
    
    var nb_cols = 0;
    database_infos.tables.forEach( function (ds) {
        if (ds.table_id == $('#datasets_creation_fkey_modal_select_table').val()) {
            nb_cols = ds.columns.length;
        }
    });
    
    if (!fkey_matrix_disabled) {
        
        var nb_checked = 0
        
        list.each( function() {
            if (this.checked) {
                nb_checked += 1;
            }
        });
        
        if (nb_checked != nb_cols) {
            $('#datasets_creation_fkey_modal_validate_button').prop("disabled",true);
        }
        else {
            $('#datasets_creation_fkey_modal_validate_button').prop("disabled",false);
        }
    }
}


function datasets_creation_new_fkey(from_what) {
    var cols_in = [];
    var cols_out = [];
    var table_name = ''
    
    var rows = []
    var cols = []
    
    database_infos.tables.forEach( function (ds) {
        if (ds.table_id == $('#datasets_creation_fkey_modal_select_table').val()) {
            table_name = ds.name;
            ds.columns.forEach( function(c) {
                cols.push(c[0]);
            });
        }
    });
    
    $("[id^='datasets_creation_col_name_"+from_what+"_']").each( function () {
        rows.push($(this).val());
    });
    
    $('[name^="datasets_creation_'+from_what+'_radio"]').each( function() {
        if (this.checked) {
            var tab1 = this.name.split('_');
            var tab2 = this.className.split('_');
            
            cols_in.push(rows[tab1[tab1.length -1]]);
            cols_out.push(cols[tab2[tab2.length -1]]);
        }
    });
    
    if (cols_in.length > 0) {
        s = '<b>('+cols_in[0];
        for (var i=1; i<cols_in.length; i++) {
            s += ', '+cols_in[i];
        }
        s += ')</b> references <b>\''+table_name+'\'('+cols_out[0];
        for (var i=1; i<cols_out.length; i++) {
            s += ', '+cols_out[i];
        }
        s += ')</b>';
        var body = $('#datasets_creation_'+from_what+'_fkey_list').find('tbody');
        var nb_rows = body[0].childElementCount - 1;
        var new_row = $(body[0].insertRow(nb_rows));
        
        var span = $('<span>', {title: "delete this foreign key",
                                class: "glyphicon glyphicon-remove",
                                style: "cursor: pointer;",
                                onclick: "datasets_creation_fkey_list_remove(\'datasets_creation_"+from_what+"_fkey_td_"+nb_rows+"\', \'"+from_what+"\');" });
        var td = $('<td>', {id:"datasets_creation_"+from_what+"_fkey_td_"+nb_rows});
        
        td.append(s+ '&nbsp;&nbsp;');
        td.append(span);
        new_row.append(td);
    }
    
    $('#datasets_creation_fkey_modal').modal('hide');
}


function datasets_creation_fkey_list_remove(row, from_what) {
    $('#'+row).remove();
}


function datasets_creation_remove_all_fkeys(from_what) {
    var body = $('#datasets_creation_'+from_what+'_fkey_list').find('tbody');
    var nb_rows = body[0].childElementCount - 1;
    for (var i=0; i<nb_rows; i++) {
        var new_row = $(body[0].deleteRow(0));
    }
}


function datasets_creation_check_keys(row, from_what) {
    console.log('Entering Check keys function !');
}

/*
function datasets_foreign_key(row, from_what) {
    
    $('#datasets_foreign_key_modal')[0].style.top = (mouse.y-75)+'px';
    $('#datasets_fkey_select_table').empty();
    $('#datasets_fkey_select_column').empty();
    
    var options_ds          = "";
    var options_cols        = "";
    var found_at_least_one  = false
    var table_filled        = false
    
    var type = $($('#datasets_'+from_what+'_row_'+row).find('select')[0]).val();
    
    database_infos.tables.forEach( function (ds) {
        //as this table a primary key ?
        var as_a_pkey = false;
        ds.columns.forEach( function(c) {
            if (c[3] && c[1] == type) {
                as_a_pkey = true;
                found_at_least_one = true;
            }
        });
        
        if (as_a_pkey) {
            options_ds += '<option value='+ds.table_id+'>'+ds.name+'</option>';        
            if (!table_filled) {
                ds.columns.forEach( function(col, index) {
                    options_cols += '<option value='+index+'>'+col[0]+'</option>';
                });
                table_filled = true;
            }
        }
    });
    
    if (!found_at_least_one) {
        $('#datasets_fkey_select_table').append('<option>No table has a pkey of '+type+' for now</option>');
        $('#datasets_fkey_validate_button').attr('onClick', '');
        $('#datasets_fkey_validate_button').prop('disabled', true);
        $('#datasets_fkey_cancel_button').attr('onClick', '');
    }
    else {
        $('#datasets_fkey_select_table').append(options_ds);
        $('#datasets_fkey_select_table').attr('onChange', 'datasets_fkey_select_table_onchange();');
        $('#datasets_fkey_select_column').append(options_cols);    
        $('#datasets_fkey_validate_button').prop('disabled', false);
        $('#datasets_fkey_validate_button').attr('onClick', 'datasets_fkey_validate('+row+',"'+from_what+'");');
        $('#datasets_fkey_cancel_button').attr('onClick', 'datasets_fkey_cancel('+row+',"'+from_what+'");');
    }
    
    //filling if already defined
    if ($('#fkey_'+from_what+'_'+row).attr("class").indexOf('active') != -1) {
        var index = datasets_creation_fkeys[from_what].rows.indexOf(row);
        $('#datasets_fkey_select_table').val(datasets_creation_fkeys[from_what].data[index][0]);
        datasets_fkey_select_table_onchange();
        $('#datasets_fkey_select_column').val(datasets_creation_fkeys[from_what].data[index][1]);
    }
    
    $('#datasets_foreign_key_modal').modal();
}


function datasets_fkey_select_table_onchange() {
    database_infos.tables.forEach( function (ds, index) {
        if (ds.table_id == $('#datasets_fkey_select_table').val()) {
            $('#datasets_fkey_select_column').empty();
            var options_cols = "";
            ds.columns.forEach( function(col, index2) {
                options_cols += '<option value='+index2+'>'+col[0]+'</option>';
            });
            $('#datasets_fkey_select_column').append(options_cols);
        }
    });
}


function datasets_fkey_validate(row, from_what) {
    
    var ds  = $('#datasets_fkey_select_table').val();
    var col = $('#datasets_fkey_select_column').val();
    
    datasets_creation_fkeys[from_what].rows.push(row);
    datasets_creation_fkeys[from_what].data.push([ds, col]);
    
    $('#fkey_'+from_what+'_'+row).addClass("active");
    $('#fkey_'+from_what+'_'+row).addClass("btn-primary");
}


function datasets_fkey_cancel(row, from_what) {
    var index = datasets_creation_fkeys[from_what].rows.indexOf(row);
    if (index != -1) {
        datasets_creation_fkeys[from_what].rows.splice(index, 1);
        datasets_creation_fkeys[from_what].data.splice(index, 1);
    }
    $('#fkey_'+from_what+'_'+row).removeClass("active");
    $('#fkey_'+from_what+'_'+row).removeClass("btn-primary");
}
*/

/////////////////////////////////////////////////////////////////////////////////////
// DATES AND TYPES
function datasets_type_change(row_id, from) {
    
    var select = $(from);
    var td = from.parentNode.parentNode;
    
    if (select.val() == 'date' && from.id.indexOf("ff") >= 0) {
        var tmp = document.createElement('input');
        $(tmp).load("templates/date_format_input.html", function (input) {
            var div = $(document.createElement('div'));
            div.attr("id", "datasets_date_format_ff_div_"+row_id);
            div.append($(input));
            $(td).append(div);
            $(tmp).remove();
            var date = datasets_creation_csv_file.lines[0][0][datasets_creation_csv_file.headers[row_id]];
            
            datasets_check_date_format( date,
                                        $(div[0].children[1]),
                                        $(div[0].children[1].children[0]),
                                        $(div[0].children[5]),
                                        $(div[0].children[5].children[0])
                                        );
            
            $(div[0].children[3].children[0]).val(date);
            $(div[0].children[1].children[0]).on('keyup', {'date': date, 
                                                    'format_div': $(div[0].children[1]),
                                                    'format_input': $(div[0].children[1].children[0]),
                                                    'result_div': $(div[0].children[5]),
                                                    'result_input': $(div[0].children[5].children[0])
                                                    }, function(event) {
                
                datasets_check_date_format( event.data.date, 
                                            event.data.format_div,
                                            event.data.format_input,
                                            event.data.result_div,
                                            event.data.result_input);
            });
        });
    }
    else if (td.childElementCount > 1) {
        td.children[1].remove();
    }
    
    //When type changes we should delete the fkey
    if (from.id.indexOf("ff") >= 0)
        datasets_creation_check_keys(row_id, 'ff');
    else
        datasets_creation_check_keys(row_id, 'fs');
}


function getType(str){
    if (typeof str !== 'string') str = str.toString();
    var nan = isNaN(Number(str));
    var isfloat = /^\d*(\.|,)\d*$/;
    var commaFloat = /^(\d{0,3}(,)?)+\.\d*$/;
    var dotFloat = /^(\d{0,3}(\.)?)+,\d*$/;
    var date = /^\d{0,4}(\.|\/)\d{0,4}(\.|\/)\d{0,4}$/;
    
    if (!nan){
        if (parseFloat(str) === parseInt(str)) return "int32";
        else return "float32";
    }
    else if (isfloat.test(str) || commaFloat.test(str) || dotFloat.test(str)) return "float32";
    else if (date.test(str)) return "date";
    else return "string";
}

