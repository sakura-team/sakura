//Code started by Michael Ortega for the LIG
//August, 22nd, 2017


var database_infos = null;
var columns_tags_list = null;

function not_yet() {
    alert("not yet implemented");
}


function recover_datasets() {
    
    var database_id = window.location.search.substr(1).split("=")[1];
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
            //Filling dataset
            var body = $('#table_of_datasets').find('tbody');
            body.empty();
            result.tables.forEach( function(dataset, index) {
                console.log(dataset);
                var dataset_id = index;
                var new_row = $(document.createElement('tr'));
                new_row.load('templates/dataset.html', function () {
                    var tds = new_row.find('td');
                    var spans = $(tds[2]).find('span');
                    
                    $(tds[0]).empty();
                    $(tds[1]).empty();
                    $(tds[0]).append(dataset.name);
                    $(tds[1]).append(dataset.description);
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


function dataset_upload(dataset_id) {
    not_yet();
}


function dataset_download(dataset_id) {
    not_yet();
}


function dataset_analytics(dataset_id) {
    not_yet();
}


function dataset_delete(dataset_id) {
    not_yet();
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

