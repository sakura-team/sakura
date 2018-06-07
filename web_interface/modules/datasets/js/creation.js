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
var datasets_creation_fkeys             = []
var errors                              = {'name': true, 'fs_names': true, 'ff_names': false};
var fkey_matrix_disabled                = false;
var fkey_matrix_message                 = "";

/////////////////////////////////////////////////////////////////////////////////////
// CREATION
function datasets_open_creation(db_id) {

    if (true) { //datasets_creation_first_time) {
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

        //Disable creation button
        $('#datasets_cancel_creation_button').prop("disabled", false);
        $('#datasets_creation_button').html('Create Dataset');
        $('#datasets_creation_button').addClass('btn-primary');
        $('#datasets_creation_button').removeClass('btn-success');

        $('#datasets_creation_div_progress_bar').hide();

        datasets_creation_pkeys = { 'fs': {
                                        'rows': []},
                                    'ff': {
                                        'rows': []} };
        datasets_creationfkeys  = []
        datasets_creation_first_time = false;

        $('#datasets_creation_datetimepicker').datetimepicker();
        $('#datasets_creation_datetimepicker').data("DateTimePicker").date(new Date());
    }

    $('#datasets_creation_modal').modal();
}


function datasets_creation_change_pan(new_pan) {
    datasets_creation_check_name($('#datasets_creation_name'));
    datasets_creation_check_column_names(new_pan);
}

function datasets_creation_check_name(input) {
    if (input.val().replace(/^\s+|\s+$/g, '').length != 0) {
        $(input[0].parentElement).removeClass('has-error');
        $(input[0].parentElement).addClass('has-success');
        errors.name = false;

    }
    else {
        $(input[0].parentElement).removeClass('has-success');
        $(input[0].parentElement).addClass('has-error');
        errors.name = true;
    }
    var from_what = 'fs';
    $('#datasets_creation_ff_pan').attr("class").split(' ').forEach( function (elt) {
        if (elt == 'active') {
            from_what = 'ff';
        }
    });

    datasets_creation_check_column_names(from_what);
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
    //var body = $('#datasets_creation_fs_columns').find('tbody');

    $('#datasets_creation_ff_pan').attr("class").split(' ').forEach( function (elt) {
        if (elt == 'active') {
            from_what = 'ff';
        }
    });

    var col_names = $('[id^="datasets_creation_col_name_'+from_what+'"]');
    var col_types = $('[id^="datasets_'+from_what+'_type_select"]');
    var col_tags = $('[id^="datasets_'+from_what+'_tags_select"]');
    var fkeys = $('[id^="datasets_creation_'+from_what+'_fkey_td"]');

    var columns = [];
    //Data from each row
    for (var i=0; i< col_names.length; i++)
        columns.push([$(col_names[i]).val(), $(col_types[i]).val(), $(col_tags[i]).val()]);

    //Dates, for from_file creation
    var dates = []
    if (from_what == 'ff') {
        date_divs = $('[id^="datasets_date_format_ff_div_"]');
        date_divs.toArray().forEach( function(div) {
            var tab = div.id.split('_');
            var i = tab[tab.length-1];
            dates.push({'column_id': parseInt(i), 'column_name': columns[i][0], 'format': div.children[1].children[0].value});
        });
    }

    //Primary Key
    var pkey = []
    datasets_creation_pkeys[from_what].rows.forEach( function(id) {
        pkey.push($('#datasets_creation_col_name_'+from_what+'_'+id).val());
    });


    //Foreign Keys
    var fkeys = datasets_creation_fkeys;

    //Creation Date
    var creation_date = ($('#datasets_creation_datetimepicker').data("DateTimePicker").date()).unix();

    /*console.log('DB id:', database_id);
    console.log('DS name:', name);
    console.log('Columns:', columns);
    console.log('Short d:', desc);
    console.log('C date:', creation_date);
    console.log('Dates:', dates);
    console.log('PKey:', pkey);
    console.log('FKey:', fkeys);
    */

    //Sending the new dataset description
    if (from_what == 'ff') {
        $('#datasets_creation_div_progress_bar').show();
        $('#datasets_cancel_creation_button').prop("disabled", true);
        $('#datasets_creation_button').prop("disabled", true);
        $('#datasets_creation_button').removeClass('btn-primary');
        $('#datasets_creation_button').addClass('btn-success');
        $('#datasets_creation_button').html("Creating Table <span class=\"glyphicon glyphicon-refresh glyphicon-refresh-animate\"></span>");
    }
    sakura.common.ws_request(   'new_table',
                                [database_id, name, columns],
                                {   'short_desc':       desc,
                                    'creation_date':    creation_date,
                                    'primary_key':      pkey,
                                    'foreign_keys':     fkeys   },
                                function(dataset_id) {
        if (dataset_id >= 0) {
            //Sending file
            if (from_what == 'ff') {
                datasets_send_file(dataset_id, $('#datasets_file_from_HD')[0].files[0], dates, $("#datasets_creation_modal"), 'creation');
            }
            else {
                $('#datasets_creation_modal').modal('hide');
                recover_datasets();
            }
            datasets_creation_first_time = true;
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
            chunk: function(line) {
                datasets_creation_csv_file.lines.push(line.data);
                if (datasets_creation_csv_file.headers.length == 0)
                    datasets_creation_csv_file.headers = line.meta.fields;
            },
            complete: function() {
                //Reading columns and first line
                var body = $('#datasets_creation_ff_columns').find('tbody');
                body.empty();

                datasets_creation_csv_file.headers.forEach( function(col, index) {
                    var new_row = $(body[0].insertRow(-1));
                    new_row.attr('id', 'datasets_ff_row_' + index);
                    new_row.load('templates/creation_dataset_row.html', function () {
                        var before_last_cel = $(new_row[0].childNodes[new_row[0].childNodes.length - 2]);
                        var inputs = new_row.find('input');
                        inputs[0].value = col;

                        var col_name    = $('#datasets_creation_col_name_temp');
                        col_name.attr('id', 'datasets_creation_col_name_ff_'+index);
                        col_name.attr('disabled', true);

                        var select = new_row.find('select');
                        var type_select = $(select[0]);
                        var tags_select = $(select[1]);

                        $('#datasets_creation_pkey_temp').attr('onclick', 'datasets_primary_key('+index+', "ff");');
                        $('#datasets_creation_pkey_temp').attr('id', 'datasets_creation_ff_pkey_'+index);

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
                        datasets_creation_check_name($('#datasets_creation_name'));
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

        datasets_creation_check_column_names('fs');
    });

    return new_row;
}


function datasets_creation_empty_tables() {
    var body = $('#datasets_creation_ff_columns').find('tbody');
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
    console.log("Removing row", row, from_what);
    //Remove the foreign key if there is one
    datasets_creation_check_keys(row, from_what);

    //Remove the line
    $('#datasets_'+from_what+'_row_'+row).remove();

    var index = datasets_creation_pkeys[from_what].rows.indexOf(row);
    if (index != -1)
        datasets_creation_pkeys[from_what].rows.splice(index, 1);

    datasets_creation_check_column_names('fs');
    datasets_creation_update_pkey(from_what);
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

    var whole_error = false;
    if (from_what == 'fs') {
        errors.fs_names = error;
        whole_error = errors.name || errors.fs_names;
    }
    else {
        errors.ff_names = error;
        whole_error = errors.name || errors.ff_names;
    }
    if (! whole_error)
        $('#datasets_creation_button').prop("disabled",false);
    else
        $('#datasets_creation_button').prop("disabled",true);

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

    //Updating GUI text, and global var
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

    var error =  errors.fs_names || errors.name;
    if (from_what == 'ff')
        error = errors.ff_names || errors.name;

    if (error) {
        datasets_alert('Cannot open Foreign Key modal', '<b>Main Name</b> and <b>Column Names</b> should be circled in green before creating a foreign key !');
        return;
    }

    var select = $('#datasets_creation_fkey_modal_select_table');
    var found_at_least_one  = false

    var options_ds          = "";

    //Filling the select
    database_infos.tables.forEach( function (ds) {
        //as this table a primary key ?
        var as_a_pkey = false;
        if (ds.primary_key.length > 0) {
            found_at_least_one = true;
            options_ds += '<option value='+ds.table_id+'>'+ds.name+'</option>';
        }
    });

    if (found_at_least_one) {
        select.empty();
        select.append(options_ds);
    }

    //Now we fill the matrix
    datasets_creation_fill_fkey_matrix(from_what);
    $('#datasets_creation_fkey_modal_validate_button').attr('onclick', "datasets_creation_new_fkey(\'"+from_what+"\')");

    $('#datasets_creation_fkey_modal_select_table').attr('onchange', 'datasets_creation_fill_fkey_matrix(\''+from_what+'\')')
    $('#datasets_creation_fkey_modal').modal();
}


function datasets_creation_fill_fkey_matrix(from_what) {

    var new_name    = $('#datasets_creation_name').val()
    var ref_id      = $('#datasets_creation_fkey_modal_select_table').val();
    var ref_name    = $('#datasets_creation_fkey_modal_select_table :selected').text();
    var new_cols    = [];
    var new_types   = [];
    var ref_cols    = [];
    var ref_types   = [];

    database_infos.tables.forEach( function (ds) {
        if (ds.table_id == ref_id) {
            ds.columns.forEach( function(c) {
                if (ds.primary_key.indexOf(c[0]) != -1) {
                    ref_cols.push(c[0]);
                    ref_types.push(c[1]);
                }
            });
        }
    });

    $("[id^='datasets_creation_col_name_"+from_what+"_']").each( function () {
        new_cols.push($(this).val());
    });

    $("[id^='datasets_"+from_what+"_type_select_']").each( function () {
        new_types.push($(this).val());
    });

    //Testing number of columns
    var td_class = '';
    if (new_cols.length < ref_cols.length) {
        td_class = 'bg-danger';
        $('#datasets_creation_fkey_modal_validate_button').prop("disabled",true);
        fkey_matrix_disabled = true;
        fkey_matrix_message = "New table has not enough columns !";
    }
    else {
        $('#datasets_creation_fkey_modal_validate_button').prop("disabled",false);
        fkey_matrix_disabled = false;
        fkey_matrix_message = '';
    }

    //Testing types
    var ref_poss_types  = [];
    var ref_poss_nb     = [];
    ref_types.forEach( function(rc) {
        var index = ref_poss_types.indexOf(rc);
        if (index == -1) {
            ref_poss_types.push(rc);
            ref_poss_nb.push(1);
        }
        else {
            ref_poss_nb[index] += 1;
        }
    });

    var new_poss_types  = [];
    var new_poss_nb     = [];
    new_types.forEach( function(nc) {
        var index = new_poss_types.indexOf(nc);
        if (index == -1) {
            new_poss_types.push(nc);
            new_poss_nb.push(1);
        }
        else {
            new_poss_nb[index] += 1;
        }
    });

    var error = false;
    ref_poss_types.forEach( function(rpt, rpt_i) {
        var index = new_poss_types.indexOf(rpt);
        if (index == -1) {
            error = true;
        }
        else if (ref_poss_nb[rpt_i] > new_poss_nb[index]) {
            error = true;
        }
    });
    if (error) {
        fkey_matrix_disabled = true;
        td_class = 'bg-danger';
        if (fkey_matrix_message == '')
            fkey_matrix_message = "Issues with column types !";
        else
            fkey_matrix_message += "\n And issues with column types !";
    }

    var body = $('#datasets_creation_fkey_modal_matrix').find('tbody');
    body.empty();

    //ref name
    var new_row = $(body[0].insertRow(-1));
    if (!fkey_matrix_disabled)
        new_row.append('<td>');
    else {
        var td = $('<td>', {    align: "middle",
                                style:"cursor: pointer;",
                                title: fkey_matrix_message } );

        td.append('<font color=red><span class="glyphicon glyphicon-info-sign"></font></span>');
        new_row.append(td);
    }

    new_row.append('<td>&nbsp;&nbsp;<td class="bordered_td" bgcolor="lightblue" colspan='+ref_cols.length+' align="middle"><h4 style="margin-top: 5px; margin-bottom: 5px;">'+ref_name+'</h4>');

    //ref cols
    new_row = $(body[0].insertRow(-1));
    new_row.append('<td><td>');
    ref_cols.forEach( function (rf) {
        new_row.append('<td bgcolor="lightgrey" align="middle" class="bordered_td">'+rf);
    });

    //new_name
    new_row = $(body[0].insertRow(-1));
    new_row.append('<td class="bordered_td" bgcolor="lightblue" align="middle"><h4 style="margin-top: 5px; margin-bottom: 5px;">'+new_name+'</h4><td>');
    ref_cols.forEach( function (rf) {
        new_row.append('<td>');
    });

    var index = 0;

    new_cols.forEach( function(name, index) {
        new_row = $(body[0].insertRow(-1));
        new_row.append('<td align="middle" bgcolor="lightgrey" class="bordered_td">'+name+'<td>');
        ref_cols.forEach(function (cn, i) {
            if (ref_types[i] == new_types[index]) {
                var td = $('<td align="middle" class="'+td_class+'">');
                var input = $('<input>', {  type: "radio",
                                            class: "datasets_creation_"+from_what+"_radio_"+i,
                                            name: "datasets_creation_"+from_what+"_radio_"+index,
                                            onclick: "datasets_creation_check_mat(this, \'"+from_what+"\');"
                                            } );
                td.append(input)
            }
            else {
                var td = $('<td align="middle" class="'+td_class+'">&nbsp;');
                console.log(ref_types[i], new_types[index]);
            }
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
            nb_cols = ds.primary_key.length;
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
    var rows = [];
    var cols = [];
    var new_fkey = {'local_columns': [],
                    'remote_table': {},
                    'remote_columns': []}

    database_infos.tables.forEach( function (ds) {
        if (ds.table_id == $('#datasets_creation_fkey_modal_select_table').val()) {
            new_fkey.remote_table   = {'name': ds.name, 'id': ds.table_id};
            cols = ds.primary_key;
        }
    });

    $("[id^='datasets_creation_col_name_"+from_what+"_']").each( function () {
        rows.push($(this).val());
    });

    $('[name^="datasets_creation_'+from_what+'_radio"]').each( function() {
        if (this.checked) {
            var tab1 = this.name.split('_');
            var tab2 = this.className.split('_');

            new_fkey.local_columns.push(rows[tab1[tab1.length -1]]);
            new_fkey.remote_columns.push(cols[tab2[tab2.length -1]]);
        }
    });

    if (new_fkey.local_columns.length > 0) {
        s = '<b>('+new_fkey.local_columns[0];
        for (var i=1; i<new_fkey.local_columns.length; i++) {
            s += ', '+new_fkey.local_columns[i];
        }
        s += ')</b> references <b>\''+new_fkey.remote_table.name+'\'('+new_fkey.remote_columns[0];
        for (var i=1; i<new_fkey.remote_columns.length; i++) {
            s += ', '+new_fkey.remote_columns[i];
        }
        s += ')</b>';

        var body = $('#datasets_creation_'+from_what+'_fkey_list').find('tbody');
        var nb_rows = body[0].childElementCount - 1;
        var new_row = $(body[0].insertRow(nb_rows));

        var span = $('<span>', {title: "delete this foreign key",
                                class: "glyphicon glyphicon-remove",
                                style: "cursor: pointer;",
                                onclick: "datasets_creation_fkey_list_remove(\'"+nb_rows+"', \'"+from_what+"\');" });
        var td = $('<td>', {id:"datasets_creation_"+from_what+"_fkey_td_"+nb_rows});

        td.append(s+ '&nbsp;&nbsp;');
        td.append(span);
        new_row.append(td);

        datasets_creation_fkeys.push({
                    'local_columns': new_fkey.local_columns,
                    'remote_table_id': new_fkey.remote_table.id,
                    'remote_columns': new_fkey.remote_columns
        });
    }

    $('#datasets_creation_fkey_modal').modal('hide');
}


function datasets_creation_fkey_list_remove(id, from_what) {
    console.log(id);

    var row_i = 0;
    $('[id^=datasets_creation_'+from_what+'_fkey_td_]').each( function () {
        var tab = this.id.split("_");
        console.log(id);
        console.log(tab[tab.length -1]);
        if (id == tab[tab.length -1]) {
            datasets_creation_fkeys.splice(row_i, 1);
            return false;
        }
        row_i += 1;
    });

    $('#datasets_creation_'+from_what+'_fkey_td_'+id).remove();
    console.log(datasets_creation_fkeys);
}


function datasets_creation_remove_all_fkeys(from_what) {
    $('[id^=datasets_creation_'+from_what+'_fkey_td_]').each( function () {
        var tab = this.id.split("_");
        datasets_creation_fkey_list_remove(tab[tab.length -1], from_what);
    });
}


function datasets_creation_check_keys(row, from_what) {
    console.log('Entering Check keys function !');
}

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
        if (parseFloat(str) === parseInt(str) && str.indexOf('.') == -1) return "int32";
        else return "float32";
    }
    else if (isfloat.test(str) || commaFloat.test(str) || dotFloat.test(str)) return "float32";
    else if (date.test(str)) return "date";
    else return "string";
}
