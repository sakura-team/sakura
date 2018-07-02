/// LIG March 2017

////////////GLOBALS
var web_interface_current_id = -1;  //database or dataflow id
var web_interface_current_object_info = null;
var web_interface_current_object_type = '';
var simplemde  = null;           //large description textarea
var empty_text = "__";

////////////FUNCTIONS
function not_yet(s) {
    if (!s) {
        alert('Not implemented yet');
    }
    else {
        alert('Not implemented yet: '+ s);
    }
}

function matching_hub_name(obj) {
    if (web_interface_current_object_type == 'datas')
        return 'database';
    else if (web_interface_current_object_type == 'dataflows')
        return 'dataflow';
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

function fill_work() {
    var req = 'get_database_info';

    if (web_interface_current_object_type == 'dataflows')
        req = 'get_dataflow_info';


    sakura.common.ws_request(req, [web_interface_current_id], {}, function(info) {

        web_interface_current_object_info = info;

        $($('#web_interface_'+web_interface_current_object_type+'_main_name')[0]).html('&nbsp;&nbsp;<em>' + info.name + '</em>&nbsp;&nbsp;');
        if (info.short_desc)
            $($('#web_interface_'+web_interface_current_object_type+'_main_short_desc')[0]).html('<font color=grey>&nbsp;&nbsp;' + info.short_desc + '</font>&nbsp;&nbsp;');
        else
            $($('#web_interface_'+web_interface_current_object_type+'_main_short_desc')[0]).html('<font color=lightgrey>&nbsp;&nbsp; no short description</font>' + '&nbsp;&nbsp;');
    });
}

function fill_metadata() {
    var req = 'get_database_info';

    if (web_interface_current_object_type == 'dataflows')
        req = 'get_dataflow_info';


    sakura.common.ws_request(req, [web_interface_current_id], {}, function(info) {

        web_interface_current_object_info = info;

        //General
        $('#web_interface_'+web_interface_current_object_type+'_metadata1').empty();

        //Name
        $($('#web_interface_'+web_interface_current_object_type+'_main_name')[0]).html('&nbsp;&nbsp;<em>' + info.name + '</em>&nbsp;&nbsp;');

        //Description
        var empty_desc = 'No short description for now';
        if (info.grant_level == 'own') {
            var elt = $($('#web_interface_'+web_interface_current_object_type+'_main_short_desc')[0]);
            elt.empty();
            if (!(info.short_desc != undefined && info.short_desc))
                  info.short_desc = '';
            var a = $('<a name="short_desc" href="#" data-type="text" data-title="Short discription"><font color="grey"><i>'+info.short_desc+'<i></font></a>');
            a.editable({emptytext: empty_desc,
                        url: function(params) {web_interface_updating_metadata(a, params);}});
            elt.append(a);
        }
        else {
            if (info.short_desc)
                $($('#web_interface_'+web_interface_current_object_type+'_main_short_desc')[0]).html('<font color=grey>&nbsp;&nbsp;' + info.short_desc + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</font>&nbsp;&nbsp;');
            else
                $($('#web_interface_'+web_interface_current_object_type+'_main_short_desc')[0]).html('<font color=lightgrey>&nbsp;&nbsp; '+empty_desc+'</font>' + '&nbsp;&nbsp;');
        }

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
                    a.editable({emptytext: empty_text,
                                url: function(params) {web_interface_updating_metadata(a, params);}});
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
            sakura.common.ws_request('list_datastores', [], {}, function(lds) {
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

        $('#web_interface_'+web_interface_current_object_type+'_metadata2').append(dl2);


        //Large Description
        var l_desc = '<span style="color:grey">*No description !';
        if (info.large_desc)
            l_desc = info.large_desc;
        else {
            if (l_desc, info.grant_level == 'own' || info.grant_level == 'write')
                l_desc += ' Edit one by clicking on the eye';
            l_desc += '*</span>';
        }
        fill_collaborators_table_body(info);


        //Large description can only been modified by writers
        web_interface_create_large_description_area(web_interface_current_object_type,
                                                    'web_interface_'+web_interface_current_object_type+'_markdownarea',
                                                    l_desc,
                                                    info.grant_level == 'own' || info.grant_level == 'write');
    });
}

function web_interface_updating_metadata(a, params) {
    var obj = matching_hub_name(web_interface_current_object_type);
    var id = web_interface_current_object_info[obj+'_id'];
    var jsn = JSON.parse('{"'+a.get(0).name+'": "'+params.value+'"}');

    sakura.common.ws_request('update_'+obj+'_info', [id], jsn ,
        function(result) {
        },
        function (error) {
            alert(error);
            a.html(empty_text);
        }
    );
}

function fill_history() {
    not_yet('code 3');
}

function get_edit_toolbar(datatype, web_interface_current_id) {
    return [{
                name: "preview",
                action: function () {
                    if (!simplemde.isPreviewActive()) {
                        web_interface_save_large_description(datatype, web_interface_current_id);
                    }
                    simplemde.togglePreview();
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
                    web_interface_save_large_description(datatype, web_interface_current_id);
                  },
                className: "glyphicon glyphicon-floppy-disk",
                title: "Save description",
              }
            ]
}

function web_interface_create_large_description_area(datatype, area_id, description, toolbar) {

    //Erasing previous one
    if (simplemde)
        simplemde.toTextArea();
        simplemde = null;

    simplemde = new SimpleMDE({   hideIcons: ['side-by-side'],
                                  element: document.getElementById(area_id),
                                  toolbar: toolbar ? get_edit_toolbar(datatype, web_interface_current_id) : false
                                  });
    simplemde.value(description);
    simplemde.togglePreview();
}

function web_interface_save_large_description(data_type, id) {
    var obj = matching_hub_name(data_type);

    if (obj.length != 0)
        sakura.common.ws_request('update_'+obj+'_info', [id], {'large_desc': simplemde.value()}, function(result) {});
}



function showDiv(event, dir, div_id) {

    //set url
    if (event instanceof PopStateEvent) {
        // rien dans l'history
    }
    else {
        var stateObj = { where: dir };
        try {  //try catch, car en local, cela soulève une securityError pour des raisons de same origin policy pas gérées de la meme manière  ...
            history.pushState(stateObj, "page", "#"+dir);
        }
        catch (e) {
            tmp=0;
        }
    }

    //normalize dir
    if ((dir.split("?").length>1) && (dir.split("?")[1].match(/page=(-?\d+)/).length>1))
        document.pageElt = +dir.split("?")[1].match(/page=(-?\d+)/)[1];
    else
        document.pageElt = 1;

    dir = dir.split("?")[0];

    if (dir == "") {
        dir = "Home";
    }
    else if (dir.match("tmp") || isUrlWithId(dir)) {
        if (!(dir.match("Work") || dir.match("Historic") || dir.match("Meta")))  {
            if (dir[dir.length -1] == '/')
                dir = dir + "Meta";
            else
                dir = dir + "/Meta";
        }
    }
    var dirs = dir.split("/");

    //show div
    mainDivs = document.getElementsByClassName('classMainDiv');
    for(i=0;i<mainDivs.length;i++) {
        mainDivs[i].style.display='none';
    }

    var idDir = "web_interface";
    dirs.forEach(function (dir) {
        if (isUrlWithId(dir)) {  //tmpLocDir.match(/[A-Za-z]+-[0-9]+/)
            idDir += '_tmp';//dir.replace(/([A-Za-z]+)-[0-9]+/,"tmp$1");
        }
        else {
            idDir += "_"+dir;
        }
    });
    idDir = idDir.toLowerCase();
    if (dirs.length == 1)
        idDir += "_div";

    document.getElementById(idDir).style.display='inline';


    //activate navbar
    var d = document.getElementById("navbar_ul");
    for (var i=0; i< d.children.length; i++) {
        d.children[i].className = "";
    }
    var navBarElt = document.getElementById("idNavBar"+dirs[0])
    if (navBarElt) {
        navBarElt.className = "active";
    }

    //set breadcrumb
    var bct = "<li><a onclick=\"showDiv(event,'');\" href=\"http://sakura.imag.fr\" title=\"Sakura\">Sakura</a></li>";
    var tmpDir = "";
    for(i=0;i<dirs.length-1;i++) {
        tmpDir = tmpDir + dirs[i] ;
        bct = bct + "<li><a onclick='showDiv(event,\""+tmpDir+"\");' href=\"http://sakura.imag.fr/"+tmpDir+"\" title= \""+tmpDir+"\">"+dirs[i]+"</a></li>";
        tmpDir = tmpDir + "/";
    }

    bct = bct + "<li class='active'>"+dirs[i]+"</li>";
    var d = document.getElementById("breadcrumbtrail");
    d.innerHTML = bct;

    if (window.location.toString().indexOf('tmpData') == -1 && window.location.toString().indexOf('tmpDataflow') == -1) {
        var tab = window.location.toString().split("/");
         if (tab.length == 5) {
            tab = tab[tab.length-1].split("-");
        }
        else {
            tab = tab[tab.length-2].split("-");
        }
        web_interface_current_id = parseInt(tab[tab.length -1]);
    }

    function change_class(elts, acts, _class) {
        elts.forEach( function(elt, i) {
            if (acts[i])
                elt.addClass(_class);
            else
                elt.removeClass(_class);
        });
    }

    ////////////////////////////////////////////////////////////////////////////////
    if (dir != 'Home') {
        var obj_type = '';

        if (dir.indexOf("Datas") != -1)
            web_interface_current_object_type = 'datas';
        else if (dir.indexOf("Dataflows") != -1)
            web_interface_current_object_type = 'dataflows';

        var obj = web_interface_current_object_type;

        var li_main = $($('#web_interface_'+obj+'_buttons_main')[0].parentElement);
        var li_work = $($('#web_interface_'+obj+'_buttons_work')[0].parentElement);
        var li_history = $($('#web_interface_'+obj+'_buttons_history')[0].parentElement);

        document.getElementById('web_interface_'+obj+'_tmp_main').style.display='inline';

        if (div_id == 'web_interface_'+obj+'_main_toFullfill') {
            if (dir.indexOf('Meta') != -1) {
                change_class([li_main, li_work, li_history], [true, false, false], "active");
                fill_metadata();
            }
            else if (dir.indexOf('Work') != -1) {
                change_class([li_main, li_work, li_history], [false, true, false], "active");
            }
            else if (dir.indexOf('Historic') != -1) {
                change_class([li_main, li_work, li_history], [false, false, true], "active");
            }
        }
        else {
            var n1 = 'Datas';
            var n2 = 'Data';
            if (web_interface_current_object_type == 'dataflows') {
                n1 = 'Dataflows';
                n2 = 'Dataflow';
            }
            $('#web_interface_'+obj+'_buttons_main').attr('onclick', "showDiv(event, '"+n1+"/"+n2+"-"+web_interface_current_id+"/', 'web_interface_"+obj+"_main_toFullfill');");
            $('#web_interface_'+obj+'_buttons_work').attr('onclick', "showDiv(event, '"+n1+"/"+n2+"-"+web_interface_current_id+"/Work', 'web_interface_"+obj+"_main_toFullfill');");
            //$('#web_interface_datas_buttons_history').attr('onclick', "showDiv(event, 'Datas/Data-"+web_interface_current_id+"/Historic', 'web_interface_datas_main_toFullfill');");

            if (dir.indexOf("Meta") != -1) {
                change_class([li_main, li_work, li_history], [true, false, false], "active");
                fill_metadata();
            }
            else if (dir.indexOf("Work") != -1) {
                change_class([li_main, li_work, li_history], [false, true, false], "active");
                fill_work();
            }
            else if (dir.indexOf('Historic') != -1) {
                change_class([li_main, li_work, li_history], [false, false, true], "active");
                fill_history();
            }
            else {
                document.getElementById('web_interface_'+obj+'_tmp_main').style.display='none';
            }
        }
    }

    var actionsOnShow = document.getElementById(idDir).getElementsByClassName("executeOnShow");

    for (i = 0; i < actionsOnShow.length; i++)
        if (actionsOnShow[i].nodeName == "IFRAME") {
            var aos = actionsOnShow[i];
            sakura.common.ws_generate_secret(function(ss) {
                let url;
                if (aos.id == 'iframe_datasets')
                    url = "/modules/datasets/index.html?database_id=";
                else if (aos.id == 'iframe_workflow')
                    url = "/modules/workflow/index.html?dataflow_id=";
                url += web_interface_current_id;
                aos.src = sakura.common.ws_url_add_secret(url, ss);
            });
        }
        else
            if (!div_id)
                eval(actionsOnShow[i].href);
    if (event)
        event.preventDefault();
}

//Access Managment
function web_interface_asking_access_open_modal(o_name, o_type, o_id, grant, callback) {

    var txt1 = "An email will be sent to the owner of <b>"+o_name+"</b> for asking for a <b>"+grant+"</b> access on this "+o_type;
    txt1 += "Please describe your needs.";

    var txt2 = "Hello,\n\nI am a ...,\n";
    txt2 += "I would like to be able to "+grant+" to this "+o_type+" for my ... activity on...\n\n";
    txt2 += "Thanks you !";
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
    $('#web_interface_asking_access_modal_button').click(function () { web_interface_asking_access(o_type, o_id, grant, callback)});
    $('#web_interface_asking_access_modal').modal('show');
}

function web_interface_asking_access(o_type, o_id, grant, callback) {

    var txt = $('#web_interface_asking_access_textarea').val();
    sakura.common.ws_request('request_'+o_type+'_grant', [o_id, grant, txt], {}, function(result) {
        if (!result) {
            $('#web_interface_asking_access_modal').modal('hide');

            //displayig success modal during 1 sec
            $('#web_interface_success_modal_body').html('<h4 align="center" style="margin: 5px;"><font color="black"> Email sent !!</font></h4>');
            $('#web_interface_success_modal').modal('show');
            setTimeout( function () {
                $('#web_interface_success_modal').modal('hide');
                if (callback)
                    callback();
            }, 1000, callback);
        }
        else {
            console.log("SHIT");
        }
    });
}

// Collaborators Management

function fill_collaborators_table_body(info) {
    var tbody = $('#web_interface_'+web_interface_current_object_type+'_collaborators_table_body');
    tbody.empty();

    $('#web_interface_'+web_interface_current_object_type+'_collaborators_select_div').hide();
    if (info.access_scope == 'open' || info.access_scope == 'public' || info.grant_level == 'own' || info.grant_level == 'write') {
        for (let user in info.grants) {
            grant = info.grants[user];
            if (grant == 'own')
                continue;
            var td2 = $('<td>')
            if (info.grant_level == 'own') {
                var sel = $('<select>', { class: "selectpicker"});
                sel.change( function() {
                    change_collaborator_access(web_interface_current_id, user, $(this));
                });
                if (info.access_scope != 'public')
                    sel.append($('<option>', { text: "Read"}));

                var op2 = $('<option>', { text: "Write"});
                if (grant == 'write')
                    op2.attr("selected","selected");
                sel.append(op2);
                td2.append(sel);
                sel.selectpicker('refresh');
            }

            var td3 = $('<td>');
            if (info.grant_level == 'own')
                td3 = $('<td>', {html: '<span title="delete collaborator from list" class="glyphicon glyphicon-remove" style="cursor: pointer;" onclick="delete_collaborator('+web_interface_current_id+', \''+user+'\');"></span>'});

            var tr = $('<tr>');
            tr.append($('<td>', {html: user}), td2, td3);
            tbody.append(tr);
        }

        if (info.grant_level == 'own') {
            $('#web_interface_'+web_interface_current_object_type+'_collaborators_select_div').show();
            $('#web_interface_'+web_interface_current_object_type+'_adding_collaborators_select option').remove();

            sakura.common.ws_request('list_all_users', [], {}, function(result) {
                for (let user in info.grants)
                    result.splice(result.indexOf(user), 1);

                result.forEach( function(user) {
                    $('#web_interface_'+web_interface_current_object_type+'_adding_collaborators_select').append($('<option>', {text: user}));
                });
                $('#web_interface_'+web_interface_current_object_type+'_adding_collaborators_select').selectpicker('refresh');
            });
        }
    }
    else if (info.grant_level == 'read') {
        var hobj_type = matching_hub_name(web_interface_current_object_type);
        var tr = $('<tr>');
        var td = $('<td>');
        var a = $('<button>', { html: "Ask for <b>write</b> access"});

        a.click(function () {
            web_interface_asking_access_open_modal(info.name, hobj_type, info[hobj_type+'_id'], 'write', null);
        });

        td.append(a);
        tr.append(td);
        tbody.append(tr);
    }
}

function change_collaborator_access(id, login, sel) {
    var obj = matching_hub_name(web_interface_current_object_type);
    if (obj.length != 0)
        sakura.common.ws_request('update_'+obj+'_grant', [id, login, sel[0].value.toLowerCase()], {}, function(result) {});
}

function delete_collaborator(id, login) {
    var obj = matching_hub_name(web_interface_current_object_type);

    if (obj.length != 0)
        sakura.common.ws_request('update_'+obj+'_grant', [id, login, 'hide'], {}, function(result) {
            sakura.common.ws_request('get_'+obj+'_info', [id], {}, function(info) {
                fill_collaborators_table_body(info);
            });
        });
}

function adding_collaborators() {
    var obj   = matching_hub_name(web_interface_current_object_type);
    if (obj.length == 0)
        return;

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
            sakura.common.ws_request('update_'+obj+'_grant', [web_interface_current_id, opt.value, 'read'], {}, function(result) {
                  if (index == nbs) {
                      sakura.common.ws_request('get_'+obj+'_info', [web_interface_current_id], {}, function(info) {
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

    $('#web_interface_yes_no_modal').modal('show');
}

function web_interface_change_access_scope() {

    //sakura.common.ws_request('update_'+obj+'_info', [id], {'large_desc': simplemde.value()}, function(result) {});
    var obj = matching_hub_name(web_interface_current_object_info);
    var id  = web_interface_current_object_info[obj+'_id'];
    console.log('access_scope', $('#web_interface_access_scope_select').val());
    sakura.common.ws_request('update_'+obj+'_info', [id], {'access_scope': $('#web_interface_access_scope_select').val()}, function(result) {
        $('#web_interface_yes_no_modal').modal('hide');
    });
}

/* Divers */
function isUrlWithId(url) {
    return url.match(/[A-Za-z]+-[0-9]+/);
}


function getIdFromUrl(url) {
    return url.match(/[A-Za-z]+-[0-9]+/)[0].replace(/[A-Za-z]+-([0-9]+)/,"$1");
}


function chgShowColumns(event) {
    showDiv(event,window.location.href.split("#")[1]);
    return;
}


function editModeSubmitControl(event) {
    menuSpans=document.getElementsByClassName('editZoneContextualMenu');
    for(i=0;i<menuSpans.length;i++) {
        menuSpans[i].innerHTML='<a class="editDescriptionField" href="" onclick="editField(this,event);" title="edit"><i class="glyphicon glyphicon-edit"></i></a>';
    }
    document.getElementById("idEditModeWidget").innerHTML= '<a onclick="saveModeSubmitControl(event);"  style="cursor: pointer;">Save</a>';
    plusFieldButtons=document.getElementsByClassName('clPlusFieldButton');
    for(i=0;i<plusFieldButtons.length;i++) {
        plusFieldButtons[i].style.display='';
    }
}


function addFile(fileSystem,event) {
    event.preventDefault();
    fileSystem.parentElement.children[1].children[1].children[fileSystem.parentElement.children[1].children[1].children.length-1].insertAdjacentHTML("afterend",
    '<tr><td><input type="file" /></td>'
    + '<td><input value="description" type="text" size="60"></td>'
    + '<td><a onclick="saveFile(this,event);" class="validateDescriptionFile" title="save"><i class="glyphicon glyphicon-ok"></i></a></td></tr>');
}


function saveFile(fileSystem,event) {
    event.preventDefault();
    if (fileSystem.parentElement.parentElement.children[0].children[0].files.length == 0) {
        alert('select file');
    }
    else {
        fileSystem.parentElement.parentElement.innerHTML = '<tr><td><a onclick="not_yet();">'+fileSystem.parentElement.parentElement.children[0].children[0].files[0].name+'</a></td>'
        + '<td>'+fileSystem.parentElement.parentElement.children[1].children[0].value+'</td></tr>';
    }
}


function editField(field,event) {
    event.preventDefault();
    initFieldValue = field.parentElement.parentElement.childNodes[0].textContent;
    field.parentElement.parentElement.innerHTML="<span class='editZoneContextualMenu'><input value='"+initFieldValue+"' type='text'><a onclick='saveField(this,event);' class='validateDescriptionField' title='save'><i class='glyphicon glyphicon-ok'></i></a>"
    +" <a  onclick='revertField(this,\""+initFieldValue+"\",event);' class='unvalidateDescriptionField' title='cancel'><i class='glyphicon glyphicon-ban-circle'></i></a>"
    +" <a  onclick='deleteField(this,event);' class='unvalidateDescriptionField' title='delete'><i class='glyphicon glyphicon-remove'></i></a></span>";
}


function saveField(field,event) {
    event.preventDefault();
    fieldValue = field.parentElement.childNodes[0].value;
    field.parentElement.parentElement.innerHTML=fieldValue+ '<span class="editZoneContextualMenu"><a class="editDescriptionField" href="" onclick="editField(this,event);"><i class="glyphicon glyphicon-edit"></i></a></span>';
}


function revertField(field,fieldValue,event) {
    event.preventDefault();
    field.parentElement.parentElement.innerHTML=fieldValue+ '<span class="editZoneContextualMenu"><a class="editDescriptionField" href="" onclick="editField(this,event);"><i class="glyphicon glyphicon-edit"></i></a></span>';
}


function deleteField(field,event) {
    event.preventDefault();
    res=confirm("Delete Field?");
    if (res) {
        field.parentElement.parentElement.previousSibling.remove();
        field.parentElement.parentElement.remove();
    }
}


function addField(field,event) {
    res=prompt("Name for your field","Field Name");
    if ((res!="")&&(res!=null)) {
        field.parentElement.children[field.parentElement.children.length-2].insertAdjacentHTML("afterend","<dt class='description-terms-align-left'>"+res+"</dt><dd class='editableDescriptionField'>value?<span class='editZoneContextualMenu'><a class='editDescriptionField' href='' onclick='editField(this,event);'><i class='glyphicon glyphicon-edit'></i></a></span></dd>");
        return;
    }
}


function addComment(field,event,idComment) {
    var comment = document.getElementById(idComment).value;
    document.getElementById(idComment).value = "Your comments";
    document.getElementById("commentDataflow").parentElement.parentElement.nextSibling.nextSibling.firstChild.insertAdjacentHTML("beforebegin",
                '<li><div class="commenterImage"><span class="glyphicon glyphicon-user"></span></div>'
                + '<div class="commentText"><p class="">'+comment+'</p> '
                + '<span class="date sub-text">you just now</span></div></li>');
    return;
}


function saveModeSubmitControl(event) {
    sav=confirm("Save modification (or abort)?");
    if (sav) {
        //alert("Save")
    }
    else {
        alert("Abort (not yet impemented)");
    }

    menuSpans=document.getElementsByClassName('editZoneContextualMenu');
    for(i=0;i<menuSpans.length;i++) {
        menuSpans[i].innerHTML='';
    }
    document.getElementById("idEditModeWidget").innerHTML= '<a onclick="editModeSubmitControl(event);"  style="cursor: pointer;">Edit Mode</a>';
    plusFieldButtons=document.getElementsByClassName('clPlusFieldButton');
    for(i=0;i<plusFieldButtons.length;i++) {
        plusFieldButtons[i].style.display='none';
    }
}


function searchSubmitControl(event,elt) {
    listeInit = document.getElementById("idTBodyList"+elt).innerHTML.replace(/ style="display:none;"/g,"").replace(/ style='display:none;'/g,"");
    listeInit = listeInit.split("<tr");
    searchString = document.getElementById("idInputSearch"+elt).value;
    s="";
    for(i=1;i<listeInit.length;i++) {
        if (listeInit[i].match(searchString)) {
            s =  s + "<tr"+listeInit[i];
        }
        else {
            s = s + "<tr style='display:none;'"+listeInit[i];
        }
    }
    document.getElementById("idTBodyList"+elt).innerHTML = s;
}


function showDivCGU(event) {
    var d = document.getElementById('idDivCGU');
    console.log("RMS: In SHOWDIVCGU,doc",d);
    $("#signInModal").modal("hide");
    event.preventDefault();
    console.log("windowL:",window.location);
    showDiv(event,"CGU");
//    return; //dismisses the modal box, of course !
}
