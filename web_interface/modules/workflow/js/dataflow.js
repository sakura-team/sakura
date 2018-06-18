//Code started by Michael Ortega for the LIG
//March 9th, 2017


var global_dataflow_jsFlag = true;
var current_dataflow_id = null;

//This function is apart because of the asynchronous aspect of ws.
//Links can only be recovered after recovering all operator instances
function create_dataflow_links(df_links) {

    //Cleaning the gui from current links
    remove_all_links();

    //Creating the links
    df_links.forEach( function (link) {
        var lgui = eval("("+link.gui_data+")");
        if (! link_exist(link.src_id, link.dst_id)) {
            var src_inst = instance_from_id(link.src_id);
            var dst_inst = instance_from_id(link.dst_id);

            //jsPlumb creation
            global_dataflow_jsFlag = false;
            js_link = jsPlumb.connect({ uuids:[src_inst.ep.out.getUuid(),dst_inst.ep.in.getUuid()] });
            global_dataflow_jsFlag = true;

            //our creation
            create_link_from_hub(js_link.id, link.link_id, link.src_id, link.dst_id, link.src_out_id, link.dst_in_id, lgui);
        }
        else {
            var link = link_from_instances(link.src_id, link.dst_id);
            var interval_id = null;
            var check_modal = function () {
                if (link.modal) {
                    link.params.push({  'out_id': link.src_out_id,
                                        'in_id': link.dst_in_id,
                                        'hub_id': link.link_id,
                                        'top':    lgui.top,
                                        'left':   lgui.left,
                                        'line':  lgui.line});
                    $("#svg_modal_link_"+link.id+'_out_'+link.src_out_id).html(svg_round_square_crossed(""));
                    $("#svg_modal_link_"+link.id+'_in_'+link.dst_in_id).html(svg_round_square_crossed(""));
                    copy_link_line(link, link.src_out_id, link.dst_in_id, lgui);
                    clearInterval(interval_id);
                }
            }
            interval_id = setInterval(check_modal, 500);
        }
    });
}

function current_dataflow() {

    var starting = 0;

    var searchParams = new URLSearchParams(window.location.search);
    if (searchParams.has('dataflow_id')) {
        current_dataflow_id = searchParams.get('dataflow_id')
    }

    if (current_dataflow_id == null) {
      alert("Issue with dataflow id");
        return;
    }

    //Now we ask for the operator classes
    sakura.common.ws_request('list_operators_classes', [], {}, function (result) {
        global_ops_cl = JSON.parse(JSON.stringify(result));
        //Then we ask for the instance ids
        sakura.common.ws_request('get_dataflow_info', [current_dataflow_id], {}, function (df_info) {
            console.log(df_info);
            df_info.op_instances.forEach( function(opi) {
                if (opi.gui_data) {
                    var jgui = eval("("+opi.gui_data+")");
                    create_operator_instance_from_hub(jgui.x, jgui.y, opi.cls_id, opi);
                }
            });
            create_dataflow_links(df_info.links);
        });
    });

    //Finally, the panels and the comments
    sakura.common.ws_request('get_dataflow_gui_data', [current_dataflow_id], {}, function (result) {

        if (!result)
            return
        var res = eval("(" + result + ")");
        global_op_panels = eval(res.panels);
        if (! global_op_panels) {
            global_op_panels = []
            return;
        }

        //Emptying current accordion
        var acc_div = document.getElementById('op_left_accordion');
        var butt = document.getElementById('select_op_add_button').cloneNode(true);
        while(acc_div.firstChild){
            acc_div.removeChild(acc_div.firstChild);
        }
        acc_div.appendChild(butt);

        //Filling accordion with panels
        var index = 0;
        global_op_panels.forEach( function (panel) {

            var divs = []
            panel['selected_ops'].forEach( function(item) {
                divs.push(select_op_new_operator(item, false));
            });

            var tmp_el = document.createElement("div");
            tmp_el.appendChild(select_op_make_table(4, divs));

            panel.id = "accordion_"+index
            index++;

            select_op_create_accordion(panel, tmp_el.innerHTML);
        });

        res.comments.forEach( function(com) {
            var ncom = comment_from(com);
        });

    });
}


function save_dataflow() {
    //The panels and the comments first

    var coms = [];
    global_coms.forEach( function(com) {
        coms.push(get_comment_info(com));
    });

    sakura.common.ws_request('set_dataflow_gui_data', [current_dataflow_id, JSON.stringify({'panels': global_op_panels, 'comments': coms})], {}, function(result){});

    //Second the operators
    global_ops_inst.forEach( function(inst) {
        var gui = {x: inst.gui.x,    y: inst.gui.y};
        sakura.common.ws_request('set_operator_instance_gui_data', [parseInt(inst.hub_id), JSON.stringify(gui)], {}, function(result) {});
    });

    //Finally the links
    global_links.forEach( function(link) {
        link.params.forEach( function(para) {
            var js = JSON.stringify({'op_src':  link.src,
                                    'op_dst':   link.dst,
                                    'top':      para.top,
                                    'left':     para.left,
                                    'line':     para.line});
            sakura.common.ws_request('set_link_gui_data', [   parseInt(para.hub_id), js], {}, function(result) {});
        });
    });
};

function new_dataflow() {
    var res = confirm("Are you sure you want to erase the current dataflow ?");
    if (!res)
        return false;

    //removing links
    remove_all_links();

    //removing operators instances
    remove_all_operators_instances();
};


function context_new_dataflow() {
    $('#sakura_main_div_contextMenu').css({visibility: "hidden"});
    new_dataflow();
}
