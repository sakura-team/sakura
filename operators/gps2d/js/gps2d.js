var trajectories = []
var gps2d_map = null;

function update_trajectories(data) {
    console.log('toto');
    gps2d_map.setView([51.505, -0.09], 13);
}

function init_gps2d() {

    //Get data
    sakura.apis.operator.fire_event('get_data_first').then(
        update_trajectories
    );

    //map creation
    gps2d_map = L.map('gps2d_map_div');
    L.tileLayer('https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; <a href="https://carto.com/attribution">CARTO</a>',
        maxZoom: 18
        }).addTo(gps2d_map);
    gps2d_map.setView([51.505, -0.09], 13);
}
