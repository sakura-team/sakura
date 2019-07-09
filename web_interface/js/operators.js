//Code started by Michael Ortega for the LIG
//February, 13, 2019

function byID(id) {
    return document.getElementById(id);
}

function display_as_error(div) {
    div.classList.remove('has-success');
    div.classList.add('has-error');
}

function display_as_success(div) {
    div.classList.remove('has-error');
    div.classList.add('has-success');
}

function display_as_nothing(div) {
    div.classList.remove('has-success');
    div.classList.remove('has-error');
}

function creation_operator_check_URL() {
    var code_url = byID('operators_creation_url_input').value;
    if (code_url == "") {
        return;
    }

    //var code_url = 'https://github.com/sakura-team/sakura';

    var butt = byID('operators_creation_url_input_button');
    butt.innerHTML = '<span class="glyphicon glyphicon-hourglass"></span>';
    $('#operators_creation_sub_dir_refresh_icon').show();

    sakura.apis.hub.misc.list_code_revisions(code_url).then(function(result) {
        var butt = byID('operators_creation_url_input_button');
        butt.innerHTML = '<span class="glyphicon glyphicon-search"></span>';

        display_as_success(byID('operators_creation_url_input_div'));
        fill_revision_select(result);
        fill_sub_dir_select(code_url, result[0][0]);

        $("#operators_creation_div_step2").show();
        operators_creation_check_possible_submission();

    }).catch(function (error) {
        display_as_error(byID('operators_creation_url_input_div'));
        var butt = byID('operators_creation_url_input_button');
        butt.innerHTML = '<span class="glyphicon glyphicon-search"></span>';

        empty_revision_select();
        empty_sub_dir_select();
        $("#operators_creation_div_step2").hide();
        operators_creation_check_possible_submission();

        var msg = error.split(':')[1];
        main_alert('Error in URL checking !', msg);
    });
}

function empty_revision_select() {
    var select = $('#operators_creation_revision');
    select.empty();
    select.selectpicker('refresh');
}

function empty_sub_dir_select() {
    var select = $('#operators_creation_sub_dir');
    select.empty();
    select.selectpicker('refresh');
}

function fill_revision_select(result) {
    var select = $('#operators_creation_revision');
    select.empty();
    select.selectpicker('refresh');
    result.forEach( function(item) {
        var branch = item[0].split(':');
        var opt = $('<option>', { value: item[0]});
        opt.html('<b>'+branch[0]+' : </b> '+branch[1]);
        opt.prop('commit_hash', item[1]);
        opt.prop('branch', item[0]);
        select.append(opt);
    });
    select.selectpicker('refresh');
}

function fill_sub_dir_select(code_url, revision) {
    var select = $('#operators_creation_sub_dir');
    select.empty();
    select.selectpicker('refresh');
    sakura.apis.hub.misc.list_operator_subdirs(code_url, revision).then (function(result) {
        result.forEach( function(item) {
          var opt = $('<option>', { value: item});
          opt.html(item);
          select.append(opt);
        });
        select.selectpicker('refresh');
        operators_creation_check_possible_submission();
        $('#operators_creation_sub_dir_refresh_icon').hide();
    }).catch(function (error) {
        main_alert('Error in filling sub dir select !', error);
        $('#operators_creation_sub_dir_refresh_icon').hide();
    });
}

function operators_creation_url_input_change(event) {
    byID('operators_submit_button').disabled = true;
    display_as_error(byID('operators_creation_url_input_div'));
    empty_revision_select();
    empty_sub_dir_select();
    $("#operators_creation_div_step2").hide();
    operators_creation_check_possible_submission();
}

function operators_update_creation_modal() {
    $("#operators_submit_button").html('Submit');

    var select1 = $('#operators_creation_revision');
    select1.selectpicker('refresh');
    var select2 = $('#operators_creation_sub_dir');
    select2.selectpicker('refresh');
}

function operators_creation_revision_change(event) {
    byID('operators_submit_button').disabled = true;
    $('#operators_creation_sub_dir_refresh_icon').show();

    var code_url  = byID('operators_creation_url_input').value;
    var select    = byID('operators_creation_revision');
    var opt       = select.options[select.selectedIndex];
    var revision  = opt.value;
    fill_sub_dir_select(code_url, revision);
}

function operators_creation_check_possible_submission() {
    var url_div     = byID('operators_creation_url_input_div');
    if (url_div.classList.value.search('has-success') != -1) {
            byID('operators_submit_button').disabled = false;
        }
    else {
        byID('operators_submit_button').disabled = true;
    }
}

function operators_creation_new() {
    var select  = byID('operators_creation_revision');
    var opt     = select.options[select.selectedIndex];

    var hash      = opt.commit_hash;
    var url       = byID('operators_creation_url_input').value;
    var sub_dir   = byID('operators_creation_sub_dir').value;
    var revision  = opt.branch


    sakura.apis.hub.op_classes.register(url, revision, hash, sub_dir).then(function (result){
        main_success_alert('Operator Registration', 'Registered !', function () {
            operators_close_modal();
        }, 3);
    }).catch( function(error_msg) {
        main_alert('Error while Registering Operator !', error_msg);
    });
}

function operators_close_modal() {
    $('#declare_operators_modal').modal('hide');
}
