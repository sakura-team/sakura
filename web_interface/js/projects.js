///////////////PROJECTS PART
var projects_mandatory = {'name': false, 'short_description': false};
var pages_mandatory = {'name': false};

function projects_update_creation_modal() {
}

function projects_close_modal() {
    $('#create_projects_modal').modal('hide');
}

function projects_creation_check_name() {
    let name = $('#projects_name_input').val();
    if ((name.replace(/ /g,"")).length > 0) {
        $('#projects_div_name_input').removeClass('has-error');
        projects_mandatory.name = true;
    }
    else {
        $('#projects_div_name_input').addClass('has-error');
        projects_mandatory.name = false;
    }
    projects_creation_check_mandatory();
}


function projects_creation_check_shortdescription() {
    let desc = $('#projects_shortdescription_input').val();
    if ((desc.replace(/ /g,"")).length > 0) {
      $('#projects_div_shortdescription_input').removeClass('has-error');
        projects_mandatory.short_description = true;
    }
    else {
        $('#projects_div_shortdescription_input').addClass('has-error');
        projects_mandatory.short_description = false;
    }
    projects_creation_check_mandatory();
}

function projects_creation_check_mandatory() {
    var ok = true;
    for (x in projects_mandatory) if (!projects_mandatory[x])  ok = false;
    if (ok) $('#projects_submit_button').prop('disabled', false);
    else    $('#projects_submit_button').prop('disabled', true);
}


function new_project() {
    var name          = $('#projects_name_input').val();
    var short_d       = $('#projects_shortdescription_input').val();
    var access_scope  = 'restricted';
    $('[id^="projects_creation_access_scope_radio"]').each( function() {
        if (this.checked) {
            var tab = this.id.split('_');
            access_scope = tab[tab.length - 1];
        }
    });

    sakura.apis.hub.projects.create(name, { 'short_desc': short_d,
                                            'access_scope': access_scope }
                                ).then(function(project_id) {
        if (project_id < 0) {
            alert("Something Wrong with the values ! Please check and submit again.");
        }
        else {
            sakura.apis.hub.projects[project_id].info().then (function (info) {
                sakura.apis.hub.pages[info.pages[0].page_id].update({ 'page_name': 'Page 1',
                                                                      'page_content': pages_init_text}
                        ).then (function(result) {
                      $('#create_projects_modal').modal('hide');
                      showDiv(null, 'Projects/Project-'+project_id, null);
                  })
            });


        }
    });
}

///////////////PAGES PART
function pages_creation_check_name() {
    let name = $('#pages_name_input').val();
    if ((name.replace(/ /g,"")).length > 0) {
        $('#pages_div_name_input').removeClass('has-error');
        pages_mandatory.name = true;
    }
    else {
        $('#pages_div_name_input').addClass('has-error');
        pages_mandatory.name = false;
    }
    pages_creation_check_mandatory();
}

function pages_creation_check_mandatory() {
    var ok = true;
    for (x in pages_mandatory)  if (!pages_mandatory[x])  ok = false;
    if (ok) $('#pages_submit_button').prop('disabled', false);
    else    $('#pages_submit_button').prop('disabled', true);
}

function new_page() {
    let name          = $('#pages_name_input').val();
    let access_scope  = 'restricted';
    let id            = web_interface_current_object_info.project_id;
    $('[id^="pages_creation_access_scope_radio"]').each( function() {
        if (this.checked) {
            var tab = this.id.split('_');
            access_scope = tab[tab.length - 1];
        }
    });
    sakura.apis.hub.pages.create(id, name).then(function (page_id) {
        console.log('Great !!', page_id);
        sakura.apis.hub.pages[page_id].update({'page_content': pages_init_text}
                        ).then (function(result) {
              pages_close_modal();
              showDiv(null, 'Projects/Project-'+web_interface_current_object_info.project_id+'/Page-'+page_id, null);
        })
    }).catch( function(result) {
        console.log('Pas Great !!', result);
    });
}

function delete_page(page_id){
    stub_asking( 'Delete a Page',
                  'Are you sure you want to definitely delete this page from the project ??',
                  'rgba(217,83,79)',
                  function() {
                      sakura.apis.hub.pages[page_id].delete().then( function(result){
                          let project_id = web_interface_current_object_info.project_id;
                          let li = document.getElementById("web_interface_projects_li_project_"+project_id+"_page_"+page_id);
                          li.remove();
                          showDiv(null, 'Projects/Project-'+project_id, null);
                      });
                  },
                  function() {} );


}

function pages_close_modal() {
    $('#create_pages_modal').modal('hide');
}