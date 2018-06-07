//Code started by Michael Ortega for the LIG
//October, 16th, 2017


var datasets_upload_expected_columns    = null;
var datasets_upload_headers             = null;
var datasets_upload_lines               = null;
var datasets_upload_current_column      = null;
var datasets_upload_checked_columns     = null;

function datasets_open_upload_modal(dataset_id) {
    var dataset = $.grep(database_infos.tables, function(e){ return e.table_id == dataset_id; });
    $('#datasets_upload_header').html('<h3>Upload Data into <b>'+dataset[0].name+'</b></h3>');
    $('#datasets_upload_select_file').attr('onchange', 'datasets_upload_on_file_selected(this, '+dataset_id+');');
    $('#datasets_upload_button').attr('onclick', 'datasets_upload('+dataset_id+');');
    var tbody       = $('#datasets_upload_preview_table').find('tbody');
    var thead       = $('#datasets_upload_preview_table').find('thead');
    thead.empty();
    tbody.empty();

    $('#datasets_upload_select_file')[0].value = '';

    sakura.common.ws_request('get_table_info', [dataset_id], {}, function(result) {
            var thead = $('#datasets_upload_expected_columns_table').find('thead');
            var tbody = $('#datasets_upload_expected_columns_table').find('tbody');
            thead.empty()
            tbody.empty()
            var new_row_head = $(thead[0].insertRow());
            var new_row_body = $(tbody[0].insertRow());

        result.columns.forEach( function (col) {
            new_row_head.append('<th>'+col[0]+'</th>');
            if (col[1] != '<U0')
                if (! this_col_is_a_date(col))
                    new_row_body.append('<td>'+col[1]+'</td>');
                else
                    new_row_body.append('<td>date</td>');
            else
                new_row_body.append('<td>string</td>');
        });
        datasets_upload_expected_columns = result.columns;
    });

    $('#datasets_upload_button').html('Upload data');
    $('#datasets_upload_button').removeClass("btn-success");
    $('#datasets_upload_button').addClass("btn-primary");
    $('#datasets_upload_button').prop("disabled",true);
    $('#datasets_cancel_upload_button').prop("disabled", false);

    $('#datasets_upload_div_progress_bar').hide();

    $('#datasets_upload_modal').modal();
}

function datasets_upload_on_file_selected(f, dataset_id) {
    if (!datasets_extension_check(f.value, 'csv')) {
        return;
    }

    var nb_lines        = 0
    var nb_preview_rows = 10;
    datasets_upload_lines = [];
    datasets_upload_headers = [];

    //We parse the 10 first lines only
    Papa.parse(f.files[0], {
            comments: true,
            header: true,
            skipEmptyLines: true,
            preview: nb_preview_rows,
            chunk: function(line) {
                datasets_upload_headers = Object.keys(line.data[0]);
                datasets_upload_lines.push(Object.values(line.data[0]));
            },
            complete: function() {
                datasets_upload_checked_columns = [];
                if (datasets_upload_headers.length == datasets_upload_expected_columns.length) {
                    for (var i=0; i<datasets_upload_headers.length;i++) {
                        if (! this_col_is_a_date(datasets_upload_expected_columns[i]))
                            datasets_upload_checked_columns.push('none');
                        else
                            datasets_upload_checked_columns.push(null);
                    }
                }
                datasets_upload_table_full = false;
                if (nb_lines == nb_preview_rows)
                    datasets_upload_table_full = true;
                datasets_upload_fill_table();
            },
            error: function(error) {
                datasets_alert("Parsing error:", error);
            },
    });
}


function datasets_upload_fill_table() {

    var tbody       = $('#datasets_upload_preview_table').find('tbody');
    var thead       = $('#datasets_upload_preview_table').find('thead');
    thead.empty();
    tbody.empty();

    var bg_color    = '';
    if (datasets_upload_headers.length != datasets_upload_expected_columns.length)
        bg_color = 'bg-danger';

    if (datasets_upload_headers.length != datasets_upload_expected_columns.length) {
        bg_color = 'bg-danger';
        datasets_alert("Columns number",'This file has a wrong number of columns, that does not match the table header');
        $('#datasets_upload_button').prop("disabled",true);
    }
    else if (datasets_upload_checked_columns.indexOf(null) != -1) {
        $('#datasets_upload_button').prop("disabled",true);
    }
    else {
        $('#datasets_upload_button').prop("disabled",false);
    }


    //Filling Headers
    var new_row_head = $(thead[0].insertRow());
    datasets_upload_headers.forEach( function(elt, index) {
        if (datasets_upload_headers.length != datasets_upload_expected_columns.length ||
            ! this_col_is_a_date(datasets_upload_expected_columns[index]))
            new_row_head.append("<th class='"+bg_color+"'>"+elt+"</th>");
        else {
            var bg_color2 = bg_color;
            if (datasets_upload_checked_columns[index] == null) {
                bg_color2 = 'bg-danger';
            }
            new_row_head.append("<th class='"+bg_color2+"'>"+
                                    elt+
                                    '&nbsp;<button type="button" class="btn btn-xs" onclick="datasets_upload_data_format_modal('+
                                    index
                                    +');"><span class="glyphicon glyphicon-pencil"></span></button></th>');
        }
    });

    //Filling Rows
    datasets_upload_lines.forEach( function (line) {
        var new_row = $(tbody[0].insertRow(-1));
        line.forEach( function (elt, index) {
            if (datasets_upload_headers.length != datasets_upload_expected_columns.length ||
                ! this_col_is_a_date(datasets_upload_expected_columns[index]))
                new_row.append('<td class="'+bg_color+'">'+elt+'</td>');
            else {
                var bg_color2 = bg_color;
                if (datasets_upload_checked_columns[index] == null) {
                    bg_color2 = 'bg-danger';
                }
                else {
                    var mo = moment(elt, datasets_upload_checked_columns[index]);
                    elt = mo._d.toLocaleString();
                }
                new_row.append('<td class="'+bg_color2+'">'+elt+'</td>');
            }
        });
    });

    if (!datasets_upload_table_full) {
        var new_row = $(tbody[0].insertRow(-1));
        new_row.append("<td class='"+bg_color+"' colspan="+datasets_upload_headers.length+">...</td>");
    }
}

function datasets_upload(dataset_id) {
    var f = $('#datasets_upload_select_file')[0].files[0];

    if (datasets_upload_checked_columns.indexOf(null) != -1) {
        datasets_alert("Date format", "At least one date format is missing (red column)!!!");
        return;
    }

    $('#datasets_upload_div_progress_bar').show();
    $('#datasets_cancel_upload_button').prop("disabled", true);
    $('#datasets_upload_button').prop("disabled", true);
    $('#datasets_upload_button').html('Uploading ...');
    $('#datasets_upload_button').addClass('btn-success');

    var date_formats = []
    datasets_upload_checked_columns.forEach( function(date, index) {
        if (date != 'none')
            date_formats.push({'column_id': index, 'format': date});
    });

    datasets_send_file(dataset_id, f, date_formats, $('#datasets_upload_modal'), 'upload');
}


function datasets_upload_data_format_modal(col) {
    datasets_upload_current_column = col;
    $('#datasets_date_format_header').html('<h3>Date Format for column '+col+': '+datasets_upload_expected_columns[col][0]+'</h3>');
    $('#datasets_date_format_body').html('');
    $('#datasets_date_format_body').load('templates/date_format_input.html', function () {
        var div = $('#datasets_date_format_body')[0];
        $(div.children[3].children[0]).val(datasets_upload_lines[0][col]);
        if (datasets_upload_checked_columns[col] != null) {
            $(div.children[1].children[0]).val(datasets_upload_checked_columns[col]);
        }
        //First check
        datasets_check_date_format( datasets_upload_lines[0][col],
                                    $(div.children[1]),
                                    $(div.children[1].children[0]),
                                    $(div.children[5]),
                                    $(div.children[5].children[0])
                                    );

        //check at each input change
        $(div.children[1].children[0]).on('keyup', {'date': datasets_upload_lines[0][col],
                                                    'format_div': $(div.children[1]),
                                                    'format_input': $(div.children[1].children[0]),
                                                    'result_div': $(div.children[5]),
                                                    'result_input': $(div.children[5].children[0])
                                                    }, function(event) {

                datasets_check_date_format( event.data.date,
                                            event.data.format_div,
                                            event.data.format_input,
                                            event.data.result_div,
                                            event.data.result_input);
        });
    });
    $('#datasets_date_format_modal').modal();
}


function datasets_upload_save_date_format() {
    var result = $($('#datasets_date_format_body')[0].children[5].children[0]).val();
    if (result != 'Invalid format') {
        var format = $($('#datasets_date_format_body')[0].children[1].children[0]).val();
        datasets_upload_checked_columns[datasets_upload_current_column] = format;
    }
    datasets_upload_fill_table();
    $('#datasets_date_format_modal').modal('hide');
}
