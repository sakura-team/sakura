sakura = {
    common: {}
}

// debugging
// ---------
// uncomment / comment to activate debug
//sakura.common.debug = function (s) { console.log(s); };
sakura.common.debug = function (s) { };


// document ready state management
// -------------------------------
sakura.common.document_ready = false;

sakura.common.add_document_onready = function (cb) {
    document.addEventListener("DOMContentLoaded", function(event) {
        cb();
    });
}

sakura.common.add_document_onready(function() {
    sakura.common.document_ready = true;
    sakura.common.debug('document now ready');
});

// websocket management
// --------------------
sakura.common.pending_requests = {};
sakura.common.next_req_idx = 0;
sakura.common.free_ws = [];

sakura.common.get_ws_url = function () {
    var loc = window.location, proto;
    if (loc.protocol === "https:") {
        proto = "wss:";
    } else {
        proto = "ws:";
    }
    return proto + "//" + loc.host + "/websockets/rpc";
}

sakura.common.default_error_callback = function (msg) {
    alert(msg);
}

sakura.common.ws_onmessage = function (evt) {
    // parse the message
    var json = JSON.parse(evt.data);
    var req_idx = json[0];
    sakura.common.debug('ws_request ' + req_idx + ' got answer');
    var response = json[1];
    var req = sakura.common.pending_requests[req_idx];
    // sakura.common.pending_requests[req_idx] will no longer be needed
    delete sakura.common.pending_requests[req_idx];
    // we have the response, thus this websocket is free again
    sakura.common.free_ws.push(req.ws);
    // call the callback that was given with the request
    if (response[0])
    {
        req.callback(response[1]);
    }
    else
    {
        req.error_callback(response[1]);
    }
}

sakura.common.ws_request = function (func_name, args, kwargs, callback, error_callback) {
    var ws;
    if (typeof error_callback === 'undefined')
    {
        error_callback = sakura.common.default_error_callback;
    }
    // firefox fails if we call ws API too early
    if (sakura.common.document_ready == false)
    {
        sakura.common.debug('document NOT ready');
        // restart the call when document is ready
        sakura.common.add_document_onready(function() {
            sakura.common.debug('recalling ws_request ' + func_name + ' after document is ready');
            sakura.common.ws_request(func_name, args, kwargs, callback, error_callback);
        });
        return;
    }

    // check if we have at least one websocket free
    if (sakura.common.free_ws.length == 0)
    {   // existing websockets are busy, create new one
        ws = new WebSocket(sakura.common.get_ws_url());
        ws.onmessage = sakura.common.ws_onmessage;
        ws.onopen = function() {
            sakura.common.free_ws.push(ws);
            // restart the call
            sakura.common.debug('recalling ws_request ' + func_name + ' with new ws');
            sakura.common.ws_request(func_name, args, kwargs, callback, error_callback);
        }
        ws.onerror = function() {
            console.error("ws " + func_name + " error!");
        }
        return;
    }
    // everything is fine, continue
    // get a callback id
    var req_idx = sakura.common.next_req_idx;
    sakura.common.next_req_idx += 1;
    // pop one of the free websockets
    ws = sakura.common.free_ws.pop();
    // record the request using its id
    sakura.common.pending_requests[req_idx] = {
        'ws': ws,
        'callback': callback,
        'error_callback': error_callback
    };
    // prepare the message and send it
    var msg = JSON.stringify([ req_idx, [func_name], args, kwargs ]);
    console.log('ws_request: ' + msg);
    sakura.common.debug('ws_request sending msg');
    ws.send(msg);
}

// tools
// -----
sakura.common.load_files = function (sources, cb) {
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

