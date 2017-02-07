//Code started by Michael Ortega for the LIG
//January 16th, 2017


var max_rows = 20;

function fill_all(id) {
    fill_in_out('input', id);
    fill_params(id);
    fill_in_out('output', id);
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
                fill_in_out('output', op_id);
        });
    });
}


function fill_in_out(in_out, id) {
    var inst_id     = parseInt(id.split("_")[2]);    
    var d           = document.getElementById('modal_'+id+'_tab_'+in_out+'s');
    
    //cleaning
    while (d.firstChild) {
        d.removeChild(d.firstChild);
    }
    
    //infos
    ws_request('get_operator_instance_info', [inst_id], {}, function (result_info) {
        var nb_in_out = result_info[in_out+'s'].length;
        
        if (nb_in_out == 0) {
            d.innerHTML = '<br><p align="center"> No '+in_out+'s</p>';
        }
        else {
            var div_tab = document.createElement('div');
            div_tab.className = 'modal-body';
            div_tab.id = id+'_'+in_out+'s';
            
            var ul          = document.createElement('ul');
            var tab_content = document.createElement('div');
            ul.className            = "nav nav-tabs";
            tab_content.className   = "tab-content";
            s = '<li class="active"> \
                    <a data-toggle="tab" href="#'+id+'_'+in_out+'_'+0+'" onclick=\'fill_one_in_out(\"'+in_out+'\",\"'+id+'\",'+0+','+0+','+max_rows+');\'>'+result_info[in_out+'s'][0]['label']+'</a></li>';
            for (var i =1; i < nb_in_out; i++) {
                s += '<li><a data-toggle="tab" href="#'+id+'_'+in_out+'_'+i+'" onclick=\'fill_one_in_out(\"'+in_out+'\",\"'+id+'\",'+i+','+0+','+max_rows+');\'>'+result_info[in_out+'s'][i]['label']+'</a></li>';
            }
            ul.innerHTML = s;
        
            s = '<div id="'+id+'_'+in_out+'_'+0+'" class="tab-pane fade in active"></div>';
            for (var i =1; i < nb_in_out; i++)
                s += '<div id="'+id+'_'+in_out+'_'+i+'" class="tab-pane fade in active"></div>';
            tab_content.innerHTML = s;
        
            div_tab.appendChild(ul);
            div_tab.appendChild(tab_content);
            d.appendChild(div_tab);
        
            fill_one_in_out(in_out, id, 0, 0, max_rows);
        }
    });
}


function fill_one_in_out(in_out, id, id_in_out, min, max) {
    var d = document.getElementById(id+'_'+in_out+'_'+id_in_out);
    var inst_id = parseInt(id.split("_")[2]);
    
    //cleaning
    while (d.firstChild) {
        d.removeChild(d.firstChild);
    }
    
    //infos
    ws_request('get_operator_instance_info', [inst_id], {}, function (result_info) {        
        ws_request('get_operator_'+in_out+'_range', [inst_id, id_in_out, min, max], {}, function (result_in_out) {
            s = '<table class="table table-sm table-hover table-striped">\n<thead><tr>';
            s += '<th>#</th>';
            result_info[in_out+'s'][id_in_out]['columns'].forEach( function(item) {
                s+= '<th>'+item[0]+'</th>';
            });
            s += '</tr></thead><tbody>';
            
            var index = 0;
            result_in_out.forEach( function(row) {
                s += '<tr>\n';
                s += '<td>'+parseInt(index+min)+'</td>';
                row.forEach( function(col) {
                    s += '<td>'+col+'</td>'; 
                });
                s += '</tr>';
                index += 1;
            });
            s += '</tbody></table>';
            
            if (result_info[in_out+'s'][id_in_out]['length'] != null) {
                var nb_pages = parseInt(result_info[in_out+'s'][id_in_out]['length']/(max-min));
                if (nb_pages*(max-min) < result_info[in_out+'s'][id_in_out]['length'])
                    nb_pages++;
                if (nb_pages > 1 && nb_pages < 10) {
                    s+= '   <ul class="pagination pagination-sm">\n';
                    for (var i=0; i< nb_pages; i++)
                        s+= '<li><a style="cursor: pointer;" onclick=\'fill_one_in_out(\"'+in_out+'\",\"'+id+'\",'+id_in_out+','+(i*(max-min))+','+((i+1)*(max-min))+');\'>'+(i+1)+'</a></li>\n';
                    s+= '   </ul>';
                }
                else if (nb_pages > 10) {
                    var current_page = Math.floor(min/(max-min));
                    s+= '   <ul class="pagination pagination-sm">\n';
                    if (current_page > 0) {
                        s += '<li><a style="cursor: pointer;" onclick=\'fill_one_in_out(\"'+in_out+'\",\"'+id+'\",'+id_in_out+','+0+','+(max-min)+');\'><span class="glyphicon glyphicon-fast-backward" style="color: grey; cursor: pointer;"></a></li>\n';
                        s += '<li><a style="cursor: pointer;" onclick=\'fill_one_in_out(\"'+in_out+'\",\"'+id+'\",'+id_in_out+','+(min - (max-min))+','+(max - (max-min))+');\'><span class="glyphicon glyphicon-backward" style="color: grey; cursor: pointer;"></a></li>\n';
                    }
                    else {
                        s += '<li class="disabled"><a style="cursor: pointer;"><span class="glyphicon glyphicon-fast-backward" style="color: grey; cursor: pointer;"></a></li>\n';
                        s += '<li class="disabled"><a style="cursor: pointer;"><span class="glyphicon glyphicon-backward" style="color: grey; cursor: pointer;"></a></li>\n';
                    }
                    var up_limit = current_page+10;
                    if (up_limit > nb_pages) {
                        up_limit = nb_pages;
                    }
                    for (var i=current_page; i< up_limit; i++)
                        if (i == current_page) {
                            s+= '<li class="disabled"><a style="cursor: pointer;");\'>'+(i+1)+'</a></li>\n';
                        }
                        else {
                            s+= '<li><a style="cursor: pointer;" onclick=\'fill_one_in_out(\"'+in_out+'\",\"'+id+'\",'+id_in_out+','+(i*(max-min))+','+((i+1)*(max-min))+');\'>'+(i+1)+'</a></li>\n';
                        }
                    
                    if (up_limit < nb_pages) {
                        s += '<li><a style="cursor: pointer;" onclick=\'fill_one_in_out(\"'+in_out+'\",\"'+id+'\",'+id_in_out+','+((current_page+1)*(max-min))+','+((current_page+2)*(max-min))+');\'><span class="glyphicon glyphicon-forward" style="color: grey; cursor: pointer;"></a></li>\n';
                        s += '<li><a style="cursor: pointer;" onclick=\'fill_one_in_out(\"'+in_out+'\",\"'+id+'\",'+id_in_out+','+((nb_pages-1)*(max-min))+','+((nb_pages)*(max-min))+');\'><span class="glyphicon glyphicon-fast-forward" style="color: grey; cursor: pointer;"></a></li>\n';
                    }
                    s+= '   </ul>';
                }
            }
            else {
                s+= '   <ul class="pagination pagination-sm">\n';
                if (min > 0) {
                    s += '<li><a style="cursor: pointer;" onclick=\'fill_one_in_out(\"'+in_out+'\",\"'+id+'\",'+id_in_out+','+0+','+(max-min)+');\'><span class="glyphicon glyphicon-fast-backward" style="color: grey; cursor: pointer;"></a></li>\n';
                    s += '<li><a style="cursor: pointer;" onclick=\'fill_one_in_out(\"'+in_out+'\",\"'+id+'\",'+id_in_out+','+(min - (max-min))+','+(max - (max-min))+');\'><span class="glyphicon glyphicon-backward" style="color: grey; cursor: pointer;"></a></li>\n';
                }
                else {
                    s += '<li class="disabled"><a style="cursor: pointer;" ><span class="glyphicon glyphicon-fast-backward" style="color: grey; cursor: pointer;"></a></li>\n';
                    s += '<li class="disabled"><a style="cursor: pointer;" ><span class="glyphicon glyphicon-backward" style="color: grey; cursor: pointer;"></a></li>\n';
                }
                if (!(result_in_out.length < max-min))
                    s += '<li><a style="cursor: pointer;" onclick=\'fill_one_in_out(\"'+in_out+'\",\"'+id+'\",'+id_in_out+','+(min + (max-min))+','+(max + (max-min))+');\'><span class="glyphicon glyphicon-forward" style="color: grey; cursor: pointer;"></a></li>\n';
                s+= '   </ul>';
            }
            d.innerHTML = s;
        });
    });
}
