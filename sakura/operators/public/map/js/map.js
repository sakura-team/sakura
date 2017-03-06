function update_markers() {
    var old_markers_layer = markers_layer;
    markers_layer = new L.FeatureGroup();
    var markers_stream = sakura.operator.get_internal_stream('Markers');
    markers_stream.get_range(0, 1000, function (markers) {
        markers.forEach(function(lnglat) {
            add_marker([lnglat[1], lnglat[0]]);
        });
    });
    map.addLayer(markers_layer);
    if (old_markers_layer != null) {
        map.removeLayer(old_markers_layer)
    }
}

function add_marker(latlng) {
    L.marker(latlng).addTo(markers_layer);
}

function map_clicked(e) {
    // send event, then update map
    sakura.operator.fire_event(["map_clicked", e.latlng],
        function(result) {
            add_marker(e.latlng);
        });
}

function map_move(e) {
    // send event, then update map
    var bounds = map.getBounds();
    sakura.operator.fire_event(["map_move", bounds.getSouthWest(), bounds.getNorthEast()],
        function(result) {
            update_markers();
        });
}

function init_map() {
    map = L.map('map').setView([51.505, -0.09], 13);
    markers_layer = null;

    var layer = L.tileLayer('https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; <a href="https://carto.com/attribution">CARTO</a>'
      });

    map.addLayer(layer);

    map.setView(new L.LatLng(51.3, 0.7),9);
    map.on('click', map_clicked);
    map.on('moveend', map_move);
}

sakura.operator.onready(init_map);
