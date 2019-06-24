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

    var butt = byID('operators_creation_url_input_button');
    butt.innerHTML = '<span class="glyphicon glyphicon-hourglass"></span>';

    sakura.apis.hub.misc.list_code_revisions(code_url).then(function(result) {
        //https://github.com/sakura-team/operator-spacetime
        var butt = byID('operators_creation_url_input_button');
        butt.innerHTML = '<span class="glyphicon glyphicon-search"></span>';

        display_as_success(byID('operators_creation_url_input_div'));

        var sub_dir_text  = byID('operators_creation_sub_dir');
        var sub_dir_div   = byID('operators_creation_sub_dir_div');
        var sub_dir_butt  = byID('operators_creation_sub_dir_button');
        sub_dir_text.disabled = false;
        sub_dir_butt.disabled = false;
        sub_dir_text.value = '';
        display_as_success(sub_dir_div);
        fill_revision_select(result);
        operators_creation_check_possible_submission();

    }).catch(function (error) {
        display_as_error(byID('operators_creation_url_input_div'));
        var butt = byID('operators_creation_url_input_button');
        butt.innerHTML = '<span class="glyphicon glyphicon-search"></span>';

        empty_revision_select();
        operators_creation_check_possible_submission();

        alert(error);
    });
}

function empty_revision_select() {
    var select = $('#operators_creation_revision');
    select.empty();
    select.selectpicker('refresh');
}

function fill_revision_select(result) {
    var select = $('#operators_creation_revision');
    select.empty();
    result.forEach( function(item) {
        console.log(item);
        var branch = item[0].split(':')[1];
        var opt = $('<option>', { value: branch});
        opt.html('<b>Branch : </b> '+branch);
        opt.prop('commit_hash', item[1]);
        opt.prop('branch', item[0]);
        select.append(opt);
    });
    select.selectpicker('refresh');
}

function operators_creation_url_input_change(event) {
    display_as_error(byID('operators_creation_url_input_div'));

    var sub_dir_text = byID('operators_creation_sub_dir');
    var sub_dir_butt = byID('operators_creation_sub_dir_button');
    sub_dir_text.disabled = true;
    sub_dir_butt.disabled = true;
    display_as_nothing(byID('operators_creation_sub_dir_div'));

    empty_revision_select();
    operators_creation_check_possible_submission();
}

function creation_operator_check_sub_dir() {
    var code_url  = byID('operators_creation_url_input').value;
    var sub_dir   = byID('operators_creation_sub_dir').value;
    var url       = code_url + '/' + sub_dir;

    var butt = byID('operators_creation_sub_dir_button');
    butt.innerHTML = '<span class="glyphicon glyphicon-hourglass"></span>';

    sakura.apis.hub.misc.list_code_revisions(url).then(function(result) {
        var butt = byID('operators_creation_sub_dir_button');
        butt.innerHTML = '<span class="glyphicon glyphicon-search"></span>';
        var sub_dir_div   = byID('operators_creation_sub_dir_div');
        display_as_success(sub_dir_div);
        fill_revision_select(result);
        operators_creation_check_possible_submission();

    }).catch( function(error) {
        var butt = byID('operators_creation_sub_dir_button');
        butt.innerHTML = '<span class="glyphicon glyphicon-search"></span>';
        var sub_dir_div   = byID('operators_creation_sub_dir_div');
        display_as_error(sub_dir_div);

        empty_revision_select();
        operators_creation_check_possible_submission();

        alert(error);
    });
}

function operators_creation_sub_dir_change(event) {
    display_as_error(byID('operators_creation_sub_dir_div'));
    operators_creation_check_possible_submission();
}

function operators_update_creation_modal() {
    //submit button: back to initial display
    $("#operators_submit_button").html('Submit');

    var select = $('#operators_creation_revision');
    select.selectpicker('refresh');
}

function operators_creation_revision_change(event) {
    //Nothing to do here for now
}

function operators_creation_check_possible_submission() {
    var sub_dir_div = byID('operators_creation_sub_dir_div');
    var url_div     = byID('operators_creation_url_input_div');
    if (url_div.classList.value.search('has-success') != -1 &&
        sub_dir_div.classList.value.search('has-success') != -1) {
            byID('operators_submit_button').disabled = false;
        }
    else {
        byID('operators_submit_button').disabled = true;
    }
}

function operators_creation_new() {
    var select  = byID('operators_creation_revision');
    var opt     = select.options[select.selectedIndex];

    var burl    = byID('operators_creation_url_input').value;
    var sub_dir = byID('operators_creation_sub_dir').value;
    var hash    = opt.commit_hash;
    var branch  = opt.branch
    var url     = burl + '/' + sub_dir;

    console.log('Should send:', url, branch, hash);
}

function operators_close_modal(id) {
    $('#'+id).modal('hide');
}
