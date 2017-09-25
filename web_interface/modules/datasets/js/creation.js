//Code started by Michael Ortega for the LIG
//August, 22nd, 2017


var current_select  = null;

function datasets_send_new(database_id) {
    
    
    //Reading first main elements: name and description
    var name = $('#datasets_creation_name').val();
    var desc = $('#datasets_creation_description').val();
    if ( name == "") {
        datasets_alert("Dataset Name", "We cannot create a dataset with an empty name !");
        return;
    }
    
    
    //Which table body ?
    var body = $('#datasets_creation_from_scratch_columns').find('tbody');
    var cols = body.find('tr');
    var nb_cols = cols.length - 1;
    $('#datasets_creation_from_file_pan').attr("class").split(' ').forEach( function (elt) {
        if (elt == 'active') {
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
        console.log(result);
    });
    
    $("#datasets_creation_modal").modal('hide');
}


function on_file_selected(f) {
    var fr = new FileReader();
    
    fr.onload = function(e) {
        //check the name: should have .csv extension
        
        var s_name = f.value.split('.');
        if (s_name[s_name.length - 1] != 'csv' && s_name[s_name.length - 1] != 'CSV') {
            datasets_alert("File Extension Issue", "The extension of this file is not .csv !!\nPlease be sure it is a csv file, and rename it with extension.");
            return;
        }
        file_lines = e.target.result.split(/[\r\n]+/g);
        
        //ask for the separator
        $('#datasets_csv_separator_modal').modal();
    };
    
    fr.readAsText(f.files[0]);
}


function datasets_parse_file() {
    
    //read separator
    var sep = $('#datasets_csv_separator')[0].value;
    
    //check the columns and the first line (dealing with comments)
    var index  = 0
    var cols =['#'];    
    while (cols[0].indexOf('#') >= 0) {
        cols = file_lines[index].split(sep);
        index ++;
    }
    
    //separator tests
    var b_lines = [];
    for (var i = index; i<file_lines.length; i++) {
        line = file_lines[i].split(sep);
        if (cols.length != line.length && file_lines[i][0] != '#' && file_lines[i].length != 0) {
            b_lines.push(parseInt(i));
        }
    }
    
    if (b_lines.length > 0 && b_lines.length < 20) {
        var txt = "Considering the separator, ";
        if (b_lines.length == 1) 
            txt += "\nline: ";
        else 
            txt += "\nlines: ";
        b_lines.forEach( function(item) {
            txt += ""+item+",";
        });
        if (b_lines.length == 1) 
            txt += "\ndoes ";
        else
            txt += "\ndo ";
        txt += "not have the correct number of columns (line indices start from 0)";
        datasets_alert("Columns Issue",txt);
        return;
    }
    else if (b_lines.length > 20) {
        datasets_alert("Columns Issue","Considering the separator, many lines (more than 20) \ndo not have the correct number of columns !");
        return;
    }
    
    //Dealing with first comments 
    var first_line = ['#'];
    while (first_line[0].indexOf('#') >= 0) {
        first_line = file_lines[index].split(sep);
        index ++;
    }
    
    //Reading columns and first line
    var body = $('#datasets_creation_from_file_columns').find('tbody');
    body.empty();
    cols.forEach( function(col, index) {
        var new_row = $(body[0].insertRow(-1));
        new_row.load('creation_dataset_row.html', function () {
            var inputs = new_row.find('input');
            var buttons = new_row.find('span');
            var select = new_row.find('select');
            
            new_row.find("td:last").remove();
            var type_select = $(select[0]);
            var tags_select = $(select[1]);
            
            type_select.attr('id', 'datasets_ff_type_select_'+index);
            type_select.attr('onchange', "datasets_type_change("+index+", this);");
            type_select.val(getType(first_line[index]));
            
            tags_select.attr('id', 'datasets_ff_tags_select_'+index);
            
            tags_select.append('<option data-hidden="true" value="Select..."></option>')
            columns_tags_list.forEach(function (group) {
                group_elem = '<optgroup label="' + group[0] + '">';
                group[1].forEach(function (tag) {
                    group_elem += '<option value="' + tag + '">' + tag + '</option>';
                });
                group_elem += '</optgroup>';
                tags_select.append(group_elem);
            });
            tags_select.append('<option data-icon="glyphicon glyphicon-plus" value="datasets_add_tag"></option>')
            
            inputs[0].value = col;
            
            $('#datasets_ff_type_select_'+index).selectpicker('refresh');
            $('#datasets_ff_tags_select_'+index).selectpicker('refresh');
        });
    });
}


function datasets_add_a_row(dataset_id) {
    var body = $('#'+dataset_id).find('tbody');
    var nb_rows = body[0].childElementCount - 1;
    var new_row = $(body[0].insertRow(nb_rows));
    new_row.attr('id', 'datasets_row_' + global_ids);
    
    new_row.load('creation_dataset_row.html', function () {
        var last_cel = $(new_row[0].childNodes[new_row[0].childNodes.length - 1]);
        $(last_cel.find('span')[0]).attr('onclick', "$('#datasets_row_"+global_ids+"').remove();");
        
        var select = new_row.find('select');
        var type_select = $(select[0]);
        var tags_select = $(select[1]);
        type_select.attr('id', 'datasets_fs_type_select_'+global_ids);
        type_select.attr('onchange', "datasets_type_change("+global_ids+",this);");
        
        tags_select.attr('id', 'datasets_fs_tags_select_'+global_ids);
        
        tags_select.append('<option data-hidden="true" value="Select..."></option>')
        var existing_groups = []
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
        tags_select.append('<option data-icon="glyphicon glyphicon-plus" value="datasets_add_tag" data-subtext="add new tags"></option>')
        
        $('#datasets_fs_type_select_'+global_ids).selectpicker('refresh');
        $('#datasets_fs_tags_select_'+global_ids).selectpicker('refresh');
        $('#datasets_fs_tags_select_'+global_ids).change(datasets_tags_select_change);
        $('#datasets_new_tag_select_group').selectpicker('refresh');
        $('#datasets_new_tag_name').val("");
        
        global_ids ++;
    });
    
    return new_row;
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
    var group   = $('#datasets_new_tag_select_group').val()
    var tag     = $('#datasets_new_tag_name').val();
    
    if (tag.replace(/ /g, '') == "") {
        return;
    }
    
    var selects = $('*').filter(function() {
        return this.id.match(/.*_tags_select_.*/);
    });
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
    
    
    columns_tags_list.forEach( function (tags_group) {
        if (tags_group[0] == group) {
            tags_group[1].push(tag);
        }
    });
    
    $('#datasets_new_tag_name').val("");
}


function datasets_type_change(row_id, from) {
    var td = from.parentNode.parentNode;
    var select = $(from);
    if (select.val() == 'date') {
        if (td.childElementCount == 1) {
            var tmp = document.createElement('input');
            $(tmp).load("date_format_input.html", function (input) {
                $(td).append(input);
                $(tmp).remove();
           });
        }
    }
    else if (td.childElementCount > 1) {
        td.children[1].remove();
    }
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
