//Code started by Michael Ortega for the LIG
//August, 21st, 2017

var database_datastores = null;

function database_update_creation_modal() {
    //submit button: back to initial display
    $("#database_submit_button").html('Submit');
    
    //first we ask the hub the datastore
    sakura.common.ws_request('list_datastores', [], {}, function (result) {
        database_datastores = result;
        $('#database_datastore_input').empty();
        result.forEach( function(ds) {
            if (ds['online']) {
                console.log(ds);
                $('#database_datastore_input').append('<option value="'+ds['datastore_id']+'">'+ds['driver_label']+" service on "+ds['host']+'</option>');
            }
        });
        $('#database_datastore_input').append('<option value="more">more (in progress)</option>');
        $('#database_datastore_input').selectpicker('refresh');

    });
    
}


function new_database() {
    var name = $('#database_name_input').val();
    
    if ((name.replace(/ /g,"")).length == 0) {
        alert("Empty name!! We cannot create data without a name.");
        return ;
    }
    
    var short_d     = $('#database_shortdescription_input').val();
    var ds_id       = parseInt($('#database_datastore_input').val());
    var public_val  = $('#database_public_input')[0].checked;
    
    $("#database_submit_button").html('Creating...<span class="glyphicon glyphicon-refresh glyphicon-refresh-animate"></span>');
    
    
    sakura.common.ws_request('new_database', [ds_id, name], {'short_desc': short_d}, function(result) {
        //result = new database id
        if (result < 0) {
            alert("Something Wrong with the values ! Please check and submit again.");
        }
        else {
            $('#create_database_modal').modal('hide');
            showDiv(null, 'Datas/Data-'+result, null);
        }
    });
}


function database_close_modal(id) {
    $('#'+id).modal('hide');
}


function database_datastore_on_change() {
    if ($('#database_datastore_input').val() == 'more') {
        var tab = $('#database_offline_datastores');
        tab.empty();
        database_datastores.forEach( function(ds) {
            if (!ds['online']) {
                var new_b_row = $(tab[0].insertRow());
                var line = "<td>"+ds['driver_label']+" service on "+ds['host']+"</td>";
                new_b_row.append(line);
            }
        });
        
        $('#databases_other_datastores_modal').modal('show');
    }
}