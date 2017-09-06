//Code started by Michael Ortega for the LIG
//August, 22nd, 2017


function not_yet() {
    alert("not yet implemented");
}


function recover_tables() {
    
    var dataset_id = window.location.search.substr(1).split("=")[1];
    sakura.common.ws_request('get_dataset_info', [parseInt(dataset_id)], {}, function (result) {
    
        //Filling table
        var body = $('#table_of_dataset_tables').find('tbody');
        body.empty();
        result['tables'].forEach( function(table) {
            body.append('<tr>   <td>'+table['label']+'</td><td>'+table['short_description']+'</td> \
                                <td align="right"> \
                                    <span title="Upload data in this table" class="glyphicon glyphicon-upload" style="cursor: pointer;" onclick="dataset_table_upload('+dataset_id+','+table['id']+');"> </span> \
                                    <span title="Download the table" class="glyphicon glyphicon-download" style="cursor: pointer;" onclick="dataset_table_download('+dataset_id+','+table['id']+');"> </span> \
                                    <span>&nbsp</span> \
                                    <span title="Look at the table" class="glyphicon glyphicon-eye-open" style="cursor: pointer;" onclick="dataset_table_look_at('+dataset_id+','+table['id']+');"></span> \
                                    <span title="Analytics" class="glyphicon glyphicon-info-sign" style="cursor: pointer;" onclick="dataset_table_analytics('+dataset_id+','+table['id']+');"></span> \
                                    <span>&nbsp</span> \
                                    <span title="delete" class="glyphicon glyphicon-remove" style="cursor: pointer;" onclick="dataset_table_delete('+dataset_id+','+table['id']+');"></span> \
                                </td>\
                        </tr>');
        });
        
        //Updating html elements
        
        //Creation from file
        $('#datasets_table_creation_from_file_button').attr('onclick', 'new_dataset_table_from_file('+dataset_id+')');
        $('#datasets_table_creation_name_from_file').val("");
        $('#datasets_table_creation_description_from_file').val("");
        $("#datasets_table_file_from_HD").val("");
        
        //Creation from Scratch
        $('#datasets_table_creation_from_scratch_button').attr('onclick', 'new_dataset_table_from_scratch('+dataset_id+')');
        $('#datasets_table_creation_name_from_scratch').val("");
        $('#datasets_table_creation_description_from_scratch').val("");
        
    });
}


function new_dataset_table_from_file(dataset_id) {
    console.log("dataset_id", dataset_id);
    console.log("file", $('#datasets_table_file_from_HD').val() );
    $("#datasets_table_creation_fromfile_modal").modal('hide');
}


function new_dataset_table_from_scratch(dataset_id) {
    console.log("dataset_id", dataset_id);
    $("#datasets_table_creation_fromscratch_modal").modal('hide');
}


function dataset_table_upload(dataset_id, table_id) {
    not_yet();
}


function dataset_table_download(dataset_id, table_id) {
    not_yet();
}

function dataset_table_look_at(dataset_id, table_id) {
    not_yet();
}


function dataset_table_analytics(dataset_id, table_id) {
    not_yet();
}


function dataset_table_delete(dataset_id, table_id) {
    not_yet();
}


function on_file_selected(f) {
    var fr = new FileReader();
    
    fr.onload = function(e) {
        //check the name: should have .csv extension
        
        var s_name = f.value.split('.');
        if (s_name[s_name.length - 1] != 'csv' && s_name[s_name.length - 1] != 'CSV') {
            console.log(s_name[s_name.length - 1]);
            alert("The extension of this file is not .csv !! Please be sure it is a csv file, and rename it with extension.");
            return;
        }
        
        //check the columns
        var lines = e.target.result.split(/[\r\n]+/g);
        var cols = lines[0].split(',');
        
        cols.forEach( function(col) {
            console.log(col);
        });
    };
    
    fr.readAsText(f.files[0]);
}


function dataset_tables_add_a_row() {
    var body = $('#datasets_table_creation_from_scratch_columns').find('tbody');
    var nb_rows = body[0].childElementCount - 1;
    var new_row = $(body[0].insertRow(nb_rows));
    
    new_row.load('creation_table_row.html', function () {
        $(new_row[0].childNodes[0]).find('input')[0].value = "Column "+ (nb_rows + 1);
    });
}