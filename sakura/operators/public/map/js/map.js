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
    /*
    // send event, then update map
    sakura.operator.fire_event(["map_clicked", e.latlng],
        function(result) {
            add_marker(e.latlng);
        });
    */
}

function update_heatmap() {

    var t0 = new Date().getTime();

    // get lat / lng map bounds
    var geo_bounds = map.getBounds();
    var geo_sw = geo_bounds.getSouthWest();
    var geo_ne = geo_bounds.getNorthEast();

    // get pixel width / height
    // Note: map.getSize() gives us the whole map zone,
    // including top and bottom margins if the user zooms out
    // at maximum. Thus the height obtained this way may not
    // be correct.
    // We compute the size by projecting the lat / lng bounds
    // instead.
    var px_bottomleft = map.project(geo_sw);
    var px_topright = map.project(geo_ne);
    var width = Math.round(px_topright.x - px_bottomleft.x);
    var height = Math.round(px_bottomleft.y - px_topright.y);

    // geo_bounds latitude values seem wrong when the users zooms
    // out at maximum: they are outside the bounds given by the
    // web mercator projection, i.e. [-85.051129, 85.051129].
    // we unproject the pixel values to fix this.
    geo_ne = map.unproject(px_topright);
    geo_sw = map.unproject(px_bottomleft);
    geo_bounds = L.latLngBounds(geo_sw, geo_ne);

    info = {
        'width': width,
        'height': height,
        'westlng': geo_sw.lng,
        'eastlng': geo_ne.lng,
        'southlat': geo_sw.lat,
        'northlat': geo_ne.lat
    }
    console.log(info);

    // send event, then update map
    sakura.operator.fire_event(["map_move", info],
        function(result) {
            heatmap_values = expand_heatmap_values(result.heatmap);
            if (heatmap_layer != null)
            {
                map.removeLayer(heatmap_layer)
            }
            heatmap_layer = L.heatLayer(heatmap_values, {
                        radius:     15
            });
            heatmap_layer.addTo(map);
            var t1 = new Date().getTime();
            console.log('map update: ' + ((t1 - t0)/1000.0) + " seconds");
        });
}

/* In order to lower network usage, heatmap data is transfered in
 * a compressed form. lat / lng values are transmitted as integers
 * and we must now recompute the actual values by applying a given
 * scale and offset.
 */
function expand_heatmap_values(info) {
    var data = info.data, scales = info.scales, offsets = info.offsets,
        heatmap_values = [];
    for(var i = 0; i < data.lat.length; i++) {
        heatmap_values[i] = [
            data.lat[i] * scales.lat + offsets.lat,
            data.lng[i] * scales.lng + offsets.lng,
            data.val[i]
        ];
    }
    return heatmap_values;
}

function init_map() {
    map = L.map('map').setView([48.86, 2.34], 9);
    markers_layer = null;
    heatmap_layer = null;

    var layer = L.tileLayer('https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; <a href="https://carto.com/attribution">CARTO</a>'
      });

    map.addLayer(layer);

    map.on('click', map_clicked);
    map.on('moveend', update_heatmap);
    map.on('load', update_heatmap); // update when ready
}

sakura.operator.onready(init_map);
