//Code started by Michael Ortega for the LIG
//December 06th, 2016


//This function ask about all the operators, and then update the "operators selection" modal
function select_op_open_modal() {
    
    //cleaning
    $('#select_op_tags_select').empty();
    $('#select_op_names_select').empty();
    document.getElementById('select_op_panel_title').value = '';
    
    //Before opening the modal, we have to ask about the existing operators, and then make the tags list
    ws_request('list_operators_classes', [], {}, function (result) {
        var tags_list = [];
        var sostl = document.getElementById('select_op_tags_select');
        var sosnl = document.getElementById('select_op_names_select');
        
        var arr = JSON.parse(JSON.stringify(result));
        for (var i=0; i<arr.length; i++) {
            arr[i][3].forEach( function (item) {
                    if (tags_list.indexOf(item) == -1) {
                        tags_list.push(item);
                        var option = document.createElement("option");
                        option.text = item;
                        sostl.add(option);
                    }
                });
            var option = document.createElement("option");
            option.text = arr[i][1];
            option.setAttribute("data-subtext", arr[i][2]);
            console.log(option);
            sosnl.add(option);
        }
        $('#select_op_tags_select').selectpicker('refresh');
        $('#select_op_names_select').selectpicker('refresh');
        $('#modal_op_selector').modal();
    });
}


function select_op_on_change_tag() {
    var ops = document.getElementById("select_op_tags_select").options;
    for (var i=0;i<ops.length;i++) {
        console.log(ops[i].selected);
    }
}


function select_op_on_change_name() {
    var ops = document.getElementById("select_op_names_select").options;
    for (var i=0;i<ops.length;i++) {
        console.log(ops[i].selected);
    }
}