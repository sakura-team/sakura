//Code started by Michael Ortega for the LIG
//January 16th, 2017


var max_rows = 10;
var current_nb_rows = max_rows;
var current_instance_info = null;


function create_op_modal(main_div, id, cl_id, tabs) {
    // load in a temporary div element, then
    // append content obtained to main div.
    var cl = class_from_id(cl_id);
    var wrapper= document.createElement('div');
    load_from_template(
                    wrapper,
                    "modal-operator.html",
                    {'id': id, 'cl': cl, 'tabs': tabs, 'inst_id': parseInt(id.split("_")[2])},
                    function () {
                        let modal = wrapper.firstChild;
                        // update the svg icon
                        $(modal).find("#tdsvg").html(cl.svg);
                        // append to main div
                        main_div.appendChild(modal);
                    }
    );
}

function set_tab_urls(id, url_formatter) {
    let op_hub_id = parseInt(id.split("_")[2]);
    return new Promise(function(resolve, reject) {
        sakura.apis.hub.operators[op_hub_id].info().then(function (instance_info) {
            current_instance_info = instance_info;
            let index = 0;
            instance_info.tabs.forEach( function(tab) {
                let iframe = $(document.getElementById('modal_'+id+'_tab_tab_'+index));
                let tab_url = url_formatter(op_hub_id, tab);
                iframe.attr('src', tab_url);
                index++;
            });
            resolve();
        });
    });
}

function full_width(elt) {
    $('#'+elt+"_dialog").toggleClass('full_width');
    if ($('#'+elt+"_dialog").attr('class').includes("full_width")) {
        var h = ($(window).height()-$('#'+elt+"_header").height()-80);
        $('#'+elt+"_body").css("height", h+"px");
        $('#'+elt+"_body").children().eq(1).css("height", (h-60)+"px");
    }
    else {
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


function fill_params(id) {
    sakura.apis.hub.operators[parseInt(id.split("_")[2])].info().then(function (result) {
        var d = document.getElementById('modal_'+id+'_tab_params');
        while (d.firstChild) {
            d.removeChild(d.firstChild);
        }

        var index = -1;

        if (result['parameters'].length == 0) {
            d.innerHTML = '<br><p align="center"> No Params</p>';
        }
        else {
            result['parameters'].forEach( function (item) {
                index++;
                
                if (item['gui_type'] == 'COMBO') {
                    var ndiv = document.createElement('div');
                    ndiv.setAttribute('align', 'center');
                    ndiv.id = 'modal_'+id+'_tab_params_'+index;

                    var label = document.createElement('label');
                    label.innerHTML = item['label']+'&nbsp;'+'&nbsp;'+'&nbsp;';

                    var select      = document.createElement('select');
                    select.id       = 'modal_'+id+'_tab_params_select_'+index;
                    select.onchange = function(){
                        params_onChange(id, index, select.id);
                    };

                    var warn_icon = document.createElement("span");
                    warn_icon.className ="glyphicon glyphicon-warning-sign icon-large";

                    if (!item['enabled']) {
                        select.disabled = true;
                        warn_icon.title = item['disabled_message'];
                        warn_icon.style = 'color:red;';
                    }
                    else {
                        for (var i =0; i< item['possible_values'].length; i++) {
                            var pvalue = item['possible_values'][i];
                            if (pvalue.length > 40)
                                pvalue = pvalue.substring(0,37) + '...';
                            select.options[i] = new Option(pvalue);
                        }
                        if (item['warning_message']) {
                            warn_icon.title = item['warning_message'];
                            warn_icon.style = 'color:orange;';
                        }
                    }

                    ndiv.appendChild(document.createElement('br'));
                    ndiv.appendChild(label);
                    ndiv.appendChild(select);
                    if (!item['enabled'] || item['warning_message']) {
                        ndiv.appendChild(warn_icon);
                    }
                    d.appendChild(ndiv);
                }
                else {
                    console.log("Ouch !!!");
                }
            });
        }
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

function params_onChange(op_id, param_index, select_id) {

    let index = document.getElementById(select_id).selectedIndex;
    let hub_remote_op = sakura.apis.hub.operators[parseInt(op_id.split("_")[2])];
    hub_remote_op.info().then(function (instance_info) {
        let param_value = index;
        hub_remote_op.parameters[param_index].set_value(param_value).then(function (result) {
            current_instance_info = instance_info;
            if (result)
                console.log(result);
            else {
                fill_in_out('output', op_id);
                var index = 0;
                current_instance_info.tabs.forEach( function(tab) {
                    var iframe = document.getElementById('modal_'+op_id+'_tab_tab_'+index);
                    iframe.src = iframe.src;
                    index += 1;
                });

                // value change on one param may change possible values of another one.
                fill_params(op_id);
            }
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
    sakura.apis.hub.operators[inst_id].info().then(function (result_info) {
        var nb_in_out = result_info[in_out+'s'].length;

        if (nb_in_out == 0) {
            d.innerHTML = '<br><p align="center"> No '+in_out+'s</p>';
            return;
        }

        var div_tab = document.createElement('div');
        div_tab.className = 'modal-body';
        div_tab.id = id+'_'+in_out+'s';
        div_tab.style["paddingBottom"] = '0px';

        var ul          = document.createElement('ul');
        var tab_content = document.createElement('div');
        ul.className            = "nav nav-tabs";
        tab_content.className   = "tab-content";
        s = '<li class="active"> \
                <a style="padding-top: 0px; padding-bottom: 0px;" data-toggle="tab" href="#'+id+'_'+in_out+'_'+0+'" onclick=\'fill_one_in_out(\"'+in_out+'\",\"'+id+'\",'+0+','+0+','+current_nb_rows+');\'>'+result_info[in_out+'s'][0]['label']+'</a></li>';
        for (var i =1; i < nb_in_out; i++) {
            s += '<li><a style="padding-top: 0px; padding-bottom: 0px;" data-toggle="tab" href="#'+id+'_'+in_out+'_'+i+'" onclick=\'fill_one_in_out(\"'+in_out+'\",\"'+id+'\",'+i+','+0+','+current_nb_rows+');\'>'+result_info[in_out+'s'][i]['label']+'</a></li>';
        }
        ul.innerHTML = s;

        s = '<div id="'+id+'_'+in_out+'_'+0+'" class="tab-pane fade in active"></div>';
        for (var i =1; i < nb_in_out; i++)
            s += '<div id="'+id+'_'+in_out+'_'+i+'" class="tab-pane fade in active"></div>';
        tab_content.innerHTML = s;

        div_tab.appendChild(ul);
        div_tab.appendChild(tab_content);
        d.appendChild(div_tab);

        fill_one_in_out(in_out, id, 0, 0, current_nb_rows);
    });
}


function fill_one_in_out(in_out, id, id_in_out, min, max) {
    var d = document.getElementById(id+'_'+in_out+'_'+id_in_out);
    var inst_id = parseInt(id.split("_")[2]);

    //cleaning
    while (d.firstChild) {
        d.removeChild(d.firstChild);
    }

    var sp = $('<span>', {class:"glyphicon glyphicon-refresh glyphicon-refresh-animate"});
    var p = $('<p>', {align: "center"});
    p.append(sp);
    p.append(' Working, please wait... ')
    $(d).append(p);

    //infos
    sakura.apis.hub.operators[inst_id].info().then(function (result_info) {
        let plugs;
        if (in_out == 'input') {
            plugs = sakura.apis.hub.operators[inst_id].inputs;
        } else {
            plugs = sakura.apis.hub.operators[inst_id].outputs;
        }
        plugs[id_in_out].get_range(min, max).then(function (result_in_out) {
            if (in_out == 'output' || result_info[in_out+'s'][id_in_out].enabled) {
                var nb_cols = result_info[in_out+'s'][id_in_out]['columns'].length + 1;
                s = '<table class="table table-condensed table-hover table-striped" style="table-layout:fixed; margin-bottom: 1px;">\n';
                s += '<thead><tr>';
                s += '<th style="padding: 1px;  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">#</th>';

                result_info[in_out+'s'][id_in_out]['columns'].forEach( function(item) {
                    s+= '<th style="padding: 1px;  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">'+item[0]+'</th>';
                });
                s += '</tr></thead>';

                s+= '<tbody>';
                var index = 0;
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

                var ul = '';
                if (result_info[in_out+'s'][id_in_out]['length'] != null) {

                    var nb_pages = parseInt(result_info[in_out+'s'][id_in_out]['length']/(max-min));
                    if (nb_pages*(max-min) < result_info[in_out+'s'][id_in_out]['length'])
                        nb_pages++;
                    if (nb_pages > 1 && nb_pages < 10) {
                        ul = '   <ul class="pagination pagination-sm" style="margin-top: 5px; margin-bottom: 1px;">\n';
                        for (var i=0; i< nb_pages; i++)
                            ul+= '<li><a style="cursor: pointer;" onclick=\'fill_one_in_out(\"'+in_out+'\",\"'+id+'\",'+id_in_out+','+(i*(max-min))+','+((i+1)*(max-min))+');\'>'+(i+1)+'</a></li>\n';
                        ul+= '   </ul>';
                    }
                    else if (nb_pages > 10) {

                        var current_page = Math.floor(min/(max-min));
                        ul = '   <ul class="pagination pagination-sm">\n';
                        if (current_page > 0) {
                            ul += '<li><a style="cursor: pointer;" onclick=\'fill_one_in_out(\"'+in_out+'\",\"'+id+'\",'+id_in_out+','+0+','+(max-min)+');\'><span class="glyphicon glyphicon-fast-backward" style="color: grey; cursor: pointer;"></a></li>\n';
                            ul += '<li><a style="cursor: pointer;" onclick=\'fill_one_in_out(\"'+in_out+'\",\"'+id+'\",'+id_in_out+','+(min - (max-min))+','+(max - (max-min))+');\'><span class="glyphicon glyphicon-backward" style="color: grey; cursor: pointer;"></a></li>\n';
                        }
                        else {
                            ul += '<li class="disabled"><a style="cursor: pointer;"><span class="glyphicon glyphicon-fast-backward" style="color: grey; cursor: pointer;"></a></li>\n';
                            ul += '<li class="disabled"><a style="cursor: pointer;"><span class="glyphicon glyphicon-backward" style="color: grey; cursor: pointer;"></a></li>\n';
                        }
                        var up_limit = current_page+10;
                        if (up_limit > nb_pages) {
                            up_limit = nb_pages;
                        }
                        for (var i=current_page; i< up_limit; i++)
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
                var span = $('<span>', {title:    "Download the dataset",
                                        class:    "glyphicon glyphicon-download",
                                        style:    "cursor: pointer;"
                                        });
                var butt = $('<button>', {class: "button",
                                          onclick:  "download_table("+id_in_out+", \'"+in_out+"\')"});
                butt.append(span);
                butt.append('&nbsp;Download');
                s+= '<table width="100%"><tr><td>'+ul+'<td align="right">'+butt.get(0).outerHTML+'</table>';
                d.innerHTML = s;
            }
        });
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
