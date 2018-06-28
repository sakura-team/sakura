sakura = {
    common: {
        ws: {
            internal: {
            }
        }
    }
}

CRYPTO_JS_FILES = [
        "/webcache/cdnjs/crypto-js/3.1.2/rollups/hmac-sha256.js",
        "/webcache/cdnjs/crypto-js/3.1.2/components/enc-base64-min.js"
];

// debugging
// ---------
// uncomment / comment to activate debug
//sakura.common.debug = function (s) { console.log("" + new Date().getTime() + " -- " + s); };
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
// whereas subsequent ones use /websockets/sessions/connect?session-secret=<secret>.
// For this secret to be valid on the hub side, one has to call web API function
// save_session_recovery_token(<hash>) in advance. When the hub catches such
// an URL, it verifies that hashing the <secret> results in <hash>.
// A given <secret> can only be used once.
sakura.common.ws.internal.running_requests = {};
sakura.common.ws.internal.next_req_idx = 0;
sakura.common.ws.internal.free_ws = [];
sakura.common.ws.internal.buffer = [];
sakura.common.ws.internal.bufferize = false;
sakura.common.ws.internal.session_secret = null;

sakura.common.ws.internal.complete_url = function (path) {
    var loc = window.location, proto;
    if (loc.protocol === "https:") {
        proto = "wss:";
    } else {
        proto = "ws:";
    }
    return proto + "//" + loc.host + path;
}

sakura.common.ws.internal.get_first_url = function () {
    var searchParams = new URLSearchParams(window.location.search);
    if (searchParams.has('session-secret')) {
        return sakura.common.ws.internal.get_duplicate_url(
                searchParams.get('session-secret')
        );
    }
    return sakura.common.ws.internal.complete_url("/websockets/sessions/new");
}

sakura.common.ws_url_add_secret = function (url, secret) {
    var param = "session-secret=" + encodeURIComponent(secret);
    url += (url.split('?')[1] ? '&':'?') + param;
    return url;
}

sakura.common.ws.internal.get_duplicate_url = function (secret) {
    var url = sakura.common.ws.internal.complete_url("/websockets/sessions/connect");
    return sakura.common.ws_url_add_secret(url, secret);
}

sakura.common.ws.internal.default_error_callback = function (msg) {
    alert(msg);
}

sakura.common.ws.internal.onmessage = function (evt) {
    sakura.common.debug('sakura.common.ws.internal.onmessage called');
    IO_TRANSFERED = 0;
    IO_REQUEST_ERROR = 2;
    // parse the message
    var json = JSON.parse(evt.data);
    var req_idx = json[0];
    sakura.common.debug('ws_request ' + req_idx + ' got answer');
    var req = sakura.common.ws.internal.running_requests[req_idx];
    // sakura.common.ws.internal.running_requests[req_idx] will no longer be needed
    delete sakura.common.ws.internal.running_requests[req_idx];
    // we have the response, thus this websocket is free again
    sakura.common.ws.internal.free_ws.push(req.ws);
    sakura.common.debug('+1 (response received) *** ' + sakura.common.ws.internal.free_ws.length);
    if (json[1] == IO_TRANSFERED)
    {   // all ok, and result could be transfered
        // call the callback that was given with the request
        req.callback(json[2]);
        return;
    }
    if (json[1] == IO_REQUEST_ERROR)
    {   // backend returned an error, pass it to error_callback
        req.error_callback(json[2]);
        return;
    }
    console.error('Bug: result of ws_request() got unknown status: ' + json[1]);
}

sakura.common.ws.internal.send = function (func_name, args, kwargs, callback, error_callback) {
    sakura.common.debug('sakura.common.ws.internal.send called');
    IO_FUNC = 0;
    if (typeof error_callback === 'undefined')
    {
        error_callback = sakura.common.ws.internal.default_error_callback;
    }
    // get a callback id
    var req_idx = sakura.common.ws.internal.next_req_idx;
    sakura.common.ws.internal.next_req_idx += 1;
    // pop one of the free websockets
    // we select the 1st (using shift()), and we will append it back
    // at the end of the array (using push()) when receiving the response,
    // in to avoid having idle websockets that would be closed by HTTP proxies.
    let ws = sakura.common.ws.internal.free_ws.shift();
    sakura.common.debug('-1 (sending message..) *** ' + sakura.common.ws.internal.free_ws.length);
    if (ws == undefined) {
        console.error('ws undefined!!');
        return;
    }
    // record the request using its id
    sakura.common.ws.internal.running_requests[req_idx] = {
        'ws': ws,
        'callback': callback,
        'error_callback': error_callback
    };
    // prepare the message and send it
    var msg = JSON.stringify([ req_idx, [ IO_FUNC, [func_name], args, kwargs ]]);
    sakura.common.debug('ws_request sent: ' + msg);
    ws.send(msg);
}

sakura.common.ws.internal.create = function (ws_url, cb) {
    sakura.common.debug('sakura.common.ws.internal.create called');
    let ws = new WebSocket(ws_url);
    ws.onmessage = sakura.common.ws.internal.onmessage;
    ws.onopen = function() {
        sakura.common.debug('ws.onopen called');
        sakura.common.ws.internal.free_ws.push(ws);
        sakura.common.debug('+1 (ws just created!!) *** ' + sakura.common.ws.internal.free_ws.length);
        sakura.common.debug('new ws ready!');
        // update secret for next time, then call cb()
        sakura.common.ws.internal.update_local_secret(cb);
    }
    ws.onerror = function() {
        console.error("ws error!");
        ws.close();
    }
    ws.onclose = function() {
        sakura.common.debug("ws closed!");
        // remove from free websockets
        sakura.common.ws.internal.free_ws = sakura.common.ws.internal.free_ws.filter(function(free_ws) {
            return free_ws != ws;
        });
        sakura.common.debug('-1?(ws was closed....) *** ' + sakura.common.ws.internal.free_ws.length);
    }
}

sakura.common.ws.internal.keep_alive = function() {
    sakura.common.ws_request('renew_session', [], {}, function() {})
}

sakura.common.ws.internal.with_crypto_js = function(cb) {
    if (typeof CryptoJS == 'undefined') {
        // we need to load crypto-js first.
        // we cannot load all files at once, because
        // crypto-js 'components' have to be loaded after
        // the 'rollup'.
        sakura.common.load_files_in_order(CRYPTO_JS_FILES, cb);
    }
    else {  // cb can be called directly
        cb();
    }
}

sakura.common.ws.internal.generate_secret = function(cb) {
    sakura.common.debug('sakura.common.ws.internal.generate_secret called');
    sakura.common.ws.internal.with_crypto_js(function() {
        // generate a random secret
        var session_secret = CryptoJS.lib.WordArray.random(32);
        // hash it
        var recovery_token = CryptoJS.SHA256(session_secret);
        // encode as base64
        session_secret = session_secret.toString(CryptoJS.enc.Base64);
        recovery_token = recovery_token.toString(CryptoJS.enc.Base64);
        // transmit the hash to the hub as a session recovery token
        // then call cb(session_secret)
        sakura.common.ws.internal.send('save_session_recovery_token',
                                [ recovery_token ],
                                {},
                                function() {
                                    cb(session_secret);
                                });
    });
}

sakura.common.ws.internal.update_local_secret = function(cb) {
    sakura.common.debug('sakura.common.ws.internal.update_local_secret called');
    // generate a random secret
    sakura.common.ws.internal.generate_secret(function(session_secret) {
        // save random secret for later session retrieval
        sakura.common.ws.internal.session_secret = session_secret;
        sakura.common.debug('updated local secret saved.');
        // call cb()
        cb();
    });
}

sakura.common.ws.internal.duplicate = function (cb) {
    sakura.common.debug('sakura.common.ws.internal.duplicate called');
    // Use our previously recorded session secret to create
    // a new websocket.
    let url = sakura.common.ws.internal.get_duplicate_url(sakura.common.ws.internal.session_secret);
    sakura.common.ws.internal.create(url, cb);
}

sakura.common.ws.internal.unset_bufferize = function() {
    sakura.common.debug('sakura.common.ws.internal.unset_bufferize called');
    let idx;
    // we first make a copy because callbacks may deal
    // with the buffer
    let delayed_callbacks = sakura.common.ws.internal.buffer.slice();
    // set the flag
    sakura.common.ws.internal.bufferize = false;
    // empty buffer
    sakura.common.ws.internal.buffer = [];
    // run delayed callbacks.
    for (idx in delayed_callbacks) {
        let cb = delayed_callbacks[idx];
        cb();
    }
}

sakura.common.ws.internal.prepare = function (cb) {
    sakura.common.debug('sakura.common.ws.internal.prepare called');
    let recall = function() {
        sakura.common.debug('recalling sakura.common.ws.internal.prepare...');
        sakura.common.ws.internal.prepare(cb);
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
    if (sakura.common.ws.internal.bufferize)
    {
        sakura.common.ws.internal.buffer.push(recall);
        return;
    }

    // check if this is the first call (no session yet)
    if (sakura.common.ws.internal.session_secret == null)
    {
        // set buffering mode
        sakura.common.ws.internal.bufferize = true;
        sakura.common.ws.internal.buffer.push(recall);
        // create the 1st websocket, retry when it's done
        let url = sakura.common.ws.internal.get_first_url();
        sakura.common.debug('creating 1st ws');
        sakura.common.ws.internal.create(url, sakura.common.ws.internal.unset_bufferize);
        return;
    }

    // if there is no free websocket, create a new one
    if (sakura.common.ws.internal.free_ws.length == 0)
    {
        sakura.common.ws.internal.bufferize = true;
        sakura.common.ws.internal.buffer.push(recall);
        sakura.common.debug('creating other ws');
        sakura.common.ws.internal.duplicate(sakura.common.ws.internal.unset_bufferize);
        return;
    }

    // everything is fine, call cb
    cb();
}

sakura.common.ws_request = function (func_name, args, kwargs, callback, error_callback) {
    sakura.common.debug('sakura.common.ws_request called');
    sakura.common.ws.internal.prepare(function() {
        sakura.common.ws.internal.send(func_name, args, kwargs, callback, error_callback);
    });
}

sakura.common.ws_generate_secret = function(cb) {
    sakura.common.ws.internal.prepare(function() {
        sakura.common.ws.internal.generate_secret(cb);
    });
}

// send a keep alive every 30s
setInterval(sakura.common.ws.internal.keep_alive, 30000);

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

sakura.common.load_files_in_order = function (sources, cb) {
    let remaining_sources = sources.slice();     // copy
    let first_item = remaining_sources.shift();  // 1st item removed
    sakura.common.load_files(
            [ first_item ],
            function() {
                if (remaining_sources.length > 0)
                {
                    sakura.common.load_files_in_order(remaining_sources, cb);
                }
                else
                {
                    cb();
                }
            }
    );
}
