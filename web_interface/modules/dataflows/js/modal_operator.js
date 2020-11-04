//Code started by Michael Ortega for the LIG
//January 16th, 2017


var max_rows = 10;
var current_nb_rows = max_rows;
var current_instance_info = null;

function create_op_modal(op_id, info) {
    // load in a temporary div element, then
    // append content obtained to main div.
    let cl = class_from_id(info.cls_id);

    let wrapper = document.createElement('div');
    let revision = info.code_ref+' @'+info.commit_hash.substring(0,7);
    load_from_template(
                    wrapper,
                    "modal-operator.html",
                    { 'id': op_id, 'cl': cl, 'inst': info, 'tabs': info.tabs,
                      'inst_id': info.op_id},
                    function (r_text) {
                        let modal = wrapper.firstChild;
                        $(modal).find("#tdsvg").html(cl.svg);
                        main_div.appendChild(modal);
                        let select  = $('#modal_'+op_id+'_select_revision');
                        let cr      = info.code_ref;
                        let t       = cr.split(':');
                        if (t[0] == 'branch')
                            cr = t[1];
                        let txt = '<b>'+cr +
                                  '</b>@' +
                                  info.commit_hash.substring(0,7);

                        let opt = $('<option>', { 'value': 0,
                                                  'html': txt,
                                                  'selected': true});
                        select.append(opt);
                        select.on('shown.bs.select', function(e) {
                                      function cb() {
                                          let op_id = dataflows_open_modal.split('modal_')[1];
                                          $('#'+dataflows_open_modal).modal('hide');
                                          reload_operator_instance(op_id);
                                      }

                                      $(e.target).selectpicker('toggle');
                                      operators_revision_panel_select_open($(e.target), info, true, cb);
                                      e.preventDefault();
                                  });
                        select.selectpicker('refresh');
                    }
    );
}

function set_tab_urls(id, url_formatter) {
    let op_hub_id = parseInt(id.split("_")[2]);
    return new Promise(function(resolve, reject) {
        push_request('operators_info');
        sakura.apis.hub.operators[op_hub_id].info().then(function (instance_info) {
            pop_request('operators_info');
            current_instance_info = instance_info;
            let index = 0;
            instance_info.tabs.forEach( function(tab) {
                let iframe = $(document.getElementById('modal_'+id+'_tab_tab_'+index));
                let tab_url = url_formatter(op_hub_id, tab);
                iframe.attr('src', tab_url);
                index++;
            });
            resolve();
        }).catch( function (error){
            pop_request('operators_info');
            alert('Tab display -- Failed to retrieve operator information:\n' + error);
        });
    });
}

function full_width(elt) {
    $('#'+elt+"_dialog").toggleClass('full_width');
    if ($('#'+elt+"_dialog").attr('class').includes("full_width")) {
        let h = ($(window).height()-$('#'+elt+"_header").height()-80);
        $('#'+elt+"_dialog").css('width', '100%');
        $('#'+elt+"_body").css("height", h+"px");
        $('#'+elt+"_body").children().eq(1).css("height", (h-60)+"px");
    }
    else {
        $('#'+elt+"_dialog").css('width', '');
        $('#'+elt+"_body").css("height", "100%");
        $('#'+elt+"_body").children().eq(1).css("height", "100%");
    }
}

function fill_all(id) {
    $('#tab_button_inputs').attr('onclick', 'fill_in_out("input", \''+id+'\');');
    $('#tab_button_params').attr('onclick', 'fill_params(\''+id+'\');');
    $('#tab_button_outputs').attr('onclick', 'fill_in_out("output", \''+id+'\');');

    fill_in_out('input', id);
    fill_params(id);
    fill_in_out('output', id);
    fill_tabs(id);
}


function fill_tabs(id) {
    return set_tab_urls(id, function(op_hub_id, tab) {
        return '/opfiles/' + op_hub_id + '/' + tab.html_path;
    });
}

function display_issue(id, disabled, warned) {
    if (disabled) {
        w_div = document.getElementById(id+"_warning");
        w_div.style.color = 'red';
        w_div.style.visibility = "visible";
    }
    else if (warned) {
        w_div = document.getElementById(id+"_warning");
        w_div.style.color = 'orange';
        w_div.style.visibility = "visible";
    }
    else {
      w_div = document.getElementById(id+"_warning");
      w_div.style.visibility = "hidden";
    }
}

function fill_params(id) {
    push_request('operators_info');
    sakura.apis.hub.operators[parseInt(id.split("_")[2])].info().then(function (result) {
        pop_request('operators_info');
        let disabled  = false;
        let warned    = false;
        result.parameters.forEach( function(param) {
            if (!param.enabled) {
                disabled = true;
            }
            else if (param.warning_message) {
              warned = true;
            }
        });
        display_issue(id, disabled, warned);

        let d = document.getElementById('modal_'+id+'_tab_params');
        if (d.firstChild)
            while (d.firstChild) {
                d.removeChild(d.firstChild);
            }

        if (result['parameters'].length == 0) {
            d.innerHTML = '<br><p align="center"> No Params</p>';
        }
        else {
            let tbl   = document.createElement("table");
            tbl.align = 'center';

            result['parameters'].forEach( function (item, index) {
                if (item['gui_type'] == 'COMBO') {
                    let tr   = document.createElement("tr");
                    let td1   = document.createElement("td");
                    let td2   = document.createElement("td");
                    let td3   = document.createElement("td");
                    td3.style.padding = '3px';

                    //Label
                    td2.innerHTML = item['label']+'&nbsp;'+'&nbsp;'+'&nbsp;';
                    if (!item['enabled'] || item['warning_message'])
                        td2.innerHTML = '&nbsp;'+'&nbsp;'+'&nbsp;'+item['label']+'&nbsp;'+'&nbsp;'+'&nbsp;';

                    //Select & warn icon
                    let select = $('<select/>', { 'class': "selectpicker",
                                                  'multiple': "multiple"});
                    select.attr("id", 'modal_'+id+'_tab_params_select_'+index);
                    select.change(function(){
                        params_onChange(id, index, $(this));
                    });
                    select.prop('my_val', []);

                    let warn_icon = document.createElement("span");
                    warn_icon.className ="glyphicon glyphicon-exclamation-sign icon-large";

                    if (!item['enabled']) {
                        select.attr('disabled', 'true');
                        warn_icon.title = item['disabled_message'];
                        warn_icon.style = 'color:red;';
                    }
                    else {
                        for (let i =0; i <item['possible_values'].length; i++) {
                            let pvalue = item['possible_values'][i];
                            if (pvalue.length > 40)
                                pvalue = pvalue.substring(0,37) + '...';
                            select.append(new Option(pvalue));

                            if (i == item['value']) {
                                select.val(pvalue);
                                select.prop('my_val').push(pvalue);
                            }
                        }
                        //if ((item.value == 'None' || !item.value) && item.value !== 0) {
                        //    //select.selectpicker('deselectAll');
                        //}

                        if (item['warning_message']) {
                            warn_icon.title = item['warning_message'];
                            warn_icon.style = 'color:orange;';
                        }
                    }
                    select.appendTo(td3).selectpicker('refresh');

                    if (!item['enabled'] || item['warning_message']) {
                        $('#tab_button_params_a')[0].innerHTML = 'Params&nbsp;&nbsp;';
                        $('#tab_button_params_a')[0].appendChild(warn_icon);
                        td1.appendChild(warn_icon.cloneNode(true));
                    }
                    else {
                        $('#tab_button_params_a')[0].innerHTML = 'Params';
                    }

                    tr.appendChild(td1);
                    tr.appendChild(td2);
                    tr.appendChild(td3);
                    tbl.appendChild(tr);
                }
                else {
                     alert("Only combo parameters are handled!!!");
                }
            });
            d.appendChild(document.createElement('br'));
            d.appendChild(tbl);
        }
    }).catch( function (error){
        pop_request('operators_info');
        alert('Parameters init -- Failed to retrieve operator information:\n' + error);
    });
}

function release_all(id) {
    return release_tabs(id);
}

function release_tabs(id) {
    return set_tab_urls(id, function(op_hub_id, tab) {
        return '';
    });
}

function params_onChange(op_id, param_index, select) {

    let selected = '';
    select.val().forEach( function (item) {
        if (select.prop('my_val').indexOf(item) == -1)
            selected = item
    });
    select.val(selected);
    select.prop('my_val').pop(0);
    select.prop('my_val').push(selected);

    let index = select[0].selectedIndex;
    let hub_remote_op = sakura.apis.hub.operators[parseInt(op_id.split("_")[2])];
    push_request('operators_info');
    hub_remote_op.info().then(function (instance_info) {
        pop_request('operators_info');
        let param_value = index;
        hub_remote_op.parameters[param_index].set_value(param_value).then(function (result) {
            current_instance_info = instance_info;
            fill_in_out('output', op_id);
            let index = 0;
            current_instance_info.tabs.forEach( function(tab) {
                let iframe = document.getElementById('modal_'+op_id+'_tab_tab_'+index);
                iframe.src = iframe.src;
                index += 1;
            });

            // value change on one param may change possible values of another one.
            fill_params(op_id);
        });
    }).catch( function (error){
        pop_request('operators_info');
        alert('Parameter update -- Failed to retrieve operator information:\n' + error);
    });
}


function fill_in_out(in_out, id) {
    let inst_id     = parseInt(id.split("_")[2]);
    let d           = document.getElementById('modal_'+id+'_tab_'+in_out+'s');

    //cleaning
    if (d.firstChild)
        while (d.firstChild) {
            d.removeChild(d.firstChild);
        }

    //infos
    let proxy = sakura.apis.hub.operators[inst_id];
    if (proxy) {
        push_request('operators_info');
        proxy.info().then(function (result_info) {
            pop_request('operators_info');
            let nb_in_out = result_info[in_out+'s'].length;

            if (nb_in_out == 0) {
                d.innerHTML = '<br><p align="center"> No '+in_out+'s</p>';
                return;
            }

            let div_tab = document.createElement('div');
            div_tab.className = 'modal-body';
            div_tab.id = id+'_'+in_out+'s';
            div_tab.style["paddingBottom"] = '0px';

            let ul          = document.createElement('ul');
            let tab_content = document.createElement('div');
            ul.className            = "nav nav-tabs";
            tab_content.className   = "tab-content";
            s = '<li class="active"> \
                    <a style="padding-top: 0px; padding-bottom: 0px;" data-toggle="tab" href="#'+id+'_'+in_out+'_'+0+'" onclick=\'fill_one_in_out(\"'+in_out+'\",\"'+id+'\",'+0+','+0+','+current_nb_rows+');\'>'+result_info[in_out+'s'][0]['label']+'</a></li>';
            for (let i =1; i < nb_in_out; i++) {
                s += '<li><a style="padding-top: 0px; padding-bottom: 0px;" data-toggle="tab" href="#'+id+'_'+in_out+'_'+i+'" onclick=\'fill_one_in_out(\"'+in_out+'\",\"'+id+'\",'+i+','+0+','+current_nb_rows+');\'>'+result_info[in_out+'s'][i]['label']+'</a></li>';
            }
            ul.innerHTML = s;

            s = '<div id="'+id+'_'+in_out+'_'+0+'" class="tab-pane fade in active"></div>';
            for (let i =1; i < nb_in_out; i++)
                s += '<div id="'+id+'_'+in_out+'_'+i+'" class="tab-pane fade in active"></div>';
            tab_content.innerHTML = s;

            div_tab.appendChild(ul);
            div_tab.appendChild(tab_content);
            d.appendChild(div_tab);

            fill_one_in_out(in_out, id, 0, 0, current_nb_rows, );

        }).catch( function (error){
            pop_request('operators_info');
            console.log('Failed to retrieve operator information:\n' + error);
        });
    }
}


function fill_one_in_out(in_out, id, id_in_out, min, max, elt) {
    let d = document.getElementById(id+'_'+in_out+'_'+id_in_out);
    let inst_id = parseInt(id.split("_")[2]);

    //cleaning
    if (d.firstChild)
        while (d.firstChild) {
            d.removeChild(d.firstChild);
        }

    let sp = $('<span>', {class:"glyphicon glyphicon-refresh glyphicon-refresh-animate"});
    let p = $('<p>', {align: "center"});
    p.append(sp);
    p.append(' Working, please wait... ')
    $(d).append(p);

    //infos
    push_request('operators_info');
    sakura.apis.hub.operators[inst_id].info().then(function (result_info) {
        pop_request('operators_info');
        let plugs;
        if (in_out == 'input') {
            plugs = sakura.apis.hub.operators[inst_id].inputs;
        } else {
            plugs = sakura.apis.hub.operators[inst_id].outputs;
        }
        if (!result_info[in_out+'s'][id_in_out].enabled) {
            d.innerHTML = '<br><p align="center">'+result_info[in_out+'s'][id_in_out].disabled_message+'</p>';
            return;
        }
        push_request('operators_plugs_get_range');
        plugs[id_in_out].get_range(min, max).then(function (result_in_out) {
            pop_request('operators_plugs_get_range');
            let nb_cols = result_info[in_out+'s'][id_in_out]['columns'].length + 1;
            s = '<table class="table table-condensed table-hover table-striped" style="table-layout:fixed; margin-bottom: 1px;">\n';
            s += '<thead><tr>';
            s += '<th style="padding: 1px;  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">#</th>';

            result_info[in_out+'s'][id_in_out]['columns'].forEach( function(item) {
                s+= '<th style="padding: 1px;  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">'+item[0]+'</th>';
            });
            s += '</tr></thead>';

            s+= '<tbody>';
            let index = 0;
            result_in_out.forEach( function(row) {
                s += '<tr>\n';
                s += '<td style="padding: 1px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">'+parseInt(index+min)+'</td>';
                row.forEach( function(col) {
                    if (typeof col === 'string') {
                        s += '<td style="padding: 1px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">'+escapeHtml(col)+'</td>';
                    }
                    else {
                        if (col == null)
                            col = '';
                        s += '<td style="padding: 1px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">'+col+'</td>';
                    }
                });
                s += '</tr>';
                index += 1;
            });

            s += '</tbody></table>';

            let ul = '';
            if (result_info[in_out+'s'][id_in_out]['length'] != null) {

                let nb_pages = parseInt(result_info[in_out+'s'][id_in_out]['length']/(max-min));
                if (nb_pages*(max-min) < result_info[in_out+'s'][id_in_out]['length'])
                    nb_pages++;
                if (nb_pages > 1 && nb_pages < 10) {
                    ul = '   <ul class="pagination pagination-sm" style="margin-top: 5px; margin-bottom: 1px;">\n';
                    for (let i=0; i< nb_pages; i++)
                        ul+= '<li><a style="cursor: pointer;" onclick=\'fill_one_in_out(\"'+in_out+'\",\"'+id+'\",'+id_in_out+','+(i*(max-min))+','+((i+1)*(max-min))+');\'>'+(i+1)+'</a></li>\n';
                    ul+= '   </ul>';
                }
                else if (nb_pages > 10) {

                    let current_page = Math.floor(min/(max-min));
                    ul = '   <ul class="pagination pagination-sm">\n';
                    if (current_page > 0) {
                        ul += '<li><a style="cursor: pointer;" onclick=\'fill_one_in_out(\"'+in_out+'\",\"'+id+'\",'+id_in_out+','+0+','+(max-min)+');\'><span class="glyphicon glyphicon-fast-backward" style="color: grey; cursor: pointer;"></a></li>\n';
                        ul += '<li><a style="cursor: pointer;" onclick=\'fill_one_in_out(\"'+in_out+'\",\"'+id+'\",'+id_in_out+','+(min - (max-min))+','+(max - (max-min))+');\'><span class="glyphicon glyphicon-backward" style="color: grey; cursor: pointer;"></a></li>\n';
                    }
                    else {
                        ul += '<li class="disabled"><a style="cursor: pointer;"><span class="glyphicon glyphicon-fast-backward" style="color: grey; cursor: pointer;"></a></li>\n';
                        ul += '<li class="disabled"><a style="cursor: pointer;"><span class="glyphicon glyphicon-backward" style="color: grey; cursor: pointer;"></a></li>\n';
                    }
                    let up_limit = current_page+10;
                    if (up_limit > nb_pages) {
                        up_limit = nb_pages;
                    }
                    for (let i=current_page; i< up_limit; i++)
                        if (i == current_page) {
                            ul+= '<li class="disabled"><a style="cursor: pointer;");\'>'+(i+1)+'</a></li>\n';
                        }
                        else {
                            ul+= '<li><a style="cursor: pointer;" onclick=\'fill_one_in_out(\"'+in_out+'\",\"'+id+'\",'+id_in_out+','+(i*(max-min))+','+((i+1)*(max-min))+');\'>'+(i+1)+'</a></li>\n';
                        }

                    if (up_limit < nb_pages) {
                        ul += '<li><a style="cursor: pointer;" onclick=\'fill_one_in_out(\"'+in_out+'\",\"'+id+'\",'+id_in_out+','+((current_page+1)*(max-min))+','+((current_page+2)*(max-min))+');\'><span class="glyphicon glyphicon-forward" style="color: grey; cursor: pointer;"></a></li>\n';
                        ul += '<li><a style="cursor: pointer;" onclick=\'fill_one_in_out(\"'+in_out+'\",\"'+id+'\",'+id_in_out+','+((nb_pages-1)*(max-min))+','+((nb_pages)*(max-min))+');\'><span class="glyphicon glyphicon-fast-forward" style="color: grey; cursor: pointer;"></a></li>\n';
                    }
                    ul+= '   </ul>';
                }
            }
            else {
                ul = '   <ul class="pagination pagination-sm">\n';
                if (min > 0) {
                    ul += '<li><a style="cursor: pointer;" onclick=\'fill_one_in_out(\"'+in_out+'\",\"'+id+'\",'+id_in_out+','+0+','+(max-min)+');\'><span class="glyphicon glyphicon-fast-backward" style="color: grey; cursor: pointer;"></span></a></li>\n';
                    ul += '<li><a style="cursor: pointer;" onclick=\'fill_one_in_out(\"'+in_out+'\",\"'+id+'\",'+id_in_out+','+(min - (max-min))+','+(max - (max-min))+');\'><span class="glyphicon glyphicon-backward" style="color: grey; cursor: pointer;"></span></a></li>\n';
                }
                else {
                    ul += '<li class="disabled"><a style="cursor: pointer;" ><span class="glyphicon glyphicon-fast-backward" style="color: grey; cursor: pointer;"></a></li>\n';
                    ul += '<li class="disabled"><a style="cursor: pointer;" ><span class="glyphicon glyphicon-backward" style="color: grey; cursor: pointer;"></a></li>\n';
                }
                if (!(result_in_out.length < max-min))
                    ul += '<li><a style="cursor: pointer;" onclick=\'fill_one_in_out(\"'+in_out+'\",\"'+id+'\",'+id_in_out+','+(min + (max-min))+','+(max + (max-min))+');\'><span class="glyphicon glyphicon-forward" style="color: grey; cursor: pointer;"></a></li>\n';

                ul += '   </ul>';



            }
            let span = $('<span>', {title:    "Download the dataset",
                                    class:    "glyphicon glyphicon-download",
                                    style:    "cursor: pointer;"
                                    });
            let butt = $('<button>', {class: "button",
                                      onclick:  "dataflows_download_table("+id_in_out+", \'"+in_out+"\')"});
            butt.append(span);
            butt.append('&nbsp;Download');
            s+= '<table width="100%"><tr><td>'+ul+'<td align="right">'+butt.get(0).outerHTML+'</table>';
            d.innerHTML = s;

        }).catch (function(error) {
            pop_request('operators_plugs_get_range');
            alert('Failed to get ' + in_out + ' stream values:\n' + error);
        });
    }).catch (function(error) {
        pop_request('operators_info');
        alert(in_out + ' retrieval -- Failed to retrieve operator information:\n' + error);
    });
}

function loadIFrame(url, id) {
    /* by default the iframe is initialized with current url
       with the condition it will not reload if already loaded
     */
    let iframe = document.getElementById("codeEditorIframe_"+id);
    if (iframe.src.indexOf(url) == -1) {
        iframe.src = url;
    }
}
