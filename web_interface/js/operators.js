//Code started by Michael Ortega for the LIG
//February, 13, 2019

var waiting_icon = '<span class="fa fa-cog fa-spin" style="font-size:18px"></span>';

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
    let repo_url = byID('operators_creation_url_input').value;
    if (repo_url == "") {
        return;
    }
    let butt = byID('operators_creation_url_input_button');
    butt.innerHTML = waiting_icon;
    $('#operators_creation_sub_dir_refresh_icon').show();

    push_request('misc_list_code_revisions');
    sakura.apis.hub.misc.list_code_revisions(repo_url).then(function(result) {
        pop_request('misc_list_code_revisions');
        let butt = byID('operators_creation_url_input_button');
        butt.innerHTML = '<span class="glyphicon glyphicon-search"></span>';

        display_as_success(byID('operators_creation_url_input_div'));
        fill_revision_select(result);
        fill_sub_dir_select(repo_url, result[0][0]);

        $("#operators_creation_div_step2").show();
        operators_creation_check_possible_submission();

    }).catch(function (error) {
        pop_request('misc_list_code_revisions');
        display_as_error(byID('operators_creation_url_input_div'));
        let butt = byID('operators_creation_url_input_button');
        butt.innerHTML = '<span class="glyphicon glyphicon-search"></span>';

        empty_revision_select();
        empty_sub_dir_select();
        $("#operators_creation_div_step2").hide();
        operators_creation_check_possible_submission();

        let msg = error.split(':')[1];
        main_alert('Error in URL checking !', msg);
    });
}

function empty_revision_select() {
    let select = $('#operators_creation_revision');
    select.empty();
    select.selectpicker('refresh');
}

function empty_sub_dir_select() {
    let select = $('#operators_creation_sub_dir');
    select.empty();
    select.selectpicker('refresh');
}

function fill_revision_select(result) {
    let select = $('#operators_creation_revision');
    select.empty();
    select.selectpicker('refresh');
    result.forEach( function(item) {
        let branch = item[0].split(':');
        let opt = $('<option>', { value: item[0]});
        opt.html('<b>'+branch[0]+' : </b> '+branch[1]);
        opt.prop('commit_hash', item[1]);
        opt.prop('branch', item[0]);
        select.append(opt);
    });
    select.selectpicker('refresh');
}

function fill_sub_dir_select(repo_url, revision) {
    let select = $('#operators_creation_sub_dir');
    select.empty();
    select.selectpicker('refresh');
    push_request('misc_list_operator_subdirs');
    sakura.apis.hub.misc.list_operator_subdirs(repo_url, revision).then (function(result) {
        pop_request('misc_list_operator_subdirs');
        result.forEach( function(item) {
          let opt = $('<option>', { value: item});
          opt.html(item);
          select.append(opt);
        });
        select.selectpicker('refresh');
        operators_creation_check_possible_submission();
        $('#operators_creation_sub_dir_refresh_icon').hide();
    }).catch(function (error) {
        pop_request('misc_list_operator_subdirs');
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
    //Before opening, we should be sure the user can register an operator
    push_request('users_current_info');
    sakura.apis.hub.users.current.info().then( function(infos) {
        pop_request('users_current_info');
        if (infos.privileges != null &&
            infos.privileges.indexOf('developer') != -1) {
            $("#operators_submit_button").html('Register');
            let select1 = $('#operators_creation_revision');
            select1.selectpicker('refresh');
            let select2 = $('#operators_creation_sub_dir');
            select2.selectpicker('refresh');
            let select3 = $('#operators_creation_access_scope');
            select3.empty();
            select3.append('<option>Private</option>');
            select3.append('<option>Public</option>');
            select3.selectpicker('refresh');
            creation_operator_check_URL();
            $('#declare_operators_modal').modal('show');
        }
        else {
            let mod = $('#main_alert_modal');
            let mod_h = $('#main_alert_header');
            let mod_b = $('#main_alert_body');
            mod_h.empty();
            mod_b.empty();

            mod_h.append('<h3>Developer Status</h3>');
            mod_b.append('<p>You do not have the <b>Developer</b> status needed for registering a new operator.<br>Please update your profile (user up-right button) and ask for it.');
            mod.modal('show');
        }
    });
}

function operators_creation_revision_change(event) {
    byID('operators_submit_button').disabled = true;
    $('#operators_creation_sub_dir_refresh_icon').show();

    let repo_url  = byID('operators_creation_url_input').value;
    let select    = byID('operators_creation_revision');
    let opt       = select.options[select.selectedIndex];
    let revision  = opt.value;
    fill_sub_dir_select(repo_url, revision);
}

function operators_creation_check_possible_submission() {
    let url_div     = byID('operators_creation_url_input_div');
    if (url_div.classList.value.search('has-success') != -1) {
            byID('operators_submit_button').disabled = false;
        }
    else {
        byID('operators_submit_button').disabled = true;
    }
}

function operators_creation_new() {

    $("#operators_submit_button").html('Please wait ... '+waiting_icon);
    byID('operators_submit_button').disabled = true;

    let select  = byID('operators_creation_revision');
    let opt     = select.options[select.selectedIndex];

    let hash      = opt.commit_hash;
    let url       = byID('operators_creation_url_input').value;
    let sub_dir   = byID('operators_creation_sub_dir').value;
    let access    = byID('operators_creation_access_scope').value.toLowerCase();
    let revision  = opt.branch


    push_request('op_classes_register');
    sakura.apis.hub.op_classes.register({
                "repo_type": "git",
                "repo_url": url,
                "default_code_ref": revision,
                "default_commit_hash": hash,
                "repo_subdir": sub_dir,
                "access_scope": access}).then(function (result){
          pop_request('op_classes_register');
          main_success_alert('Operator Registration', 'Registered !', function () {
            showDiv(null, 'Operators', null);
            operators_close_modal();
        }, 2);
        $("#operators_submit_button").html('Succefully Registered !');
        //byID('operators_submit_button').disabled = False;
    }).catch( function(error_msg) {
        pop_request('op_classes_register');
        $("#operators_submit_button").html('Register');
        byID('operators_submit_button').disabled = false;
        main_alert('Error while Registering Operator !', error_msg);
    });
}

function operators_close_modal() {
    $('#declare_operators_modal').modal('hide');
}

//---------OPERATOR REVISIONS

function operators_revision_panel_open(code_url, elt, instance = false, pos, end_cb) {

    let orp       = $('#operators_revision_panel2');
    let op_cl     = null;
    let op_inst   = null;
    let op_type   = 'class';
    let rev_type  = null;

    if (!instance) {
        op_cl = current_op_classes_list.find( function (e) {
                            return e.id === parseInt(elt.id);
                  });
        rev_type = {'reference_cls_id': parseInt(elt.id)};
        current_revised_op = {'id': elt.id,
                              'name': op_cl.name,
                              'type': 'class',
                              'data': op_cl};
    }
    else {
        op_inst = global_ops_inst.find( function (e) {
                           return e.hub_id === parseInt(elt.op_id);
                 });
        rev_type = {'reference_op_id': parseInt(elt.op_id)};
        current_revised_op = {'id': elt.op_id,
                              'name': op_inst.cl.name,
                              'type': 'instance',
                              'data': op_inst};
    }

    orp.css({ left: pos.left + 10, top: pos.top +10});

    orp.empty();
    let select = $('<select>', {'class': 'selectpicker',
                                'id': 'operators_revision_panel_select',
                                'data-live-search': 'true',
                                'data-width': '100%'
                                });
    select.change( function (event) {
        operators_change_revision(end_cb);
    });

    select.on('hidden.bs.select', function(e) {
        $('#operators_revision_panel2').hide();
    });

    let span = $('<span>', {'class': "glyphicon \
                                      glyphicon-refresh \
                                      glyphicon-refresh-animate"});
    orp.append(select.append($('<option>').append(span)));
    select.selectpicker('refresh');
    orp.show();

    //fill
    let remote = sakura.apis.hub.misc;
    push_request('misc_list_code_revisions');
    remote.list_code_revisions(code_url, rev_type).then( function (result) {
            pop_request('misc_list_code_revisions');
            current_code_url = code_url;
            current_revisions = result;
            select.empty();
            result.forEach( function(revision, index) {
                let txt = '<b>'+revision[0]+'</b> &nbsp;&nbsp;@'+revision[1].substring(0,7)+' &nbsp;&nbsp;<i>'+revision[2]+'<i>';
                let opt = $('<option>', { 'value': index,
                                          'html': txt});
                if (revision[2].indexOf('current') != -1) {
                    current_operator_revision = revision;
                    opt.prop('selected', true);
                }
                select.append(opt);
            });
            select.selectpicker('refresh');
            select.selectpicker('toggle');

            let panW    = $('#operators_revision_panel').outerWidth();
            let scrW    = $(window).width();
            let leftW   = parseInt(orp.css('left').split('px')[0]);
            let rightW  = scrW - leftW - panW;

            if (rightW < 0)
                orp.css({left: Math.max(0, leftW + rightW - 20)});

    }).catch( function(err) {
        pop_request('misc_list_code_revisions');
        function cb() {
            $('#operators_revision_panel').hide();
        }
        main_alert('Revision of '+current_revised_op.name, err, cb);
    });
}

function operators_revision_panel_select_open(select, elt, is_instance, cb) {
    let pos = { top: select.offset().top - select.position().top,
                left: select.offset().left - select.position().left};
    operators_revision_panel_open(elt.repo_url, elt, is_instance, pos, cb);
}

function operators_change_revision(end_cb) {
    let opt       = $('#operators_revision_panel_select option:selected');
    let revision  = current_revisions[parseInt(opt[0].value)];
    let id        = parseInt(current_revised_op.id);

    let remote = null;
    if (current_revised_op.type != 'instance')
        remote = sakura.apis.hub.op_classes[id].update_default_revision;
    else
        remote = sakura.apis.hub.operators[id].update_revision;

    push_request('operators_update_revision');
    remote(revision[0], revision[1]).then(function(result) {
        pop_request('operators_update_revision');
        $('#operators_revision_panel').hide();
        if (!end_cb)  showDiv(null, 'Operators');
        else          end_cb();
    }).catch( function(error) {
        pop_request('operators_update_revision');
        main_alert('Revision of '+current_revised_op.name, error);
    });
}
