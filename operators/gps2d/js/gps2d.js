var trajectories = []
var gps2d_map = null;

var trajectories = null;
var bounds = null;

function update_trajectories(chunk) {

  if (chunk.db !== null) {
      if (bounds === null)
          bounds = [chunk.min, chunk.max];
      else {
          bounds = [ [Math.min(bounds[0][0], chunk.min[0]),
                      Math.min(bounds[0][1], chunk.min[1])],
                     [Math.max(bounds[1][0], chunk.max[0]),
                      Math.max(bounds[1][1], chunk.max[1])]];
      }
      var coords = chunk.db.map(t => ([t[1], t[2]]));
      var polygon = L.polyline(coords, {color: 'red',
                                        weight: 3,
                                        opacity: 0.5,
                                        smoothFactor: 1}).addTo(gps2d_map);
      gps2d_map.fitBounds(bounds);

      sakura.apis.operator.fire_event('get_data_continue').then(
        update_trajectories
      );
  }
  else {
      console.log('Ended');
  }
}

function init_gps2d() {

    //Get data
    bounds = null;
    sakura.apis.operator.fire_event('get_data_first').then(
        update_trajectories
    );

    //map creation
    gps2d_map = L.map('gps2d_map_div');
    L.tileLayer('https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; <a href="https://carto.com/attribution">CARTO</a>',
        maxZoom: 18
        }).addTo(gps2d_map);
    gps2d_map.setView([51.505, -0.09], 7);
}
