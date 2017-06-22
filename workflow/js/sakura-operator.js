//Code started by Etienne Dublé for the LIG
//February 16th, 2017

REQUIRED_JS = [
        "/js/jquery-2.2.4.min.js",
        "/js/websocket.js",
        "https://code.jquery.com/ui/1.12.1/jquery-ui.js",
];

REQUIRED_CSS = [
        "/css/main.css",
        "/bootstrap-3.3.7/css/bootstrap.min.css",
        "/bootstrap-3.3.7/css/bootstrap-select.min.css",
        "https://code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css",
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

function testOperatorUrl(url){
    var op_id;
    var match= url.match(/opfiles\/([0-9]*)\//);

    if(match!=null){
        /* if url of type .../opfile/[1-9]/[1-9] */
        op_id = parseInt(match[1],10);

    }else{
        /* if url of type .../code-editor/index.html?[1-9] */
        var url_path2 = window.location.href;
        var op_match =url_path2.split("/");
        if(op_match[op_match.length-2]=="code-editor"){
            var op_match2 =op_match[op_match.length-1].split("?");
            var op_id2 = op_match2[1];
            op_id=parseInt(op_id2);
        }
    }
    return op_id;
}

function SakuraOperatorInterface() {
    this.op_info = null;
    this._early_callbacks = [];

    this.init = function () {
        // parse the operator instance id from the page url
        var url_path = window.location.pathname;

        if(url_path!=null){

            /* parsing of the url to get the operator instance */
            var op_id=testOperatorUrl(url_path);
            var op = this;  // 'this' will be overriden in the body of the function below
            ws_request('get_operator_instance_info', [op_id], {}, function (op_info) {
                op.op_info = op_info;
                // if early callbacks were defined, call them.
                op.run_early_callbacks();
            });
        }
    };

    this.run_early_callbacks = function() {
        var i;
        for (i = 0; i < this._early_callbacks.length; i++) {
            var cb = this._early_callbacks[i];
            cb(this.op_info);
        }
        this._early_callbacks = [];
    };

    this.do_when_init_done = function (cb) {
        if (this.op_info == null) {
            this._early_callbacks.push(cb);
        }
        else {
            cb(this.op_info);
        }
    };

    this.ws_request_with_op_id = function (path, args, kwargs, cb) {
        this.do_when_init_done(function(op_info) {
            args.unshift(op_info.op_id);    // insert op_id as 1st arg
            ws_request(path, args, kwargs, cb);
        });
    };

    this.get_internal_stream = function (stream_label) {
        this.do_when_init_done(function(op_info) {
            var result = null;
            for (id in op_info.internal_streams) {
                if (op_info.internal_streams[id].label == stream_label)
                    return new InternalStreamInterface(op_info.op_id, parseInt(id));
            }
        });
    };

    this.onready = function(cb) {
        // cb expects no arg, we ignore the op_info here
        this.do_when_init_done(function(op_info) {
            cb();
        });
    };

    this.fire_event = function (event, cb) {
        this.ws_request_with_op_id(
            'fire_operator_event', [event], {}, cb);
    };
    this.get_file_content = function (file_path, cb) {
        this.ws_request_with_op_id(
            'get_operator_file_content', [file_path], {}, cb);
    };
    this.get_file_tree = function (cb) {
        this.ws_request_with_op_id(
            'get_operator_file_tree', [], {}, cb);
    };
    this.save_file_content = function (file_path, file_content, cb) {
        this.ws_request_with_op_id(
            'save_operator_file_content', [file_path, file_content], {}, cb);
    };
    this.new_file = function (file_path, file_content, cb) {
        this.ws_request_with_op_id(
            'new_operator_file', [file_path, file_content], {}, cb);
    };
    this.new_directory = function (dir_path, cb) {
        this.ws_request_with_op_id(
            'new_operator_directory', [dir_path], {}, cb);
    };
    this.move_file = function (file_src, file_dst, cb) {
        this.ws_request_with_op_id(
            'move_operator_file', [file_src, file_dst], {}, cb);
    };
    this.delete_file = function (file_path, cb) {
        this.ws_request_with_op_id(
            'delete_operator_file', [file_path], {}, cb);
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
