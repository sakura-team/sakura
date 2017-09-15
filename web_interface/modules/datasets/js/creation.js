//Code started by Michael Ortega for the LIG
//August, 22nd, 2017

function datasets_send_new(database_id) {
    
    //Reading first main elements: name and description
    var name = $('#datasets_creation_name').val();
    var desc = $('#datasets_creation_description').val();
    if ( name == "") {
        alert("We cannot create a dataset with an empty name !");
        return;
    }
    var dataset = { 'name': name, 'description': desc, 'columns': [] };
    
    
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
    
    //Data from each row
    for (var i=0; i< nb_cols; i++) {
        var inputs = $(cols[i]).find('input');
        var label = $(inputs[0]).val();
        
        if (label == 'Column Name') {
            alert("Each column should have an explicit name");
            return;
        }
        
        var type = $($(cols[i]).find('select')[0]).val();
        var desc = $(inputs[1]).val();
        var tags = $(inputs[2]).val();
        dataset.columns.push([label, type, desc, tags]);
    };
    console.log("Params", dataset);
    
    //Sending the new dataset description
    sakura.common.ws_request('new_database', [database_id, dataset], {}, function(result) {
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
            console.log(s_name[s_name.length - 1]);
            alert("The extension of this file is not .csv !! Please be sure it is a csv file, and rename it with extension.");
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
        alert(txt);
        return;
    }
    else if (b_lines.length > 20) {
        alert("Considering the separator, many lines (more than 20) \ndo not have the correct number of columns !");
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
            var buttons = new_row.find('button');
            var select = new_row.find('select');
            inputs[0].value = col;
            
            buttons[buttons.length - 1].remove();
            
            select.val(getType(first_line[index]));
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
        $(last_cel.find('button')[0]).attr('onclick', 'datasets_delete_row('+global_ids+');');
        global_ids ++;
    });    
    
    return new_row;
}


function datasets_delete_row(row_id) {
    $('#datasets_row_'+row_id).remove();
}


function getType(str){
    if (typeof str !== 'string') str = str.toString();
    var nan = isNaN(Number(str));
    var isfloat = /^\d*(\.|,)\d*$/;
    var commaFloat = /^(\d{0,3}(,)?)+\.\d*$/;
    var dotFloat = /^(\d{0,3}(\.)?)+,\d*$/;
    var date = /^\d{0,4}(\.|\/)\d{0,4}(\.|\/)\d{0,4}$/;
    var email = /^[A-za-z0-9._-]*@[A-za-z0-9_-]*\.[A-Za-z0-9.]*$/;
    var phone = /^\+\d{2}\/\d{4}\/\d{6}$/g;
    if (!nan){
        if (parseFloat(str) === parseInt(str)) return "integer";
        else return "float";
    }
    else if (isfloat.test(str) || commaFloat.test(str) || dotFloat.test(str)) return "float";
    else if (date.test(str)) return "date";
    else {
        if (email.test(str)) return "e-mail";
        else if (phone.test(str)) return "phone";
        else return "string";
    }
}