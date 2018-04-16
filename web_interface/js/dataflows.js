//Code started by Michael Ortega for the LIG
//April, 16, 2018


var dataflow_mandatory = {'name': false, 'short_description': false}

function dataflow_creation_check_name() {
    if ($('#dataflow_name_input').val().length > 0) {
        $('#dataflow_div_name_input').removeClass('has-error');
        dataflow_mandatory.name = true;
    }
    else {
        $('#dataflow_div_name_input').addClass('has-error');
        dataflow_mandatory.name = false;
    }
    dataflow_creation_check_mandatory();
}


function dataflow_creation_check_shortdescription() {
    if ($('#dataflow_shortdescription_input').val().length > 0) {
        $('#dataflow_div_shortdescription_input').removeClass('has-error');
        dataflow_mandatory.short_description = true;
    }
    else {
        $('#dataflow_div_shortdescription_input').addClass('has-error');
        dataflow_mandatory.short_description = false;
    }
    dataflow_creation_check_mandatory();
}

function dataflow_creation_check_mandatory() {
    var ok = true;
    for (x in dataflow_mandatory)
        if (!dataflow_mandatory[x])
            ok = false;
    if (ok)
        $('#dataflow_submit_button').prop('disabled', false);
    else
        $('#dataflow_submit_button').prop('disabled', true);
}


function dataflow_update_creation_modal() {

    //submit button: back to initial display
    $("#dataflow_submit_button").html('Submit');

}


function new_dataflow() {
    var name = $('#dataflow_name_input').val();

    if ((name.replace(/ /g,"")).length == 0) {
        alert("Empty name!! We cannot create data without a name.");
        return ;
    }

    var short_d     = $('#dataflow_shortdescription_input').val();

    var access_scope      = 'restricted';
    $('[id^="dataflow_creation_access_scope_radio"]').each( function() {
        if (this.checked) {
            var tab = this.id.split('_');
            access_scope = tab[tab.length - 1];
        }
    });

    var topic= $('#dataflow_topic_input').val();

    var licence = "Public";
    $('[id^="dataflow_data_licence"]').each( function() {
        if (this.checked) {
            var tab = this.id.split("_");
            licence = tab[tab.length-1];
        }
    });

    $("#dataflow_submit_button").html('Creating...<span class="glyphicon glyphicon-refresh glyphicon-refresh-animate"></span>');

    sakura.common.ws_request('new_dataflow',
                                [name],
                                {   'short_desc': short_d,
                                    'access_scope': access_scope,
                                    'topic': topic,
                                    'licence': licence  },
                                function(result) {
        if (result < 0) {
            alert("Something Wrong with the values ! Please check and submit again.");
        }
        else {
            $('#create_dataflow_modal').modal('hide');
            showDiv(null, 'Dataflows/Dataflow-'+result, null);
        }
    });
}


function dataflow_close_modal(id) {
    console.log(id);
    $('#'+id).modal('hide');
}
