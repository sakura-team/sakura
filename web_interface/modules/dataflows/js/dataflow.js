//Code started by Michael Ortega for the LIG
//March 9th, 2017


var global_dataflow_jsFlag  = true;
var dataflow_events         = [ 'created_link',
                                'deleted_link',
                                'created_instance',
                                'deleted_instance'];

function dataflows_deal_with_events(evt_name, args, proxy) {
    switch (evt_name) {
        case ('created_link'):
            push_request('links_info');
            sakura.apis.hub.links[args].info().then(function (link) {
                pop_request('links_info');
                if (LOG_DATAFLOW_EVENTS) {
                    console.log('----');
                    console.log(evt_name, args);
                    console.log(link);
                    console.log('----');
                }
                create_dataflow_links([link], from_shell=true);
            });
            break;

        case ('deleted_link'):
            if (LOG_DATAFLOW_EVENTS) { console.log('DELETED LINK', args);}
            global_links.some( function (link) {
                link.params.some( function (param) {
                    if (param.hub_id == args) {
                        if (link.params.length > 1) {
                            delete_link_param(link.id, 'in', param.in_id, false);
                        }
                        else {
                            remove_link(link, false);
                        }
                        return true;
                    }
                });
                // if (link.params[0].hub_id == args) {
                //     remove_link(link, false);
                //     return true;
                // }
                return false;
            });
            break;

        case ('created_instance'):
            if (LOG_DATAFLOW_EVENTS) {  console.log('CREATED INSTANCE', args);  }

            if (! waiting_gui) {
                waiting_gui = { x: $('#sakura_main_div').width()/2,
                                y: $('#sakura_main_div').height()/2};
            }
            instances_waiting_for_creation.push({id: args, gui: waiting_gui});
            waiting_gui = null;

            let proxy = sakura.apis.hub.operators[args];
            if (proxy) {
                op_events.forEach( function(e) {
                  proxy.subscribe_event(e, function(evt_name, argus) {
                        operators_deal_with_events(evt_name, argus, proxy, args);
                  });
              });
            }
            else {  console.log('Cannot subscribe_event on op', args);  }

            break;

        case ('deleted_instance'):
            if (LOG_DATAFLOW_EVENTS) {  console.log('DELETED INSTANCE', args);  }
            let inst = instance_from_id(args);
            remove_operator_instance('op_'+inst.cl.id+"_"+inst.hub_id, false);
            break;

        default:
            if (LOG_DATAFLOW_EVENTS) {  console.log('Unknown Event', evt_name); }
    }
}


//This function is apart because of the asynchronous aspect of ws.
//Links can only be recovered after recovering all operator instances
function create_dataflow_links(df_links, from_shell=false) {
    //Creating the links
    for (let i=0; i < df_links.length; i++) {
        let link = df_links[i];

        let lgui = {};
        if (link.gui_data !== "") {
            lgui = eval("("+link.gui_data+")");
        }
        if (! link_exist(link.src_id, link.dst_id)) {
            //jsPlumb creation
            let src_inst = instance_from_id(link.src_id);
            let dst_inst = instance_from_id(link.dst_id);

            if ( src_inst.ep.out && dst_inst.ep.in) {
                global_dataflow_jsFlag = false;
                js_link = jsPlumb.connect({ uuids:[ src_inst.ep.out.getUuid(),
                                                    dst_inst.ep.in.getUuid()]});
                global_dataflow_jsFlag = true;
                create_link_from_hub( js_link, link, lgui, from_shell);
            }
        }
        else {
            llink = link_from_instances(link.src_id, link.dst_id);
            let interval_id = null;
            let check_modal = function () {
                let ij = param_exist(link.link_id);
                if (!ij) {
                    llink.params.push({ 'out_id': link.src_out_id,
                                        'in_id': link.dst_in_id,
                                        'hub_id': link.link_id,
                                        'top':    lgui.top,
                                        'left':   lgui.left,
                                        'line':  lgui.line});
                }
                else {
                    llink.params[ij[1]].top = lgui.top;
                    llink.params[ij[1]].left = lgui.left;
                    llink.params[ij[1]].line = lgui.line;
                }

                $("#svg_modal_link_"+llink.id+'_out_'+link.src_out_id).html(svg_round_square_crossed(""));
                $("#svg_modal_link_"+llink.id+'_in_'+link.dst_in_id).html(svg_round_square_crossed(""));
                copy_link_line(llink, link.src_out_id, link.dst_in_id, lgui);
                clearInterval(interval_id);
            }
            interval_id = setInterval(check_modal, 500);
        }
    };
}

function current_dataflow() {

    //Cleanings
    remove_all_links(false);
    remove_all_operators_instances(false);
    remove_all_comments(false);
    global_op_panels = [];

    //Emptying current accordion
    let acc_div = document.getElementById('op_left_accordion');
    let butt = document.getElementById('select_op_add_button').cloneNode(true);
    $(acc_div).empty();
    acc_div.appendChild(butt);

    //We first ask for the operator classes
    push_request('op_classes_list');
    sakura.apis.hub.op_classes.list().then(function (result) {
        pop_request('op_classes_list');
        current_op_classes_list = JSON.parse(JSON.stringify(result));

        //Then we ask for the instance ids
        push_request('dataflows_info');
        sakura.apis.hub.dataflows[web_interface_current_id].info().then(function (df_info) {
            pop_request('dataflows_info');
            //Subscribe to hub events
            let proxy = sakura.apis.hub.dataflows[web_interface_current_id];
            if (proxy) {
                dataflow_events.forEach( function(e) {
                    proxy.subscribe_event(e, function(evt_name, args) {
                          dataflows_deal_with_events(evt_name, args, proxy);
                    });
                });
            }
            else {
                console.log('Cannot subscribe_event on dataflow', df_info);
            }

            df_info.op_instances.forEach( function(opi) {
                if (opi.gui_data) {
                    let jgui = eval("("+opi.gui_data+")");
                    create_operator_instance_from_hub(jgui.x, jgui.y, opi.cls_id, opi);
                }
                else {
                    console.log('NO GUI for this op !!!!');
                    let g = { x: $('#sakura_main_div').width()/2,
                              y: $('#sakura_main_div').height()/2};
                    push_request('operators_set_gui_data');
                    sakura.apis.hub.operators[parseInt(opi.op_id)].set_gui_data(JSON.stringify(g)).then(  function(){
                        pop_request('operators_set_gui_data');
                        create_operator_instance_from_hub(g.x, g.y, opi.cls_id, opi);
                    });
                }
            });
            create_dataflow_links(df_info.links);
            df_info.op_instances.forEach( function(opi) {
                check_operator(opi);
            });

            //Finally, the panels and the comments
            push_request('dataflows_get_gui_data');
            sakura.apis.hub.dataflows[web_interface_current_id].get_gui_data().then(function (result) {
                pop_request('dataflows_get_gui_data');
                //Cleanings
                if (result) {
                    var res = eval("(" + result + ")");
                    global_op_panels = eval(res.panels);
                    if (! global_op_panels) {
                        global_op_panels = []
                        return;
                    }
                }

                if (!result)
                    return

                //Filling accordion with panels
                var index = 0;
                let filtered_global_op_panels = [];
                global_op_panels.forEach( function (panel) {

                    var divs = []
                    let filtered_selected_ops = [];
                    panel['selected_ops'].forEach( function(item) {
                        let cl = class_from_id(item);
                        if (cl == null) {
                            return;
                        }
                        filtered_selected_ops.push(item);
                        divs.push(select_op_new_operator(item, false));
                    });

                    panel['selected_ops'] = filtered_selected_ops;

                    var tmp_el = document.createElement("div");
                    tmp_el.appendChild(select_op_make_table(4, divs));

                    panel.id = "accordion_"+index
                    index++;

                    select_op_create_accordion(panel, tmp_el.innerHTML);
                    filtered_global_op_panels.push(panel);
                });

                global_op_panels = filtered_global_op_panels;

                res.comments.forEach( function(com) {
                    var ncom = comment_from(com);
                });
            });
        });
    });
}


function save_dataflow() {
    //The panels and the comments first
    let coms = [];
    global_coms.forEach( function(com) {
        coms.push(get_comment_info(com));
    });

    let gui_data = JSON.stringify({'panels': global_op_panels, 'comments': coms});
    push_request('dataflows_set_gui_data');
    sakura.apis.hub.dataflows[web_interface_current_id].set_gui_data(gui_data).then( function(result) {
        pop_request('dataflows_set_gui_data');
    }).catch(function(error) {
        console.log('SET GUI ERROR', error);
        pop_request('dataflows_set_gui_data');
    });

    //Second the operators
    global_ops_inst.forEach( function(inst) {
        var gui = {x: inst.gui.x,    y: inst.gui.y};
        push_request('operators_set_gui_data');
        sakura.apis.hub.operators[parseInt(inst.hub_id)].set_gui_data(JSON.stringify(gui)).then( function() {
            pop_request('operators_set_gui_data');
        });
    });

    //Finally the links
    for (let i=0; i< global_links.length; i++) {
        let link = global_links[i];
        for (let j=0; j< link.params.length; j++) {
            let param = link.params[j];
            //if -> Bad behavior of length with object arrays
            if (param.out_id !== undefined) {
                var js = JSON.stringify({'op_src':  link.src,
                                        'op_dst':   link.dst,
                                        'top':      param.top,
                                        'left':     param.left,
                                        'line':     param.line});
                push_request('links_set_gui_data');
                sakura.apis.hub.links[parseInt(param.hub_id)].set_gui_data(js).then( function () {
                    pop_request('links_set_gui_data');
                });
            }
        };
    };
};

function clean_dataflow() {
    var res = confirm("Are you sure you want to erase the current dataflow ?");
    if (!res)
        return false;

    //removing links
    remove_all_links();

    //removing operators instances
    remove_all_operators_instances(true);
};


function context_new_dataflow() {
    $('#sakura_main_div_contextMenu').css({visibility: "hidden"});
    clean_dataflow();
}
