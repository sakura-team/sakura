/**
 * The classes is intended to keep the data from GUI.
 */

function Model(){
    this.researches = [];
    this.currentResearch = null;
    this.rid = 0;
    this.mapLayers = new MapLayers;
    this.allMarkers = new PruneClusterForLeaflet(160);
}

// Research class that contains:
// - A zone of interst 
// - Time range 
// - Color
// Attention: please use GUI.addResearch to create new research
function Research() {

    var thisResearch = this;

    this.rid = null;
    this.nameResearch = '';
    this.colorBorder = 'rgba(107, 142, 35, 1.0)';
    this.colorPoint = 'rgba(107, 142, 35, 1.0)';
    this.colorBackground = 'rgba(107, 142, 35, 1.0)';
    this.roi = new L.LayerGroup;
    this.expandRoi = new L.LayerGroup;
    this.expandRoi.addLayer(this.roi);
    this.timeRange = null;  
    this.loacationMarker = null;

    this.actualize = function() {
        
    };

    this.removeAllRoi = function() {
        thisResearch.roi.clearLayers();
    };
}

// Override toString() for degging
Research.prototype.toString = function() {
    return "    [Research Infor]rid = " + this.rid + " | name = " + this.nameResearch + " | Border color = " + this.colorBorder
            + " | Point color " + this.colorPoint + " | Background color " + this.colorBackground
            + " | Time Range " + this.timeRange ;
};

// Manipulate layers
function MapLayers(){

    this.dict = {};
    var layer;

    // Add new map layer here
    // // -- Simple baseMap --
    layer = L.tileLayer('https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; <a href="https://carto.com/attribution">CARTO</a>'
      });
    this.dict["Simple"] = layer;

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

    // // -- Rivers baseMap --
    layer = L.tileLayer('http://server.arcgisonline.com/ArcGIS/rest/services/World_Shaded_Relief/MapServer/tile/{z}/{y}/{x}',{
        attribution: '<a href="http://www.arcgis.com/home/item.html?id=9c5370d0b54f4de1b48a3792d7377ff2">ESRI shaded relief</a>, <a href="http://www.horizon-systems.com/NHDPlus/NHDPlusV2_home.php">NHDPlus v2</a>',
        maxZoom: 13
    });
    this.dict["Rivers"] = layer;

    this.getDefault = function() {
        return 0;
    };

}

var WEIGHT_ROI = 2; 
var FILLOPACITY_DISABLED = 0;
var FILLOPACITY_ENABLED = 0;

//---------------------------------------------Model Singleton------------------------------------//
var myModel = new Model;

