/// LIG March 2017

////////////GLOBALS
var web_interface_current_id = -1;  //database or dataflow id
var web_interface_current_obj_info = null;
var web_interface_current_object_type = '';
var simplemde  = null;           //large description textarea

////////////FUNCTIONS
function not_yet(s) {
    if (!s) {
        alert('Not implemented yet');
    }
    else {
        alert('Not implemented yet: '+ s);
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

        web_interface_current_obj_info = info;

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

        web_interface_current_obj_info = info;

        //General
        $('#web_interface_'+web_interface_current_object_type+'_metadata1').empty();
        $('#web_interface_'+web_interface_current_object_type+'_metadata1').load('divs/templates/metadata_'+web_interface_current_object_type+'.html', function() {

            //Name
            $($('#web_interface_'+web_interface_current_object_type+'_main_name')[0]).html('&nbsp;&nbsp;<em>' + info.name + '</em>&nbsp;&nbsp;');
            //Description
            if (info.short_desc)
                $($('#web_interface_'+web_interface_current_object_type+'_main_short_desc')[0]).html('<font color=grey>&nbsp;&nbsp;' + info.short_desc + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</font>&nbsp;&nbsp;');
            else
                $($('#web_interface_'+web_interface_current_object_type+'_main_short_desc')[0]).html('<font color=lightgrey>&nbsp;&nbsp; no short description</font>' + '&nbsp;&nbsp;');

            //Owner
            var owner = '_';
            if (info.owner && info.owner != 'null')
                owner =  info.owner;

            //Creation date
            var date = "__";
            if (info.creation_date)
                date = moment.unix(info.creation_date).local().format('YYYY-MM-DD,  HH:mm');

            //All now
            if (web_interface_current_object_type == 'datas') {

                sakura.common.ws_request('list_datastores', [], {}, function(lds) {
                    var dt_store = '__';
                    lds.forEach( function(ds) {
                        if (ds.datastore_id == info.datastore_id)
                          dt_store = ds.host+'';
                    });

                    [   {name: "_db_date_", value: date},
                        {name: "_db_datastore_", value: dt_store},
                        {name: "_db_agent_type_", value: info.agent_type},
                        {name: "_db_licence_", value: info.licence},
                        {name: "_db_topic_", value: info.topic},
                        {name: "_db_data_type_", value: info.data_type}
                        ].forEach( function (elt){
                        if (elt.value != undefined)
                            recursiveReplace($('#web_interface_'+web_interface_current_object_type+'_tmp_meta')[0], elt.name, elt.value);
                        else
                            recursiveReplace($('#web_interface_'+web_interface_current_object_type+'_tmp_meta')[0], elt.name, '__');
                        });
                });
            }

            else if (web_interface_current_object_type == 'dataflows') {
                [     {name: "_db_date_", value: date},
                      {name: "_db_licence_", value: info.licence},
                      {name: "_db_topic_", value: info.topic},
                      ].forEach( function (elt) {
                          if (elt.value != undefined && elt.value)
                              recursiveReplace($('#web_interface_'+web_interface_current_object_type+'_tmp_meta')[0], elt.name, elt.value);
                          else
                              recursiveReplace($('#web_interface_'+web_interface_current_object_type+'_tmp_meta')[0], elt.name, '__');
                          });
            }
        });

        //Access
        $('#web_interface_'+web_interface_current_object_type+'_metadata2').empty();
        $('#web_interface_'+web_interface_current_object_type+'_metadata2').load('divs/templates/metadata_access.html', function() {

            //Owner
            var owner = '..';
            if (info.owner && info.owner != 'null')
                owner =  info.owner;

            [   {name: "_db_access_",         value: info.access_scope},
                {name: "_db_owner_",          value: owner},
                {name: "_db_grant_",          value: info.grant_level},
                ].forEach( function (elt){
                    if (elt.value)
                        recursiveReplace($('#web_interface_'+web_interface_current_object_type+'_tmp_meta')[0], elt.name, elt.value);
                    else
                        recursiveReplace($('#web_interface_'+web_interface_current_object_type+'_tmp_meta')[0], elt.name, '..');
                      });

            fill_collaborators_table_body(info);
        });


        //Large Description
        var l_desc = '<span style="color:grey">*No description !';
        if (info.large_desc)
            l_desc = info.large_desc;
        else {
            if (l_desc, info.grant_level == 'own' || info.grant_level == 'write')
                l_desc += ' Edit one by clicking on the eye';
            l_desc += '*</span>';
        }

        //Large description can only been modified by writers
        web_interface_create_large_description_area(web_interface_current_object_type,
                                                    'web_interface_'+web_interface_current_object_type+'_markdownarea',
                                                    l_desc,
                                                    info.grant_level == 'own' || info.grant_level == 'write');
    });
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

    /*if (idDir.match("Meta") &&  document.getElementById("idSignInWidget").innerText.match("Hello")){ //todo : ameliorer test hello == test droit en edition
        document.getElementById("idEditModeWidget").style.display='';
    }
    else {
        document.getElementById("idEditModeWidget").style.display='none';
    }*/


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
            sakura.common.ws_request('generate_session_secret', [], {}, function(ss) {
                if (aos.id == 'iframe_datasets')
                    aos.src = "/modules/datasets/index.html?database_id="+web_interface_current_id+"&session-secret="+ss;
                else if (aos.id == 'iframe_workflow')
                  aos.src = "/modules/workflow/index.html?dataflow_id="+web_interface_current_id+"&session-secret="+ss;
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

    var txt1 = "You can send an email to the owner of <b>"+o_name+"</b> and then ask for a <b>"+grant+"</b> access on this "+o_type+".</br>";
    txt1 += "Here is a default text that the owner will receive. Feel free to update it before sending.";

    var txt2 = "Dear owner of '"+o_name+"' (on Sakura plateform),\n\n";
    txt2 += "\tPlease, could you give me '"+grant+"' access on your "+o_type+" ?\n\n";
    txt2 += "Thanks in advance,\n";
    txt2 += "Sincerely,\n";
    txt2 += current_login;
    h = $('#web_interface_asking_access_modal_header');
    b = $('#web_interface_asking_access_modal_body');
    h.empty();
    b.empty();
    h.append("<h3><font color='white'>Asking Access for </font>"+o_name+" </h3>");
    b.append($('<p>', {html: txt1}));

    var ti = $('<textarea>', {  class: 'form-control',
                                id: 'web_interface_asking_access_textarea',
                                rows: '7',
                                text: txt2});
    b.append(ti);
    $('#web_interface_asking_access_modal_button').click(function () { web_interface_asking_access(o_type, o_id, grant, callback)});
    $('#web_interface_asking_access_modal').modal('show');
}

function web_interface_asking_access(o_type, o_id, grant, callback) {
    var txt = $('#web_interface_asking_access_textarea').val();
    sakura.common.ws_request('request_'+o_type+'_grant', [o_id, grant, txt], {}, function(result) {
        if (!result) {
            if (callback)
                callback();
            $('#web_interface_asking_access_modal').modal('hide');
        }
        else {
            console.log("SHIT");
        }
    });
}

// Collaborators Management
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
        var a = $('<button>', { text: "Ask for writer access"});

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

function cleaning_collaborators() {
    $('#web_interface_'+web_interface_current_object_type+'_adding_collaborators_select option:selected').prop("selected", false);
    $('#web_interface_'+web_interface_current_object_type+'_adding_collaborators_select').selectpicker('refresh');
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

// RMS: The function below has been moved to signIn.js and the name here is affixed with '_old'
// RMS: Can be removed or commented
function signInSubmitControl_old(event) {
    if ((document.getElementById("signInEmail").value.length>2) && (document.getElementById("signInEmail").value	== document.getElementById("signInPassword").value)) {
        showDiv(event,'HelloYou');
        $("#signInModal").modal("hide");
        document.getElementById("idSignInWidget").innerHTML= '<a onclick="signOutSubmitControl(event);" href="http://sakura.imag.fr/signOut" style="cursor: pointer;"><span class="glyphicon glyphicon-user" aria-hidden="true"></span> Hello you</a>';
        return;
    }
    else {
        alert('not yet, try email=password=guest');
        return;
    }
}

// RMS: The function below has been moved to signIn.js and the name here is affixed with '_old'
// RMS: Can be removed or commented
function signOutSubmitControl_old(event) {
    res=confirm("Sign Out?");
    if (res) {
        document.getElementById("idSignInWidget").innerHTML= '<a class="btn" data-toggle="modal" data-target="#signInModal"><span class="glyphicon glyphicon-user" aria-hidden="true"></span> Sign in</a>';
        showDiv(event,"");
        return;
    }
    else {
        showDiv(event,'HelloYou');
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
