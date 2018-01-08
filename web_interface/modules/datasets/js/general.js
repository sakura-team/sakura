//Code started by Michael Ortega for the LIG
//August, 22nd, 2017


var database_infos = null;
var columns_tags_list = null;
var mouse = {x: 0, y: 0};

function not_yet() {
    alert("not yet implemented");
}


function datasets_sort_func(a, b) {
    return a.name > b.name ? 1 : -1;
}


$(document).mousemove(function(e) {
    mouse.x = e.pageX;
    mouse.y = e.pageY;
}).mouseover(); // call the handler immediately



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


function datasets_extension_check(f_name, ext) {
    //check the name: should have .csv extension
    var s_name = f_name.split('.');
    if (s_name[s_name.length - 1].toLowerCase() != ext.toLowerCase()) {
        datasets_alert("File Extension Issue", "The extension of this file is not .csv !!\nPlease be sure it is a csv file, and rename it with extension.");
        return false;
    }
    return true;

}
function recover_datasets() {
    
    var searchParams = new URLSearchParams(window.location.search);
    var database_id = null;
    if (searchParams.has('database_id')) {
        database_id = searchParams.get('database_id')
    }
    
    sakura.common.ws_request('get_database_info', [parseInt(database_id)], {}, function (result) {
            
        //Sorting tables by name
        result.tables.sort(datasets_sort_func);
        $('#datasets_name').html(result.name);
        if (result.short_desc) {
            $('#datasets_description').html(result.short_desc);
        }
        else {
            $('#datasets_description').html('No short description');
        }
        
        
        //Filling dataset
        var body = $('#table_of_datasets').find('tbody');
        body.empty();
        result.tables.forEach( function(dataset, index) {
            var dataset_id = dataset.table_id;
            var new_row = $(document.createElement('tr'));
            new_row.load('templates/dataset.html', function () {
                var tds = new_row.find('td');
                var spans = $(tds[2]).find('span');
                
                $(tds[0]).empty();
                $(tds[0]).append($('<a>',{  text: dataset.name,
                                            style: "cursor: pointer;",
                                            onclick: "datasets_visu_dataset("+dataset_id+");"
                                            })
                                );
                
                $(tds[1]).empty();
                if (dataset.short_desc)
                    $(tds[1]).append(dataset.short_desc);
                else
                    $(tds[1]).append("__");
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
}


function datasets_send_file(dataset_id, f, dates, modal) {
    var first_chunk = true;
    Papa.parse(f, {
        comments: true,
        header: false,
        skipEmptyLines: true,
        chunk: function(chunk) {
            if (first_chunk) {
                chunk.data.splice(0, 1);
                first_chunk = false;
            }
            chunk.data.forEach( function(line) {
                dates.forEach(function(date) {
                    d = line[date.column_id];
                    line[date.column_id] = moment(d, date.format).unix();
                });
            });
            
            sakura.common.ws_request('add_rows_into_table', [dataset_id, chunk.data], {}, function(result) {
                if (result) {
                    console.log("Issue in sending file");
                }
            });
        },
        complete: function() {
            datasets_info('Sending File', 'Done !!');
            modal.modal('hide');
        },
        error: function (error) {
            datasets_alert("Parsing error:", error);
        }
    });
}


function this_col_is_a_date(col) {
    if (col[2].indexOf('timestamp') === -1)
        return false;
    return true;
}


function datasets_delete(dataset_id) {
    not_yet();
}

