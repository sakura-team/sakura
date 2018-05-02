//Code started by Michael Ortega for the LIG
//August, 21st, 2017

var database_datastores = null;


var database_mandatory = {'name': false, 'short_description': false}

function database_creation_check_name() {
    if ($('#database_name_input').val().length > 0) {
        $('#database_div_name_input').removeClass('has-error');
        database_mandatory.name = true;
    }
    else {
        $('#database_div_name_input').addClass('has-error');
        database_mandatory.name = false;
    }
    database_creation_check_mandatory();
}


function database_creation_check_shortdescription() {
    if ($('#database_shortdescription_input').val().length > 0) {
        $('#database_div_shortdescription_input').removeClass('has-error');
        database_mandatory.short_description = true;
    }
    else {
        $('#database_div_shortdescription_input').addClass('has-error');
        database_mandatory.short_description = false;
    }
    database_creation_check_mandatory();
}


function database_creation_check_mandatory() {
    var ok = true;
    for (x in database_mandatory)
        if (!database_mandatory[x])
            ok = false;
    if (ok)
        $('#database_submit_button').prop('disabled', false);
    else
        $('#database_submit_button').prop('disabled', true);
}


function database_update_creation_modal() {

    //submit button: back to initial display
    $("#database_submit_button").html('Submit');

    //first we ask the hub the datastore
    sakura.common.ws_request('list_datastores', [], {}, function (result) {
        database_datastores = result;
        $('#database_datastore_input').empty();
        result.forEach( function(ds) {
            console.log(ds);
            if (ds['online']) {
                $('#database_datastore_input').append('<option value="'+ds['datastore_id']+'">'+ds['driver_label']+" service on "+ds['host']+'</option>');
            }
        });
        $('#database_datastore_input').append('<option value="other" data-subtext="Requesting access to private datastores">Other</option>');
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

    var access_scope      = 'restricted';
    $('[id^="database_creation_access_scope_radio"]').each( function() {
        if (this.checked) {
            var tab = this.id.split('_');
            access_scope = tab[tab.length - 1];
        }
    });

    var agent_type  = $('#database_agent_type_input').val();
    var topic= $('#database_topic_input').val();
    //var licence     = $('#database_licence_input').val();

    var data_type   = '';
    $('[id^="database_data_type_input"]').each( function() {
        if (this.checked) {
            var tab = this.id.split("_");
            data_type = tab[tab.length-1];
        }
    });

    var licence = "Public";
    $('[id^="database_data_licence"]').each( function() {
        if (this.checked) {
            var tab = this.id.split("_");
            licence = tab[tab.length-1];
        }
    });


    $("#database_submit_button").html('Creating...<span class="glyphicon glyphicon-refresh glyphicon-refresh-animate"></span>');

    /*console.log("Name:", name);
    console.log("Short:", short_d);
    console.log("Datastore:", ds_id);
    console.log("Access scope:", access_scope);
    console.log("Agent type:", agent_type);
    console.log("Topic:", topic);
    console.log("Data type:", data_type);
    console.log("Licence:", licence);
    */

    sakura.common.ws_request('new_database',
                                [ds_id, name],
                                {   'short_desc': short_d,
                                    'access_scope': access_scope,
                                    'agent_type': agent_type,
                                    'topic': topic,
                                    'data_type': data_type,
                                    'licence': licence  },
                                function(result) {
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
    if ($('#database_datastore_input').val() == 'other') {
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
