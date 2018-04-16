/// LIG Sept 2017


function buildListStub(idDiv,result,elt) {

    var eltAncetre=elt.split("/")[0];

    //Head of the list, according to the selected columns
    var thead = $('#'+idDiv).find('thead');
    var tbody = $('#'+idDiv).find('tbody');
    thead.empty();
    tbody.empty();
    var new_row_head = $(thead[0].insertRow());
    var list_cols_gui = ['Tags', 'Id', 'ShortDesc', 'Date', 'Modification', 'Owner'];
    var list_cols_hub = ['tags', 'id', 'shortDesc', 'date', 'modification', 'owner'];

    new_row_head.append('<th>Name</th>');
    list_cols_gui.forEach( function (lelt) {
    if (document.getElementById("cbColSelect"+lelt).checked)
        new_row_head.append('<th>'+lelt+'</th>');
    });

    //Last col for the wrench
    var last_cell = new_row_head[0].cells[new_row_head[0].cells.length-1];
    var cell = $('<th>', { style: "width:26px; padding:0px; overflow:hidden"});
    cell.append('<a class="btn" style="padding:6px;" data-toggle="modal" data-target="#colSelectModal">'
        + '<span class="glyphicon glyphicon-wrench" aria-hidden="true"></span></a>'
        + '<a href="javascript:listRequestStub(\''+idDiv+'\',10,\''+elt+'\',false)" class="executeOnShow"> </a>');
    new_row_head.append(cell);

    //Body of the list
    result.forEach( function (row) {

        var new_row = $(tbody[0].insertRow());
        var tmp_elt=elt.replace(/tmp(.*)/,"$1-"+row.id);
        //adding link
        var cell = $('<td>');
        if (row.name.indexOf('OFFLINE') === -1)
            cell.append($('<a>',{   text: row.name,
                                    href: 'http://sakura.imag.fr/'+tmp_elt+'/'+row.id,
                                    onclick: 'web_interface_current_db_id = '+row.id+'; showDiv(event, "'+tmp_elt+'","' +row.id+'");'
                                })
                        );
        else
            cell.append(row.name);

        new_row.append(cell);

        list_cols_gui.forEach( function (lelt, index) {
            if (document.getElementById("cbColSelect"+lelt).checked) {
                if (lelt == 'Date' && row[list_cols_hub[index]] instanceof Date) {
                    var d = row[list_cols_hub[index]].toDateString();
                    var h = row[list_cols_hub[index]].toLocaleTimeString();
                    new_row.append('<td>'+d+'</td>');
                }
                else {
                    new_row.append('<td>'+row[list_cols_hub[index]]+'</td>');
                }
            }
        });
        var last_cell = new_row[0].cells[new_row[0].cells.length-1];
        last_cell.colSpan = 2;
    });
    tbody[0].id = 'idTBodyList'+eltAncetre;

}


function databases_sort(a, b) {
    return a.name > b.name ? 1 : -1;
}


function listRequestStub(idDiv, n, elt, bd) {

    //Here we deal with the databases
    if (elt == 'Datas/tmpData') {
        sakura.common.ws_request('list_databases', [], {}, function (databases) {
            var result = new Array();
            databases.sort(databases_sort);
            var index = 0;
            n = databases.length;

            databases.forEach( function(db) {
                result_info = {'name': db.name,'id':db.database_id, 'isGreyedOut': !db.online,
                                       'shortDesc': db.short_desc, 'date': moment.unix(db.creation_date)._d,
                                       'tags': db.tags };
                if (db.online) {
                    result_info['owner'] = db.owner;
                }
                else {
                    result_info['name'] += ' (OFFLINE)';
                }
                result.push(result_info);
                if (result.length == n) {
                    result.sort(databases_sort);
                    buildListStub(idDiv,result,elt);
                }
            });
        });
    }
    else if (elt == 'Operators/tmpOperator') {
        sakura.common.ws_request('list_operators_classes', [], {}, function (operators) {
            var result = new Array();
            operators.forEach( function(op) {
                result_info = { 'name': op.name,
                                'shortDesc': op.short_desc,
                                'tags': op.tags,
                                'id': op.id,
                                'daemon': op.daemon,
                                'svg': op.svg,
                                'date': op.date,
                                'owner': op.owner,
                                'modif': op.modification_date};

                //Display of undefined fields
                Object.keys(result_info).forEach( function(key) {
                    if (!result_info[key]) {
                        result_info[key] = "__";
                    }
                });
                result.push(result_info);
            });
            buildListStub(idDiv,result,elt);
        });
    }
    else {
        result=listStubAlea(n); // tableau de {"name":_,"id":_,"tags":_,"shortDesc":_,"date":_,"modif":_,"owner":_,"isViewable":_,"isEditable":_} détail : {"name":fullNameAlea(), "id":numAlea(100,100),"tags":aleaAlea(firstNamesAlea),"shortDesc":shortTextAlea(),"date":dateAlea(),"modif":dateAlea(),"owner":aleaAlea(usersAlea),"isViewable":boolAlea(0.7),"isEditable":boolAlea(0.3)}
        buildListStub(idDiv,result,elt);
    }
    return ;
}


function listRequestStubForRestart(idDiv) {
    //TODO : supprimer/deplacer alea
    result=new Array();
    s="";
    i=0;
    result.push({"name":fullNameAlea(),"shortDesc":shortTextAlea(),"isViewable":"true","isEditable":"true"});
    elt='Projects/tmpProject';
    s = s + "<tr><td><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\">"+result[i].name
        + "</a>&nbsp;&nbsp;<img  width='40px' height='40px' src='media/Simpleicons_Business_notebook.svg.png' alt='CC-BY-3.0 Wikipedia Gears'></img></td>\n"
        + "<td>"+result[i].shortDesc+"</td>"
        + "<td align='center'><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span></a>"
        + "  <a onclick=\"showDiv(event,'"+elt+"/Work');\" href=\"http://sakura.imag.fr/"+elt+"/Work\" class='btn btn-default'><span class='glyphicon glyphicon-pencil' aria-hidden='true'></span></a>"
        + "  <a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><img src='media/IconFinder_298785_fork.png'></img></a>"
        + "</td></tr>";
    i=i+1;
    result.push({"name":fullNameAlea(),"shortDesc":shortTextAlea(),"isViewable":"true","isEditable":"true"});
    elt='Datas/tmpData';
    s = s + "<tr><td><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\">"+result[i].name
        + "</a>&nbsp;&nbsp;<img  width='40px' height='40px' src='media/Linecons_database.svg.png' alt='CC-BY-3.0 Wikipedia Gears'></img></td>\n"
        + "<td>"+result[i].shortDesc+"</td>"
        + "<td align='center'><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span></a>"
        + "  <a onclick=\"showDiv(event,'"+elt+"/Work');\" href=\"http://sakura.imag.fr/"+elt+"/Work\" class='btn btn-default'><span class='glyphicon glyphicon-pencil' aria-hidden='true'></span></a>"
        + "  <a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><img src='media/IconFinder_298785_fork.png'></img></a>"
        + "</td></tr>";
    i=i+1;
    result.push({"name":fullNameAlea(),"shortDesc":shortTextAlea(),"isViewable":"true","isEditable":"true"});
    elt='Operators/tmpOperator';
    s = s + "<tr><td><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\">"+result[i].name
        + "</a>&nbsp;&nbsp;<img  width='40px' height='40px' src='media/Octicons-gear.svg.png' alt='CC-BY-3.0 Wikipedia Gears'></img></td>\n"
        + "<td>"+result[i].shortDesc+"</td>"
        + "<td align='center'><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span></a>"
        + "  <a onclick=\"showDiv(event,'"+elt+"/Work');\" href=\"http://sakura.imag.fr/"+elt+"/Work\" class='btn btn-default'><span class='glyphicon glyphicon-pencil' aria-hidden='true'></span></a>"
        + "  <a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><img src='media/IconFinder_298785_fork.png'></img></a>"
        + "</td></tr>";
    i=i+1;
    result.push({"name":fullNameAlea(),"shortDesc":shortTextAlea(),"isViewable":"true","isEditable":"true"});
    elt='Dataflows/tmpDataflow';
    s = s + "<tr><td><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\">"+result[i].name
        + "</a>&nbsp;&nbsp;<img  width='40px' height='40px' src='media/Share_icon_BLACK-01.svg.png' alt='CC-BY-3.0 Wikipedia Gears'></img></td>\n"
        + "<td>"+result[i].shortDesc+"</td>"
        + "<td align='center'><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span></a>"
        + "  <a onclick=\"showDiv(event,'"+elt+"/Work');\" href=\"http://sakura.imag.fr/"+elt+"/Work\" class='btn btn-default'><span class='glyphicon glyphicon-pencil' aria-hidden='true'></span></a>"
        + "  <a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><img src='media/IconFinder_298785_fork.png'></img></a>"
        + "</td></tr>";
    i=i+1;
    result.push({"name":fullNameAlea(),"shortDesc":shortTextAlea(),"isViewable":"true","isEditable":"true"});
    elt='Results/tmpResult';
    s = s + "<tr><td><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\">"+result[i].name
        + "</a>&nbsp;&nbsp;<img  width='40px' height='40px' src='media/Article_icon_cropped.svg.png' alt='CC-BY-3.0 Wikipedia Gears'></img></td>\n"
        + "<td>"+result[i].shortDesc+"</td>"
        + "<td align='center'><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span></a>"
        + "  <a onclick=\"showDiv(event,'"+elt+"/Work');\" href=\"http://sakura.imag.fr/"+elt+"/Work\" class='btn btn-default'><span class='glyphicon glyphicon-pencil' aria-hidden='true'></span></a>"
        + "  <a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><img src='media/IconFinder_298785_fork.png'></img></a>"
        + "</td></tr>";
    s = s + '<a href="javascript:listRequestStubForRestart(\''+idDiv+'\')" class="executeOnShow"> </a></div>';
    document.getElementById(idDiv).innerHTML = s;

    return ;
}


function buildHistoryStub(idDiv,result,elt) {
    s="";
    for(i=0;i<result.length;i++) {
        s = s + "<li>On "+result[i].dateVersion+" (<a onclick='javascript:not_yet();'>view</a> / <a onclick='javascript:not_yet();'>revert</a>)<p> Revision message from "+result[i].userName+" : "+result[i].msgVersion+"</li>";
    }
    document.getElementById(idDiv).innerHTML = s;
}


function historyRequestStub(idDiv,n,elt,bd) {
    if (!bd) {  // version local
        result=historyStubAlea(n);
        buildHistoryStub(idDiv,result,elt);}
    else {     // version réseau à faire
        sakura.common.ws_request('list_nObjets', [10,'etude_'], {}, function (idDiv,result) {buildHistoryStub(idDiv,result,elt);});}
    return ;}


function buildEltStub(idDiv,result,elt) {
    var s = "";
    if (elt=="Project") {
        imageElt = "Simpleicons_Business_notebook.svg.png";
        imageEltInverse = "Simpleicons_Business_notebook_inverse.svg.png";
    }
    else if (elt=="Data") {
        imageElt = "Linecons_database.svg.png";
        imageEltInverse = "Linecons_database_inverse.svg.png";
    }
    else if (elt=="Operator") {
        imageElt = "Octicons-gear.svg.png";
        imageEltInverse = "Octicons-gear_inverse.svg.png";
    }
    else if (elt=="Dataflow") {
        imageElt = "Share_icon_BLACK-01.svg.png";
        imageEltInverse = "Share_icon_BLACK-01_inverse.svg.png";
    }
    else {
        imageElt = "Article_icon_cropped.svg.png";
        imageEltInverse = "Article_icon_cropped_inverse.svg.png";
    }

    // MAJ tabs
    /*var tmpCompleteDir ='';
    if (isUrlWithId(window.location.toString())) {
        idElt = getIdFromUrl(window.location.toString());
        var ongletsMain = document.getElementById(idDiv).parentElement.querySelectorAll('ul>li>a');
        var ongletWork = document.getElementById(document.getElementById(idDiv).parentElement.id.replace("Main","Work")).querySelectorAll('ul>li>a');;
        var ongletHistoric = document.getElementById(document.getElementById(idDiv).parentElement.id.replace("Main","Historic")).querySelectorAll('ul>li>a');;
        var onglets = Array();
        for(var i=0;i<ongletsMain.length;i++) {
          onglets.push(ongletsMain[i]);}
        for(var i=0;i<ongletWork.length;i++) {
          onglets.push(ongletWork[i]);}
        for(var i=0;i<ongletHistoric.length;i++) {
          onglets.push(ongletHistoric[i]);}
        for(var i=0;i<onglets.length;i++) {
            var tmpOnglet = onglets[i];
            if (tmpOnglet.href.split('/').length<4) {
                continue;}
            dir=tmpOnglet.href.split('/')[3]+'/'+tmpOnglet.href.split('/')[4].replace('tmp','').replace(/-\d+/,'');
            if (tmpOnglet.href.split('/').length<6) {
                numOnglet="";}
            else {
                numOnglet=tmpOnglet.href.split('/')[5];}
            tmpOnglet.href=tmpOnglet.href.replace(/tmp([A-Za-z]+)/,"$1-"+idElt);
            tmpOnglet.href=tmpOnglet.href.replace(/([A-Za-z]+)-[0-9]+/,"$1-"+idElt);
            tmpCompleteDir = dir+'-'+idElt;
            if (numOnglet=="Work") {
                tmpOnglet.onclick=function (event) {showDiv(event,tmpCompleteDir+"/Work");};
                onclick_work = 'showDiv(event, "'+tmpCompleteDir+'/Work");';
            }
            else if (numOnglet=="Historic") {
                tmpOnglet.onclick=function (event) {showDiv(event,tmpCompleteDir+"/Historic");};
                onclick_history = 'showDiv(event, "'+tmpCompleteDir+'/Historic");';
            }
            else {
                tmpOnglet.onclick=function (event) {showDiv(event,tmpCompleteDir+"/");};
                onclick_main = 'showDiv(event, "'+tmpCompleteDir+'/");';
            }
        }
    }*/

    /*
    //////////////////////////MIKE START
    if (isUrlWithId(window.location.toString())) {
        idElt = getIdFromUrl(window.location.toString());

        if (idDiv.indexOf('Datas') != -1) {
            tmpCompleteDir = 'Datas/Data-'+idElt
        }
        else if (idDiv.indexOf('Dataflows') != -1) {
            tmpCompleteDir = 'Dataflows/Dataflow-'+idElt
        }

        var container = $('#'+idDiv);
        var childs = $(container[0].parentNode)[0].children;
        if (childs.length > 1) {
            childs[0].remove();
        }

        console.log(container[0].id);
        container.empty();

        var title = $('<h3>', {html: elt+' '+result.name + '&nbsp;&nbsp;'});
        title.append($('<img>', {  src: 'media/'+imageElt,
                                style: 'width: 40px; height: 40px; margin-right: 30px;'
                                }));

        var button_main     = $('<button>', {   html: '<span class="glyphicon glyphicon-eye-open" aria-hidden="true"></span>',
                                                class: 'btn btn-ms',
                                                style: 'border-color: #AAAAAA;',
                                                title: 'Main page',
                                                onclick: 'showDiv(event, "'+tmpCompleteDir+'/");'});
        var button_work     = $('<button>', {   html: '<span class="glyphicon glyphicon-wrench" aria-hidden="true"></span>',
                                                class: 'btn btn-ms',
                                                style: 'border-color: #AAAAAA;',
                                                onclick: 'showDiv(event, "'+tmpCompleteDir+'/Work");'});
        var button_history  = $('<button>', {   html: '<span class="glyphicon glyphicon-time" aria-hidden="true"></span>',
                                                class: 'btn btn-ms',
                                                style: 'border-color: #AAAAAA;',
                                                title: 'History of modifications',
                                                //onclick: 'showDiv(event, "'+tmpCompleteDir+'/Historic");',
                                                disabled: true});

        title.append(button_main);
        title.append(button_work);
        title.append(button_history);
        container.before(title);
    }
    //////////////////////////MIKE END
    */

    /*s = s + '<div class="col-md-12" id="studyPageContentMain">'
        + '<div class="row well">'
        + '<h4 class="">'+elt+' information</h4>'
        + '<dl class="dl-horizontal col-md-6">';

    //Informations
    for(i=0;i<result.info.length;i++) {
        s = s + '<dt class="description-terms-align-left">'+result.info[i].name+'</dt><dd class="editableDescriptionField">'+result.info[i].value;
        if ((result.info[i].name!="Name") && (result.info[i].name!="Project-id") && (result.info[i].name!="Data-id")&& (result.info[i].name!="Operator-id")&& (result.info[i].name!="Dataflow-id")&& (result.info[i].name!="Result-id")) {
            s = s +'<span class="editZoneContextualMenu"></span>';
        }
        s = s +'</dd>';
    }
    s = s + '<dt></dt><dd></dd>';

    if (result.datas.length>0) {
        s = s + '<dt class="description-terms-align-left">Datas</dt><dd>';
        for(i=0;i<result.datas.length;i++) {
            s = s + "<a onclick=\"showDiv(event,'Datas/tmpData');\" href=\"http://sakura.imag.fr/Datas/tmpData\">"+result.datas[i].name+"</a>, ";
        }
        s = s + '</dd>';
    }

    if (result.process.length>0) {
        s = s + '<dt class="description-terms-align-left">Dataflows processes</dt><dd>';
        for(i=0;i<result.process.length;i++) {
            s = s + "<a onclick=\"showDiv(event,'Dataflows/tmpDataflow');\" href=\"http://sakura.imag.fr/Dataflows/tmpDataflow\">"+result.process[i].name+"</a>, ";
        }
        s = s + '</dd>';
    }

    if (result.results.length>0) {
        s = s + '<dt class="description-terms-align-left">Results</dt><dd>';
        for(i=0;i<result.results.length;i++) {
            s = s + "<a onclick=\"showDiv(event,'Results/tmpResult');\" href=\"http://sakura.imag.fr/Results/tmpResult\">"+result.results[i].name+"</a>, ";
        }
        s = s + '</dd>';
    }
    s = s + '<a class="clPlusFieldButton" onclick="addField(this,event);" style="cursor: pointer; display:none;" title="add field"><span style="left:33%;" class="glyphicon glyphicon-plus" aria-hidden="true"></span></a>';
    s = s + '</dl>'
        + '<ul class="list-group col-md-6">'
        +   '<li class="list-group-item list-group-item-info"><strong>About <em>'+result.name+'</em> :</strong></li>'
        +   '<li class="list-group-item"><strong>Qualitative indicator:</strong> <span class="label label-primary pull-right">5</span></li>'
        +   '<li class="list-group-item"><strong>Volumetric indicator:</strong> <span class="label label-primary pull-right">5</span></li>'
        +   '<li class="list-group-item"><strong>Contact:</strong> <span class="label label-primary pull-right">'+result.userName+'@mail.uni</span></li>'
        + '</ul></div>';

    //Description
    s = s + '<div id="descriptionModalAbout'+elt+'" class="modal fade" role="dialog"><div class="modal-dialog">'
        + '<div class="modal-content"><div class="modal-header"><button type="button" class="close" data-dismiss="modal">&times;</button>'
        + '<h4 class="modal-title">Edit Explanation About</h4></div><div class="modal-body">';
    s = s + '<form><textarea name="editor1'+elt+'" id="editor1'+elt+'" rows="10" cols="60">'+result.description+'</textarea></form>';
    s = s + '</div><div class="modal-footer"><button type="button" class="btn btn-default" data-dismiss="modal" onClick="not_yet();">Save and close</button></div></div></div></div>'
    s = s + '<br /><br /><div class="panel panel-primary"><div class="panel-heading">'
        + '<table width="100%"><tbody><tr><td><h4 class="">'
        + '<font color="#ffffff">Explanation About '+result.name+"&nbsp;&nbsp;<img  width='40px' height='40px' src='media/"+imageEltInverse+"' alt='CC-BY-3.0 Wikipedia Gears'></img></h3>"+'</font></h4></td>'
        + '<td align="right"><button title="Modification of the Explanation About" class="btn btn-default btn-xs pull-right clPlusFieldButton" style="cursor: pointer; display:none;" data-toggle="modal" data-target="#descriptionModalAbout'+elt+'"><span class=" glyphicon glyphicon-pencil"></span></button></td>'
        + '</tr></tbody></table></div>'
        + '<div id="processShownAboutArea'+elt+'" class="panel-body">'+result.description+'</div></div>';

    //FileSystem
    if (result.fileSystem.length>0) {
        s = s + '<br /><br /><div class="well row"><h4 class="">Filesystem related to '+result.name+'</h4>'
            + '<table class="table table-bordered" id="fileBrowser"><thead>'
            + '<tr><th>Name</th><th colspan=2>Description</th></tr></thead><tbody>';
        for(i=0;i<result.fileSystem.length;i++) {
            s = s + '<tr><td><a onclick="not_yet();">'+result.fileSystem[i].filename+'</a></td><td>'+result.fileSystem[i].description+'</td></tr>';
        }
        s = s + '</tbody></table>';
        s = s + '<a class="clPlusFieldButton" onclick="addFile(this,event);" style="cursor: pointer; display:none;" title="add file"><span style="left:33%;" class="glyphicon glyphicon-plus" aria-hidden="true"></span></a>';
        s = s + '</div>';
    }

    //Comments
    s = s +'<hr style="border-bottom:5px solid;" /><br /><h3>Comments • '+result.comments.length+'</h3>'
        + '<span class="glyphicon glyphicon-user"></span><form class="form-inline" role="form"><label>Add your Comment: </label><div class="form-group">'
        + '<textarea class="form-control" rows="1" id="comment'+elt+'">Your comments</textarea></div>'
        + '<div class="form-group"><button onclick="addComment(this,event,\'comment'+elt+'\');" class="btn btn-default"><span class="glyphicon glyphicon-plus"></span></button></div></form><hr />'
        + '<ul class="commentList">';

    for(i=0;i<result.comments.length;i++) {
        s = s + '<li><div class="commenterImage"><span class="glyphicon glyphicon-user"></span></div>'
            + '<div class="commentText"><p class="">'+result.comments[i].comment+'</p> '
            + '<span class="date sub-text">'+result.comments[i].name+' on '+result.comments[i].date+'</span></div></li><br />';
        }
    s = s + '<a href="javascript:eltRequestStub(\''+idDiv+'\',\''+elt+'\',false)" class="executeOnShow"> </a></div>'; //TODO : relance l'affichage aleatoire, à supprimer quand on aura la version avec bd

    document.getElementById(idDiv).innerHTML = document.getElementById(idDiv).innerHTML + s;

    editorAbout = CKEDITOR.replace( "editor1"+elt);
    editorAbout.on( "change", function( evt ) {
        sDesc =  editorAbout.getData();
        document.getElementById("processShownAboutArea"+elt).innerHTML = sDesc;
    });
    */
}


function eltRequestStub(idDiv, elt, bd) {
    if (elt == 'Data') {
        idElt = getIdFromUrl(window.location.toString());
        console.log("DB_info: ask 3");
        sakura.common.ws_request('get_database_info', [+idElt], {}, function(db_info) {
            var result = {'name': db_info.name, "userName":db_info.owner,
            "info":[{"name":'Data-id',"value":idElt},{"name":"Name","value":db_info.name},{"name":"Owner","value":db_info.owner}],
            "datas":[], "process":[], "results":[], "comments":[],"fileSystem":[]};
            buildEltStub(idDiv,result,elt);
        });
    }
    else if (elt == 'Operator') {
        sakura.common.ws_request('list_operators_classes', [], {}, function (operators) {
            var result = new Array();
            idElt = getIdFromUrl(window.location.toString());
            operators.forEach( function(op) {
                if (op.id == idElt) {
                    result = {  'name': op.name,
                                'userName': op.owner,
                                'info': [   {'name': 'shortDesc', 'value': op.short_desc},
                                            {'name': 'tags', 'value': op.tags},
                                            {'name': 'id', 'value': op.id},
                                            {'name': 'daemon', 'value': op.daemon},
                                            {'name': 'owner', 'value': op.owner},
                                            {'name': 'creation date', 'value': op.date},
                                            {'name': 'modification date', 'value': op.modification_date} ],
                                'datas':[],
                                'process':[],
                                'results':[],
                                'comments':[],
                                'fileSystem':[]
                    }
                }
            });
            buildEltStub(idDiv,result,elt);
        });
    }
    else {
        result = eltStubAlea(elt); // objet {"name":_,"userName":_,"description":_, "info":[...],"datas":[...], "process":[...], "results":[...], "comments":[...],"fileSystem":[...]} détail : {  "name":eltName,"userName":userName,"info":infos, "datas":datas, "process":procs, "results":results, "comments":comments,"fileSystem":fs,"description":desc}
        buildEltStub(idDiv,result,elt);
    }
    return ;
}
