//Code started by Etienne Dublé for the LIG
//February 16th, 2017

REQUIRED_JS = [
        "/js/jquery-2.2.4.min.js",
        "/js/websocket.js",
        // "https://cdnjs.cloudflare.com/ajax/libs/ace/1.2.6/ace.js",
        "https://cdnjs.cloudflare.com/ajax/libs/jstree/3.2.1/jstree.min.js",
        "https://code.jquery.com/ui/1.12.1/jquery-ui.js",
        "/code-editor/js/library.js",
        "/code-editor/js/index.js",
        "/code-editor/js/tabClasses.js",
];

REQUIRED_CSS = [
        "/css/main.css",
        "/bootstrap-3.3.7/css/bootstrap.min.css",
        "/bootstrap-3.3.7/css/bootstrap-select.min.css",
        // "https://cdnjs.cloudflare.com/ajax/libs/ace/1.2.6/ext-modelist.js",
        "https://cdnjs.cloudflare.com/ajax/libs/jstree/3.2.1/themes/default/style.min.css",
        "https://code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css",
        "/code-editor/style.css"
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
    this._on_ready_cb = null;

    this.init = function () {
        // parse the operator instance id from the page url
        var url_path = window.location.pathname;

        if(url_path!=null){

            /* parsing of the url to get the operator instance */
            var op_id=testOperatorUrl(url_path);
            var op = this;  // 'this' will be overriden in the body of the function below
            ws_request('get_operator_instance_info', [op_id], {}, function (op_info) {
                op.op_info = op_info;
                // if an on-ready callback has been defined, call it.
                if (op._on_ready_cb != null) {
                    op._on_ready_cb();
                }
            });
        }
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
    this.get_file_content = function (file_path, cb) {
        ws_request( 'get_operator_file_content',
                    [this.op_info.op_id, file_path],
                    {},
                    cb);
    };
    this.get_file_tree = function (cb) {
        ws_request( 'get_operator_file_tree',
                    [this.op_info.op_id],
                    {},
                    cb);
    };
    this.save_file_content = function (file_path, file_content, cb) {
        ws_request( 'save_operator_file_content',
                    [this.op_info.op_id, file_path, file_content],
                    {},
                    cb);
    };
    this.new_file = function (file_path, file_content, cb) {
        ws_request( 'new_operator_file',
                    [this.op_info.op_id, file_path, file_content],
                    {},
                    cb);
    };
    this.new_directory = function (dir_path, cb) {
        ws_request( 'new_operator_directory',
                    [this.op_info.op_id, dir_path],
                    {},
                    cb);
    };
    this.move_file = function (file_src, file_dst, cb) {
        ws_request( 'move_operator_file',
                    [this.op_info.op_id, file_src, file_dst],
                    {},
                    cb);
    };
    this.delete_file = function (file_path, cb) {
        ws_request( 'delete_operator_file',
                    [this.op_info.op_id, file_path],
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
