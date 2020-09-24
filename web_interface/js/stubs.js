/// LIG Sept 2017

function buildListStub(idDiv, result, elt) {
    //ask for the current login
    sakura.apis.hub.users.current.info().then( function (curr_login) {

        let eltAncetre=elt.split("/")[0];
        let elt_type = elt.split('/')[0].toLowerCase();

        //Head of the list, according to the selected columns
        let thead = $('#'+idDiv).find('thead');
        let tbody = $('#'+idDiv).find('tbody');
        thead.empty();
        tbody.empty();
        let new_row_head = $(thead[0].insertRow());
        let list_cols_gui = ['Tags', 'Id', 'ShortDesc', 'Date', 'Modification', 'Owner'];
        let list_cols_hub = ['tags', 'id', 'shortDesc', 'date', 'modification', 'owner'];

        let list_cols_gui_op  = ['ShortDesc', 'Tags', 'CodeURL', 'Revision', 'Owner', 'Id',  'SubDir' ];
        let list_cols_hub_op  = ['shortDesc', 'tags', 'repo_url', 'revision', 'owner',  'id',  'code_subdir'];

        let lcg = list_cols_gui;
        let lch = list_cols_hub;

        if (elt.indexOf('Operator') != -1) {
            lcg = list_cols_gui_op;
            lch = list_cols_hub_op;
        }

        new_row_head.append('<th>Name</th>');

        lcg.forEach( function (lelt) {
            if (document.getElementById("cbColSelect"+lelt).checked)
                new_row_head.append('<th>'+lelt+'</th>');
        });

        //Last col for the wrench
        let last_cell = new_row_head[0].cells[new_row_head[0].cells.length-1];

        let cell = $('<th>', { style: "width:26px; padding:0px; overflow:hidden"});
        cell.append('<a class="btn" style="padding:6px;" data-toggle="modal" data-target="#colSelectModal">'
            + '<span class="glyphicon glyphicon-wrench" aria-hidden="true"></span></a>'
            + '<a href="javascript:listRequestStub(\''+idDiv+'\',10,\''+elt+'\')" class="executeOnShow"> </a>');
        new_row_head.append(cell);

        //Body of the list
        result.forEach( function (row, index) {

            let new_row = $(tbody[0].insertRow());
            let tmp_elt=elt.replace(/tmp(.*)/,"$1-"+row.id);

            //adding link
            let new_td = $('<td>');
            let n_table = $('<table width=100%>');
            let n_row = $('<tr>');
            n_table.append(n_row);

            let n_td1 = $('<td>');
            let n_td2 = $('<td align="right">');
            let warn_icon = create_warn_icon(row);
            if (warn_icon)
                n_td1.append(warn_icon);

            if ((row.name.indexOf('OFFLINE') === -1) && (tmp_elt.indexOf('Operators') === -1)) {
                let name = $('<a>');
                name.html(row.name+'&nbsp;');
                if (row.grant_level == 'list') {
                    name.css('cursor', 'pointer');
                    name.attr('title', 'Accessing '+elt_type.slice(0, -1));
                    name.attr('onclick', 'open_metadata(\''+tmp_elt+'\','+row.id+',\''+row.name+'\');');
                }
                else {
                    name.attr('href', '/'+tmp_elt+'/'+row.id);
                    name.attr('title', 'Accessing '+elt_type.slice(0, -1));
                    name.attr('onclick', 'web_interface_current_db_id = '+row.id+'; showDiv(event, "'+tmp_elt+'/'+row.id+'");');
                }

                n_td1.append(name);
                if (row.grant_level == 'own') {
                    n_td2.append('<span title="delete" class="glyphicon glyphicon-trash" style="cursor: pointer;" onclick="stub_delete('+row.id+',\''+idDiv+'\',\''+elt+'\');"></span>');
                }
            }
            else if (tmp_elt.indexOf('Operators') != -1){

                //Updating svg
                let svg_div = $('<div>');
                svg_div.append(row.svg);
                let svg     = svg_div.children()[0];

                let width   = svg.getAttribute('width').split('px')[0];
                let height  = svg.getAttribute('height').split('px')[0];
                let viewbox = svg.getAttribute('viewBox');
                vb_vals = [0, 0];
                if (viewbox != null)
                    vb_vals = viewbox.split(' ')

                svg.setAttribute('width', '20px');
                svg.setAttribute('height', '20px');
                svg.setAttribute('viewBox', ""+vb_vals[0]+" "+vb_vals[1]+" "+width+" "+height);

                //Adding svg and name
                let op_table = $('<table width="100%">');
                let op_tr = $('<tr>');
                let op_td1 = $('<td style="width: 30px;">');
                let op_td2 = $('<td>');
                let op_td3 = $('<td align="right">');


                op_td1.append(svg);
                op_td2.append('&nbsp;'+row.name+'&nbsp;');
                op_tr.append(op_td1);
                op_tr.append(op_td2);

                //Adding delete option if Owner
                //No grant_level attribut for operators,
                //so I make the test on the owner attribut
                if (curr_login !== null) {
                    if (row.owner == curr_login.login) {
                        op_td3.append('<span title="delete" class="glyphicon glyphicon-trash" style="cursor: pointer;" onclick="stub_delete('+row.id+',\''+idDiv+'\',\''+elt+'\');"></span>');
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

            lcg.forEach( function (lelt, index) {
                if (document.getElementById("cbColSelect"+lelt).checked) {
                    switch (lelt) {
                        case 'Date':
                            if (row[lch[index]] instanceof Date) {
                                let d = row[lch[index]].toDateString();
                                let h = row[lch[index]].toLocaleTimeString();
                                new_row.append('<td>'+d+'</td>');
                            }
                            else {
                                new_row.append('<td>'+replace_undefined(row[lch[index]])+'</td>');
                            }
                            break;

                        case ('Revision'):
                            let new_td = $('<td>');
                            let cr = row.default_code_ref;
                            if (! cr) {
                                new_row.append('<td>&lt;not applicable&gt;</td>');
                                break;
                            }
                            let t = cr.split(':');
                            if (t[0] == 'branch')
                                cr = t[1];
                            let txt = '<b>'+cr +
                                      '</b>@' +
                                      row.default_commit_hash.substring(0,7);

                            if (curr_login !== null  && row.owner == curr_login.login) {
                                let select = $('<select>', {'class': 'selectpicker',
                                                'data-live-search': 'true',
                                                'data-width': '100%'
                                                });

                                let opt = $('<option>', { 'value': 0,
                                                          'html': txt,
                                                          'selected': true});
                                select.append(opt);
                                new_td.append(select);
                                select.on('shown.bs.select', function(e) {
                                              $(e.target).selectpicker('toggle');
                                              operators_revision_panel_select_open($(e.target), row, false, null);
                                              e.preventDefault();
                                          });
                                select.selectpicker('refresh');
                            }
                            else {
                                new_td.append(txt);
                            }
                            new_row.append(new_td);
                            break;

                        case ('CodeURL'):
                            if (row[lch[index]]) {
                                let a = '<a href="'+row[lch[index]]+'">'+row[lch[index]]+'<a>'
                                new_row.append('<td>'+a+'</td>');
                            }
                            else {
                                new_row.append('<td>&lt;sandbox&gt;</td>');
                            }
                            break;

                        default:
                            new_row.append('<td>'+replace_undefined(row[lch[index]])+'</td>');

                    }
                }
            });
            let last_cell = new_row[0].cells[new_row[0].cells.length-1];
            last_cell.colSpan = 2;
        });
        tbody[0].id = 'idTBodyList'+eltAncetre;

        if (result.length == 0) {
            let new_row = $(tbody[0].insertRow());
            let msg = "There is no accessible "+elt_type;
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

    let type = null;
    let asking_msg = null;
    let stub = null;
    let method = null;

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
        push_request('databases_list');
        sakura.apis.hub.databases.list().then(function (databases) {
            pop_request('databases_list');
            let result = new Array();
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
        push_request('dataflows_list');
        sakura.apis.hub.dataflows.list().then(function (dataflows) {
            pop_request('dataflows_list');
            let result = new Array();
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
        push_request('op_classes_list');
        sakura.apis.hub.op_classes.list().then(function (operators) {
            pop_request('op_classes_list');
            let result = new Array();
            current_op_classes_list = operators;
            operators.forEach( function(op) {

                let result_info = { 'shortDesc': op.short_desc,
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
        push_request('projects_list');
        sakura.apis.hub.projects.list().then(function (projects) {
            pop_request('projects_list');
            let result = new Array();
            projects.forEach( function (proj) {
                let result_info = { 'type': 'project',
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
