main_alert/// LIG March 2017

////////////GLOBALS
var empty_text = "__";


var collab_bloc = '<select data-size="5" id="web_interface_obj_adding_collaborators_select" multiple class="selectpicker form-control" data-live-search="true" title="Please select one or several logins ..."></select> \
<span class="input-group-addon" style="cursor: pointer;" onclick="cleaning_collaborators();"> \
    <span class="glyphicon glyphicon-trash"></span> \
</span> \
<span class="input-group-addon" style="cursor: pointer;" onclick="adding_collaborators();">Add Collaborators</span>';

////////////FUNCTIONS
function not_yet(s) {
    if (!s) {
        alert('Not implemented yet');
    }
    else {
        alert('Not implemented yet: '+ s);
    }
}

function main_alert(header_str, body_str) {
    var h = $('#main_alert_header');
    var b = $('#main_alert_body');
    h.html("<h3><font color=\"white\">"+header_str+"</font></h3>");
    b.html("<p>"+body_str+"</p>");
    $('#main_alert_modal').modal();
}

function main_success_alert(header_str, body_str, callback, time=0) {
    //displayig success modal during 'time' sec
    var h = $('#web_interface_success_modal_header');
    var b = $('#web_interface_success_modal_body');
    h.html("<h3><font color=\"white\">"+header_str+"</font></h3>");
    b.html('<h4 align="center" style="margin: 5px;"><font color="black"> '+body_str+'</font></h4>');

    $('#web_interface_success_modal').modal('show');
    setTimeout( function () {
        $('#web_interface_success_modal').modal('hide');
        if (callback)
            callback();
    }, time*1000, callback);
}

$('body').mousemove(function(e) {
    web_interface_mouse.x = e.clientX;
    web_interface_mouse.y = e.clientY;
});


function web_interface_deal_with_events(evt_name, args) {
    switch (evt_name) {
        case 'registered_opclass':
            if (  location.href.indexOf('Operators') != -1 ||
                  (location.href.indexOf('Dataflows') != -1 &&
                  location.href.indexOf('Work') != -1)  ) {
                sakura.apis.hub.op_classes[args].info().then( function (result) {
                    location.reload();
                }).catch(function (result) {
                    // access to this object is not allowed, nothing to do
                });
            }
            break;
        case 'unregistered_opclass':
            if (  location.href.indexOf('Operators') != -1 ||
                  (location.href.indexOf('Dataflows') != -1 &&
                  location.href.indexOf('Work') != -1)  ) {
                if (current_op_classes_list == null) {
                    // TODO mike -- rework this (current_op_classes_list is not available in this iframe)
                    // current workaround: always refresh
                    location.reload();
                }
                else {
                    current_op_classes_list.forEach( function (oc){
                        if (oc.id == args)
                            location.reload();
                    });
                }
            }
            break;
        default:
            if (DEBUG)
                console.log('Unmanaged event', evt_name);
    }
}

function stub_asking(header_str, body_str, rgba_color, func_yes, func_no) {
    var h = $('#stub_asking_header');
    var b = $('#stub_asking_body');
    var b_yes = $('#stub_asking_button_yes');
    var b_no = $('#stub_asking_button_no');

    h.css('background-color', rgba_color);
    h.html("<h3><font color=\"white\">"+header_str+"</font></h3>");
    b.html("<p>"+body_str+"</p>");

    b_yes.unbind("click");
    b_no.unbind("click");

    b_yes.click(function() {  func_yes(); });
    b_no.click(function() { func_no();  });

    $('#stub_asking_modal').modal();
}

function yes_no_asking(header_str, body_str, func_yes, func_no) {
    var h = $('#web_interface_yes_no_modal_header');
    var b = $('#web_interface_yes_no_modal_body');
    var b_yes = $('#web_interface_yes_no_modal_yes_button');
    var b_no = $('#web_interface_yes_no_modal_no_button');

    h.html("<h3><font color=\"white\">"+header_str+"</font></h3>");
    b.html("<p>"+body_str+"</p>");
    $('#web_interface_yes_no_modal').modal('show');

    b_yes.unbind("click");
    b_yes.click(function() {
        func_yes();
        $('#web_interface_yes_no_modal').modal('hide');
    });

    b_no.unbind("click");
    b_no.click(function() {
        func_no();
        $('#web_interface_yes_no_modal').modal('hide');
    });
}

function matching_hub_name(obj) {
    if (web_interface_current_object_type == 'datas')
        return 'database';
    else if (web_interface_current_object_type == 'dataflows')
        return 'dataflow';
    else if (web_interface_current_object_type == 'projects')
        return 'project';
    else {
        console.log('We do not deal with '+obj+' for now');
        not_yet('code 1');
        return '';
    }
}

function recursiveReplace(node, init_text, new_text) {
    if (node.nodeType == 3) { // text node
        node.nodeValue = node.nodeValue.replace(init_text, new_text);
    } else if (node.nodeType == 1) { // element
        $(node).contents().each(function () {
            recursiveReplace(this, init_text, new_text);
        });
    }
}

function current_remote_api_object() {
    var api_objects = sakura.apis.hub.databases;
    if (web_interface_current_object_type == 'dataflows')
        api_objects = sakura.apis.hub.dataflows;
    else if (web_interface_current_object_type == 'operators')
        api_objects = sakura.apis.hub.op_classes;
    else if (web_interface_current_object_type == 'projects')
        api_objects = sakura.apis.hub.projects;
    else if (web_interface_current_object_type == 'pages')
        api_objects = sakura.apis.hub.pages;
    return api_objects[web_interface_current_id]
}

function fill_head() {
    current_remote_api_object().info().then(function(info) {
        web_interface_current_object_info = info;

        //Icon
        $('#web_interface_generic_main_icon').attr("src", "media/"+web_interface_current_object_type+"_icon.svg.png");
        //Name
        $($('#web_interface_generic_main_name')[0]).html('&nbsp;&nbsp;<em>' + info.name + '</em>&nbsp;&nbsp;');

        //Description
        let desc = $($('#web_interface_generic_main_short_desc')[0]);
        let empty_desc = '<font color="grey"><i>No short description for now</i></font>';

        if (info.grant_level == 'own') {
            desc.empty();
            if (!(info.short_desc != undefined && info.short_desc))
                info.short_desc = '';
            else
                info.short_desc = '<font color="grey"><i>'+info.short_desc+'</i></font>';

            var a = $('<a name="short_desc" href="#" data-type="text" data-title="Short discription">'+info.short_desc+'</a>');
            a.editable({emptytext: empty_desc,
                        url: function(params) {
                                web_interface_updating_metadata(a, params);
                            }
                        });
            desc.append(a);
        }
        else {
            if (info.short_desc)
                desc.html('<font color=grey><i>' + info.short_desc + '</i></font>');
            else
                desc.html(empty_desc + '&nbsp;&nbsp;');
        }
    });
}

function fill_metadata() {
    current_remote_api_object().info().then(function(info) {
        web_interface_current_object_info = info;
        //General
        $('#web_interface_'+web_interface_current_object_type+'_metadata1').empty();

        //Owner
        var owner = empty_text;
        if (info.owner && info.owner != 'null')
            owner =  info.owner;

        //Creation date
        var date = empty_text;
        if (info.creation_date)
            date = moment.unix(info.creation_date).local().format('YYYY-MM-DD,  HH:mm');

        //Main Meta
        function add_fields(list, elt) {
            var dl1 = $('<dl>', { class:  "dl-horizontal col-md-6",
                                  style:  "margin-bottom:0px;"});
            list.forEach( function (elt){
                var dt = $('<dt>', {html: '<i>'+elt.label+'</i>'});
                var dd = $('<dd>');
                if (elt.editable && info.grant_level == 'own') {
                    if (!(elt.value != undefined && elt.value))
                        elt.value = '';
                    var a = $('<a name="'+elt.name+'" href="#" data-type="text" data-title="'+elt.label+'">'+elt.value+'</a>');
                    a.editable({url: function(params) {web_interface_updating_metadata(a, params);}});
                    dd.append(a);
                }
                else {
                    if (!(elt.value != undefined && elt.value))
                        elt.value = empty_text;
                    dd.append("<i>"+elt.value+"</i>")
                }
                dl1.append(dt, dd);
            });
            $('#web_interface_'+web_interface_current_object_type+'_metadata1').append(dl1);
        }

        if (web_interface_current_object_type == 'datas') {
            //Should call for datastores list
            sakura.apis.hub.datastores.list().then(function(lds) {
                var dt_store = empty_text;
                lds.forEach( function(ds) {
                    if (ds.datastore_id == info.datastore_id)
                      dt_store = ds.host+'';
                });

                var list = [{name: '', label: "Creation Date", value: date, editable: false},
                            {name: '', label: "Datastore Host", value: dt_store, editable: false},
                            {name: 'agent_type', label: "Agent Type", value: info.agent_type, editable: true},
                            {name: '', label: "Licence", value: info.licence, editable: false},
                            {name: 'topic', label: "Topic", value: info.topic, editable: true},
                            {name: 'data_type', label: "Data Type", value: info.data_type, editable: true}  ];
                add_fields(list);
            });
        }
        else if (web_interface_current_object_type == 'dataflows') {
            var list = [  {name: '', label: "Creation Date", value: date, editable: false},
                          {name: 'topic', label: "Topic", value: info.topic, editable: true} ];
            add_fields(list);
        }

        else if (web_interface_current_object_type == 'projects') {
            var list = [  {name: '', label: "Creation Date", value: date, editable: false},
                          {name: 'topic', label: "Topic", value: info.topic, editable: true} ];
            add_fields(list);
        }

        //Access
        $('#web_interface_'+web_interface_current_object_type+'_metadata2').empty();
        var dl2 = $('<dl>', { class:  "dl-horizontal col-md-6",
                              style:  "margin-bottom:0px;"});
        var dt1 = $('<dt>', { html:  "<i>Access Scope</i>"});
        var dd1 = $('<dd>');
        if (info.grant_level == 'own') {
            dt1.attr('style', "vertical-align: middle; margin-top: 5px;");
            var select = $('<select>', {id:   'web_interface_access_scope_select',
                                        class: 'selectpicker',
                                        onchange: 'web_interface_asking_change_access_scope();'
                                        });

            select.append('<option value="private">private</option>');
            if (web_interface_current_object_type != 'projects')
                select.append('<option value="restricted">restricted</option>');
            select.append('<option value="public">public</option>');
            select.find('option').each( function () {
                if ($(this).val() == info.access_scope)
                    $(this).prop('selected', true);
            });

            dd1.append(select);
            select.selectpicker('refresh');
        }
        else {
            dd1.append(info.access_scope);
        }
        dl2.append(dt1, dd1);

        //Owner
        var owner = '__';
        if (info.owner && info.owner != 'null')
            owner =  info.owner;

        //Grant level
        var grant = "__"
        if (info.grant_level && info.grant_level != 'null')
            grant =  info.grant_level;

        [   {name: "<i>Owner</i>", value: owner},
            {name: "<i>Your Grant Level</i>", value: grant }].forEach( function(elt) {

            var dt = $('<dt>', { html:  elt.name});
            var dd = $('<dd>', { html: elt.value});
            dl2.append(dt, dd);
        });

        if (info.grant_level && info.grant_level == 'own') {
            update_access_exclamation(info);
        }

        $('#web_interface_'+web_interface_current_object_type+'_metadata2').append(dl2);

        //Large Description
        var l_desc = '<span style="color:grey">*No description !';

        if (info.large_desc) {
            l_desc = info.large_desc;
        }
        else {
            if (l_desc, info.grant_level == 'own' || info.grant_level == 'write')
                l_desc += ' Edit one by clicking on the eye';
            l_desc += '*</span>';
        }
        if (web_interface_current_object_type != 'projects')
            web_interface_create_large_description_area(web_interface_current_object_type,
                                                        'web_interface_'+web_interface_current_object_type+'_markdownarea',
                                                        l_desc,
                                                        info.grant_level == 'own' || info.grant_level == 'write');

        function cb() {
            let meta_div = document.getElementById('web_interface_'+web_interface_current_object_type+'_tmp_meta');
            meta_div.style.display = 'inline';

            let curr_div = $($('#web_interface_metadata_modal_body').html());
            curr_div.css('display', 'none');
            $('body').append(curr_div);
            $('#web_interface_metadata_modal_body').empty();
            $('#web_interface_metadata_modal_body').html(meta_div);
            $('#web_interface_metadata_modal').modal('show');
        }

        fill_collaborators_table_body(info, cb);
    });
}

function web_interface_updating_metadata(a, params) {
    var jsn = JSON.parse('{"'+a.get(0).name+'": "'+params.value+'"}');

    current_remote_api_object().update(jsn).then(
        function(result) {
        }).catch(
        function (error) {
            alert(error);
            if (DEBUG) console.log("E1", error);
            else console.log("TTTTT E1", error);
            a.html(empty_text);
        }
    );
}

function open_metadata(type, id, name) {
    if (!type) {
        $('#web_interface_metadata_modal_obj_name').html(web_interface_current_object_info.name);
        $('#web_interface_metadata_modal_obj_icon').attr('src', '/media/'+web_interface_current_object_type+'_icon_inverse.svg.png');
        fill_metadata();
    }
    else{
        web_interface_current_id = id;
        web_interface_current_object_type = type.toLowerCase();
        $('#web_interface_metadata_modal_obj_name').html(name);
        $('#web_interface_metadata_modal_obj_icon').attr('src', '/media/'+web_interface_current_object_type+'_icon_inverse.svg.png');
        fill_metadata();
    }
}

function fill_pages(dir) {
    let ul = $('#web_interface_projects_ul');
    let icon_pap = '<h5 class="glyphicon glyphicon-file" style="margin-left: 2px; margin-right: 2px; margin-top: 0px; margin-bottom: 0px;"></h5>'
    let icon_pen = '<h5 class="glyphicon glyphicon-pencil" style="margin-left: 2px; margin-right: 2px; margin-top: 0px; margin-bottom: 0px;"></h5>'
    let icon_rem = '<h5 class="glyphicon glyphicon-remove" style="margin-left: 2px; margin-right: 2px; margin-top: 0px; margin-bottom: 0px;"></h5>'

    //cleaning pages
    $("[id^='web_interface_projects_li_project_']").each(function(){
        let pname = 'project_'+web_interface_current_id;
        if (this.id.indexOf(pname) == -1)
            this.remove();
    });

    current_remote_api_object().info().then(function(info) {
        if (info.pages) {
            info.pages.forEach( function(page) {
                let active_page = false;
                if (dir.indexOf('Page-') != -1) {
                    let id = dir.split('Page-')[1].split('/')[0];
                    if (id == page.page_id) {
                        active_page = true;
                    }
                }
                else {
                    dir += '/Page-'+page.page_id;
                    active_page = true;
                }

                let page_name = "web_interface_projects_li_project_"+page.project_id+"_page_"+page.page_id;
                let li = $(document.getElementById(page_name));

                if ( ! document.getElementById(page_name)) {
                    li = $('<li>', {'id': page_name});
                    let url = "Projects/"+web_interface_current_id+"/Page-"+page.page_id;
                    let a = $('<a>',  { 'onclick': "showDiv(event, '"+url+"', 'web_interface_projects_main_toFullfill');",
                                        'style': "color: dimgrey; padding: 2px; padding-right: 10px; padding-left: 10px; cursor: pointer;",
                                        'html': icon_pap+'<font size=2>'+page.page_name+'</font>'
                                      });
                    li.append(a);
                    li.insertBefore($('#web_interface_projects_li_add'));
                }

                if (active_page) {
                    current_page = page;
                    li.addClass('active');
                    web_interface_create_large_description_area(web_interface_current_object_type,
                                                                'web_interface_'+web_interface_current_object_type+'_markdownarea',
                                                                page.page_content,
                                                                info.grant_level == 'own' || info.grant_level == 'write');
                  let d_button = $('#web_interface_projects_delete_page_button');
                  d_button.attr('onclick', 'delete_page('+page.page_id+');');
                }
                else {
                    li.removeClass('active');
                }
            });
            document.getElementById('web_interface_projects_tmp_work').style.display = 'inline';

            let rem = document.getElementById('web_interface_projects_delete_page_button');
            if (info.grant_level != 'write' && info.grant_level != 'own')
                rem.style.display = 'none';
            else {
                if (info.pages.length == 1)   rem.style.display = 'none';
                else                          rem.style.display = 'inline';
            }
        }
        else {
            console.log('NO PAGES');
            document.getElementById('web_interface_projects_tmp_no_pages').style.display = 'inline';
        }

        let li_add = document.getElementById('web_interface_projects_li_add');
        if (info.grant_level != 'write' && info.grant_level != 'own')
            li_add.style.display = 'none';
        else
            li_add.style.display = 'inline';
    });
}

function fill_history() {
    not_yet('code 3');
}

function get_edit_toolbar(datatype, web_interface_current_id) {
    tb = [{
                name: "preview",
                action: function () {
                    if (!current_simpleMDE.isPreviewActive()) {
                        web_interface_save_large_description(web_interface_current_id);
                    }
                    current_simpleMDE.togglePreview();
                  },
                className: "fa fa-eye no-disable active",
                title: "Toggle Preview (Cmd-P)",
              },
              "fullscreen","|","bold","italic","heading","|","quote",
              "unordered-list","ordered-list","|","link","image","|",
              "guide", "|",
              {
                name: "save",
                action: function () {
                    web_interface_save_large_description(web_interface_current_id);
                  },
                className: "glyphicon glyphicon-floppy-disk",
                title: "Save description",
              }];
    if (datatype == 'projects') {
        tb.push("|");
        tb.push(  {
                    id: 'toto',
                    name: "addObject",
                    action: project_add_object_in_markdown,
                    className: "glyphicon glyphicon-search",
                    title: "Add a link to a sakura object"
                }
        );
    }

    return tb;
}

function web_interface_create_large_description_area(datatype, area_id, description, toolbar) {
    //Deleting previous simplemde
    let parent = document.getElementById(area_id).parentElement;
    let simpleMdeClasses = ['editor-toolbar', 'CodeMirror', 'editor-preview-side' ,'editor-statusbar'];
    for (let i in simpleMdeClasses) {
        let elementToRemove = parent.querySelector('.' + simpleMdeClasses[i])
        elementToRemove && elementToRemove.remove();
    }

    current_simpleMDE = null;
    current_simpleMDE = new SimpleMDE({   hideIcons: ['side-by-side'],
                                  element: document.getElementById(area_id),
                                  toolbar: toolbar ? get_edit_toolbar(datatype, web_interface_current_id) : false
                                  });
    current_simpleMDE.value(description);
    current_simpleMDE.togglePreview();
}

function web_interface_save_large_description(id) {
    if (web_interface_current_object_type != 'projects')
        current_remote_api_object().update({'large_desc': current_simpleMDE.value()});
    else {
        sakura.apis.hub.pages[current_page.page_id].update({'page_content': current_simpleMDE.value()});
    }
}

function l_html(obj, event, dir) {
    $.getScript("js/"+obj+".js", function(scp, status) {
      $('#main_div').append($('<div>').load("divs/generic/main.html", function () {
        $('#main_div').append($('<div>').load("divs/"+obj+"/index.html", function () {
         $('#main_div').append($('<div>').load("divs/"+obj+"/meta.html", function() {
           $('#main_div').append($('<div>').load("divs/"+obj+"/work.html", function() {
            $('#main_div').append($('<div>').load("divs/"+obj+"/historic.html", function() {
             $('#main_div').append($('<div>').load("divs/create/"+obj+".html", function() {
                if (obj == 'databases')       loaded_datas_files      = 'done';
                else if (obj == 'operators')  loaded_operators_files  = 'done';
                else if (obj == 'dataflows')  loaded_dataflows_files  = 'done';
                else if (obj == 'projects')   loaded_projects_files   = 'done';
                showDiv(event, dir);
    }));}));}));}));}));}));});
}

function files_on_demand(dir, div_id) {
    var ldf = null;
    var d   = null;
    if (dir.startsWith('Datas')) {
        ldf = loaded_datas_files;
        d = 'databases';
        $.getScript("/webcache/cdnjs/PapaParse/4.3.6/papaparse.min.js");
    }
    else if (dir.startsWith('Operators')) {
        ldf = loaded_operators_files;
        d = 'operators';
    }
    else if (dir.startsWith('Dataflows')) {
        ldf = loaded_dataflows_files;
        d = 'dataflows';
        if (div_id) {
            $.getScript("/webcache/cdnjs/ckeditor/4.7.3/ckeditor.js");
        }
    }
    else if (dir.startsWith('Projects')) {
        ldf = loaded_projects_files;
        d = 'projects';
    }
    else if (dir.length && !dir.startsWith('Home'))
        console.log('Unexpected showDiv() on', dir);

    if (ldf && !(ldf == 'done')) {
        if (ldf == 'no') {
            ldf = 'in_progress';
            l_html(d, event, dir, div_id);
            return;
        }
        return;
    }
}

function update_navbar(obj) {

    //cleaning nav bar
    let ids = $("[id^='idNavBar']");
    Object.keys(ids).forEach( function (k) {
        $(ids[k]).removeClass('active');
    });
    $('#idNavBar'+obj).addClass('active');
}

function update_main_div(dir, obj, id) {
    //cleaning current main div
    let mainDivs = document.getElementsByClassName('classMainDiv');
    for (let i=0;i < mainDivs.length;i++) {
        mainDivs[i].style.display='none';
    }

    //filling main div
    if (!id) {
        let div = document.getElementById('web_interface_'+obj+'_div');
        if (div) {
            div.style.display='inline';
            listRequestStub('web_interface_'+obj+'_table_toFullfill', 10, obj);
        }
    }
    else {
        let div_head = document.getElementById('web_interface_generic_tmp_main');
        let div_main = document.getElementById('web_interface_'+obj+'_tmp_work');

        if (div_head) {
            fill_head();
            div_head.style.display='inline';
            if (obj == 'datas') {
                recover_datasets();
                div_main.style.display='inline';
            }
            else if (obj == 'dataflows') {
                open_workflow();
                div_main.style.display='inline';
            }
            else if (obj == 'projects') {
                fill_pages(dir);
            }
        }
    }

    //changing current URL
    var stateObj = { where: dir };
    try {//try catch, car en local, cela soulève une securityError pour des raisons de same origin policy pas gérées de la meme manière  ...
        history.pushState(stateObj, "page", '#'+dir);
    }
    catch (e) { tmp=0; }
}

function update_main_header(dir) {
    function toggle(add_cl, rem_cl) {

        [ [document.getElementById('anim_logo_cell'),   '_logo_cell'  ],
          [document.getElementById('anim_logo'),        '_logo'       ],
          [document.getElementById('anim_head_table'),  '_head_table' ],
          [document.getElementById('anim_desc_cell'),   '_desc_cell'  ],
          [document.getElementById('anim_title_cell'),  '_title_cell' ]].forEach (function (e) {
              e[0].classList.remove('basic'+e[1]);
              e[0].classList.remove(rem_cl+e[1]);
              e[0].classList.add(add_cl+e[1]);
        });
        logo_size = add_cl;
    }

    if (dir == 'Home' && logo_size == 'small') {
        toggle('big', 'small');
    }
    else if (dir != 'Home' && logo_size == 'big') {
        toggle('small', 'big');
    }
}

function showDiv(event, dir) {
    let obj_names = ["Datas", "Dataflows", "Operators", "Projects", "Home"];

    //Deal with unknown adresses -> always back to home
    let obj = false;
    obj_names.forEach( function (n) {
        if (dir.indexOf(n) != -1)
          obj = n;
    });
    if (!obj) {
        dir = "Home";
        obj = "Home";
    }
    else
        web_interface_current_object_type = obj.toLowerCase();

    let tab = dir.split('/');
    if (tab.length > 1)
        web_interface_current_id = tab[1];
    else
        web_interface_current_id = -1

    if (web_interface_current_object_type &&
        web_interface_current_object_type != "Home" &&
        tab.length > 1) {

        current_remote_api_object().info().then( function(o_info) {
            if (o_info.grant_level != 'list') {
                update_main_header(dir);
                files_on_demand(dir, tab[1]);
                update_navbar(obj);
                update_main_div(dir, obj.toLowerCase(), tab[1]);
            }
            else {
                main_alert('Access Issue', 'You cannot access this object!');
                showDiv(event, "Home");
            }
        }).catch( function(error) {
            console.log(error);
            main_alert('Access Issue', error);
            showDiv(event, "Home");
        });
    }
    else {
        update_main_header(dir);
        files_on_demand(dir, tab[1]);
        update_navbar(obj);
        update_main_div(dir, obj.toLowerCase(), tab[1]);
    }

    if (event)  event.preventDefault();
}

//Access Managment
function web_interface_asking_access_open_modal(o_name, o_type, grant, callback) {
    var txt1 = "An email will be sent to the owner of <b>"+o_name+"</b> for asking for a <b>"+grant+"</b> access on this "+o_type;
    txt1 += "Please describe your needs.";

    var txt2 = "Hello,\n\nI am a ...,\n";
    txt2 += "I would like to get "+grant+" access to this "+o_type+" for my ... activity on...\n\n";
    txt2 += "Thank you !";
    h = $('#web_interface_asking_access_modal_header');
    b = $('#web_interface_asking_access_modal_body');
    h.empty();
    b.empty();
    h.append("<h3><font color='white'>Asking Access for </font>"+o_name+" </h3>");
    b.append($('<p>', {html: txt1}));

    var ti = $('<textarea>', {  class: 'form-control',
                                id: 'web_interface_asking_access_textarea',
                                rows: '6',
                                text: txt2});
    b.append(ti);
    $('#web_interface_asking_access_modal_button').unbind();
    $('#web_interface_asking_access_modal_button').click(function () { web_interface_asking_access(grant, callback)});
    $('#web_interface_asking_access_modal').modal('show');
}

function web_interface_asking_access(grant, callback) {
    var txt = $('#web_interface_asking_access_textarea').val();
    current_remote_api_object().grants.request(grant, txt).then(function(result) {
        if (!result) {
            $('#web_interface_asking_access_modal').modal('hide');
            var header = 'Asking for Access';
            var body = '<h4 align="center" style="margin: 5px;"><font color="black"> Email sent !!</font></h4>';
            main_success_alert(header, body, null, 1);
            current_remote_api_object().info().then(function(info) {
                fill_collaborators_table_body(info);
            });
        }
        else {
            console.log("SHIT");
        }
    });
}

// Collaborators Management
function fill_collaborators_table_body(info, cb) {
    var tbody = $('#web_interface_'+web_interface_current_object_type+'_collaborators_table_body');
    tbody.empty();

    function access_button(access) {
        var hobj_type = matching_hub_name(web_interface_current_object_type);
        var a = $('<button>', { html: "Ask for <b>"+access+"</b> access"});
        a.click(function () {
            web_interface_asking_access_open_modal(info.name, hobj_type, access, null);
        });
        a.prop('class', "btn btn-primary btn-xs");
        return a;
    }

    $('#web_interface_'+web_interface_current_object_type+'_collaborators_select_div').hide();
    if (info.access_scope == 'open' || info.access_scope == 'public' || info.grant_level == 'own' || info.grant_level == 'write') {
        for (let user in info.grants) {
            grant = info.grants[user];
            if (grant.level == 'own')
                continue;
            var td2 = $('<td>')
            if (info.grant_level == 'own') {
                if (grant.requested_level) {
                    td2.attr('bgcolor', '#f0ad4e');
                    var b1 = $('<button>', { html: "Accept"});
                    var b2 = $('<button>', { html: "Refuse"});
                    b1.attr('onclick','access_requested('+true+',"'+user+'","'+grant.requested_level+'");');
                    b2.attr('onclick','access_requested('+false+',"'+user+'","'+grant.requested_level+'");');
                    var p = $('<p>', {html: '<font color=white><b>'+grant.requested_level+'</b> level requested'+'</font>',
                                      style: 'margin-bottom: 0px;'});
                    td2.append(p.append(b1, b2));
                }
                else {
                    var sel = $('<select>', { class: "selectpicker"});
                    sel.change( function() {
                        change_collaborator_access(web_interface_current_id, user, $(this));
                    });
                    if (info.access_scope != 'public')
                        sel.append($('<option>', { text: "Read"}));

                    var op2 = $('<option>', { text: "Write"});
                    if (grant.level == 'write')
                        op2.attr("selected","selected");
                    sel.append(op2);
                    td2.append(sel);
                    sel.selectpicker('refresh');
                }
            }

            var td3 = $('<td>');
            if (info.grant_level == 'own')
                td3 = $('<td>', {html: '<span title="delete collaborator from list" class="glyphicon glyphicon-remove" style="cursor: pointer;" onclick="delete_collaborator('+web_interface_current_id+', \''+user+'\');"></span>'});

            var td1 = $('<td>', {html: user});
            if (grant.requested_level)
            {
                td1.attr('bgcolor', '#f0ad4e');
                td3.attr('bgcolor', '#f0ad4e');
            }
            var tr = $('<tr>');
            tr.append(td1, td2, td3);

            tbody.append(tr);
        }

        if (info.grant_level == 'own') {
            sakura.apis.hub.users.list().then(function(result) {
                let div = $('#web_interface_'+web_interface_current_object_type+'_collaborators_select_div');
                div.empty();
                div.html(collab_bloc.replace('obj', web_interface_current_object_type));

                let select = $('#web_interface_'+web_interface_current_object_type+'_adding_collaborators_select');
                select.empty();

                let granted_users = Object.keys(info.grants)
                let potential_collaborators = [];
                result.forEach (function (user){
                    if (granted_users.indexOf(user.login) == -1)
                        potential_collaborators.push(user.login);
                });

                potential_collaborators.forEach( function(login) {
                    select.append($('<option>', {text: login}));
                });

                $('#web_interface_'+web_interface_current_object_type+'_collaborators_select_div').show();
                select.selectpicker('refresh');

                if (cb) {
                  cb();
                }
            });
            return;
        }
    }
    else if (info.grant_level == 'read') {
        var tr = $('<tr>');
        var td = $('<td>');

        if (current_user != null) {
            if (info.grants[current_user.login] && info.grants[current_user.login].requested_level) {
              var access = info.grants[current_user.login].requested_level;
              var a = $('<button>');
              a.html('Pending <b>'+access+'</b> access');
              a.prop('disabled', true);
              a.prop('class', 'btn btn-warning btn-xs');
              td.append(a);
            }
            else {
                td.append(access_button('write'));
            }
        }
        tr.append(td);
        tbody.append(tr);
    }
    else if (info.grant_level == 'list') {
        var tr = $('<tr>');
        var td = $('<td>');
        if (current_user != null) {
            var granted_users = Object.keys(info.grants);
            var uindex = granted_users.indexOf(current_user.login);

            if (info.grants[current_user.login] && info.grants[current_user.login].requested_level) {
              var access = info.grants[current_user.login].requested_level;
              var a = $('<button>');
              a.html('Pending <b>'+access+'</b> access');
              a.prop('disabled', true);
              a.prop('class', 'btn btn-warning btn-xs');
              td.append(a);
            }

            else {
                td.append(access_button('read'), '&nbsp;');
                td.append(access_button('write'));
            }
        }
        else {
            td.append("You have to be logged for asking read or write access");
        }
        tr.append(td);
        tbody.append(tr);
    }
    cb();
}

function update_access_exclamation(info) {
    var header = $('#web_interface_datas_access_header_exclamation');
    header.css('display', 'none');

    for (let user in info.grants) {
        if (info.grants[user].requested_level) {
            header.css('display', 'block');
            break;
        }
    }
}
function access_requested(value, login, level){
    if (value) {
        current_remote_api_object().grants.update(login, level).then( function(result) {
            current_remote_api_object().info().then(function(info) {
                update_access_exclamation(info);
                fill_collaborators_table_body(info);
            });
        });
    }
    else {
        current_remote_api_object().grants.deny(login).then( function(result) {
            current_remote_api_object().info().then(function(info) {
                update_access_exclamation(info);
                fill_collaborators_table_body(info);
            });
        });
    }
}

function change_collaborator_access(id, login, sel) {
    current_remote_api_object().grants.update(login, sel[0].value.toLowerCase());
}

function delete_collaborator(id, login) {
    current_remote_api_object().grants.update(login, 'hide').then(function(result) {
        current_remote_api_object().info().then(function(info) {
            fill_collaborators_table_body(info);
        });
    });
}

function adding_collaborators() {
    var opts  = $('#web_interface_'+web_interface_current_object_type+'_adding_collaborators_select option');
    var nbs   = 0;
    var index = 0;

    opts.map( function (i, opt) {
        if (opt.selected)
          nbs += 1;
    });

    opts.map( function (i, opt) {
        if (opt.selected) {
            index = index+1;
            current_remote_api_object().grants.update(opt.value, 'read').then(function(result) {
                  if (index == nbs) {
                      current_remote_api_object().info().then(function(info) {
                          fill_collaborators_table_body(info);
                      });
                  }
            });
        }
    });
}

function web_interface_access_collapse() {
    var label = $('<label>', {class:    "glyphicon ",
                              href:     "#web_interface_"+web_interface_current_object_type+"_collapse",
                              onclick:  "web_interface_access_collapse();",
                              style:    "cursor: pointer;"});

    label.attr('data-toggle',  'collapse');

    if ($('#web_interface_'+web_interface_current_object_type+'_collapse')[0].className.indexOf('in') != -1)
        label.addClass('glyphicon-chevron-down');
    else
        label.addClass('glyphicon-chevron-up');

    $('#web_interface_'+web_interface_current_object_type+'_collapse_icon_cell').html('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'+label.get(0).outerHTML);
}

function cleaning_collaborators() {
    $('#web_interface_'+web_interface_current_object_type+'_adding_collaborators_select option:selected').prop("selected", false);
    $('#web_interface_'+web_interface_current_object_type+'_adding_collaborators_select').selectpicker('refresh');
}

function web_interface_asking_change_access_scope() {
    var h = $('#web_interface_yes_no_modal_header');
    var b = $('#web_interface_yes_no_modal_body');

    h.css('background-color', 'rgba(91,192,222)');
    h.html("<h3><font color='white'>Changing Access Scope on </font>"+web_interface_current_object_info.name+"</h3");

    b.html("Are you sure you want to change access scope from <b>'"+web_interface_current_object_info.access_scope+"'</b> to <b>'"+$('#web_interface_access_scope_select').val()+"'</b> ?");

    var butt = $('#web_interface_yes_no_modal_yes_button');
    butt.unbind("click");
    butt.click(function() { web_interface_change_access_scope(); });

    $('#web_interface_yes_no_modal').modal('show');
}

function web_interface_change_access_scope() {
    console.log('access_scope', $('#web_interface_access_scope_select').val());
    current_remote_api_object().update({'access_scope': $('#web_interface_access_scope_select').val()}).then(function(result) {
        $('#web_interface_yes_no_modal').modal('hide');
    });
}

function chgShowColumns(event) {
    showDiv(event,window.location.href.split("#")[1]);
    return;
}

function create_warn_icon(obj) {
    var warn_icon = document.createElement("span");
    warn_icon.className ="glyphicon glyphicon-exclamation-sign icon-large";
    warn_icon.innerHTML = '&nbsp;';
    if (obj.disabled_message) {
        warn_icon.title = obj.disabled_message;
        warn_icon.style = 'color:red;';
        return warn_icon;
    }
    else if (obj.warning_message) {
            warn_icon.title = obj.warning_message;
            warn_icon.style = 'color:orange;';
            return warn_icon;
    }
    return null;
}


function searchSubmitControl(event, obj_type) {
    let srch  = $('#web_interface_'+web_interface_current_object_type+'_inputSearch');
    let value = srch.val().replace(/ /g, "'):containsi('")
    let trs   = $('#idTBodyList'+obj_type).children('tr');

    $.extend($.expr[':'], {'containsi': function(elem, i, match, array){
        return (elem.textContent ||
                elem.innerText || '')
                .toLowerCase().indexOf((match[3] || "").toLowerCase()) >= 0;
        }
    });

    for ( let i =0; i< trs.length; i++) {
        
        let found = false;
        $(trs[i]).filter(":containsi('"+value+"')").each(function(e){
            found = true;
        });
        if (found)    $(trs[i]).show();
        else          $(trs[i]).hide();
    }
}
