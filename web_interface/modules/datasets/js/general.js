//Code started by Michael Ortega for the LIG
//August, 22nd, 2017

var database_infos = null;
var columns_tags_list = null;
var mouse = {x: 0, y: 0};
var chunk_size = 100000;
var openned_accordion = null;

function not_yet() {
    alert("not yet implemented");
}


function datasets_sort_func(a, b) {
    return a.name > b.name ? 1 : -1;
}

function min(a, b) {
    if (a <= b) return a;
    return b;
}

$(document).mousemove(function(e) {
    mouse.x = e.pageX;
    mouse.y = e.pageY;
}).mouseover(); // call the handler immediately



function datasets_info(header_str, body_str) {
    let h = $('#datasets_info_header');
    let b = $('#datasets_info_body');
    h.html("<h3><font color=\"black\">"+header_str+"</font></h3>");
    b.html("<p>"+body_str+"</p>");
    $('#datasets_info_modal').modal();
}


function datasets_alert(header_str, body_str) {
    let h = $('#datasets_alert_header');
    let b = $('#datasets_alert_body');
    h.html("<h3><font color=\"white\">"+header_str+"</font></h3>");
    b.html("<p>"+body_str+"</p>");
    $('#datasets_alert_modal').modal();
}


function datasets_asking(header_str, body_str, rgba_color, func_yes, func_no) {
    let h = $('#datasets_asking_header');
    let b = $('#datasets_asking_body');
    let b_yes = $('#datasets_asking_button_yes');
    let b_no = $('#datasets_asking_button_no');

    h.css('background-color', rgba_color);
    h.html("<h3><font color=\"white\">"+header_str+"</font></h3>");
    b.html("<p>"+body_str+"</p>");

    b_yes.unbind("click");
    b_no.unbind("click");

    b_yes.click(function() {  func_yes(); });
    b_no.click(function() { func_no();  });

    $('#datasets_asking_modal').modal();
}


function datasets_extension_check(f_name, exts) {
    //check the name: should have .csv extension
    let s_name = f_name.split('.');
    ext = s_name[s_name.length - 1].toLowerCase();

    function diff(e, i, arr) {
        return (e.toLowerCase() == ext);
    }
    return exts.some(diff);
}

function close_other_accordions(acc_id) {
    let acc = document.getElementsByClassName("dataset_accordion");
    for (let i = 0; i < acc.length; i++) {
        if (i != acc_id) {
          let panel = document.getElementById('dataset_accordion_panel_'+i);
          panel.style.maxHeight = 0 + 'px';
        }
    };
}

function open_accordion(acc_id) {
    let panel = document.getElementById('dataset_accordion_panel_'+acc_id);
    panel.style.maxHeight = panel.scrollHeight + "px";
    openned_accordion = acc_id;
}

function close_accordion(acc_id) {
    let panel = document.getElementById('dataset_accordion_panel_'+acc_id);
    panel.style.maxHeight = panel.scrollHeight + "px";
    openned_accordion = null;
}


function recover_datasets() {
    database_id = web_interface_current_id;

    push_request('databases_info');
    sakura.apis.hub.databases[parseInt(database_id)].info().then(function (result) {
        pop_request('databases_info');
        if (result.grant_level != 'list') {

            if (result.tables == undefined)
                result.tables = [];
            //Sorting tables by name
            result.tables.sort(datasets_sort_func);

            //Saving the db infos
            database_infos = result;

            $('#datasets_name').html(result.name);
            if (result.short_desc) {
                $('#datasets_description').html(result.short_desc);
            }
            else {
                $('#datasets_description').html('<font color="lightgrey">No short description</font>');
            }


            //Filling dataset
            let body = $('#table_of_datasets').find('tbody');
            body.empty();

            if (result.tables.length == 0) {
                let tr = $('<tr>');
                let td = $('<td>', {html: "The list is empty for now"});
                tr.append(td);
                body.append(tr);
            }

            result.tables.forEach( function(dataset, index) {
                let dataset_id = dataset.table_id;
                let new_row = $(document.createElement('tr'));
                new_row.load('modules/datasets/templates/dataset.html', function () {
                    let tds = new_row.find('td');
                    let spans = $(tds[2]).find('span');

                    $(tds[0]).empty();
                    $(tds[0]).append($('<a>',{  text: dataset.name,
                                                style: "cursor: pointer;",
                                                onclick: "datasets_visu_dataset("+dataset_id+","+index+");"
                                                })
                                    );

                    $(tds[1]).empty();
                    if (dataset.short_desc)
                        $(tds[1]).append(dataset.short_desc);
                    else
                        $(tds[1]).append("<font color='lightgrey'>__</font>");
                    if (result.grant_level == 'write' || result.grant_level == 'own')
                        spans.toArray().forEach( function(span) {
                            if ($(span).attr('onclick')) {
                                let new_oc = $(span).attr('onclick').replace('ds_id', dataset_id);
                                $(span).attr('onclick', new_oc);
                            }
                        });
                    else if (result.grant_level == 'read')
                        spans.toArray().forEach( function(span) {
                            let className = $(span).attr('class');
                            if (className.indexOf('download') == -1)
                                $(span).css('display', 'none');
                            else {
                                let new_oc = $(span).attr('onclick').replace('ds_id', dataset_id);
                                $(span).attr('onclick', new_oc);
                            }
                        });
                });
                body.append(new_row);
                let tr = $('<tr>');
                let td = $('<td colspan= 3 style="padding-top: 0px; padding-bottom: 0px;">');
                td.html('<div class="dataset_accordion_panel" id="dataset_accordion_panel_'+index+'"><p>Following 2</p></div>');
                tr.append(td);
                body.append(tr);
            });

            if (result.grant_level == 'write' || result.grant_level == 'own') {
                $('#datasets_open_creation_button').attr('onclick', 'datasets_open_creation('+database_id+');');
                $('#datasets_open_creation_button').css('display', 'inline');
            }
            else
                $('#datasets_open_creation_button').css('display', 'none');

            //Ask for the existing tags
            push_request('datastores_list_expected_columns_tags');
            sakura.apis.hub.datastores[database_infos.datastore_id].list_expected_columns_tags().then(function (tags_list) {
                pop_request('datastores_list_expected_columns_tags');
                columns_tags_list = tags_list;
            });
        }
        else {
            let body = $('#table_of_datasets').find('tbody');
            body.empty();
            let tr = $('<tr>');
            let td = $('<td colspan=3>');
            td.html("You need a read access for seeing the datasets (MetaData/Access)");
            tr.append(td);
            body.append(tr);
            $('#datasets_open_creation_button').css('display', 'none');
        }
    });
}


function datasets_send_file(dataset_id, f, dates, modal, from_what) {
    let first_chunk     = true;
    let f_size          = f.size;
    let sent_data_size  = 0;
    let date            = new Date();
    let nb_cols         = 0;
    let length_alert_done = false;


    Papa.LocalChunkSize = chunk_size;
    let chunks_to_do = [];

    Papa.parse(f, {
        comments: true,
        header: false,
        skipEmptyLines: true,
        chunk: function(chunk, parser) {

            if (first_chunk) {
                nb_cols = chunk.data[0].length;
                chunk.data.splice(0, 1);
                first_chunk = false;
            }
            chunk.data.forEach( function(line) {
                if (line.length != nb_cols) {
                    if (! length_alert_done) {
                        $('#datasets_alert_header').html('<h3>Data Upload</h3>');
                        $('#datasets_alert_body').html('One or more lines of your file doesn\'t have the correct number of columns. These lines are truncated, or filled with null values.');
                        $('#datasets_alert_modal').modal('show');
                    }
                    let diff = nb_cols - line.length;
                    if (diff > 0)
                        for (let i =0; i< diff; i++)
                            line.push('');
                    else
                        line.splice(line.length + diff, - diff)
                }
                //Dates
                dates.forEach(function(date) {
                    d = line[date.column_id];
                    line[date.column_id] = moment(d, date.format).unix();
                });

                //null values
                for (i=0; i<line.length; i++)
                  if (line[i].length == 0)
                      line[i] = null;
            });

            if (chunk.data.length) {
                parser.pause();

                chunks_to_do.push(1);
                push_request('tables_add_rows');
                sakura.apis.hub.tables[dataset_id].add_rows(chunk.data).then(function(result) {
                    pop_request('tables_add_rows');
                    sent_data_size += Papa.LocalChunkSize;
                    let perc = parseInt(sent_data_size/f.size * 100);
                    $('#datasets_'+from_what+'_button').removeClass("btn-primary");
                    $('#datasets_'+from_what+'_button').addClass("btn-success");
                    $('#datasets_'+from_what+'_button').html('Uploading ...'+ perc + '%');
                    $('#datasets_'+from_what+'_progress_bar').css("width", ""+perc+"%");
                    $('#datasets_'+from_what+'_progress_bar').css("aria-valuenow", ""+perc);

                    if (parser)
                        parser.resume();
                    chunks_to_do.pop();

                    if (chunks_to_do.length == 0) {
                        datasets_send_file_ended(date, modal);
                    }
                }).catch( function(error_msg){
                    console.log('Error in adding rows !!!', error_msg);
                    pop_request('tables_add_rows');
                    datasets_alert('Error in adding rows into the dataset', error_msg);
                    datasets_send_file_ended(date, modal);

                    //We delete the freshly created table
                    push_request('tables_delete');
                    sakura.apis.hub.tables[dataset_id].delete().then( function(result) {
                        pop_request('tables_delete');
                        //Update the display
                        $('#datasets_cancel_creation_button').prop("disabled", false);
                        $('#datasets_creation_button').prop("disabled", false);
                        $('#datasets_creation_button').html('Create Dataset');
                        $('#datasets_creation_button').addClass('btn-primary');
                        $('#datasets_creation_button').removeClass('btn-success');
                        $('#datasets_creation_div_progress_bar').hide();

                        //Testing chunk
                        //-- Test on types
                        let cols_list = []
                        let nb_rows = chunk.data.length;
                        let nb_cols = chunk.data[0].length;
                        for (let c=0; c<nb_cols; c++) {
                            let types = [$('#datasets_ff_type_select_'+c).val()];
                            for (let r=0; r<nb_rows; r++) {
                                types.push(get_type(chunk.data[r][c]));
                            }
                            let ntype = check_types(types);
                            if (ntype != $('#datasets_ff_type_select_'+c).val()) {
                                cols_list.push([$('#datasets_creation_col_name_ff_'+c).val(), ntype]);
                            }
                            $('#datasets_ff_type_select_'+c).val(ntype);
                            $('#datasets_ff_type_select_'+c).selectpicker('refresh');
                        }

                        //Then give the message
                        let msg = 'According to the error, the type of the following columns <b>has been udpated</b>:<br>';
                        cols_list.forEach( function(e) {
                            msg += '- <b>'+e[0]+'</b> >> '+e[1]+'<br>';
                        });
                        msg += '<br><b>Do you want to create the dataset with these column types?</b>';

                        if (cols_list.length) {
                            datasets_asking('Error in adding rows into the dataset',
                                            error_msg+'<br><br>'+msg,
                                            'rgba(217,83,79)',
                                            function() {  datasets_send_new(database_infos.database_id)},
                                            function() {  console.log("NO");}   );
                        }
                        else {
                            datasets_alert('Error in adding rows into the dataset',error_msg);
                        }
                        return false;
                    }).catch( function (error_msg) {
                        pop_request('tables_delete');
                        console.log('Error in deleting Table !!!', error_msg);
                    });
                });
            }
        },
        complete: function() {
            if (chunks_to_do.length == 0) {
                datasets_send_file_ended(date, modal);
            }
        },
        error: function (error) {
            datasets_alert("Parsing error", error);
        }
    });
}

function datasets_send_file_ended(date, modal) {
    let ndate = new Date();
    let s = parseInt((ndate.getTime() - date.getTime())/1000);
    let m = parseInt(s/60);
    console.log("Uploading time: "+m+"min:"+s+"s");
    modal.modal('hide');
    recover_datasets();
}


function datasets_check_date_format(date, format_div, format_input, result_div, result_input) {
    let m2 = moment(date, format_input.val());
    if (! m2._isValid) {
        format_div.attr("class", "has-error");
        result_div.attr("class", "has-error");
        result_input.val("Invalid format");
    }
    else{
        format_div.attr("class", "");
        result_div.attr("class", "has-success");
        result_input.val(m2._d);
    }
}


function this_col_is_a_date(col) {
    if (col[1] != 'date')
        return false;
    return true;
}


function datasets_delete(dataset_id) {
    datasets_asking('Delete a Dataset',
                    'Are you sure you want to definitely delete this dataset ??',
                    'rgba(217,83,79)',
                    function() {datasets_delete_yes(dataset_id, true);},
                    function(){});
}

function datasets_delete_yes(dataset_id, alert) {
    push_request('tables_delete');
    sakura.apis.hub.tables[dataset_id].delete().then(function() {
        pop_request('tables_delete');
        console.log("Dataset deleted");
        //refresh datasets list
        recover_datasets();
    }).catch( function (error_msg) {
        pop_request('tables_delete');
        if (alert)
            datasets_alert('Error deleting Dataset', error_msg);
        else
            console.log('Error deleting Dataset:', error_msg);
    });
}

function datasets_download(dataset_id) {

    let dataset = $.grep(database_infos.tables, function(e){ return e.table_id == dataset_id; })[0];

    let txt = 'The size of the file is unkown for now.';
    if (dataset.count_estimate)
        txt = 'This dataset has ~'+dataset.count_estimate+' rows.';

    let h = $('#datasets_download_modal_header');
    let b = $('#datasets_download_modal_body');
    let bc = $('#datasets_download_modal_button_csv');
    let bg = $('#datasets_download_modal_button_gzip');

    h.css('background-color', 'rgba(91,192,222)');
    h.html("<h3><font color=\"white\">Dataset Download</font></h3>");
    b.html("<p>"+txt+"</p>");
    bc.attr('onclick', 'datasets_download_start_transfert('+dataset_id+', false);');
    bg.attr('onclick', 'datasets_download_start_transfert('+dataset_id+', true);');

    $('#datasets_download_modal').modal();
}

function datasets_download_start_transfert(dataset_id, gzip) {

  let dataset = $.grep(database_infos.tables, function(e){ return e.table_id == dataset_id; })[0];
  stop_downloading = false;

  push_request('transfers_start');
  sakura.apis.hub.transfers.start().then(function(transfert_id) {
        pop_request('transfers_start');
        current_transfert_id = transfert_id;

        let url = "/tables/"+dataset.table_id+"/export.csv?transfer="+current_transfert_id;
        if (gzip)
            url = "/tables/"+dataset.table_id+"/export.csv.gz?transfer="+current_transfert_id;

        //Create a link from downloading the file
        let element = document.createElement('a');
        element.setAttribute('href', url);
        element.setAttribute('download', dataset.name+'.csv');
        element.style.display = 'none';
        document.body.appendChild(element);

        download_start_transfert('dataset')

        element.click();
        document.body.removeChild(element);

    });
}
