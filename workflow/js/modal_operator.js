//Code started by Michael Ortega for the LIG
//January 16th, 2017

function fill_all(id) {
    fill_inputs(id);
    fill_params(id);
    fill_outputs(id);
}

function fill_inputs(id) {
    var cl_id = id.split("_")[1];
    var nb_inputs = global_ops_cl[cl_id]['inputs'];
    var nb_outputs = global_ops_cl[cl_id]['outputs'];
    
    var d = document.getElementById('modal_'+id+'_tab_inputs');
    if (nb_inputs == 0) {
        d.innerHTML = '<br><p align="center"> No Inputs</p>';
    }
    else
        d.innerHTML = '<br><p align="center"> Coming soon</p>';
}


function fill_params(id) {
    ws_request('get_operator_instance_info', [parseInt(id.split("_")[2])], {}, function (result) {
            var d = document.getElementById('modal_'+id+'_tab_params');
            while (d.firstChild) {
                d.removeChild(d.firstChild);
            }
            
            console.log(result['parameters']);
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
                        var s = '<br>'+item['label']+' <select>';
                        item['possible_values'].forEach( function (item2) {
                            s += ' <option> '+item2[0]+' - '+item2[1]+'</option>';
                        });
                        s += ' </select>';
                        ndiv.innerHTML = s;
                        console.log(s);
                        d.appendChild(ndiv);
                    }
                    else
                        console.log("Ouch !!!");
                }
            });
    });
}


function fill_outputs(id) {
    var cl_id = id.split("_")[1];
    var nb_inputs = global_ops_cl[cl_id]['inputs'];
    var nb_outputs = global_ops_cl[cl_id]['outputs'];
    
    var d = document.getElementById('modal_'+id+'_tab_outputs');
    if (nb_outputs == 0) {
        d.innerHTML = '<br><p align="center"> No Outputs</p>';
    }
    else {
        d.innerHTML = '<br><p align="center"> Coming soon</p>';
    }
}