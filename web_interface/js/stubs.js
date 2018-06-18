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
        if (row.name.indexOf('OFFLINE') === -1) {
            var name = null;
            var table = $('<table>', {width: "100%"})
            var tr = $('<tr>')
            var td1 = $('<td>', {align: "left"})
            var td2 = $('<td>', {align: "right"})
            var eye = null;

            if (row.grant_level != 'list') {
                name = $('<a>');
                name.html(row.name );
                name.attr('href', 'http://sakura.imag.fr/'+tmp_elt+'/'+row.id);
                name.attr('title', 'Accessing database');
                name.attr('onclick', 'web_interface_current_db_id = '+row.id+'; showDiv(event, "'+tmp_elt+'","' +row.id+'");');
                eye = $('<p>', {html: '<span class=\'glyphicon glyphicon-eye-open\'></span>',
                                style: 'margin: 0px;'})
            }
            else {
                name = $('<p>');
                name.attr('style', 'margin: 0px;');
                name.html( row.name +'&nbsp;&nbsp;&nbsp;');
                eye = $('<a>', {  title:  'Request Access',
                                  style:  'cursor: pointer;',
                                  html:   '<span class=\'glyphicon glyphicon-eye-close\'></span>',
                                  onclick: 'web_interface_asking_access_open_modal(\''+row.name+'\',\''+row.type+'\',\''+row.id+'\',\'read\');'});
            }
            td1.append(name);
            td2.append(eye);
            tr.append(td1, td2);
            table.append(tr);
            cell.append(table);

        }
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
                    new_row.append('<td>'+replace_undefined(row[list_cols_hub[index]])+'</td>');
                }
            }
        });
        var last_cell = new_row[0].cells[new_row[0].cells.length-1];
        last_cell.colSpan = 2;
    });
    tbody[0].id = 'idTBodyList'+eltAncetre;

    if (result.length == 0) {
        var new_row = $(tbody[0].insertRow());
        var msg = "There is no accessible database.";
        if (idDiv.indexOf("dataflows") != -1)
            msg = "There is no accessible dataflow.";
        new_row.append('<td align=center colspan='+$(new_row_head)[0].children.length+'>'+msg+'</td>');
    }


}


function databases_sort(a, b) {
    return a.name > b.name ? 1 : -1;
}

function dataflows_sort(a, b) {
    return a.name > b.name ? 1 : -1;
}

function replace_undefined(val) {
    if (val == undefined)
        return '__';
    return val;
}

function listRequestStub(idDiv, n, elt, bd) {

    //Here we deal with the databases
    if (elt == 'Datas/tmpData') {
        sakura.common.ws_request('list_databases', [], {}, function (databases) {
            var result = new Array();
            databases.sort(databases_sort);
            databases.forEach( function(db) {
                result_info = { 'type': 'database', 'name': db.name,'id':db.database_id, 'isGreyedOut': !db.online,
                                'shortDesc': db.short_desc, 'date': moment.unix(db.creation_date)._d,
                                'tags': db.tags, 'modif': db.modification_date, 'grant_level': db.grant_level, 'access_scope': db.access_scope };
                if (db.online)
                    result_info['owner'] = db.owner;
                else
                    result_info['name'] += ' <i>(OFFLINE)</i>';
                result.push(result_info);
            });
            buildListStub(idDiv,result,elt);
        });
    }
    //Here is for Dataflows
    else if (elt == 'Dataflows/tmpDataflow') {
        sakura.common.ws_request('list_dataflows', [], {}, function (dataflows) {
            var result = new Array();
            dataflows.sort(dataflows_sort);
            dataflows.forEach( function(df) {
                result_info = { 'type': 'dataflow', 'name': df.name,'id':df.dataflow_id, 'isGreyedOut': 0,
                                'shortDesc': df.short_desc, 'date': moment.unix(df.creation_date)._d,
                                'tags': df.tags, 'owner': df.owner };

                result.push(result_info);
            });
            buildListStub(idDiv,result,elt);
        });
    }
    //Operators
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
}


function eltRequestStub(idDiv, elt, bd) {
    if (elt == 'Data') {
        idElt = getIdFromUrl(window.location.toString());
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
        result = eltStubAlea(elt);
        buildEltStub(idDiv,result,elt);
    }
    return ;
}
