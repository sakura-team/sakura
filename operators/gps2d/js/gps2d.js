var trajectories  = {};
var gps2d_map = null;
var bounds = null;

var waiting_icon = '<span class="fa fa-cog fa-spin" style="font-size:30px; color:grey;"></span>';
var finished_icon = '<span class="fa fa-check" style="font-size:30px; color:green;"></span>';

var OpenTopoMap = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
       maxZoom: 18,
       opacity: .5,
       attribution: 'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)'
});

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
      newIds = []
      chunk.db.forEach(function(elt) {
          if (newIds.indexOf(elt[0]) == -1)
              newIds.push(elt[0])
          if (!trajectories[elt[0]]) {
              var r = String(Math.floor(Math.random()*255));
              var v = String(Math.floor(Math.random()*255));
              var b = String(Math.floor(Math.random()*255));
              trajectories[elt[0]] = L.polyline([[elt[2], elt[1]]],
                                                  { color: 'rgb('+r+','+v+','+b+')',
                                                    weight: 2,
                                                    opacity: 1,
                                                    smoothFactor: 1});
              trajectories[elt[0]].addTo(gps2d_map);
              trajectories[elt[0]].bindPopup("<b>ID:</b> "+elt[0]);
          }
          else
              trajectories[elt[0]].addLatLng([elt[2], elt[1]]);
      });
      gps2d_map.fitBounds(bounds);

      sakura.apis.operator.fire_event('get_data_continue').then(
          update_trajectories
      );
  }
  else {
      console.log('Ended');
      setTimeout(function(){
        $('#working_icon').css('display', 'none');
    }, 3000);
    $('#working_icon').html(finished_icon);
  }
}

function init_gps2d() {
    $('#working_icon').html(waiting_icon);
    $('#working_icon').css('display', 'block');

    //Get data
    bounds = null;
    trajectories = {}
    sakura.apis.operator.fire_event('get_data_first').then(
        update_trajectories
    );

    //map creation
    gps2d_map = L.map('gps2d_map_div');
    OpenTopoMap.addTo(gps2d_map);

    gps2d_map.setView([51.505, -0.09], 7);
}
