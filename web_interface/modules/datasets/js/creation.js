//Code started by Michael Ortega for the LIG
//August, 22nd, 2017


var current_select  = null;
var global_ids      = 0;
//var file_lines      = null;
//var first_data_line = null;

var csv_file = {'headers': [], 'lines': []};

/////////////////////////////////////////////////////////////////////////////////////
// CREATION

function datasets_send_new(database_id) {
    
    //Reading first main elements: name and description
    var name = $('#datasets_creation_name').val();
    var desc = $('#datasets_creation_description').val();
    if ( name == "") {
        datasets_alert("Dataset Name", "We cannot create a dataset with an empty name !");
        return;
    }
    
    
    //Which table body ?
    var ff = false;
    var body = $('#datasets_creation_from_scratch_columns').find('tbody');
    var cols = body.find('tr');
    var nb_cols = cols.length - 1;
    $('#datasets_creation_from_file_pan').attr("class").split(' ').forEach( function (elt) {
        if (elt == 'active') {
            ff = true;
            body = $('#datasets_creation_from_file_columns').find('tbody');
            cols = body.find('tr');
            nb_cols = cols.length
        }
    });
    
    var columns = []
    //Data from each row
    for (var i=0; i< nb_cols; i++) {
        var inputs = $(cols[i]).find('input');
        var label = $(inputs[0]).val();
        
        if (label == 'Column Name') {
            datasets_alert("Columns Name", "Each column should have an explicit name");
            return;
        }
        
        var type = $($(cols[i]).find('select')[0]).val();
        var tags = $($(cols[i]).find('select')[1]).val();
        columns.push([label, type, tags]);
    };
    
    
    //Sending the new dataset description
    //database_id, name, description, creation_date, columns
    sakura.common.ws_request('new_table', [database_id, name, desc, ($('#datasets_creation_datetimepicker').data("DateTimePicker").date()).unix(), columns], {}, function(result) {
        var new_dataset_id = result;
        if (result >= 0) {
            if (ff) {
                console.log("TODO: table created from file, so now we should fill the table");
            }
            else {
                console.log("TODO: table created from scratch, so back to the main view, refreshed");
            }
        }
    });
    
    $("#datasets_creation_modal").modal('hide');
}


/////////////////////////////////////////////////////////////////////////////////////
// FILE MANAGEMENT

function on_file_selected(f) {
    
    //check the name: should have .csv extension
    var s_name = f.value.split('.');
    if (s_name[s_name.length - 1] != 'csv' && s_name[s_name.length - 1] != 'CSV') {
        datasets_alert("File Extension Issue", "The extension of this file is not .csv !!\nPlease be sure it is a csv file, and rename it with extension.");
        return;
    }
    
    // emptying variable
    csv_file.lines = [];
    csv_file.headers = [];
    
    //We parse the 10 first lines only
    Papa.parse(f.files[0], {
            comments: true,
            header: true,
            skipEmptyLines: true,
            preview: 10,
            worker: true,
            step: function(results) {
                csv_file.lines.push(results.data);
                if (csv_file.headers.length == 0)
                    csv_file.headers = results.meta.fields;
            },
            complete: function() {
                //Reading columns and first line
                var body = $('#datasets_creation_from_file_columns').find('tbody');
                body.empty();
                
                console.log(csv_file.lines[0]);
                csv_file.headers.forEach( function(col, index) {
                    var new_row = $(body[0].insertRow(-1));
                    new_row.load('templates/creation_dataset_row.html', function () {
                        var inputs = new_row.find('input');
                        inputs[0].value = col;
                        
                        var select = new_row.find('select');
                        var type_select = $(select[0]);
                        var tags_select = $(select[1]);
                        
                        new_row.find("td:last").remove();
                        
                        type_select.attr('id', 'datasets_ff_type_select_'+index);
                        type_select.attr('onchange', "datasets_type_change("+index+", this);");
                        type_select.val(getType(csv_file.lines[0][0][col]));
                        
                        tags_select.attr('id', 'datasets_ff_tags_select_'+index);
                        datasets_fill_select_tags(tags_select);
                        
                        $('#datasets_ff_type_select_'+index).selectpicker('refresh');
                        $('#datasets_ff_tags_select_'+index).selectpicker('refresh');
                        $('#datasets_ff_tags_select_'+index).change(datasets_tags_select_change);
                        $('#datasets_new_tag_select_group').selectpicker('refresh');
                        $('#datasets_new_tag_name').val("");
                    });
                });
            },
            error: function(error) {
                console.log(error);
            }
            
    });
}


/////////////////////////////////////////////////////////////////////////////////////
// ROWS FROM SCRATCH

function datasets_add_a_row(dataset_id) {
    var body = $('#'+dataset_id).find('tbody');
    var nb_rows = body[0].childElementCount - 1;
    var new_row = $(body[0].insertRow(nb_rows));
    new_row.attr('id', 'datasets_row_' + global_ids);
    
    new_row.load('templates/creation_dataset_row.html', function () {
        var last_cel = $(new_row[0].childNodes[new_row[0].childNodes.length - 1]);
        $(last_cel.find('span')[0]).attr('onclick', "$('#datasets_row_"+global_ids+"').remove();");
        
        var select = new_row.find('select');
        var type_select = $(select[0]);
        var tags_select = $(select[1]);
        
        type_select.attr('id', 'datasets_fs_type_select_'+global_ids);
        type_select.attr('onchange', "datasets_type_change("+global_ids+",this);");
        
        tags_select.attr('id', 'datasets_fs_tags_select_'+global_ids);
        datasets_fill_select_tags(tags_select);
        
        $('#datasets_fs_type_select_'+global_ids).selectpicker('refresh');
        $('#datasets_fs_tags_select_'+global_ids).selectpicker('refresh');
        $('#datasets_fs_tags_select_'+global_ids).change(datasets_tags_select_change);
        $('#datasets_new_tag_select_group').selectpicker('refresh');
        $('#datasets_new_tag_name').val("");
        
        global_ids ++;
    });
    
    return new_row;
}

/////////////////////////////////////////////////////////////////////////////////////
// TAGS

function datasets_fill_select_tags(tags_select) {
    tags_select.append('<option data-hidden="true" value="Select..."></option>')
    $('#datasets_new_tag_select_group').empty();
    columns_tags_list.forEach(function (group) {
        group_elem = '<optgroup label="' + group[0] + '">';
        group[1].forEach(function (tag) {
            group_elem += '<option value="' + tag + '">' + tag + '</option>';
        });
        group_elem += '</optgroup>';
        tags_select.append(group_elem);
        $('#datasets_new_tag_select_group').append('<option value="'+group[0]+'">'+group[0]+'</option>');
    });
    tags_select.append('<option data-icon="glyphicon glyphicon-plus" value="datasets_add_tag" data-subtext="add a new tag"></option>')
}


function datasets_tags_select_change(event) {
    current_select  = $(event.target);
    if (current_select.val() && current_select.val().indexOf("datasets_add_tag") >= 0) {
        var last_option = current_select[0].options[current_select[0].options.length-1];
        last_option.selected = false;
        $(current_select).selectpicker('refresh');
        $('#datasets_new_tag_modal').modal();
    }
}

function datasets_new_tag() {
    var tag     = $('#datasets_new_tag_name').val();
    
    if (tag.replace(/ /g, '') == "") {
        return;
    }
    
    var selects = $('*').filter(function() {
        return this.id.match(/.*_tags_select_.*/);
    });
    var group = "others";
    $.each(selects, function(i, select) {
        var optGroups = $(select).find('optgroup');
        for (var i=0; i < optGroups.length; i++) {
            if (optGroups[i].label == group) {
                var option = $('<option/>');
                option.attr({ 'value': tag }).text(tag);
                
                //selecting the tag
                if (select.id == current_select[0].id) {
                    $(option).prop('selected', true);
                }
                $(optGroups[i]).append(option);
            }
        }
        $(select).selectpicker("refresh");
    });
    
    //Global variable
    columns_tags_list.forEach( function (tags_group) {
        if (tags_group[0] == group) {
            tags_group[1].push(tag);
        }
    });
    
    $('#datasets_new_tag_name').val("");
}

/////////////////////////////////////////////////////////////////////////////////////
// DATES AND TYPES

function datasets_type_change(row_id, from) {
    if (from.id.indexOf("ff") >= 0) {
        var td = from.parentNode.parentNode;
        var select = $(from);
        if (select.val() == 'date') {
            if (td.childElementCount == 1) {
                var tmp = document.createElement('input');
                $(tmp).load("templates/date_format_input.html", function (input) {
                    var div = $(document.createElement('div'));
                    div.attr("id", "datasets_date_format_div_"+row_id);
                    div.append($(input));
                    $(td).append(div);
                    $(tmp).remove();
                    datasets_check_date_format(row_id, div);
                    var data = csv_file.lines[0][0][csv_file.headers[row_id]];
                    $(div[0].children[3].children[0]).val(data);
                    $(div[0].children[1].children[0]).on('keyup', {'row_id': row_id, 'div': div}, datasets_update_date_format);
               });
            }
        }
        else if (td.childElementCount > 1) {
            td.children[1].remove();
        }
    }
}


function datasets_check_date_format(row_id, div) {
    
    var format = $(div[0].children[1].children[0]).val();
    var date = csv_file.lines[0][0][csv_file.headers[row_id]];
    var m2 = moment(date, format);
    if (! m2._isValid) {
        $(div[0].children[1]).attr("class", "has-error");
        $(div[0].children[5]).attr("class", "has-error");
        $(div[0].children[5].children[0]).val("Invalid format");
    }
    else {
        $(div[0].children[1]).attr("class", "");
        $(div[0].children[5]).attr("class", "has-success");
        $(div[0].children[5].children[0]).val(m2._d);
    }
}


function datasets_update_date_format(event) {
    datasets_check_date_format(event.data.row_id, event.data.div);
}


function getType(str){
    if (typeof str !== 'string') str = str.toString();
    var nan = isNaN(Number(str));
    var isfloat = /^\d*(\.|,)\d*$/;
    var commaFloat = /^(\d{0,3}(,)?)+\.\d*$/;
    var dotFloat = /^(\d{0,3}(\.)?)+,\d*$/;
    var date = /^\d{0,4}(\.|\/)\d{0,4}(\.|\/)\d{0,4}$/;
    
    if (!nan){
        if (parseFloat(str) === parseInt(str)) return "int32";
        else return "float32";
    }
    else if (isfloat.test(str) || commaFloat.test(str) || dotFloat.test(str)) return "float32";
    else if (date.test(str)) return "date";
    else return "string";
}
