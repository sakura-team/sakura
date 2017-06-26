function update_tweetsmap(){
    
    // get data by operators
    tweetsmap.operator.fire_event(['new_zone'], function (result) {
        // data = {lat: x, lng: y}
        var data = result.tweetsmap;
        // markers layer creation
        for (var i = 0; i < data.lat.length; i++) {
            // Corresponding marker
            var marker = new PruneCluster.Marker(data.lat[i], data.lng[i]);
            // filtre by ROIS
            myPrunceCluster.pruneCluster.RegisterMarker(marker);
        }
        var dictt = {};
        var overlay_control = L.control.layers(overlays = dictt).addTo(map);
        myOverlay.dict["all"] = myOverlay.getMarkers(myOverlay.name);
        overlay_control.addOverlay(myOverlay.getMarkers(myOverlay.name),"a")
        //map.removeControl(overlay_control);
        
        // set prunceCluster layer into map
        map.addLayer(myPrunceCluster.displayedMarkers);
        update_markers();
    });

}

function update_markers(){}


function update_markers(){

    // remove all markers of displayerd Markers for refreshing
    myPrunceCluster.displayedMarkers.RemoveMarkers(
        myPrunceCluster.displayedMarkers.GetMarkers());
    // Filter marker by ROI 
    // Display all marker if there are no ROIs
    for(var i = 0; i < myPrunceCluster.pruneCluster.GetMarkers().length; i++){
        marker = myPrunceCluster.pruneCluster.GetMarkers()[i];
        // Check if there are no selected ROIs or if marker is inside the selected ROIs
        if(myEditable.polygons.length == 0 || myEditable.inside(marker)){
            myPrunceCluster.displayedMarkers.RegisterMarker(marker);
        }
    }
    // Update displayed markers
    map.removeLayer(myPrunceCluster.displayedMarkers);
    map.addLayer(myPrunceCluster.displayedMarkers);


}

function overlay_control(){
    this.name = 0;
    this.dict = {};

    var tmpMarkers = new PruneClusterForLeaflet(160);

    this.getMarkers = function(index) {
        for(var i = 0; i < myPrunceCluster.pruneCluster.GetMarkers().length; i++){
        marker = myPrunceCluster.pruneCluster.GetMarkers()[i];
        // Check if there are no selected ROIs or if marker is inside the selected ROIs
        if(index == 0 || myEditable.polygons.length == 0 || myEditable.insideOfAPoly(marker, myEditable.polygons[index-1])){
            tmpMarkers.RegisterMarker(marker);
        }
    }

    return tmpMarkers;

    }


    this.getName = function() {
        this.name ++;
        return JSON.stringify("Overlay "+this.name);
    }
}


// Manipulate Markers by pruneCluster 
// PruneCluster used to display a huge amount of markers in real time
// -- see more google/search/pruneCLuster --
function pruneCluster_control(){

    // all markers of local database
    this.pruneCluster = new PruneClusterForLeaflet(160);
    // markers filtered by selected ROI
    this.displayedMarkers = new PruneClusterForLeaflet(160);

    var thisCC = this;
    // get Element that is used to adjust 
    var currentSizeSpan = document.getElementById('currentSize');

    var updateSize = function () {
        thisCC.displayedMarkers.Cluster.Size = parseInt(this.value);
        currentSizeSpan.firstChild.data = this.value;
        thisCC.displayedMarkers.ProcessView();
    }

    document.getElementById('sizeInput').onchange = updateSize;
    document.getElementById('sizeInput').oninput  = updateSize;
    
}

// Manipulate list of layers
function map_layers(){

    this.dict = {};
    var layer;

    // Add new map layer here
    // -- Plan baseMap --
    layer = L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
        detectRetina: true, 
        maxNativeZoom: 13
    });
    this.dict["Plan"] = layer;

    // -- Satellite baseMap --
    layer = L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
        maxZoom: 13,
        id: 'mapbox.satellite',
        accessToken: 'pk.eyJ1IjoibGUxIiwiYSI6ImNqM3U4YXB1ajAwMmU0bHJ0MnZ0dGhkcTQifQ.c0N7gp3wOjcAY9sAGCEMQA'
    });
    this.dict["Satellite"] = layer;

    // -- Rivers baseMap --
    layer = L.tileLayer('http://server.arcgisonline.com/ArcGIS/rest/services/World_Shaded_Relief/MapServer/tile/{z}/{y}/{x}',{
        attribution: '<a href="http://www.arcgis.com/home/item.html?id=9c5370d0b54f4de1b48a3792d7377ff2">ESRI shaded relief</a>, <a href="http://www.horizon-systems.com/NHDPlus/NHDPlusV2_home.php">NHDPlus v2</a>',
        maxZoom: 13
    });
    this.dict["Rivers"] = layer;

    this.getDefault = function() {
        return this.dict["Plan"];
    };

}

function editable_control(){

    this.polygons = [];
    // thisEC used in the event handler 
    var thisEC = this;

    // New Polygon configure
    L.NewPolygonControl = L.Control.extend({

        options: {
            position: 'topleft',
        },

        onAdd: function (map) {
            // container div in HTML
            var container = L.DomUtil.create('div','leaflet-control leaflet-bar'),
                link = L.DomUtil.create('a', '', container);
            // div attributs
            link.href = '#';
            link.title = 'Create a new polygon';
            link.innerHTML =  '▱';
            // set up event for ROI creation
            L.DomEvent.on(link, 'click', L.DomEvent.stop)
                        .on(link, 'click', function () {
                           map.editTools.startPolygon(); 
                        });
            
            return container;
        }
    });

    map.addControl(new L.NewPolygonControl());

    map.on('editable:drawing:end', function (e) {
        // add a new polygon
        thisEC.RegistrerPoly(e.layer);
        update_markers();
    });

    this.RegistrerPoly = function (layer) {
        thisEC.polygons.push(layer);
        var s = myOverlay.getName();
        myOverlay.dict[s] = layer;
    };

    this.insideOfAPoly = function(marker, poly) {
        var x = marker.position.lat, y = marker.position.lng;
        var latlngPoly = poly.getLatLngs();
        var res = false;
        for (var ii = 0; ii < latlngPoly.length; ii++ ){
            var polyPoint = latlngPoly[ii];
            
            for (var i = 0, j = polyPoint.length -1; i< polyPoint.length;j = i++) {
                var xi = polyPoint[i].lat, yi = polyPoint[i].lng;
                var xj = polyPoint[j].lat, yj = polyPoint[j].lng;

                var intersect = ((yi > y) != (yj > y))
                    && (x < (xj - xi)*(y - yi)/(yj-yi) + xi);
                if (intersect) res = !res; 
            }
        }

        return res;
    };

    this.inside = function(marker) {
        for(var i = 0; i < this.polygons.length; i++)
            if(this.insideOfAPoly(marker, this.polygons[i]))
                return true;
        
        return false;
    };

}

function init_tweetmap(){
    
    layers = null, myPrunceCluster = null, myEditable = null, myOverlay = null;

    // Layers of map
    layers = new map_layers();
    // Map Init
    map = L.map("map", {
        editable: true,
        attributionControl: false,
        zoomControl: true,
        layers: [layers.getDefault()]
    }).setView(new L.LatLng(48.8, 2.5), 12);
    // Add layers to map
    L.control.layers(layers.dict).addTo(map);
    // Manipulation of markers
    myPrunceCluster = new pruneCluster_control();
    // Manipulation of ROI 
    myEditable = new editable_control();
    // Manipulation of Overlay
    myOverlay = new overlay_control();

    map.setView(new L.LatLng(48.51, 2.20));

}

tweetsmap.operator.onready(init_tweetmap);
update_tweetsmap();