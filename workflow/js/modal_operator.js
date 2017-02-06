//Code started by Michael Ortega for the LIG
//January 16th, 2017


var max_rows = 20;

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
        ws_request('get_operator_instance_info', [inst_id], {}, function (result_info) {
            ws_request('get_operator_input_range', [inst_id, 0, 0, 1000], {}, function (result_input) {
                if (result_input) {
                    s = '<table class="table table-hover table-striped table-sm">\n<thead><tr>';
                    result_info['inputs'][0]['columns'].forEach( function(item) {
                        s+= '<th>'+item[0]+'</th>';
                    });
                    s += '</tr></thead><tbody>';
                    result_input.forEach( function(row) {
                        s += '<tr>\n';
                        row.forEach( function(col) {
                            s += '<td>'+col+'</td>'; 
                        });
                        s += '</tr>';
                    });
                    s += '</tbody></table>';
                    d.innerHTML = '<br>'+s;
                }
                else
                    d.innerHTML = '<br><p align="center"> No Inputs for Now !!</p>';
            });
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
        ws_request('set_parameter_value', [parseInt(op_id.split("_")[2]), param_index, param_value], {}, function (result2) {
            if (result2)
                console.log(result2);
            else
                fill_outputs(op_id);
        });
    });
}


function fill_outputs(id) {
    var cl_id = parseInt(id.split("_")[1]);
    var inst_id = parseInt(id.split("_")[2]);
    var nb_outputs = global_ops_cl[cl_id]['outputs'];
    
    ws_request('get_operator_instance_info', [inst_id], {}, function (result_info) {
        var d = document.getElementById('modal_'+id+'_tab_outputs');
        while (d.firstChild) {
            d.removeChild(d.firstChild);
        }
        //console.log(result_info['outputs'][0]['label']);
        if (nb_outputs == 0) {
            d.innerHTML = '<br><p align="center"> No Outputs</p>';
        }
        else {
            var div_tab = document.createElement('div');
            div_tab.className = 'modal-body';
            div_tab.id = id+'_outputs';
            
            var ul          = document.createElement('ul');
            var tab_content = document.createElement('div');
            ul.className            = "nav nav-tabs";
            tab_content.className   = "tab-content";
            s = '<li class="active"> \
                    <a data-toggle="tab" href="#'+id+'_output_'+0+'" onclick=\'fill_one_output(\"'+id+'\",'+0+','+0+','+max_rows+');\'>'+result_info['outputs'][0]['label']+'</a></li>';
            for (var i =1; i < nb_outputs; i++) {
                s += '<li><a data-toggle="tab" href="#'+id+'_output_'+i+'" onclick=\'fill_one_output(\"'+id+'\",'+i+','+0+','+max_rows+');\'>'+result_info['outputs'][i]['label']+'</a></li>';
            }
            ul.innerHTML = s;
            
            s = '<div id="'+id+'_output_'+0+'" class="tab-pane fade in active"></div>';
            for (var i =1; i < nb_outputs; i++)
                s += '<div id="'+id+'_output_'+i+'" class="tab-pane fade in active"></div>';
            tab_content.innerHTML = s;
            
            div_tab.appendChild(ul);
            div_tab.appendChild(tab_content);
            d.appendChild(div_tab);
            
            fill_one_output(id, 0, 0, max_rows);
        }
    });
}


function fill_one_output(id, id_output, min, max) {
    var div = document.getElementById(id+'_output_'+id_output);
    var inst_id = parseInt(id.split("_")[2]);
    
    //Emptying the div
    while (div.firstChild) {
        div.removeChild(div.firstChild);
    }
    
    ws_request('get_operator_instance_info', [inst_id], {}, function (result_info) {        
        ws_request('get_operator_output_range', [inst_id, id_output, min, max], {}, function (result_output) {
            s = '<table class="table table-sm table-hover table-striped">\n<thead><tr>';
            s += '<th>#</th>';
            result_info['outputs'][id_output]['columns'].forEach( function(item) {
                s+= '<th>'+item[0]+'</th>';
            });
            s += '</tr></thead><tbody>';
            
            var index = 0;
            result_output.forEach( function(row) {
                s += '<tr>\n';
                s += '<td>'+parseInt(index+min)+'</td>';
                row.forEach( function(col) {
                    s += '<td>'+col+'</td>'; 
                });
                s += '</tr>';
                index += 1;
            });
            s += '</tbody></table>';
            
            if (result_info['outputs'][id_output]['length'] != null) {
                var nb_pages = parseInt(result_info['outputs'][id_output]['length']/(max-min));
                if (nb_pages*(max-min) < result_info['outputs'][id_output]['length'])
                    nb_pages++;
                if (nb_pages > 1) {
                    s+= '   <ul class="pagination pagination-sm">\n';
                    for (var i=0; i< nb_pages; i++)
                        s+= '<li><a style="cursor: pointer;" onclick=\'fill_one_output(\"'+id+'\",'+id_output+','+(i*(max-min))+','+((i+1)*(max-min))+');\'>'+(i+1)+'</a></li>\n';
                    s+= '   </ul>';
                }
            }
            else {
                s+= '   <ul class="pagination pagination-sm">\n';
                if (min > 0) {
                    s += '<li><a style="cursor: pointer;" onclick=\'fill_one_output(\"'+id+'\",'+id_output+','+0+','+(max-min)+');\'>'+'<<'+'</a></li>\n';
                    s += '<li><a style="cursor: pointer;" onclick=\'fill_one_output(\"'+id+'\",'+id_output+','+(min - (max-min))+','+(max - (max-min))+');\'>'+'<'+'</a></li>\n';
                }
                if (!(result_output.length < max-min))
                    s += '<li><a style="cursor: pointer;" onclick=\'fill_one_output(\"'+id+'\",'+id_output+','+(min + (max-min))+','+(max + (max-min))+');\'>'+'>'+'</a></li>\n';
                s+= '   </ul>';
            }
            
            /*s += '  <ul class="pagination pagination-sm"> \
                        <li class="active"><a style="cursor: pointer;" onclick="not_yet();">1</a></li> \
                        <li><a style="cursor: pointer;" onclick="not_yet();">2</a></li> \
                        <li><a style="cursor: pointer;" onclick="not_yet();">3</a></li> \
                        <li><a style="cursor: pointer;" onclick="not_yet();">...</a></li> \
                        <li><a style="cursor: pointer;" onclick="not_yet();">54</a></li> \
                    </ul>';
            */
            div.innerHTML = s;
        });
    });
}
