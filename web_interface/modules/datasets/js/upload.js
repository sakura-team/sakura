//Code started by Michael Ortega for the LIG
//October, 16th, 2017

function dataset_upload(dataset_id) {
    var dataset = $.grep(database_infos.tables, function(e){ return e.table_id == dataset_id; });
    $('#datasets_upload_header').html('<h3>Upload Data into <b>'+dataset[0].name+'</b></h3>');
    $('#datasets_upload_select_file').attr('onchange', 'datasets_upload_on_file_selected(this, '+dataset_id+');');
    $('#datasets_upload_button').attr('onclick', 'datasets_upload('+dataset_id+');');
    $('#datasets_upload_modal').modal();
}

function datasets_upload_on_file_selected(f, dataset_id) {
    if (!extension_check(f.value, 'csv')) {
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
                nb_lines ++;
                var new_row = $(tbody[0].insertRow(-1));
                Object.values(line.data[0]).forEach( function (elt) {
                    new_row.append("<td>"+elt+"</td>");
                });
                headers = Object.keys(line.data[0]);
            },
            complete: function() {
                headers.forEach( function(elt) {
                    thead.append("<th>"+elt+"</th>");
                });
                if (nb_lines == nb_preview_rows) {
                    var new_row = $(tbody[0].insertRow(-1));
                    new_row.append("<td colspan="+headers.length+">...</td>");
                }
            },
            error: function(error) {
                console.log(error);
            }
    });
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

