/// LIG Sept 2017

function buildListStub(idDiv, result, elt) {
    //ask for the current login
    sakura.apis.hub.users.current.info().then( function (curr_login) {

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

        var list_cols_gui_op  = ['Tags', 'Id', 'ShortDesc', 'Owner', 'CodeURL', 'SubDir'];
        var list_cols_hub_op  = ['tags', 'id', 'shortDesc', 'owner', 'repo_url', 'code_subdir'];

        var lcg = list_cols_gui;
        var lch = list_cols_hub;

        if (elt.indexOf('Operator') != -1) {
            lcg = list_cols_gui_op;
            lch = list_cols_hub_op;
        }

        new_row_head.append('<th>Name</th>');
        if (elt.indexOf('Operator') != -1) {
            new_row_head.append('<th>Revision</th>');
        }

        lcg.forEach( function (lelt) {
            if (document.getElementById("cbColSelect"+lelt).checked)
                new_row_head.append('<th>'+lelt+'</th>');
        });

        //Last col for the wrench
        var last_cell = new_row_head[0].cells[new_row_head[0].cells.length-1];

        var cell = $('<th>', { style: "width:26px; padding:0px; overflow:hidden"});
        cell.append('<a class="btn" style="padding:6px;" data-toggle="modal" data-target="#colSelectModal">'
            + '<span class="glyphicon glyphicon-wrench" aria-hidden="true"></span></a>'
            + '<a href="javascript:listRequestStub(\''+idDiv+'\',10,\''+elt+'\')" class="executeOnShow"> </a>');
        new_row_head.append(cell);

        //Body of the list
        result.forEach( function (row, index) {
            var new_row = $(tbody[0].insertRow());
            var tmp_elt=elt.replace(/tmp(.*)/,"$1-"+row.id);

            //adding link
            var new_td = $('<td>');
            var n_table = $('<table width=100%>');
            var n_row = $('<tr>');
            n_table.append(n_row);

            var n_td1 = $('<td>');
            var n_td2 = $('<td align="right">');
            var warn_icon = create_warn_icon(row);
            if (warn_icon)
                n_td1.append(warn_icon);

            if ((row.name.indexOf('OFFLINE') === -1) && (tmp_elt.indexOf('Operators') === -1)) {
                var name = $('<a>');
                name.html(row.name+'&nbsp;');
                name.attr('href', '/'+tmp_elt+'/'+row.id);
                name.attr('title', 'Accessing '+elt_type.slice(0, -1));
                name.attr('onclick', 'web_interface_current_db_id = '+row.id+'; showDiv(event, "'+tmp_elt+'/'+row.id+'");');

                n_td1.append(name);
                if (row.grant_level == 'own') {
                    n_td2.append('<span title="delete" class="glyphicon glyphicon-remove" style="cursor: pointer;" onclick="stub_delete('+row.id+',\''+idDiv+'\',\''+elt+'\');"></span>');
                }
            }
            else if (tmp_elt.indexOf('Operators') != -1){

                //Updating svg
                var svg_div = $('<div>');
                svg_div.append(row.svg);
                var svg     = svg_div.children()[0];

                var width   = svg.getAttribute('width').split('px')[0];
                var height  = svg.getAttribute('height').split('px')[0];
                var viewbox = svg.getAttribute('viewBox');
                vb_vals = [0, 0];
                if (viewbox != null)
                    vb_vals = viewbox.split(' ')

                svg.setAttribute('width', '20px');
                svg.setAttribute('height', '20px');
                svg.setAttribute('viewBox', ""+vb_vals[0]+" "+vb_vals[1]+" "+width+" "+height);

                //Adding svg and name
                var op_table = $('<table width="100%">');
                var op_tr = $('<tr>');
                var op_td1 = $('<td style="width: 30px;">');
                var op_td2 = $('<td>');
                var op_td3 = $('<td align="right">');


                op_td1.append(svg);
                op_td2.append('&nbsp;'+row.name+'&nbsp;');
                op_tr.append(op_td1);
                op_tr.append(op_td2);

                //Adding delete option if Owner
                //No grant_level attribut for operators,
                //so I make the test on the owner attribut
                if (curr_login !== null) {
                    if (row.owner == curr_login.login) {
                        op_td3.append('<span title="delete" class="glyphicon glyphicon-remove" style="cursor: pointer;" onclick="stub_delete('+row.id+',\''+idDiv+'\',\''+elt+'\');"></span>');
                        op_tr.append(op_td3);
                    }
                }

                op_table.append(op_tr);
                n_td1.append(op_table);
            }
            else
                n_td1.append(row.name);

            n_row.append(n_td1, n_td2);
            new_td.append(n_table);
            new_row.append(new_td);

            //Revision cell for operators
            if (tmp_elt.indexOf('Operators') != -1) {
                var new_td = $('<td>');
                var table = $('<table width=100%>');
                var tr = $('<tr>');
                var td1 = $('<td>');
                td1.append(row.default_code_ref);
                tr.append(td1);
                /* to be fixed (updating default revision)
                if (curr_login !== null) {
                    if (row.owner == curr_login.login) {
                        var td2 = $('<td align="right">');
                        var span = $('<span title="delete" class="glyphicon \
                        glyphicon-pencil" style="cursor: pointer;" \
                        onclick="update_operator_revision(\''+row.code_url+'\',\''+row.id+'\');"></span>');
                        td2.append(span);
                        tr.append(td2);
                    }
                }*/
                table.append(tr);
                new_td.append(table);
                new_row.append(new_td);
            }
            lcg.forEach( function (lelt, index) {
                if (document.getElementById("cbColSelect"+lelt).checked) {
                    if (lelt == 'Date' && row[lch[index]] instanceof Date) {
                        var d = row[lch[index]].toDateString();
                        var h = row[lch[index]].toLocaleTimeString();
                        new_row.append('<td>'+d+'</td>');
                    }
                    else {
                        new_row.append('<td>'+replace_undefined(row[lch[index]])+'</td>');
                    }
                }
            });
            var last_cell = new_row[0].cells[new_row[0].cells.length-1];
            last_cell.colSpan = 2;
        });
        tbody[0].id = 'idTBodyList'+eltAncetre;

        if (result.length == 0) {
            var new_row = $(tbody[0].insertRow());
            var msg = "There is no accessible "+elt_type;
            new_row.append('<td align=center colspan='+$(new_row_head)[0].children.length+'>'+msg+'</td>');
        }
        if (curr_login === null)
            $('#web_interface_'+elt_type+'_creation_button').addClass('invisible');
        else
            $('#web_interface_'+elt_type+'_creation_button').removeClass('invisible');
      });
}


function databases_sort(a, b) {
    return a.name > b.name ? 1 : -1;
}

function stub_delete(db_id, idDiv, elt) {

    var type = null;
    var asking_msg = null;
    var stub = null;
    var method = null;

    if (idDiv.indexOf('dataflows') != -1) {
        type = 'Dataflow';
        asking_msg = 'Are you sure you want to definitely delete this dataflow ??'
        stub = sakura.apis.hub.dataflows;
        method = 'delete';
    }
    else if (idDiv.indexOf('datas') != -1) {
        type = 'Database';
        asking_msg = 'Are you sure you want to definitely delete this database, with all its datasets ??'
        stub = sakura.apis.hub.databases;
        method = 'delete';
    }
    else if (idDiv.indexOf('operators') != -1) {
        type = 'Operator';
        asking_msg = 'Are you sure you want to definitely unregister this operator ??'
        stub = sakura.apis.hub.op_classes;
        method = 'unregister';
    }
    else if (idDiv.indexOf('projects') != -1) {
        type = 'Project';
        asking_msg = 'Are you sure you want to definitely delete this project, with all its pages ??';
        stub = sakura.apis.hub.projects;
        method = 'delete';
    }

    //Alert first
    stub_asking( 'Delete a '+ type,
                  asking_msg,
                  'rgba(217,83,79)',
                  function() {
                      let func = stub[parseInt(db_id)][method];
                      //then delete
                      func().then( function(result) {
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

function listRequestStub(idDiv, n, elt) {
    //Here we deal with the databases
    //if (elt == 'Datas/tmpData') {
    if (elt == 'Datas' || elt == 'datas') {
        sakura.apis.hub.databases.list().then(function (databases) {
            var result = new Array();
            databases.sort(databases_sort);
            databases.forEach( function(db) {
                result_info = { 'type': 'database', 'name': db.name,'id':db.database_id, 'isGreyedOut': !db.enabled,
                                'shortDesc': db.short_desc, 'date': moment.unix(db.creation_date)._d,
                                'tags': db.tags, 'modif': db.modification_date, 'grant_level': db.grant_level, 'access_scope': db.access_scope };
                if (db.enabled) {
                    result_info['owner'] = db.owner;
                    result_info['warning_message'] = db.warning_message;
                }
                else {
                    result_info['name'] += ' <i>(OFFLINE)</i>';
                    result_info['disabled_message'] = db.disabled_message;
                }
                result.push(result_info);
            });
            buildListStub(idDiv, result, 'Datas');
        });
    }
    //Here is for Dataflows
    //else if (elt == 'Dataflows/tmpDataflow') {
    else if (elt == 'Dataflows' || elt == 'dataflows') {
        sakura.apis.hub.dataflows.list().then(function (dataflows) {
            var result = new Array();
            dataflows.sort(dataflows_sort);
            dataflows.forEach( function(df) {

                ///////////////TEMP
                if (current_user) {
                    if (df.owner == current_user.login) {
                ///////////////TEMP
                        result_info = { 'type': 'dataflow', 'name': df.name,'id':df.dataflow_id, 'isGreyedOut': 0,
                                      'shortDesc': df.short_desc, 'date': moment.unix(df.creation_date)._d,
                                      'tags': df.tags, 'owner': df.owner, 'grant_level': df.grant_level, 'access_scope': df.access_scope };
                        result.push(result_info);
                    }
                }
            });
            buildListStub(idDiv, result, 'Dataflows');
        });
    }
    //Operators
    //else if (elt == 'Operators/tmpOperator') {
    else if (elt == 'Operators' || elt == 'operators') {
        sakura.apis.hub.op_classes.list().then(function (operators) {
            var result = new Array();
            current_op_classes_list = operators;
            operators.forEach( function(op) {

                var result_info = { 'shortDesc': op.short_desc,
                                    'modif': op.modification_date};
                Object.keys(op).forEach( function(key){
                    if (key != 'shortDesc' && key != 'modif') {
                        result_info[key] = op[key];
                    }
                });

                //Display of undefined fields
                Object.keys(result_info).forEach( function(key) {
                    if (!result_info[key]) {
                        result_info[key] = "__";
                    }
                });
                result.push(result_info);
            });
            buildListStub(idDiv, result, 'Operators');
        });
    }
    //else if (elt == 'Projects/tmpProject') {
    else if (elt == 'Projects' || elt == 'projects') {
        sakura.apis.hub.projects.list().then(function (projects) {
            var result = new Array();
            projects.forEach( function (proj) {
                var result_info = { 'type': 'project',
                                    'name': proj.name,
                                    'id':proj.project_id,
                                    'shortDesc': proj.short_desc,
                                    'date': moment.unix(proj.creation_date)._d,
                                    'tags': proj.tags,
                                    'owner': proj.owner,
                                    'grant_level': proj.grant_level,
                                    'access_scope': proj.access_scope
                                    };
                Object.keys(proj).forEach( function(key){
                    if (key != 'shortDesc' && key != 'modif') {
                        result_info[key] = proj[key];
                    }
                });

                //Display of undefined fields
                Object.keys(result_info).forEach( function(key) {
                    if (!result_info[key]) {
                        result_info[key] = "__";
                    }
                });
                result.push(result_info);
            });
            buildListStub(idDiv, result, 'Projects');
        });
    }
    else if (elt != 'Home' && elt != 'home') {
        console.log('Unknown element', elt);
    }
    return ;
}
