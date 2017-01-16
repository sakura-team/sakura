//Code started by Michael Ortega for the LIG
//January 16th, 2017

function fill_inputs(id) {
    var cl_id = id.split("_")[1];
    var nb_inputs = global_ops_cl[cl_id]['inputs'];
    var nb_outputs = global_ops_cl[cl_id]['outputs'];
    
    var d = document.getElementById('modal_'+id+'_tab_inputs');
    if (nb_inputs == 0) {
        d.innerHTML = '<br><p align="center"> No Inputs</p>';
    }
    else
        d.innerHTML = 'INPUTS HERE';
}


function fill_params(id) {
    ws_request('get_operator_instance_info', [parseInt(id.split("_")[2])], {}, function (result) {
        
            result['parameters'].forEach( function (item) {
            
            var d = document.getElementById('modal_'+id+'_tab_params');
            console.log(d);
            
            if (item['issue']) {
                d.innerHTML = '<br><p align="center">'+item['issue']+'</p>';
            }
            else {
                if (item['gui_type'] == 'COMBO') {
                    d.innerHTML = ' <div align="center"> \
                                        <select class="selectpicker" data-width="200px" data-live-search="true"/> \
                                    </div>';
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
        /*ws_request('', [], {}, function(result) {
            console.log(result);
        });*/
        console.log('TODO');
    }
}