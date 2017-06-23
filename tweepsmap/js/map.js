function update_tweetsmap(){
  tweetsmap.operator.fire_event(['new_zone'], function(result) {
    var pruneCluster = new PruneClusterForLeaflet();
    var data = result.tweetsmap;
    for(var i = 0; i < data.lat.length; i++){
      marker = new PruneCluster.Marker(data.lat[i], data.lng[i]);
      pruneCluster.RegisterMarker(marker);
    }
    pruneCluster.Cluster.Size = 20;
    map.addLayer(pruneCluster);
  });
}

function init_tweetsmap(){
// initialize the map
  // map = L.map('map').setView([48.8, 2.5], 10);
  
  // // load a tile layer
  // L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
  //   attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
  //   maxZoom: 18,
  //   id: 'mapbox.satellite',
  //   accessToken: 'pk.eyJ1IjoibGUxIiwiYSI6ImNqM3U4YXB1ajAwMmU0bHJ0MnZ0dGhkcTQifQ.c0N7gp3wOjcAY9sAGCEMQA'
  // }).addTo(map);
  
  map = L.map("map", {
        attributionControl: false,
        zoomControl: false
    }).setView(new L.LatLng(48.8, 2.5), 12);

    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
        detectRetina: true,
        maxNativeZoom: 17
    }).addTo(map);
}

tweetsmap.operator.onready(init_tweetsmap);
console.log("changed");
update_tweetsmap();
