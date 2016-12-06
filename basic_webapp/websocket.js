
// websocket management
var ws_gui = new WebSocket("ws://localhost:8080/websockets/gui");
var callbacks = {};
var next_cb_idx = 0;

function ws_request(func_name, args, kwargs, callback)
{
    var cb_idx = next_cb_idx;
    next_cb_idx += 1;
    callbacks[cb_idx] = callback;
    var msg = JSON.stringify([ cb_idx, 'list_daemons', [], {}]);
    ws_gui.send(msg);
}

ws_gui.onmessage = function (evt) {
    var json = JSON.parse(evt.data);
    var cb_idx = json[0];
    var result = json[1];
    var callback = callbacks[cb_idx];
    delete callbacks[cb_idx];
    callback(result);
};

