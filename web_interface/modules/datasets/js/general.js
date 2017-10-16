//Code started by Michael Ortega for the LIG
//August, 22nd, 2017


var database_infos = null;
var columns_tags_list = null;

function not_yet() {
    alert("not yet implemented");
}


function datasets_info(header_str, body_str) {
    var h = $('#datasets_info_header');
    var b = $('#datasets_info_body');
    h.html("<h3><font color=\"black\">"+header_str+"</font></h3>");
    b.html("<p>"+body_str+"</p>");
    $('#datasets_info_modal').modal();
}


function datasets_alert(header_str, body_str) {
    var h = $('#datasets_alert_header');
    var b = $('#datasets_alert_body');
    h.html("<h3><font color=\"white\">"+header_str+"</font></h3>");
    b.html("<p>"+body_str+"</p>");
    $('#datasets_alert_modal').modal();
}


function extension_check(f_name, ext) {
    //check the name: should have .csv extension
    var s_name = f_name.split('.');
    if (s_name[s_name.length - 1].toLowerCase() != ext.toLowerCase()) {
        datasets_alert("File Extension Issue", "The extension of this file is not .csv !!\nPlease be sure it is a csv file, and rename it with extension.");
        return false;
    }
    return true;

}
function recover_datasets() {
    
    var database_id = window.location.search.substr(1).split("=")[1];
    
    
    ////////////SANDBOX////////////////////////
    /*sakura.common.ws_request('set_dataset_gui_data', ['table 0', {'dates': [[0, 'YYYY'], [1, 'MM/DD']]}], {}, function (result) {
        console.log(result);
        sakura.common.ws_request('get_dataset_gui_data', ['table 1'], {}, function (result) {
            console.log(result);
        });
    });
    */
    ////////////SANDBOX////////////////////////

    /*
    console.log(window.location);
    console.log("DATABASE ID", parseInt(database_id));
    ////////////TEMP////////////////////////
    sakura.common.ws_request('list_databases', [], {}, function (result) {
        if (result.length)
            database_id = result[0].database_id;
        else {
            alert("No database found !!!");
            return;
        }
    
    ////////////END TEMP////////////////////////
    */
        sakura.common.ws_request('get_database_info', [parseInt(database_id)], {}, function (result) {
        
            console.log(result);
            $('#datasets_name').html(result.name);
            $('#datasets_description').html(result.short_desc);
            
            //Filling dataset
            var body = $('#table_of_datasets').find('tbody');
            body.empty();
            result.tables.forEach( function(dataset, index) {
                var dataset_id = index;
                var new_row = $(document.createElement('tr'));
                new_row.load('templates/dataset.html', function () {
                    var tds = new_row.find('td');
                    var spans = $(tds[2]).find('span');
                    
                    $(tds[0]).empty();
                    $(tds[1]).empty();
                    $(tds[0]).append(dataset.name);
                    $(tds[1]).append(dataset.short_desc);
                    spans.toArray().forEach( function(span) {
                        if ($(span).attr('onclick')) {
                            var new_oc = $(span).attr('onclick').replace('ds_id', dataset_id);
                             $(span).attr('onclick', new_oc);
                        }
                    });
                });
                body.append(new_row);
            });
            
            //Updating/emptying html elements
            $('#datasets_creation_name').val("");
            $('#datasets_creation_description').val("");
            $("#datasets_file_from_HD").val("");
            $('#datasets_creation_button').attr('onclick', 'datasets_send_new('+database_id+')');
        
            datasets_add_a_row('datasets_creation_from_scratch_columns');
            database_infos = result;
            
            //Ask for the existing tags
            var datastore_id = 0;   // TODO
            sakura.common.ws_request('list_expected_columns_tags', [datastore_id], {}, function (tags_list) {
                columns_tags_list = tags_list;
            });
        });
    /*});*/
}

/////////////////////////////////////////
// UPLOAD
function dataset_upload(dataset_id) {
    $('#datasets_upload_header').html('<h3>Upload Data into <b>'+database_infos.tables[dataset_id].name+'</b></h3>');
    $('#datasets_upload_select_file').attr('onchange', 'datasets_upload_on_file_selected(this, '+dataset_id+');');
    $('#datasets_upload_button').attr('onclick', 'datasets_upload('+dataset_id+');');
    $('#datasets_upload_modal').modal();
}

function datasets_upload_on_file_selected(f, dataset_id) {
    if (!extension_check(f.value, 'csv')) {
        return;
    }
    
    var nb_cols     = database_infos.tables[dataset_id].columns.length;
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


function datasets_send_file(dataset_id, f, dates) {
    var first_chunk = true;
    Papa.parse(f, {
        comments: true,
        header: false,
        skipEmptyLines: true,
        worker: true,
        chunk: function(chunk) {
            if (first_chunk) {
                chunk.data.splice(0, 1);
                first_chunk = false;
            }
            sakura.common.ws_request('add_rows_into_table', [dataset_id, chunk.data, dates], {}, function(result) {
                if (!result) {
                    console.log("Issue in sending file");
                }
            });
        },
        complete: function() {
            datasets_info('Sending File', 'Done !!');
        },
        error: function (error) {
            console.log(error);
        }
    });
}

function datasets_upload(dataset_id) {
    var f = $('#datasets_upload_select_file')[0].files[0];
    
    //Getting dates format
    sakura.common.ws_request('get_dataset_gui_data', [dataset_id], {}, function(result) {
        console.log(result);
    });
}


/////////////////////////////////////////
// TODO
function dataset_download(dataset_id) {
    file_text = "";
    
    //fill file text from hub
    
    
    //Create a link from downloading the file
    var element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent('col1,col2\nval1,val2\nval3,val4'));
    element.setAttribute('download', 'test_download.csv');
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}


function dataset_analytics(dataset_id) {
    not_yet();
}


function dataset_delete(dataset_id) {
    not_yet();
}

