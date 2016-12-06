
// implementation of button callbacks
function list_daemons() {
    ws_request('list_daemons', [], {}, function (result) {
        var printable_result = JSON.stringify(result);
        $('#result').html(printable_result);
    });
}
