//Code started by Etienne Dublé for the LIG
//February 16th, 2017

REQUIRED_JS = [
        "/js/jquery-2.2.4.min.js",
        "/js/websocket.js"
];

REQUIRED_CSS = [
        "/css/main.css",
        "/bootstrap-3.3.7/css/bootstrap.min.css",
        "/bootstrap-3.3.7/css/bootstrap-select.min.css"
];

var sakura_op_info = null;

function get_internal_stream_proxy(stream_index) {
    return {
        get_range: function (row_start, row_end, cb) {
            ws_request( 'get_operator_internal_range',
                        [sakura_op_info.op_id, stream_index, row_start, row_end],
                        {},
                        cb);
        }
    }
}

function sakura_operator_init() {
    // parse the operator instance id from the page url
    var url_path = window.location.pathname;
    var op_id = parseInt(url_path.match(/opfiles\/([0-9]*)\//)[1],10);
    ws_request('get_operator_instance_info', [op_id], {}, function (op_info) {
        sakura_op_info = op_info;
    });
}

sakura = {
    operator: {
        get_internal_stream: function (stream_label) {
            var result = null;
            for (id in sakura_op_info.internal_streams) {
                if (sakura_op_info.internal_streams[id].label == stream_label)
                    return get_internal_stream_proxy(parseInt(id));
            };
        },
        fire_event: function (event, cb) {
            ws_request( 'fire_operator_event',
                        [sakura_op_info.op_id, event],
                        {},
                        cb);
        }
    }
}

// load required js files, then call sakura_operator_init
load_files(REQUIRED_JS, sakura_operator_init);
// load required css files
load_files(REQUIRED_CSS, function do_nothing() {});
