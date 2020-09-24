//Code started by Michael Ortega for the LIG
//August, 21st, 2017

var datas_datastores = null;
var datas_mandatory = {'name': false, 'short_description': false}

function datas_creation_check_name() {
    if ($('#datas_name_input').val().length > 0) {
        $('#datas_div_name_input').removeClass('has-error');
        datas_mandatory.name = true;
    }
    else {
        $('#datas_div_name_input').addClass('has-error');
        datas_mandatory.name = false;
    }
    datas_creation_check_mandatory();
}


function datas_creation_check_shortdescription() {
    if ($('#datas_shortdescription_input').val().length > 0) {
        $('#datas_div_shortdescription_input').removeClass('has-error');
        datas_mandatory.short_description = true;
    }
    else {
        $('#datas_div_shortdescription_input').addClass('has-error');
        datas_mandatory.short_description = false;
    }
    datas_creation_check_mandatory();
}


function datas_creation_check_mandatory() {
    let ok = true;
    for (x in datas_mandatory)
        if (!datas_mandatory[x])
            ok = false;
    if (ok) {
        //Datastore check
        let ds_id       = parseInt($('#datas_datastore_input').val());
        if (isNaN(ds_id)) {
            $('#datas_submit_button').prop('disabled', true);
        }
        else
            $('#datas_submit_button').prop('disabled', false);
    }
    else
        $('#datas_submit_button').prop('disabled', true);
}


function datas_update_creation_modal() {

    //submit button: back to initial display
    $("#datas_submit_button").html('Submit');

    //first we ask the hub the datastore
    push_request('datastores_list');
    sakura.apis.hub.datastores.list().then(function (result) {
        pop_request('datastores_list');
        datas_datastores = result;
        $('#datas_datastore_input').empty();

        result.forEach( function(ds) {

            let opt = $('<option>', { value: ds['datastore_id']});
            let p = $('<p>');
            let txt = '';
            if (ds.grant_level == 'list') {
                opt.attr('disabled', 'disabled');
                opt.attr('style', 'cursor: pointer; background-color: rgba(255,0,0,.5);');

                p = $('<p>',  { title: "Request Access",
                                onclick: "web_interface_asking_access_open_modal(\'"+ds.host+"\','datastore',\'"+ds.id+"\','write',close_modal_datastores_other_modal);",
                                style: "margin: 0px;"});
                txt = '<font color="white"><span style="margin: 0px;" class="glyphicon glyphicon-eye-close"></span> ';
                txt += ds['driver_label']+" service on "+ds['host'];
                if (!ds['enabled']) {
                    txt += ' <i>(OFFLINE)</i>';
                }
                txt += "</font>";

                let w_icon = create_warn_icon(ds);
                if (w_icon) {
                    p.append(w_icon);
                }
                p.append(txt);
            }
            else {
                p = $('<p>',  { title: "Select this datastore",
                                style: "margin: 0px;"});
                txt = '<span style="margin: 0px;" class="glyphicon glyphicon-eye-open"></span> ';
                txt += ds['driver_label']+" service on "+ds['host'];
                if (!ds['enabled']) {
                    txt += ' <i>(OFFLINE)</i>';
                }

            }
            let w_icon = create_warn_icon(ds);
            if (w_icon) {
                p.append(w_icon);
            }
            p.append(txt);


            opt.html(p);
            $('#datas_datastore_input').append(opt);
        });

        //$('#datas_datastore_input').append('<option value="other" data-subtext="Requesting access to private datastores">Other</option>');
        $('#datas_datastore_input').selectpicker('refresh');
    });
}


function new_database() {
    let name = $('#datas_name_input').val();

    if ((name.replace(/ /g,"")).length == 0) {
        alert("Empty name!! We cannot create data without a name.");
        return ;
    }

    let short_d     = $('#datas_shortdescription_input').val();
    let ds_id       = parseInt($('#datas_datastore_input').val());
    if (isNaN(ds_id)) {
        return
    }


    let access_scope      = 'restricted';
    $('[id^="datas_creation_access_scope_radio"]').each( function() {
        if (this.checked) {
            let tab = this.id.split('_');
            access_scope = tab[tab.length - 1];
        }
    });

    let agent_type  = $('#datas_agent_type_input').val();
    let topic= $('#datas_topic_input').val();
    //let licence     = $('#datas_licence_input').val();

    let data_type   = '';
    $('[id^="datas_data_type_input"]').each( function() {
        if (this.checked) {
            let tab = this.id.split("_");
            data_type = tab[tab.length-1];
        }
    });

    let licence = "Public";
    $('[id^="datas_data_licence"]').each( function() {
        if (this.checked) {
            let tab = this.id.split("_");
            licence = tab[tab.length-1];
        }
    });


    $("#datas_submit_button").html('Creating...<span class="glyphicon glyphicon-refresh glyphicon-refresh-animate"></span>');

    push_request('databases_create');
    sakura.apis.hub.databases.create(ds_id, name,
                                {   'short_desc':   short_d,
                                    'access_scope': access_scope,
                                    'agent_type':   agent_type,
                                    'topic':        topic,
                                    'data_type':    data_type,
                                    'licence':      licence  }
                                ).then(function(result) {
        //result = new database id
        pop_request('databases_create');
        if (result < 0) {
            alert("Something Wrong with the values ! Please check and submit again.");
        }
        else {
            $('#create_datas_modal').modal('hide');
            showDiv(null, 'Datas/'+result, null);
        }
    }).catch(function(result) {
        pop_request('databases_create');
        main_alert('CREATION ISSUE', result);
    });
}


function datas_close_modal(id) {
    $('#'+id).modal('hide');
}

function close_modal_datastores_other_modal() {
    $('#web_interface_datastores_other_modal').modal('hide');
}
