//Code started by Etienne Dublé for the LIG
//February 16th, 2017

function StreamInterface(op, stream_type, stream_label) {
    this.get_range = function (row_start, row_end, cb) {
        op.do_when_init_done(function(op_info) {
            var streams;
            if (stream_type == 'input') {
                streams = op_info.inputs;
            }
            else if (stream_type == 'internal') {
                streams = op_info.internal_streams;
            }
            else if (stream_type == 'output') {
                streams = op_info.outputs;
            }
            else {
                console.error('UNKNOWN stream_type ' + stream_type);
                return;
            }
            for(var stream_id = 0; stream_id < streams.length; stream_id++) {
                if (streams[stream_id].label == stream_label) {
                    sakura.common.ws_request( 'get_operator_' + stream_type + '_range',
                            [op_info.op_id, stream_id, row_start, row_end],
                            {},
                            cb);
                }
            }
        });
    };
}

function SakuraOperatorInterface() {
    this.op_info = null;
    this._early_callbacks = [];

    this.init = function () {
        // parse the operator instance id from the page url
        var url_path = window.location.pathname;

        if(url_path!=null){
            sakura.common.debug('sakura.operator.init...');

            /* parsing of the url to get the operator instance */
            var op_id = this.get_op_id_from_url(url_path);
            var op = this;  // 'this' will be overriden in the body of the function below
            sakura.common.ws_request('get_operator_instance_info', [op_id], {}, function (op_info) {
                sakura.common.debug('sakura.operator.init... connected to hub');
                op.op_info = op_info;
                // if early callbacks were defined, call them.
                op.run_early_callbacks();
            });
        }
        else {
            console.error('url_path is null!');
        }
    };

    this.get_op_id_from_url = function (url) {
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

    this.run_early_callbacks = function() {
        var i;
        for (i = 0; i < this._early_callbacks.length; i++) {
            var cb = this._early_callbacks[i];
            sakura.common.debug('calling delayed callback');
            cb(this.op_info);
        }
        this._early_callbacks = [];
    };

    this.do_when_init_done = function (cb) {
        if (this.op_info == null) {
            sakura.common.debug('callback delayed');
            this._early_callbacks.push(cb);
        }
        else {
            sakura.common.debug('callback called directly');
            cb(this.op_info);
        }
    };

    this.ws_request_with_op_id = function (path, args, kwargs, cb) {
        this.do_when_init_done(function(op_info) {
            args.unshift(op_info.op_id);    // insert op_id as 1st arg
            sakura.common.ws_request(path, args, kwargs, cb);
        });
    };

    this.get_input_stream = function (stream_label) {
        return new StreamInterface(this, 'input', stream_label);
    };

    this.get_internal_stream = function (stream_label) {
        return new StreamInterface(this, 'internal', stream_label);
    };

    this.get_output_stream = function (stream_label) {
        return new StreamInterface(this, 'output', stream_label);
    };

    this.onready = function(cb) {
        // cb expects no arg, we ignore the op_info here
        this.do_when_init_done(function(op_info) {
            cb();
        });
    };

    this.info = function (cb) {
        this.ws_request_with_op_id(
            'get_operator_instance_info', [], {}, cb);
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

sakura.operator = new SakuraOperatorInterface();
sakura.operator.init();

