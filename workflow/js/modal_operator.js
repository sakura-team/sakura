//Code started by Michael Ortega for the LIG
//January 16th, 2017

function fill_all(id) {
    fill_inputs(id);
    fill_params(id);
    fill_outputs(id);
}

function fill_inputs(id) {
    var cl_id = id.split("_")[1];
    var inst_id = parseInt(id.split("_")[2]);
    var nb_inputs = global_ops_cl[cl_id]['inputs'];
    var nb_outputs = global_ops_cl[cl_id]['outputs'];
    
    var d = document.getElementById('modal_'+id+'_tab_inputs');
    if (nb_inputs == 0) {
        d.innerHTML = '<br><p align="center"> No Inputs</p>';
    }
    else {
        ws_request('get_operator_input_range', [inst_id, 0, 0, 1000], {}, function (result) {
            if (result) {
                s = '<table border=1>\n';
                result.forEach( function(row) {
                    s += '<tr>\n';
                    row.forEach( function(col) {
                        s += '<td>'+col; 
                    });
                });
                s += '</table>';
                d.innerHTML = '<br>'+s;
            }
            else
                d.innerHTML = '<br><p align="center"> No Inputs for Now !!</p>';
        });
        
    }
}


function fill_params(id) {
    ws_request('get_operator_instance_info', [parseInt(id.split("_")[2])], {}, function (result) {
            var d = document.getElementById('modal_'+id+'_tab_params');
            while (d.firstChild) {
                d.removeChild(d.firstChild);
            }
            
            var index = -1;
            
            if (result['parameters'].length == 0) {
                d.innerHTML = '<br><p align="center"> No Params</p>';
            }
            
            result['parameters'].forEach( function (item) {
                index++;
                
                if (item['issue']) {
                    d.innerHTML = '<br><p align="center">'+item['issue']+'</p>';
                }
                else {
                    if (item['gui_type'] == 'COMBO') {
                        var ndiv = document.createElement('div');
                        ndiv.setAttribute('align', 'center');
                        ndiv.id = 'modal_'+id+'_tab_params_'+index;
                        var select_id = 'modal_'+id+'_tab_params_select_'+index;
                        var s = '<br>'+item['label']+' <select id="'+select_id+'" onChange="params_onChange(\''+id+'\', '+index+',\''+select_id+'\');"><option></option>';
                        item['possible_values'].forEach( function (item2) {
                            s += ' <option> '+item2[0]+' - '+item2[1]+'</option>';
                        });
                        s += ' </select>';
                        ndiv.innerHTML = s;
                        d.appendChild(ndiv);
                    }
                    else
                        console.log("Ouch !!!");
                }
            });
    });
}


function params_onChange(op_id, param_index, select_id) {
    var index = document.getElementById(select_id).selectedIndex;
    if (index == 0)
        return;
    
    ws_request('get_operator_instance_info', [parseInt(op_id.split("_")[2])], {}, function (result) {
        //var options = document.getElementById(select_id).options;
        var param_value = result['parameters'][param_index]['possible_values'][index-1][0];
        
        //var param_value = options[index].index;
        ws_request('set_parameter_value', [parseInt(op_id.split("_")[2]), param_index, param_value], {}, function (result) {
            if (result)
                console.log(result);
            else
                fill_outputs(op_id);
        });
    });
}


function fill_outputs(id) {
    var cl_id = parseInt(id.split("_")[1]);
    var inst_id = parseInt(id.split("_")[2]);
    var nb_outputs = global_ops_cl[cl_id]['outputs'];
    
    var d = document.getElementById('modal_'+id+'_tab_outputs');
    if (nb_outputs == 0) {
        d.innerHTML = '<br><p align="center"> No Outputs</p>';
    }
    else {
        ws_request('get_operator_output_range', [inst_id, 0, 0, 1000], {}, function (result) {
            s = '<table border=1>\n';
            result.forEach( function(row) {
                s += '<tr>\n';
                row.forEach( function(col) {
                    s += '<td>'+col; 
                });
            });
            s += '</table>';
            d.innerHTML = '<br>'+s;
        });
        
    }
}