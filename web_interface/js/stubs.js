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
        var new_td = $('<td>');
        var n_table = $('<table width=100%>');
        var n_row = $('<tr>');
        n_table.append(n_row);

        var n_td1 = $('<td>');
        var n_td2 = $('<td align="right">');

        if ((row.name.indexOf('OFFLINE') === -1) && (tmp_elt.indexOf('Operators') === -1)) {
            var name = $('<a>');
            name.html(row.name);
            name.attr('href', 'http://sakura.imag.fr/'+tmp_elt+'/'+row.id);
            name.attr('title', 'Accessing '+elt_type.slice(0, -1));
            name.attr('onclick', 'web_interface_current_db_id = '+row.id+'; showDiv(event, "'+tmp_elt+'","' +row.id+'");');
            n_td1.append(name);
            if (row.grant_level == 'own') {
                n_td2.append('<span title="delete" class="glyphicon glyphicon-remove" style="cursor: pointer;" onclick="stub_delete('+row.id+',\''+idDiv+'\',\''+elt+'\');"></span>');
            }
        }
        else
            n_td1.append(row.name);

        n_row.append(n_td1, n_td2);
        new_td.append(n_table);
        new_row.append(new_td);

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

function stub_delete(db_id, idDiv, elt) {

    var type = null;
    var asking_msg = null;
    var stub = null;

    if (idDiv.indexOf('dataflows') != -1) {
        type = 'Dataflow';
        asking_msg = 'Are you sure you want to definitely delete this dataflow ??'
        stub = sakura.apis.hub.dataflows;
    }
    else if (idDiv.indexOf('datas') != -1) {
        type = 'Database';
        asking_msg = 'Are you sure you want to definitely delete this database, with all its datasets ??'
        stub = sakura.apis.hub.databases;
    }

    //Alert first
    stub_asking( 'Delete a '+ type,
                  asking_msg,
                  'rgba(217,83,79)',
                  function() {
                      //then delete
                      stub[parseInt(db_id)].delete().then( function(result) {
                          //then refresh
                          listRequestStub(idDiv, 10, elt, false);
                      }).catch( function (error_msg) {
                        console.log(error_msg);
                      });
                  },
                  function() {} );
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
        sakura.apis.hub.databases.list().then(function (databases) {
            var result = new Array();
            databases.sort(databases_sort);
            databases.forEach( function(db) {
                result_info = { 'type': 'database', 'name': db.name,'id':db.database_id, 'isGreyedOut': !db.enabled,
                                'shortDesc': db.short_desc, 'date': moment.unix(db.creation_date)._d,
                                'tags': db.tags, 'modif': db.modification_date, 'grant_level': db.grant_level, 'access_scope': db.access_scope };
                if (db.enabled)
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
        sakura.apis.hub.dataflows.list().then(function (dataflows) {
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
        sakura.apis.hub.op_classes.list().then(function (operators) {
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
        sakura.apis.hub.list_nObjets(10,'etude_').then(function (idDiv,result) {buildHistoryStub(idDiv,result,elt);});}
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
