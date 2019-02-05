/* We want an easy-to-use API call mechanism:
   hub.workflows[3].info().then(function(result) {
     console.log('workflow info: ' + result);
   });

   The function call may involve named parameters. In this case, they must be specified
   in the form of a directory and as the last argument:
   sakura.hub.<func>(<arg1>, <arg2>, { <name1>: <val1>, <name2>: <val2> }).then(...).catch(...);
*/

sakura = {
    internal: {
    },
    tools: {
    },
    apis: {
    }
}

// debugging
// ---------
// uncomment / comment to activate debug
//sakura.internal.debug = function (s) { console.log("" + new Date().getTime() + " -- " + s); };
sakura.internal.debug = function (s) { };

sakura.internal.debug('Loading sakura-common.js');


// document ready state management
// -------------------------------
sakura.internal.document_ready = false;

sakura.internal.add_document_onready = function (cb) {
    document.addEventListener("DOMContentLoaded", function(event) {
        cb();
    });
}

sakura.internal.add_document_onready(function() {
    sakura.internal.document_ready = true;
    sakura.internal.debug('document now ready');
});

// websocket management
// --------------------
// This code handles several parallel requests to the hub,
// because the calling javascript code is doing several things
// in parallel.
// To achieve this, we connect several websockets. Each of these websocket
// may be free or busy at a given time. 'busy' means that a request was
// sent on this websocket but the response was not obtained yet.
sakura.internal.running_requests = {};
sakura.internal.next_req_idx = 0;
sakura.internal.free_ws = [];

sakura.internal.complete_url = function (path) {
    var loc = window.location, proto;
    if (loc.protocol === "https:") {
        proto = "wss:";
    } else {
        proto = "ws:";
    }
    return proto + "//" + loc.host + path;
}

sakura.internal.get_url = function () {
    return sakura.internal.complete_url("/websocket");
}

sakura.internal.default_error_callback = function (msg) {
    alert(msg);
}

/* this wrapper around the Promise object allows to
   make sure uncaught exceptions are handled by
   our default_error_callback. */
sakura.internal.PromiseWrapper = function (cb) {
    let _resolve_func = null;
    let _reject_func = null;
    // start a real async promise, and when it will be completed,
    // resolve and reject handlers will be have been set appropriately
    // by then() and catch() methods defined below.
    let p = new Promise(cb).then(function(res){
      if (_resolve_func !== null) {
        _resolve_func(res);
      };
    }).catch(function(res){
      if (_reject_func === null) {
        sakura.internal.default_error_callback(res);
      }
      else {
        _reject_func(res);
      };
    });
    // then() method
    this.then = function(resolve_cb) {
      if (_resolve_func !== null) {
        console.error('ERROR: PromiseWrapper cannot handle chaining then() callbacks, sorry!');
      }
      _resolve_func = resolve_cb;
      return this;
    };
    // catch() method
    this.catch = function(reject_cb) {
      if (_reject_func !== null) {
        console.error('ERROR: PromiseWrapper cannot handle chaining catch() callbacks, sorry!');
      }
      _reject_func = reject_cb;
      return this;
    };
    return this;
};

sakura.internal.onmessage = function (evt) {
    sakura.internal.debug('sakura.internal.onmessage called');
    IO_TRANSFERED = 0;
    IO_REQUEST_ERROR = 2;
    // parse the message
    var json = JSON.parse(evt.data);
    var req_idx = json[0];
    sakura.internal.debug('ws_request ' + req_idx + ' got answer');
    var req = sakura.internal.running_requests[req_idx];
    // sakura.internal.running_requests[req_idx] will no longer be needed
    delete sakura.internal.running_requests[req_idx];
    // we have the response, thus this websocket is free again
    sakura.internal.free_ws.push(req.ws);
    sakura.internal.debug('+1 (response received) *** ' + sakura.internal.free_ws.length);
    if (json[1] == IO_TRANSFERED)
    {   // all ok, and result could be transfered
        // call the callback that was given with the request
        req.callback(json[2]);
        return;
    }
    if (json[1] == IO_REQUEST_ERROR)
    {   // backend returned an error, pass it to error_callback
        err_cls_name = json[2]
        err_msg = json[3]
        req.error_callback(err_cls_name + ': ' + err_msg);
        return;
    }
    console.error('Bug: result of ws_request() got unknown status: ' + json[1]);
}

sakura.internal.send = function (func_path, args, kwargs, callback, error_callback) {
    sakura.internal.debug('sakura.internal.send called');
    IO_FUNC = 0;
    if (typeof error_callback === 'undefined')
    {
        error_callback = sakura.internal.default_error_callback;
    }
    // get a callback id
    var req_idx = sakura.internal.next_req_idx;
    sakura.internal.next_req_idx += 1;
    // pop one of the free websockets
    // we select the 1st (using shift()), and we will append it back
    // at the end of the array (using push()) when receiving the response,
    // in to avoid having idle websockets that would be closed by HTTP proxies.
    let ws = sakura.internal.free_ws.shift();
    sakura.internal.debug('-1 (sending message..) *** ' + sakura.internal.free_ws.length);
    if (ws == undefined) {
        console.error('ws undefined!!');
        return;
    }
    // record the request using its id
    sakura.internal.running_requests[req_idx] = {
        'ws': ws,
        'callback': callback,
        'error_callback': error_callback
    };
    // prepare the message and send it
    var msg = JSON.stringify([ req_idx, [ IO_FUNC, func_path, args, kwargs ]]);
    sakura.internal.debug('ws_request sent: ' + msg);
    ws.send(msg);
}

sakura.internal.create = function (cb) {
    sakura.internal.debug('sakura.internal.create called');
    let ws_url = sakura.internal.get_url();
    let ws = new WebSocket(ws_url);
    let cb_called = false;
    ws.onmessage = sakura.internal.onmessage;
    ws.onopen = function() {
        sakura.internal.debug('ws.onopen called');
        sakura.internal.free_ws.push(ws);
        sakura.internal.debug('+1 (ws just created!!) *** ' + sakura.internal.free_ws.length);
        sakura.internal.debug('new ws ready!');
        // ready, call cb()
        cb_called = true;
        cb();
    }
    ws.onerror = function() {
        console.error("ws error!");
        ws.close();
    }
    ws.onclose = function() {
        sakura.internal.debug("ws closed!");
        // remove from free websockets
        sakura.internal.free_ws = sakura.internal.free_ws.filter(function(free_ws) {
            return free_ws != ws;
        });
        sakura.internal.debug('-1?(ws was closed....) *** ' + sakura.internal.free_ws.length);
        if (!cb_called) {
            // retry
            sakura.internal.create(cb);
        }
    }
}

sakura.internal.keep_alive = function() {
    sakura.internal.ws_request(['renew_session'], [], {}, function() {})
}

sakura.internal.prepare = function (cb) {
    sakura.internal.debug('sakura.internal.prepare called');
    let recall = function() {
        sakura.internal.debug('recalling sakura.internal.prepare...');
        sakura.internal.prepare(cb);
    };

    // firefox fails if we call ws API too early
    if (sakura.internal.document_ready == false)
    {
        sakura.internal.debug('document NOT ready');
        // restart the call when document is ready
        sakura.internal.add_document_onready(recall);
        return;
    }

    // if there is no free websocket, create a new one
    if (sakura.internal.free_ws.length == 0)
    {
        sakura.internal.debug('creating ws');
        sakura.internal.create(recall);
        return;
    }

    // everything is fine, call cb
    cb();
}

sakura.internal.ws_request = function (func_path, args, kwargs, callback, error_callback) {
    sakura.internal.debug('sakura.internal.ws_request called');
    sakura.internal.prepare(function() {
        sakura.internal.send(func_path, args, kwargs, callback, error_callback);
    });
};

sakura.internal.hub_api_send = function(path, args) {
    let named_args = {};
    let posit_args = args;

    /* a dictionary of named arguments may be passed as the last
       positional argument */
    if (args.length > 0) {
        let last_arg = args[args.length-1];
        if ((typeof last_arg) === 'object' && !Array.isArray(last_arg)) {
            named_args = last_arg;
            posit_args = args.slice(0, args.length-1);
        }
    }

    return new sakura.internal.PromiseWrapper(function(resolve, reject) {
        sakura.internal.ws_request(path, posit_args, named_args, resolve, reject);
    });
};

/* This relies on Proxy features, see
   https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Proxy
   We catch object property access (through get(), see below) to iterately build the API
   request path, up to the function call. The function call itself is catched by apply()
   function. */

sakura.internal.get_hub_api = function(path) {
    let _internal_attrs = {};
    return new Proxy(sakura.internal.hub_api_send, {
        path: path,
        _internal_attrs: _internal_attrs,
        set: function(target, prop, value, receiver) {
            _internal_attrs[prop] = value;
        },
        get: function(target, prop, receiver) {
            if (_internal_attrs.hasOwnProperty(prop)) {
                return _internal_attrs[prop];
            }
            let new_path = this.path.slice();
            let prop_as_int = parseInt(prop, 10);
            if (!isNaN(prop_as_int)) {
                new_path.push([ prop_as_int ]);
            }
            else {
                new_path.push(prop);
            }
            return sakura.internal.get_hub_api(new_path);
        },
        apply: function(target, this_arg, args) {
            return target(this.path, args);
        }
    });
};

sakura.apis.hub = sakura.internal.get_hub_api([]);

// send a keep alive every 30s
setInterval(sakura.internal.keep_alive, 30000);

// tools
// -----
sakura.tools.load_files = function (sources, cb) {
    // dynamically load js or css files by appending a
    // <script> or <link> element to the <head>.
    cb.counter = sources.length;
    for (src_id in sources) {
        var elem;
        var src = sources[src_id];
        if (src.endsWith('.js')) { // javascript
            elem  = document.createElement("script");
            elem.src  = sources[src_id];
            elem.type = "text/javascript";
        }
        else { // css
            elem = document.createElement("link");
            elem.rel = "stylesheet";
            elem.type = "text/css";
            elem.href = src;
        }
        elem.onload = function () {
            cb.counter -= 1;
            if (cb.counter == 0) {
                cb();
            }
        };
        document.head.appendChild(elem);
    }
}

sakura.tools.load_files_in_order = function (sources, cb) {
    let remaining_sources = sources.slice();     // copy
    let first_item = remaining_sources.shift();  // 1st item removed
    sakura.tools.load_files(
            [ first_item ],
            function() {
                if (remaining_sources.length > 0)
                {
                    sakura.tools.load_files_in_order(remaining_sources, cb);
                }
                else
                {
                    cb();
                }
            }
    );
}
