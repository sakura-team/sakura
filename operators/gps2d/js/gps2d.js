function init_gps2d() {
    var mymap = L.map('gps2d_map_div');
    L.tileLayer('https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; <a href="https://carto.com/attribution">CARTO</a>',
        maxZoom: 18
        }).addTo(mymap);
    mymap.setView([51.505, -0.09], 13);
}
