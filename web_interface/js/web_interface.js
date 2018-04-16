/// LIG March 2017

////////////GLOBALS
var web_interface_current_id = -1; //database_id


////////////FUNCTIONS
function not_yet(s = '') {
    if (s == '') {
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


function fill_database_metadata(db_id) {
    sakura.common.ws_request('get_database_info', [db_id], {}, function(db_info) {
        console.log(db_info);
        $('#web_interface_database_metadata').empty();
        $('#web_interface_database_metadata').load('divs/templates/datas_metadata.html', function() {

            //Name
            $($('#databases_db_main_name')[0]).html('&nbsp;&nbsp;<em>' + db_info.name + '</em>&nbsp;&nbsp;');

            //Description
            if (db_info.short_desc)
                $($('#databases_db_main_short_desc')[0]).html('<font color=grey>&nbsp;&nbsp;' + db_info.short_desc + '</font>&nbsp;&nbsp;');
            else
                $($('#databases_db_main_short_desc')[0]).html('<font color=lightgrey>&nbsp;&nbsp; no short description</font>' + '&nbsp;&nbsp;');

            ///////MetaData
            //Datastore Host
            sakura.common.ws_request('list_datastores', [], {}, function(lds) {
                lds.forEach( function(ds) {
                    if (ds.datastore_id == db_info.datastore_id)
                    recursiveReplace($('#idDivDatastmpDataMeta')[0], "_db_datastore_", ds.host);
                });
            });

            //Owner
            if (db_info.owner && db_info.owner != 'null')
                recursiveReplace($('#idDivDatastmpDataMeta')[0], "_db_owner_", db_info.owner);
            else
                recursiveReplace($('#idDivDatastmpDataMeta')[0], "_db_owner_", '..');

            //Rights
            if (db_info.rights)
                recursiveReplace($('#idDivDatastmpDataMeta')[0], "_db_rights_", db_info.rights);
            else
                recursiveReplace($('#idDivDatastmpDataMeta')[0], "_db_rights_", '..');

            //Creation date
            if (db_info.creation_date) {
                var date = moment.unix(db_info.creation_date).local().format('YYYY-MM-DD,  HH:mm');
                recursiveReplace($('#idDivDatastmpDataMeta')[0], "_db_date_", date);
            }
            else
                recursiveReplace($('#idDivDatastmpDataMeta')[0], "_db_date_", '..');

            //Agent Type
            if (db_info.agent_type)
                recursiveReplace($('#idDivDatastmpDataMeta')[0], "_db_agent_type_", db_info.agent_type);
            else
                recursiveReplace($('#idDivDatastmpDataMeta')[0], "_db_agent_type_", '..');

            //Agent Type
            if (db_info.licence)
                recursiveReplace($('#idDivDatastmpDataMeta')[0], "_db_licence_", db_info.licence);
            else
                recursiveReplace($('#idDivDatastmpDataMeta')[0], "_db_licence_", '..');

            //Domain Topic
            if (db_info.topic)
                recursiveReplace($('#idDivDatastmpDataMeta')[0], "_db_topic_", db_info.topic);
            else
                recursiveReplace($('#idDivDatastmpDataMeta')[0], "_db_topic_", '..');

            //Data Type
            if (db_info.data_type)
                recursiveReplace($('#idDivDatastmpDataMeta')[0], "_db_data_type_", db_info.data_type);
            else
                recursiveReplace($('#idDivDatastmpDataMeta')[0], "_db_data_type_", '..');
        });
    });
}


function fill_dataflow_metadata(ana_id) {
    sakura.common.ws_request('get_dataflow_info', [ana_id], {}, function(ana_info) {
        //Name
        $($('#Dataflow_main_name')[0]).html('&nbsp;&nbsp;<em>' + ana_info.name + '</em>&nbsp;&nbsp;');

        //Description
        if (ana_info.short_desc)
            $($('#Dataflow_main_short_desc')[0]).html('<font color=grey>&nbsp;&nbsp;' + ana_info.short_desc + '</font>&nbsp;&nbsp;');
        else
            $($('#Dataflow_main_short_desc')[0]).html('<font color=lightgrey>&nbsp;&nbsp; no short description</font>' + '&nbsp;&nbsp;');
    });
}


function showDiv(event, dir, div_id) {

    //todo : déplacer les event.preventDefault() ici ?
    //save mode ?

    //Commented for know, just for clarifying the code and avoiding bag behaviors
    /*
    if (document.getElementById("idEditModeWidget").innerText.match("Save")) {
        res=confirm("Leave edit mode?");
        if (res) {
            document.getElementById("idEditModeWidget").innerHTML= '<a onclick="editModeSubmitControl(event);"  style="cursor: pointer;">Edit Mode</a>';
            plusFieldButtons=document.getElementsByClassName('clPlusFieldButton');

            for(i=0;i<plusFieldButtons.length;i++) {
                plusFieldButtons[i].style.display='none';
            }

            sav=confirm("Save modification (or abort)?");
            if (sav) {
                //alert("Save");
            }
            else {
                alert("Abort  (not yet impemented)");
            }
        }
        else {
            event.preventDefault();
            return;
        }
    }*/

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
    if ((dir.split("?").length>1) && (dir.split("?")[1].match(/page=(-?\d+)/).length>1)) {
        document.pageElt = +dir.split("?")[1].match(/page=(-?\d+)/)[1];
    }
    else {
        document.pageElt = 1;
    }

    dir = dir.split("?")[0];

    if (dir=="") {
        dir="Home";
    }
    else if (dir.match("tmp") || isUrlWithId(dir)) {
        if (!(dir.match("Work") || dir.match("Historic") || dir.match("Main")))  {
            if (dir[dir.length -1] == '/')
                dir = dir + "Main";
            else
                dir = dir + "/Main";
        }
    }
    var dirs = dir.split("/");

    //show div
    mainDivs = document.getElementsByClassName('classMainDiv');
    for(i=0;i<mainDivs.length;i++) {
        mainDivs[i].style.display='none';
    }

    var idDir = "idDiv";
    dirs.forEach(function (tmpLocDir) {
        if (isUrlWithId(tmpLocDir)) {  //tmpLocDir.match(/[A-Za-z]+-[0-9]+/)
            idDir += tmpLocDir.replace(/([A-Za-z]+)-[0-9]+/,"tmp$1");
        }
        else {
            idDir += tmpLocDir;
        }
    });



    if (idDir.match("Main") &&  document.getElementById("idSignInWidget").innerText.match("Hello")){ //todo : ameliorer test hello == test droit en edition
        document.getElementById("idEditModeWidget").style.display='';
    }
    else {
        document.getElementById("idEditModeWidget").style.display='none';
    }

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
        console.log("-- web_interface_current_id", web_interface_current_id);
    }

    ////////////////////////////////////////////////////////////////////////////////
    //DATA
    if (div_id == 'idDatasMainToFullfill') {
        document.getElementById('idDivDatastmpDataMain').style.display='inline';
        if (dir.indexOf('Main') != -1) {
            console.log("META");
            $('#databases_buttons_main').addClass("btn-primary");
            $('#databases_buttons_work').removeClass("btn-primary");
            $('#databases_buttons_historic').removeClass("btn-primary");

            fill_database_metadata(web_interface_current_id);

            document.getElementById('idDivDatastmpDataMeta').style.display='inline';
        }
        else if (dir.indexOf('Work') != -1) {
            console.log("WORK");
            $('#databases_buttons_main').removeClass("btn-primary");
            $('#databases_buttons_work').addClass("btn-primary");
            $('#databases_buttons_historic').removeClass("btn-primary");
        }
        else if (dir.indexOf('Historic') != -1) {
            console.log("HISTORY");
            $('#databases_buttons_main').removeClass("btn-primary");
            $('#databases_buttons_work').removeClass("btn-primary");
            $('#databases_buttons_historic').addClass("btn-primary");
        }
    }
    else if (dir.indexOf("Data") != -1 && dir != 'Datas' && dir.indexOf("Main") != -1) {

        document.getElementById('idDivDatastmpDataMeta').style.display='inline';
        $('#databases_buttons_main').addClass("btn-primary");
        $('#databases_buttons_work').removeClass("btn-primary");
        $('#databases_buttons_historic').removeClass("btn-primary");

        $('#databases_buttons_main').attr('onclick', "showDiv(event, 'Datas/Data-"+web_interface_current_id+"/', 'idDatasMainToFullfill');");
        $('#databases_buttons_work').attr('onclick', "showDiv(event, 'Datas/Data-"+web_interface_current_id+"/Work', 'idDatasMainToFullfill');");
        $('#databases_buttons_historic').attr('onclick', "showDiv(event, 'Datas/Data-"+web_interface_current_id+"/Historic', 'idDatasMainToFullfill');");

        fill_database_metadata(web_interface_current_id);
    }
    else if (dir.indexOf("Work") != -1 && dir != 'Datas' && dir.indexOf("Datas") != -1) {

        document.getElementById('idDivDatastmpDataMain').style.display='inline';
        $('#databases_buttons_main').removeClass("btn-primary");
        $('#databases_buttons_work').addClass("btn-primary");
        $('#databases_buttons_historic').removeClass("btn-primary");

        $('#databases_buttons_main').attr('onclick', "showDiv(event, 'Datas/Data-"+web_interface_current_id+"/', 'idDatasMainToFullfill');");
        $('#databases_buttons_work').attr('onclick', "showDiv(event, 'Datas/Data-"+web_interface_current_id+"/Work', 'idDatasMainToFullfill');");
        $('#databases_buttons_historic').attr('onclick', "showDiv(event, 'Datas/Data-"+web_interface_current_id+"/Historic', 'idDatasMainToFullfill');");

        sakura.common.ws_request('get_database_info', [web_interface_current_id], {}, function(db_info) {
            $($('#databases_db_main_name')[0]).html('&nbsp;&nbsp;<em>' + db_info.name + '</em>&nbsp;&nbsp;');
            if (db_info.short_desc)
                $($('#databases_db_main_short_desc')[0]).html('<font color=grey>&nbsp;&nbsp;' + db_info.short_desc + '</font>&nbsp;&nbsp;');
            else
                $($('#databases_db_main_short_desc')[0]).html('<font color=lightgrey>&nbsp;&nbsp; no short description</font>' + '&nbsp;&nbsp;');
        });
    }

    ////////////////////////////////////////////////////////////////////////////////
    //Dataflow
    console.log(div_id, dir);
    if (div_id == 'idDataflowMainToFullfill') {
      console.log("HERE");
      document.getElementById('idDivDataflowstmpDataflowMain').style.display='inline';
        if (dir.indexOf('Main') != -1) {
            console.log("META");
            $('#Dataflow_buttons_main').addClass("btn-primary");
            $('#Dataflow_buttons_work').removeClass("btn-primary");
            $('#Dataflow_buttons_historic').removeClass("btn-primary");

            document.getElementById('idDivDataflowstmpDataflowMeta').style.display='inline';
        }
        else if (dir.indexOf('Work') != -1) {
            console.log("WORK");
            $('#Dataflow_buttons_main').removeClass("btn-primary");
            $('#Dataflow_buttons_work').addClass("btn-primary");
            $('#Dataflow_buttons_historic').removeClass("btn-primary");
        }
        else if (dir.indexOf('Historic') != -1) {
            console.log("HISTORY");
            $('#Dataflow_buttons_main').removeClass("btn-primary");
            $('#Dataflow_buttons_work').removeClass("btn-primary");
            $('#Dataflow_buttons_historic').addClass("btn-primary");
        }

        fill_dataflow_metadata(0);
    }
    else if (dir.indexOf("Dataflow") != -1 && dir != 'Dataflows' && dir.indexOf("Main") != -1) {

        document.getElementById('idDivDataflowstmpDataflowMeta').style.display='inline';
        $('#Dataflow_buttons_main').addClass("btn-primary");
        $('#Dataflow_buttons_work').removeClass("btn-primary");
        $('#Dataflow_buttons_historic').removeClass("btn-primary");

        $('#Dataflow_buttons_main').attr('onclick', "showDiv(event, 'Dataflows/Dataflow-"+web_interface_current_id+"/', 'idDataflowMainToFullfill');");
        $('#Dataflow_buttons_work').attr('onclick', "showDiv(event, 'Dataflows/Dataflow-"+web_interface_current_id+"/Work', 'idDataflowMainToFullfill');");
        $('#Dataflow_buttons_historic').attr('onclick', "showDiv(event, 'Dataflows/Dataflow-"+web_interface_current_id+"/Historic', 'idDataflowMainToFullfill');");

        $('#web_interface_Dataflow_metadata').empty();
        $('#web_interface_Dataflow_metadata').load('divs/templates/Dataflow_metadata.html');

        fill_dataflow_metadata(0);
    }
    else if (dir.indexOf("Work") != -1 && dir != 'Dataflows' && dir.indexOf("Dataflows") != -1) {

        document.getElementById('idDivDataflowstmpDataflowMain').style.display='inline';
        $('#Dataflow_buttons_main').removeClass("btn-primary");
        $('#Dataflow_buttons_work').addClass("btn-primary");
        $('#Dataflow_buttons_historic').removeClass("btn-primary");

        $('#Dataflow_buttons_main').attr('onclick', "showDiv(event, 'Dataflows/Dataflow-"+web_interface_current_id+"/', 'idDataflowMainToFullfill');");
        $('#Dataflow_buttons_work').attr('onclick', "showDiv(event, 'Dataflows/Dataflow-"+web_interface_current_id+"/Work', 'idDataflowMainToFullfill');");
        $('#Dataflow_buttons_historic').attr('onclick', "showDiv(event, 'Dataflow/Dataflow-"+web_interface_current_id+"/Historic', 'idDataflowMainToFullfill');");

        sakura.common.ws_request('get_dataflow_info', [0], {}, function(info) {
            $($('#Dataflow_main_name')[0]).html('&nbsp;&nbsp;<em>' + info.name + '</em>&nbsp;&nbsp;');
            if (info.short_desc)
                $($('#Dataflow_main_short_desc')[0]).html('<font color=grey>&nbsp;&nbsp;' + info.short_desc + '</font>&nbsp;&nbsp;');
            else
                $($('#Dataflow_main_short_desc')[0]).html('<font color=lightgrey>&nbsp;&nbsp; no short description</font>' + '&nbsp;&nbsp;');
        });
    }

    var actionsOnShow = document.getElementById(idDir).getElementsByClassName("executeOnShow");

    for(i=0;i<actionsOnShow.length;i++) {
        if (actionsOnShow[i].nodeName == "IFRAME") {
            var aos = actionsOnShow[i];
            console.log(aos);
            sakura.common.ws_request('generate_session_secret', [], {}, function(ss) {
                if (aos.id == 'iframe_datasets') {
                    //idElt = getIdFromUrl(window.location.toString());
                    console.log("HERE_228");
                    aos.src = "/modules/datasets/index.html?database_id="+web_interface_current_id+"&session-secret="+ss;
                }
                else if (aos.id == 'iframe_workflow') {
                  console.log("HERE_220");
                  aos.src = "/modules/workflow/index.html?session-secret="+ss;
                }
            });
        }
        else {
            if (!div_id) {
                eval(actionsOnShow[i].href);
            }
        }
    }

    if (event)
        event.preventDefault();
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
