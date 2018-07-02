/// LIG Sept 2017


function buildListStub(idDiv,result,elt) {

    var eltAncetre=elt.split("/")[0];
    var elt_type = elt.split('/')[0].toLowerCase();

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

            //own, write, read
            if (row.grant_level == 'own' ||
                row.grant_level == 'write' ||
                row.grant_level == 'read') {
                name = $('<a>');
                name.html(row.name );
                name.attr('href', 'http://sakura.imag.fr/'+tmp_elt+'/'+row.id);
                name.attr('title', 'Accessing '+elt_type.slice(0, -1));
                name.attr('onclick', 'web_interface_current_db_id = '+row.id+'; showDiv(event, "'+tmp_elt+'","' +row.id+'");');
                eye = $('<p>', {html: '<span class=\'glyphicon glyphicon-eye-open\'></span>',
                                style: 'margin: 0px;'})
            }
            //list
            else {
                name = $('<a>');
                name.html(row.name );
                name.attr('href', 'http://sakura.imag.fr/'+tmp_elt+'/'+row.id);
                name.attr('title', 'Accessing '+elt_type.slice(0, -1));
                name.attr('onclick', 'web_interface_current_db_id = '+row.id+'; showDiv(event, "'+tmp_elt+'","' +row.id+'");');
            }
            cell.append(name);
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
        var msg = "There is no accessible "+elt_type+".";
        new_row.append('<td align=center colspan='+$(new_row_head)[0].children.length+'>'+msg+'</td>');
    }

    if (current_login == null)
        $('#web_interface_'+elt_type+'_creation_button').addClass('invisible');
    else
        $('#web_interface_'+elt_type+'_creation_button').removeClass('invisible');
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
            console.log(databases);
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
                                'tags': df.tags, 'owner': df.owner, 'grant_level': df.grant_level, 'access_scope': df.access_scope };

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
