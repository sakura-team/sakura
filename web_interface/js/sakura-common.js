sakura = {
    common: {
        ws: { }
    }
}

// debugging
// ---------
// uncomment / comment to activate debug
//sakura.common.debug = function (s) { console.log(s); };
sakura.common.debug = function (s) { };

sakura.common.debug('Loading sakura-common.js');


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
// This code handles several parallel requests to the hub,
// because the calling javascript code is doing several things
// in parallel.
// To achieve this, we connect several websockets. Each of these websocket
// may be free or busy at a given time. 'busy' means that a request was
// sent on this websocket but the response was not obtained yet.
// All websockets created should target the same session on hub side.
// That's why the 1st websocket we create uses url /websockets/sessions/new,
// whereas subsequent ones use /websockets/sessions/connect/<secret>.
// The secret in this second url is obtained by calling API function
// generate_session_secret(). Thus we must already have at least one free
// websocket in order to create a new one.
// As a consequence, this code ensures we always keep at least one free
// websocket.
sakura.common.ws.running_requests = {};
sakura.common.ws.next_req_idx = 0;
sakura.common.ws.free_ws = [];
sakura.common.ws.buffer = [];
sakura.common.ws.bufferize = false;

sakura.common.ws.complete_url = function (path) {
    var loc = window.location, proto;
    if (loc.protocol === "https:") {
        proto = "wss:";
    } else {
        proto = "ws:";
    }
    return proto + "//" + loc.host + path;
}

sakura.common.ws.get_first_url = function () {
    return sakura.common.ws.complete_url("/websockets/sessions/new");
}

sakura.common.ws.get_duplicate_url = function (secret) {
    return sakura.common.ws.complete_url(
                "/websockets/sessions/connect/" + secret);
}

sakura.common.ws.default_error_callback = function (msg) {
    alert(msg);
}

sakura.common.ws.onmessage = function (evt) {
    // parse the message
    var json = JSON.parse(evt.data);
    var req_idx = json[0];
    sakura.common.debug('ws_request ' + req_idx + ' got answer');
    var response = json[1];
    var req = sakura.common.ws.running_requests[req_idx];
    // sakura.common.ws.running_requests[req_idx] will no longer be needed
    delete sakura.common.ws.running_requests[req_idx];
    // we have the response, thus this websocket is free again
    sakura.common.ws.free_ws.push(req.ws);
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

sakura.common.ws.send = function (func_name, args, kwargs, callback, error_callback) {
    if (typeof error_callback === 'undefined')
    {
        error_callback = sakura.common.ws.default_error_callback;
    }
    // get a callback id
    var req_idx = sakura.common.ws.next_req_idx;
    sakura.common.ws.next_req_idx += 1;
    // pop one of the free websockets
    var ws = sakura.common.ws.free_ws.pop();
    // record the request using its id
    sakura.common.ws.running_requests[req_idx] = {
        'ws': ws,
        'callback': callback,
        'error_callback': error_callback
    };
    // prepare the message and send it
    var msg = JSON.stringify([ req_idx, [func_name], args, kwargs ]);
    console.log('ws_request sent: ' + msg);
    ws.send(msg);
}

sakura.common.ws.create = function (ws_url, cb) {
    // isolate var ws
    (function() {

    var ws = new WebSocket(ws_url);
    ws.onmessage = sakura.common.ws.onmessage;
    ws.onopen = function() {
        sakura.common.ws.free_ws.push(ws);
        sakura.common.debug('new ws ready!');
        // callback
        cb();
    }
    ws.onerror = function() {
        console.error("ws error!");
    }

    // end and execute anonymous function
    })();
}

sakura.common.ws.duplicate = function (cb) {
    // generate a session secret by using an existing free websocket,
    // and use this secret to create another websocket linked to the
    // same session.
    sakura.common.ws.send(
        'generate_session_secret', [], {},
        function (secret) {
            var url = sakura.common.ws.get_duplicate_url(secret);
            sakura.common.ws.create(url, cb);
        }
    );
}

sakura.common.ws.unset_bufferize = function() {
    var idx;
    // we first make a copy because callbacks may deal
    // with the buffer
    var delayed_callbacks = sakura.common.ws.buffer.slice();
    // set the flag
    sakura.common.ws.bufferize = false;
    // empty buffer
    sakura.common.ws.buffer = [];
    // run delayed callbacks.
    for (idx in delayed_callbacks) {
        cb = delayed_callbacks[idx];
        cb();
    }
}

sakura.common.ws_request = function (func_name, args, kwargs, callback, error_callback) {
    // please javascript, I need var 'recall' to be a different variable instance
    // each time I call this function!
    (function() {

    var recall = function() {
        sakura.common.ws_request(func_name, args, kwargs, callback, error_callback);
    };

    // firefox fails if we call ws API too early
    if (sakura.common.document_ready == false)
    {
        sakura.common.debug('document NOT ready');
        // restart the call when document is ready
        sakura.common.add_document_onready(recall);
        return;
    }

    // check if we should bufferize
    if (sakura.common.ws.bufferize)
    {
        sakura.common.ws.buffer.push(recall);
        return;
    }

    // check if this is the first call (no websockets yet)
    if (sakura.common.ws.free_ws.length == 0)
    {
        // set buffering mode
        sakura.common.ws.bufferize = true;
        sakura.common.ws.buffer.push(recall);
        // create the 1st websocket, retry when it's done
        var url = sakura.common.ws.get_first_url();
        sakura.common.debug('creating 1st ws');
        sakura.common.ws.create(url, sakura.common.ws.unset_bufferize);
        return;
    }

    // we do not want to have all websockets busy: if this is the
    // last free websocket, create a new one before sending the request.
    if (sakura.common.ws.free_ws.length == 1)
    {
        sakura.common.ws.bufferize = true;
        sakura.common.ws.buffer.push(recall);
        sakura.common.debug('creating other ws');
        sakura.common.ws.duplicate(sakura.common.ws.unset_bufferize);
        return;
    }

    // everything is fine, send
    sakura.common.ws.send(func_name, args, kwargs, callback, error_callback);

    // end and execute anonymous function
    })();
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

