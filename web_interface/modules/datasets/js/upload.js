//Code started by Michael Ortega for the LIG
//October, 16th, 2017


var datasets_upload_expected_columns = null;

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
            var thead = $('#datasets_upload_expected_columns').find('thead');
            var tbody = $('#datasets_upload_expected_columns').find('tbody');
            thead.empty()
            tbody.empty()
            var new_row_head = $(thead[0].insertRow());
            var new_row_body = $(tbody[0].insertRow());
            
        result.columns.forEach( function (col) {
            new_row_head.append('<th>'+col[0]+'</th>');
            if (col[1] != '<U0')
                new_row_body.append('<td>'+col[1]+'</td>');
            else
                new_row_body.append('<td>string</td>');
        });
        datasets_upload_expected_columns = result.columns;
    });
    $('#datasets_upload_modal').modal();
}

function datasets_upload_on_file_selected(f, dataset_id) {
    if (!datasets_extension_check(f.value, 'csv')) {
        return;
    }
    
    var dataset = $.grep(database_infos.tables, function(e){ return e.table_id == dataset_id; });
    var nb_cols     = dataset[0].columns.length;
    var tbody       = $('#datasets_upload_preview_table').find('tbody');
    var thead       = $('#datasets_upload_preview_table').find('thead');
    thead.empty();
    tbody.empty();
    
    var nb_lines = 0
    var nb_preview_rows = 10;
    var headers     = null;
    //We parse the 10 first lines only
    Papa.parse(f.files[0], {
            comments: true,
            header: true,
            skipEmptyLines: true,
            preview: nb_preview_rows,
            worker: true,
            step: function(line) {
                var bg_color = '';
                if (Object.values(line.data[0]).length != datasets_upload_expected_columns.length)
                    bg_color = 'bg-danger';
                nb_lines ++;
                var new_row = $(tbody[0].insertRow(-1));
                Object.values(line.data[0]).forEach( function (elt) {
                    new_row.append('<td class="'+bg_color+'">'+elt+'</td>');
                });
                headers = Object.keys(line.data[0]);
            },
            complete: function() {
                var bg_color = '';
                if (headers.length != datasets_upload_expected_columns.length) {
                    bg_color = 'bg-danger';
                    alert('Wrong number of columns');
                }
                headers.forEach( function(elt, index) {
                    thead.append("<th class='"+bg_color+"'>"+elt+"</th>");
                });
                if (nb_lines == nb_preview_rows) {
                    var new_row = $(tbody[0].insertRow(-1));
                    new_row.append("<td class='"+bg_color+"' colspan="+headers.length+">...</td>");
                }
                
            },
            error: function(error) {
                console.log(error);
            }
    });
    
    console.log('here');
}


function datasets_upload(dataset_id) {
    var f = $('#datasets_upload_select_file')[0].files[0];
    
    //Getting dates format
    sakura.common.ws_request('get_table_info', [dataset_id], {}, function(result) {
        var date_formats = [];
        //var date_formats = result['gui_data']['dates'];
        
        //Then sending rows
        datasets_send_file(dataset_id, f, date_formats);
    });
}

