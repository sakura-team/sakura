
HEATMAP_RADIUS = 15;
HEATMAP_REFRESH_DELAY = 0.3;

function update_heatmap_callback(result) {
    var icon;
    if ('issue' in result)
    {
        infobox.update({ 'icon': 'alert', 'text': result.issue });
        return;
    }
    if (result.heatmap.done)
    {   // input data is complete for this map
        icon = 'check';
    }
    else {
        icon = 'hourglass';
        // request server for more complete data,
        // while we refresh the screen
        sakura.operator.fire_event(
                ["map_continue", HEATMAP_REFRESH_DELAY],
                update_heatmap_callback);
    }
    // expand compressed data
    heatmap_values = expand_heatmap_values(result.heatmap);
    // refresh the heatmap layer
    if (heatmap_layer != null)
    {
        map.removeLayer(heatmap_layer)
    }
    heatmap_layer = L.heatLayer(heatmap_values, {
                radius:     HEATMAP_RADIUS
    });
    heatmap_layer.addTo(map);
    // update infobox
    infobox.update({ "icon": icon, 'text': result.heatmap.count + ' points' });
    var t1 = new Date().getTime();
    console.log('map update: ' + ((t1 - t0)/1000.0) + " seconds");
}

function request_heatmap() {

    t0 = new Date().getTime();

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

    if (width == 0 || height == 0) {
        // the map is propably not displayed yet
        return;
    }

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
    sakura.operator.fire_event(
            ["map_move", HEATMAP_REFRESH_DELAY, info],
            update_heatmap_callback);
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
    map = L.map('map');
    map.on('moveend', request_heatmap);
    //map.on('load', request_heatmap); // update on first load
    markers_layer = null;
    heatmap_layer = null;

    var layer = L.tileLayer('https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; <a href="https://carto.com/attribution">CARTO</a>'
      });

    map.addLayer(layer);

    infobox = L.control();

    infobox.onAdd = function (map) {
        this._div = L.DomUtil.create('div', 'infobox'); // create a div with a class "infobox"
        return this._div;
    };

    // method that we will use to update the control based on feature properties passed
    infobox.update = function (props) {
        this._div.innerHTML = props.text + ' ' +
                    '<span class="glyphicon glyphicon-' + props.icon + '"></span>';
    };

    infobox.addTo(map);

    map.setView([48.86, 2.34], 9); // will cause the load event
}

