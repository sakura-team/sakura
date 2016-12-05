
var ws_gui = new WebSocket("ws://localhost:8080/websockets/gui");
ws_gui.onmessage = function (evt) {
    var json = JSON.parse(evt.data);
    if (json.event == 'list_daemons')
    {
        result = json.data
        $('#result').html(JSON.stringify(result));
    }
};
function list_daemons() {
    msg = JSON.stringify([ 'list_daemons', [], {}]);
    ws_gui.send(msg);
}
