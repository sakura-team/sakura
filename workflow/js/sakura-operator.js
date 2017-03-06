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

function InternalStreamInterface(op_id, stream_index) {
    this.op_id = op_id;
    this.stream_index = stream_index;
    this.get_range = function (row_start, row_end, cb) {
            ws_request( 'get_operator_internal_range',
                        [this.op_id, this.stream_index, row_start, row_end],
                        {},
                        cb);
    };
}

function SakuraOperatorInterface() {
    this.op_info = null;
    this._on_ready_cb = null;
    this.init = function () {
        // parse the operator instance id from the page url
        var url_path = window.location.pathname;
        var op_id = parseInt(url_path.match(/opfiles\/([0-9]*)\//)[1],10);
        var op = this;  // 'this' will be overriden in the body of the function below
        ws_request('get_operator_instance_info', [op_id], {}, function (op_info) {
            op.op_info = op_info;
            // if an on-ready callback has been defined, call it.
            if (op._on_ready_cb != null) {
                op._on_ready_cb();
            }
        });
    };
    this.get_internal_stream = function (stream_label) {
        var result = null;
        for (id in this.op_info.internal_streams) {
            if (this.op_info.internal_streams[id].label == stream_label)
                return new InternalStreamInterface(this.op_info.op_id, parseInt(id));
        };
    };
    this.fire_event = function (event, cb) {
        ws_request( 'fire_operator_event',
                    [this.op_info.op_id, event],
                    {},
                    cb);
    };
    this.onready = function (cb) {
        if (this.op_info != null) {
            // ok cb can be executed right now
            cb();
        }
        else {
            // let's have it executed when init is done
            this._on_ready_cb = cb;
        }
    };
}

function sakura_operator_init() {
    sakura.operator.init();
}

sakura = {
    operator: new SakuraOperatorInterface()
}

// load required js files, then call sakura_operator_init
load_files(REQUIRED_JS, sakura_operator_init);
// load required css files
load_files(REQUIRED_CSS, function do_nothing() {});
