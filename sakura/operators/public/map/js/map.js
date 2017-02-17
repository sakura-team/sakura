function map_test_clicked() {
    var markers = sakura.operator.get_internal_stream('Markers');
    sakura.operator.fire_event("toto", function(result) {
        markers.get_range(0, 1000, function (stream) {
            $("#label").text(stream);
        });
    });
}

