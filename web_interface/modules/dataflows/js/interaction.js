var currently_dragged   = null;
var drag_delta          = [0, 0];
var df_global_events_loaded = false;


//main
var cursorX;
var cursorY;

// var instances_waiting_for_creation = [];
// var waiting_gui = null;

var LOG_INTERACTION_EVENT   = true;
var LOG_DATAFLOW_EVENTS     = true;
var LOG_LINKS_EVENTS        = true;
var LOG_OPERATORS_EVENTS    = true;

function set_df_global_events() {

    document.onmousemove = function(e){
        cursorX = e.pageX;
        cursorY = e.pageY;
    }

    document.addEventListener("dragstart", function ( e ) {
        e.dataTransfer.setData('text/plain', null);
        var rect = e.target.getBoundingClientRect();
        currently_dragged = e.target;

        if (currently_dragged.id.includes("svg_modal_link")) {
            var modal_id = currently_dragged.id.split("_")[3];
            var bdiv = document.getElementById("modal_link_"+modal_id+"_body");
        }
        drag_delta = [e.clientX - rect.left, e.clientY - rect.top];
    }, false);

    $(window).bind('keypress', function(e){
        if ( $("#modal_op_selector").is(':visible') && (e.keyCode == 13 || e.which == 13))
            select_op_add_panel();
    });


    $('#sakura_operator_contextMenu').on("click", "a", function(e) {
        var val = e.target.attributes['value'].value;
        if (val == 'Delete') {
            let tab = op_focus_id.split("_");
            let hub_id = parseInt(tab[2]);
            push_request('operators_delete');
            sakura.apis.hub.operators[hub_id].delete().then( function (result) {
                pop_request('operators_delete');
                $('#sakura_operator_contextMenu').hide();
            }).catch( function(error) {
                pop_request('operators_delete');
                console.log('ERROR REMOVING OP ', error);
            });
        }
        else if (val == 'Info') {
            var op_cl = class_from_id(parseInt(op_focus_id.split("_")[1]));
            var url   = op_cl.repo_url;
            var dir   = op_cl.code_subdir;
            var rev   = op_cl.default_code_ref.split(":")[1];
            $('#sakura_operator_contextMenu').hide();
            window.open(url+'/tree/'+rev+'/'+dir);
        }
        else if (val == 'Reload') {
            reload_operator_instance(op_focus_id);
            $('#sakura_operator_contextMenu').hide();
        }
        e.preventDefault();
    });

    $('#sakura_link_contextMenu').on("click", "a", function(e) {
        e.preventDefault();
        $('#sakura_link_contextMenu').hide();
        remove_link(link_focus_id, true);
    });
}

function df_set_events(main_div) {

    if (!df_global_events_loaded) {
        set_df_global_events();
        df_global_events_loaded = true;
    }

    main_div[0].addEventListener("dragover", function( e ) {
        e.preventDefault();
    }, false);


    main_div[0].addEventListener("drop", function( e ) {
        if (LOG_INTERACTION_EVENT) {console.log('DROP EVENT')};
        e.preventDefault();

        //Operators
        let op = null;
        if (currently_dragged && currently_dragged.id.includes("static")) {
            op = currently_dragged;
        }
        else if (svg_up_div != null) {
            op = svg_up_div;
            svg_up_div = null;
        }


        if (op != null) {
            if (LOG_INTERACTION_EVENT) console.log('DROPPING OP');
            let rect = main_div[0].getBoundingClientRect();
            create_operator_instance_on_hub(e.clientX - rect.left - drag_delta[0],
                                            e.clientY - rect.top - drag_delta[1] + e.target.scrollTop,
                                            op.id.split("_").slice(-2)[0]);
        }

        //Link params
        else if (currently_dragged && currently_dragged.id.includes("svg_modal_link") && e.target.parentElement.parentElement.id.includes("svg_modal_link")) {
            if (LOG_INTERACTION_EVENT) {console.log('DROPPING PARAM')};

            let param_out = currently_dragged;
            let param_in = e.target.parentElement.parentElement;

            //Make sure the two links are from two objects
            if (    (param_out.id.includes("_in_") && param_in.id.includes("_in_")) ||
                    (param_out.id.includes("_out_") && param_in.id.includes("_out_")) ) {
                return ;
            }
            //Make sure out is from object out
            else if (param_out.id.includes("_in_") && param_out.id.includes("_in_")) {
                param_in = currently_dragged;
                param_out = e.target.parentElement.parentElement;
            }

            let tab1 = param_out.id.split("_");
            let out_id = parseInt(tab1[6]);
            let in_id = parseInt(param_in.id.split("_")[6]);

            var link = link_from_id('con_'+parseInt(tab1[4]));
            if (! link.params || (link.params.out_id != out_id && link.params.in_id != in_id)) {
                push_request('links_create');
                sakura.apis.hub.links.create(link.src, out_id, link.dst, in_id).then(function (link_id_from_hub) {
                    pop_request('links_create');
                    if (LOG_INTERACTION_EVENT) {console.log('CREATION SENT')};

                    //local creation
                    let line = create_link_line(link.id, out_id, in_id);
                    let svg_line = document.getElementById("line_modal_link_"+link.id+"_"+out_id+"_"+in_id);
                    let ij = param_exist(parseInt(link_id_from_hub));
                    if (!ij) {
                        link.params.push({  'out_id':   out_id,
                                        'in_id':    in_id,
                                        'hub_id':   parseInt(link_id_from_hub),
                                        'top':      svg_line.style.top,
                                        'left':     svg_line.style.left,
                                        'line':     line});
                    }
                    else {
                          link.params.top = svg_line.style.top;
                          link.params.left = svg_line.style.left;
                          link.params.line = svg_line.style.line;
                    }

                    //changing svgs
                    let div_in  = document.getElementById(param_in.id);
                    document.getElementById(param_in.id).innerHTML = svg_round_square_crossed("");
                    document.getElementById(param_out.id).innerHTML = svg_round_square_crossed("");

                    currently_dragged = null;
                    save_dataflow();
                    refresh_link_modal(link);
                }).catch (function(error) {
                    if (LOG_INTERACTION_EVENT) console.log('DID 1:', error);
                });
            }
            else {
                console.log("Already exists !!");
                currently_dragged = null;
            }
        }
        else if (currently_dragged && currently_dragged.id.includes("comment")) {
            if (LOG_INTERACTION_EVENT) console.log('DROPPING COMMENT');
            let rect = main_div[0].getBoundingClientRect();
            $('#'+currently_dragged.id).css({
                left: e.clientX - rect.x - drag_delta[0],
                top: e.clientY - rect.y - drag_delta[1]
            });
            drag_started = false;
            save_dataflow();
        }
        else {
            if (LOG_INTERACTION_EVENT) console.log('DROPPING NOTHING');
            currently_dragged = null;
        }
    }, false);

    main_div[0].addEventListener("contextmenu", function(e) {
        e.preventDefault();
        if (e.target.classList.contains("sakura_main")) {
            $('#sakura_main_div_contextMenu').css({
                visibility: "visible",
                left: e.clientX ,
                top: e.clientY
                });
        }
    }, false);

    main_div[0].addEventListener("click", function (e) {
        $('#sakura_operator_contextMenu').hide();
        $('#sakura_link_contextMenu').hide();
        link_focus_id = null;
        op_focus_id = null;
        $('#sakura_main_div_contextMenu').css({visibility: "hidden"});
    });
}

function jsp_drag_stop(e) {
    var ot = df_main_div()[0];
    if (e.el.getBoundingClientRect().left < ot.getBoundingClientRect().left)
        e.el.style.left = 20 + "px";
    if (e.el.getBoundingClientRect().top < ot.getBoundingClientRect().top)
        e.el.style.top = 20 + "px";

    var ids = e.el.id.split("_");

    //GUI update
    if (ids[0] == 'op') {
        var index = instance_index_from_id(ids[2]);
        global_ops_inst[index].gui = { x: parseInt(e.el.style.left),
                                       y: parseInt(e.el.style.top) };
        save_dataflow()
    }
    df_jsplumb().repaintEverything();        //Very Important when dragging elements manually
}

function jsp_drag_start(e) {
}
