//Code started by Michael Ortega for the LIG
//April, 16, 2018


var dataflows_mandatory = {'name': false, 'short_description': false}

function dataflows_creation_check_name() {
    if ($('#dataflows_name_input').val().length > 0) {
        $('#dataflows_div_name_input').removeClass('has-error');
        dataflows_mandatory.name = true;
    }
    else {
        $('#dataflows_div_name_input').addClass('has-error');
        dataflows_mandatory.name = false;
    }
    dataflows_creation_check_mandatory();
}


function dataflows_creation_check_shortdescription() {
    if ($('#dataflows_shortdescription_input').val().length > 0) {
        $('#dataflows_div_shortdescription_input').removeClass('has-error');
        dataflows_mandatory.short_description = true;
    }
    else {
        $('#dataflows_div_shortdescription_input').addClass('has-error');
        dataflows_mandatory.short_description = false;
    }
    dataflows_creation_check_mandatory();
}

function dataflows_creation_check_mandatory() {
    let ok = true;
    for (x in dataflows_mandatory)
        if (!dataflows_mandatory[x])
            ok = false;
    if (ok)
        $('#dataflows_submit_button').prop('disabled', false);
    else
        $('#dataflows_submit_button').prop('disabled', true);
}


function dataflows_update_creation_modal() {

    //submit button: back to initial display
    $("#dataflows_submit_button").html('Submit');

}


function new_dataflow() {
    let name = $('#dataflows_name_input').val();

    if ((name.replace(/ /g,"")).length == 0) {
        alert("Empty name!! We cannot create data without a name.");
        return ;
    }

    let short_d     = $('#dataflows_shortdescription_input').val();

    let access_scope      = 'private';
    // $('[id^="dataflows_creation_access_scope_radio"]').each( function() {
    //     if (this.checked) {
    //         let tab = this.id.split('_');
    //         access_scope = tab[tab.length - 1];
    //     }
    // });

    let topic= $('#dataflows_topic_input').val();

    let licence = "Public";
    $('[id^="dataflows_data_licence"]').each( function() {
        if (this.checked) {
            let tab = this.id.split("_");
            licence = tab[tab.length-1];
        }
    });

    $("#dataflows_submit_button").html('Creating...<span class="glyphicon glyphicon-refresh glyphicon-refresh-animate"></span>');

    push_request('dataflows_create');
    sakura.apis.hub.dataflows.create(name,
                                {   'short_desc': short_d,
                                    'access_scope': access_scope,
                                    'topic': topic,
                                    'licence': licence  }).then(
                                function(result) {
        pop_request('dataflows_create');
        if (result < 0) {
            alert("Something Wrong with the values ! Please check and submit again.");
        }
        else {
            $('#create_dataflows_modal').modal('hide');
            showDiv(null, 'Dataflows/'+result, null);
        }
    });
}


function dataflows_close_modal(id) {
    console.log(id);
    $('#'+id).modal('hide');
}
