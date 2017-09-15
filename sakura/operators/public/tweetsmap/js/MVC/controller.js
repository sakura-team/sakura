/**
 * Author: LE Van Tuan
 * Date: June 29 2017
 * Classes
 */


// Controller
'use strict';
// var HEATMAP_REFRESH_DELAY = 0.0002;

function Controller() {

    var thisControl = this;

    // Created first Research
    this.initModel = function () {
        // L.LayerGroup contains all polygons displayed actually
        this.rois = new L.LayerGroup();
        myView.mapLayersSelector.check(myModel.mapLayers.getDefault());
        this.setBasemap('Simple');
        myView.dataDisplaySelector.check(0);
        this.displayType = 'Heatmap';
        this.setDisplayType = function (name) {
            this.displayType = name;
            this.actualize();
        };
        this.changeEditableResearch(-1);
        this.actualize();
    };

    //-----------------------------Controller<->BD----------------------------

    
    /* In order to lower network usage, heatmap data is transfered in
    * a compressed form. lat / lng values are transmitted as integers
    * and we must now recompute the actual values by applying a given
    * scale and offset.
    */
    function expand_heatmap_values(info) {
        var data = info.data, scales = info.scales, offsets = info.offsets,
            heatmap_values = [];
        for (var i = 0; i < data.lat.length; i++) {
            heatmap_values[i] = [
                data.lat[i] * scales.lat + offsets.lat,
                data.lng[i] * scales.lng + offsets.lng,
                data.val[i]
            ];
        }
        return heatmap_values;
    }

    function createMarkersLayer(info, maxPopulation) {
        var data = info.data, scales = info.scales, offsets = info.offsets;
        var layer = new PruneClusterForLeaflet();
        if(!maxPopulation)
            return layer;
        for (var i = 0; i < data.lat.length; i++) {
            var marker = new PruneCluster.Marker(data.lat[i] * scales.lat + offsets.lat,
                data.lng[i] * scales.lng + offsets.lng);
            for (var j = 0; j < data.val[i]; j++) {
                layer.RegisterMarker(marker);
            }
        }
        return layer;
    }

    function update_heatmap_callback(result) {
        if(thisControl.stopTransferting) {
            thisControl.stopTransferting = false;
            thisControl.actualize();
            return;
        }
        var icon;
        if ('issue' in result) {
            myView.infobox.update({ 'icon': 'alert', 'text': result.issue });
            return;
        }
        if (result.heatmap.done) {   // input data is complete for this map
            icon = 'check';
            thisControl.loadedPoint = result.heatmap.count;
        }
        else {
            icon = 'hourglass-half';
            // request server for more complete data,
            // while we refresh the screen
            sakura.operator.fire_event(
                ["map_continue", HEATMAP_REFRESH_DELAY],
                update_heatmap_callback);
        }

        // refresh the heatmap layer
        if (heatmap_layer != null) {
            map.removeLayer(heatmap_layer)
        }
        if (thisControl.displayType == 'Heatmap') {
            heatmap_layer = L.heatLayer(expand_heatmap_values(result.heatmap), {
                radius: HEATMAP_RADIUS
            });
            heatmap_layer.addTo(map);
        }
        else if (thisControl.displayType == 'Cluster' && result.heatmap.done) {
            heatmap_layer = createMarkersLayer(result.heatmap, result.heatmap.count);
            heatmap_layer.addTo(map);
        }
        // update infobox
        myView.infobox.update({ "icon": icon, 'text': result.heatmap.count + ' points' });
    }

    this.request_data = function () {
        
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

        var info = {
            'width': width,
            'height': height,
            'westlng': geo_sw.lng,
            'eastlng': geo_ne.lng,
            'southlat': geo_sw.lat,
            'northlat': geo_ne.lat
        }
        var listPoly = [], listtimeStart = [], listtimeEnd = [], listWords = [];

        var westlng_poly = 180.0;
        var eastlng_poly = -180.0;
        var southlat_poly = 85.0;
        var northlat_poly = -85.0;
        var timeStart_poly = Date.now();
        var timeEnd_poly = 0;

        thisControl.rois.eachLayer(function (layer) {
            // check if polygon is currently in geo_bounds
            var bound_poly = layer.getBounds();
            var timeRange = layer.research.timeRange;
            var words = layer.research.words;
            if (bound_poly.intersects(geo_bounds)) {
                listPoly.push(thisControl.convertPolygonToArray(layer));
                listtimeStart.push(timeRange.timeStart/1000.0);
                listtimeEnd.push(timeRange.timeEnd/1000.0);
                listWords.push(words);
                

                if (bound_poly.getWest() < westlng_poly) westlng_poly = bound_poly.getWest();
                if (bound_poly.getSouth() < southlat_poly) southlat_poly = bound_poly.getSouth();
                if (bound_poly.getEast() > eastlng_poly) eastlng_poly = bound_poly.getEast();
                if (bound_poly.getNorth() > northlat_poly) northlat_poly = bound_poly.getNorth();
                if (timeRange.timeStart < timeStart_poly) timeStart_poly = timeRange.timeStart;
                if (timeRange.timeEnd > timeEnd_poly) timeEnd_poly = timeRange.timeEnd;
            }

        });

        var len = listPoly.length;
        if (len == 0 || westlng_poly < geo_sw.lng) westlng_poly = geo_sw.lng;
        if (len == 0 || eastlng_poly > geo_ne.lng) eastlng_poly = geo_ne.lng;
        if (len == 0 || southlat_poly < geo_sw.lat) southlat_poly = geo_sw.lat;
        if (len == 0 || northlat_poly < geo_ne.lat) northlat_poly = geo_ne.lat;

        var info_poly = {
            'westlng': westlng_poly,
            'eastlng': eastlng_poly,
            'southlat': southlat_poly,
            'northlat': northlat_poly,
            'disable': thisControl.rois.getLayers().length != 0 && listPoly.length == 0
        }

        this.stopTransferting = false;
        // send event, then update map
        sakura.operator.fire_event(
            ["map_move", HEATMAP_REFRESH_DELAY, info, listPoly, info_poly, listtimeStart, listtimeEnd, listWords],
            update_heatmap_callback);
    }

    function exportation_callback(result) {
        if(thisControl.stopTransferting){
            thisControl.stopTransferting = false;
            // thisControl.actualize();                        
            return;
        }
        var icon;
        // if(result.exportation.data.list)
        if ('issue' in result) {
            myView.infoboxExportation.update({ 'icon': 'alert', 'text': result.issue });
            $('#layout').hide();  
            return;
        }
        if (result.exportation.done) {   // input data is complete for this map
            icon = 'check';
        }
        else {
            icon = 'hourglass-half';
            // request server for more complete data,
            // while we refresh the screen
            sakura.operator.fire_event(
                ["exportation_continue", EXPORTATION_REFRESH_DELAY],
                exportation_callback);
        }
        thisControl.exportationUtil.convertArrayOfObjectsToCSV({
            data: result.exportation.data
        });
        // update infobox
        if(thisControl.exportationUtil.forAResearch)
            myView.infoboxExportation.update({ "icon": icon, 'text': thisControl.exportationUtil.count + " points"});
        else
            myView.infoboxExportation.update({ "icon": icon, 'text': thisControl.exportationUtil.count +'/' +myController.loadedPoint });
        // myView.loader.update();
        myView.dataLoadingBar.update();
        // display download window
        if(result.exportation.done){
            thisControl.exportationUtil.downloadCSV();
            $('#layout').hide();
            thisControl.request_data();
        }
    }

    function wordcloud_callback(result) {
        if(thisControl.stopTransferting){
            thisControl.stopTransferting = false;
            // thisControl.actualize();            
            return;
        }
        var data = result.wordcloud.data;
        var keywords = $('#list_keywords');
        var icon;
        if ('issue' in result) {
            myView.infoboxInfoPoly.update({ 'icon': 'alert', 'text': result.issue });
            $('#info').hide();  
            return;
        }
        if (result.wordcloud.done) {   // input data is complete for this map
            icon = 'check';
            myView.downloadWordCloud.enable();
            data.sort(function(a, b){
                return b[1] - a[1];
            });
            // myView.infoPolygonDiv.img.src = 'data:image/png;base64,'+result.wordcloud.data;
        }
        else {
            icon = 'hourglass-half';
            // request server for more complete data,
            // while we refresh the screen
            sakura.operator.fire_event(
                ["wordcloud_continue", HEATMAP_REFRESH_DELAY],
                wordcloud_callback);
        }
        // update infobox
        myView.infoboxInfoPoly.update({ "icon": icon, 'text': result.wordcloud.count + ' points' });
        for(var item in data){
            if(result.wordcloud.done)
                keywords.append('<tr><th>'+data[item][0]+'</th><th>'+data[item][1]+'</th></tr>');
            data[item][1] *= 100;
            data[item][1] += 4;
        }
        if(data){
            var options = {
                list: data,
                gridSize: 40,
                weightFactor: 4,
                fontFamily: 'Average, Times, serif',
                color: function() {
                  return (['#d0d0d0', '#e11', '#44f'])[Math.floor(Math.random() * 3)]
                },
                backgroundColor: '#333'
            };
            WordCloud(document.getElementById('my_canvas'), options );
        }
        if(result.wordcloud.done)
            thisControl.request_data();
    }

    this.exportationUtil = new Object;
    this.exportationUtil.result = '';
    this.exportationUtil.count = 0;

    this.exportationUtil.convertArrayOfObjectsToCSV = function(args){
        var result, ctr, keys, columnDelimiter, lineDelimiter, data;
        
            data = args.data || null;
            if (data == null || data.list == null ) {
                return null;
            }
            columnDelimiter = args.columnDelimiter || ',';
            lineDelimiter = args.lineDelimiter || '\n';
        
            keys = data.key;
        
            if(thisControl.exportationUtil.result == ''){
                thisControl.exportationUtil.result += keys.join(columnDelimiter);
                thisControl.exportationUtil.result += lineDelimiter;
            }
            
            var nbCol = keys.length;

            result = '';
            data.list.forEach(function(item) {
                ctr = 0;
                thisControl.exportationUtil.count ++;
                for(var i=0; i < nbCol; i++){
                    if (ctr > 0) result += columnDelimiter;
                    result += item[i];
                    ctr++;
                };
                result += lineDelimiter;
            });
            thisControl.exportationUtil.result+=result;
    }

    this.exportationUtil.downloadCSV = function() {
        // var stockData = dataExportation || {key: ['Symbol', 'Company', 'Price'],
        // list: [
        //     [ "AAPL","Apple Inc.",132.54],
        //     [ "INTC","Intel Corporation",33.45],
        //     [ "AAPL","Apple Inc.",132.54]]
        // };
        var filename, link;
        var csv = thisControl.exportationUtil.result;
        if (csv == null)
            return;
        
        filename = thisControl.exportationUtil.researchName + '.csv';
        
        var blob = new Blob([csv], {type: "text/csv;charset=utf-8;"});
        
        if (navigator.msSaveBlob){ // IE 10+
            navigator.msSaveBlob(blob, filename)
        }
        else{
            var link = document.createElement("a");
            if (link.download !== undefined){
            // feature detection, Browsers that support HTML5 download attribute
            var url = URL.createObjectURL(blob);
            link.setAttribute("href", url);
            link.setAttribute("download", filename);
            link.style = "visibility:hidden";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            }
        }
    }

    this.getInfoPolygon = function(layer){
        var westlng_poly, eastlng_poly, southlat_poly, northlat_poly;
        var bound_poly = layer.getBounds();
        var polygon = thisControl.convertPolygonToArray(layer);
        westlng_poly = bound_poly.getWest();
        southlat_poly = bound_poly.getSouth();
        eastlng_poly = bound_poly.getEast();
        northlat_poly = bound_poly.getNorth();
        var info = {
            'westlng': westlng_poly,
            'eastlng': eastlng_poly,
            'southlat': southlat_poly,
            'northlat': northlat_poly,
            'disable': false
        };
        var timeRange = layer.research.timeRange;
        myView.infoboxInfoPoly.update({ "icon": 'hourglass-half', 'text': 0 + ' points' });
        myView.downloadWordCloud.disable();
        var keywords = $('#list_keywords');
        keywords.empty();
        keywords.append('<tr><th>KeyWords</th><th>Frequency</th></tr>');
            // send event, then update map
        this.stopTransferting = false;
        sakura.operator.fire_event(
            ["wordcloud", HEATMAP_REFRESH_DELAY, info, polygon, timeRange.timeStart/1000.0, timeRange.timeEnd/1000.0, layer.research.words],
            wordcloud_callback);
        $('#info').show();
    };

    this.stopTransferting = false;
    this.exportation = function (roi, name, forAResearch) {
        this.exportationUtil.result = '';
        this.exportationUtil.count = 0;
        this.exportationUtil.researchName = name; 
        this.exportationUtil.forAResearch = forAResearch;
        var listPoly = [], listtimeStart = [], listtimeEnd = [], listWords = [];

        var westlng_poly = 180.0;
        var eastlng_poly = -180.0;
        var southlat_poly = 85.0;
        var northlat_poly = -85.0;

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
        roi.eachLayer(function (layer) {
            var bound_poly = layer.getBounds();
            var timeRange = layer.research.timeRange;
            var words = layer.research.words;
            // check if polygon is currently in geo_bounds
            var bound_poly = layer.getBounds();
            listPoly.push(thisControl.convertPolygonToArray(layer));
            listtimeStart.push(timeRange.timeStart/1000.0);
            listtimeEnd.push(timeRange.timeEnd/1000.0);
            listWords.push(words);
            if (bound_poly.getWest() < westlng_poly) westlng_poly = bound_poly.getWest();
            if (bound_poly.getSouth() < southlat_poly) southlat_poly = bound_poly.getSouth();
            if (bound_poly.getEast() > eastlng_poly) eastlng_poly = bound_poly.getEast();
            if (bound_poly.getNorth() > northlat_poly) northlat_poly = bound_poly.getNorth();
        });

        var forAResearch = myController.exportationUtil.forAResearch;
        var info_poly = {
            'westlng': forAResearch?westlng_poly:geo_sw.lng,
            'eastlng': forAResearch?eastlng_poly:geo_ne.lng,
            'southlat': forAResearch?southlat_poly:geo_sw.lat,
            'northlat': forAResearch?northlat_poly:geo_ne.lat,
            'disable':  forAResearch && listPoly.length == 0
        }
        // update infobox
        myView.infoboxExportation.update({ "icon": 'hourglass-half', 'text': 0 + ' points' });
        
        $('#layout').show();
        if(forAResearch){
            myView.dataLoadingBar.noneDisplay();
            myView.loader.display()
        } else {
            myView.loader.noneDisplay();
            myView.dataLoadingBar.update();            
            myView.dataLoadingBar.display();
        }
        this.stopTransferting = false;
        // send event, then update map
        sakura.operator.fire_event(
            ["exportation", EXPORTATION_REFRESH_DELAY, info_poly, listPoly, listtimeStart, listtimeEnd, listWords],
            exportation_callback);
        
    }

    
    map.setView([48.86, 2.34], 9);
    map.on('moveend', this.request_data);
    //---------------------------------- Data Filtering --------------------------------

    /** @function insideOfAPoly void
    * @param marker L.Marker representing the point
    * @param poly L.Poly representing the zone of intesrest
    * checking a point if it is located inside zone using the Ray Casting Method
    */
    this.insideOfAPoly = function (marker, poly) {
        var x = marker.position.lat, y = marker.position.lng;
        var latlngPoly = poly.getLatLngs();
        var res = false;
        for (var ii = 0; ii < latlngPoly.length; ii++) {
            var polyPoint = latlngPoly[ii];

            for (var i = 0, j = polyPoint.length - 1; i < polyPoint.length; j = i++) {
                var xi = polyPoint[i].lat, yi = polyPoint[i].lng;
                var xj = polyPoint[j].lat, yj = polyPoint[j].lng;

                var intersect = ((yi > y) != (yj > y))
                    && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
                if (intersect) res = !res;
            }
        }

        return res;
    };
    /**
     *  @function convertPolygonToArray void
     *  @param poly L.polygon polygon to be converted
     *  
     */
    this.convertPolygonToArray = function (poly) {
        var res = [];
        var data;
        var type;
        if (poly instanceof L.Rectangle || poly instanceof L.Polygon) {
            type = "polygon";

            //res.push("polygon");
            var latlngPoly = poly.getLatLngs();
            // exemple a triangle:  [[1, 2], [3, 4], [5, 6]]  
            // latlngPoly.length = 1, polyPoints.length =3
            for (var i = 0; i < latlngPoly.length; i++) {
                var polyPoints = latlngPoly[i];
                for (var j = 0; j < polyPoints.length; j++) {
                    res.push([polyPoints[j].lat, polyPoints[j].lng]);
                }
            }
            data = [res];
        }
        else if (poly instanceof L.Circle) {
            type = 'circle';
            data = {
                'center': {
                    'lat': poly.getLatLng().lat,
                    'lng': poly.getLatLng().lng
                },
                'radius': poly.getRadius()
            };
        }

        return { 'type': type, 'data': data };
    }

    this.getMarkers = function (layer) {
        var res = new PruneClusterForLeaflet(160);
        var marker;
        for (var i = 0; i < myModel.allMarkers.GetMarkers().length; i++) {
            marker = myModel.allMarkers.GetMarkers()[i];
            // Check if there are no selected ROIs or if marker is inside the selected ROIs
            if (this.insideOfAPoly(marker, layer)) {
                res.RegisterMarker(marker);
            }
        }
        layer.markers.addTo(map);

    };


    //----------------------------------Event Handling-------------------------------------

    // @function setBasemap(layerName string)
    // change the basemap which is determined by layerName as its key in mapLayers
    this.setBasemap = function (layerName) {
        if (this.baseMap)
            map.removeLayer(this.baseMap);
        this.baseMap = myModel.mapLayers.dict[layerName].addTo(map);
    };

    this.addResearch = function () {
        // create new Research
        var research = new Research;
        research.nameResearch = myView.nameBox.getValue();
        // update id in new Research
        ////research.rid = myModel.rid;
        var currentLength = myModel.researches.length;
        // add new Research in list research of thisControl
        myModel.researches[currentLength] = research;
        // update research select box
        //// myView.researchSelector.addOption(research.nameResearch);
        // update research checkbox list
        //// myView.researchCheckBoxList.addCheckBox(research.nameResearch);
        // change current research to research
        ////this.displayResearch(currentLength);
        myView.researchesPanel.addRow(research);
        this.changeEditableResearch(this.getIndexByResearch(research));
        ////this.updateMarkers();
        myView.nameBox.setValue('');
        this.actualize();
    };

    /**
     *  Event Handling function
     */

    // Event when click in checkbox of research checkbox
    // @function displayReseach(int)
    // index = index of to-display Research in the research list
    this.displayResearch = function (index) {
        this.addPolygonsToGUI(myModel.researches[index].roi);

    }

    // Event when finish drawing a poly
    this.registerPoly = function (layer) {

        this.editableResearch.roi.addLayer(layer);
        layer.research = this.editableResearch;
        layer.research = this.editableResearch;
        if (!this.editableResearch.roi.currentIndex)
            this.editableResearch.roi.currentIndex = 0;
        var index = ++this.editableResearch.roi.currentIndex;
        var namePoly = this.editableResearch.nameResearch + " " + index;
        layer.namePoly = namePoly;
        this.rois.addLayer(layer);
        // add to researched panel
        myView.researchesPanel.addUnderRow(this.editableResearch, layer);
    };

    // remove current research
    this.removeResearch = function (index) {
        var research = myModel.researches[index];
        if (this.editableResearch == research)
            this.changeEditableResearch(-1);
        if (research.locationMarker)
            research.locationMarker.removeFrom(map);
        this.removePolygonsFGUI(research.roi);

        myModel.researches.splice(index, 1);
    };

    // remove current research
    this.removeAllResearch = function () {
        // remove all from research checkboxes
        myView.researchCheckBoxList.removeAllCheckboxes();
        // remove all from research selector
        myView.researchSelector.removeAllOptions();
        // remove all Rois
        this.removeAllPolygonsFGUI(this.editableResearch.roi);

        myModel.researches.splice(0, myModel.researches.length);
        this.addResearch();
    };

    //  @function updateColor() called by event 'change' of tweetColorSelector 
    //  Change the roi color, researches panel color
    //  @see view.js
    this.updateColor = function () {
        this.editableResearch.roi.eachLayer(function (layer) {
            layer.setStyle({
                color: thisControl.editableResearch.colorBorder
                , fillColor: thisControl.editableResearch.colorBackground,
                fillOpacity: FILLOPACITY_ENABLED, weight: WEIGHT_ROI
            });
        });

        myView.researchesPanel.changeBackground(this.editableResearch,
            this.editableResearch.colorBackground);
        myView.editionTitle.getContainer().style.color =
            this.editableResearch.colorBackground;
    };

    this.setTimeGUI = function(){
        myView.timeStartDiv.setTime(this.editableResearch.timeRange.timeStart);
        myView.timeEndDiv.setTime(this.editableResearch.timeRange.timeEnd);
    };

    this.setKeyWordsToGUI = function(){
        myView.wordsTextBox.removeAllWords();
        for(var i = 0; i < this.editableResearch.words.length; i++){
            myView.wordsTextBox.addWord(this.editableResearch.words[i]);
        }
    };

    /**
     * @function addOverlays() called by event 'finished drawing' of newPolygonButton
     * layer: ROI 
     * add new overlay with the layer as the inside point of layer
     * @see view.js
     */
    this.addOverlays = function (layer, name) {
        //myView.layersPanel.addOverlay(layer, name);
    };

    // @function removeAllOverlays()
    this.removeAllOverlays = function () {
        this.editableResearch.roi.eachLayer(function (layer) {
            myView.layersPanel.removeLayer(layer);
        });
    };

    this.deletePolygon = function (poly) {
        this.editableResearch.roi.eachLayer(function (layer) {
            if (((layer instanceof L.Polygon || layer instanceof L.Rectangle)
                && layer.getLatLngs()[0].length == 0) || layer == poly) {
                layer.removeFrom(map);
                layer.closeTooltip();
                thisControl.editableResearch.roi.removeLayer(layer);
                myView.researchesPanel.removeUnderRow(thisControl.editableResearch, layer);
                thisControl.rois.removeLayer(layer);
            }
        });
        // this.updateMarkers();
    }

    //---------------------------------View->Controller-------------------------------------//
    /**
     *  View -> Model : These functions is intended for getting informations from GUI (FGUI)
     */
    // @function getNamFGUI(): String
    // Returns name of research filled in the the name-research text box
    this.getNameFGUI = function () {
        var res = myView.nameBox.getValue();
        return res;
    };

    // @function getColorBorderFGUI(): String
    // Returns color of ROI border selected in the color box
    this.getColorBorderFGUI = function () {
        var res = myView.borderColorSelector.getColor();
        return res || "red";
    };

    this.getKeyWords = function () {
        return myView.wordsTextBox.words;
    };

    // @function getColorPointFGUI(): String
    // Returns color of ROI Point selected in the color box
    this.getColorPointFGUI = function () {
        var res = myView.tweetsColorSelector.getColor();
        return res || "green";
    };

    // @function getColorBackgroundFGUI(): String
    // Returns color of ROI Background selected in the color box
    this.getColorBackgroundFGUI = function () {
        var res = myView.backgroundColorSelector.getColor();
        return res || "red";
    };

    // @function getRoiFGUI(): String
    // Returns polygon of ROI selected on the map
    this.getRoiFGUI = function () {
        var res = null;

        return res || null;
    };

    this.getTimeRange = function () {
        var res = new Object;
        res.timeStart = (new Date(myView.timeStartDiv.getTime())).getTime();
        res.timeEnd = (new Date(myView.timeEndDiv.getTime())).getTime();
        // myView.timeStartDiv.setTime(res.timeStart);
        if(res.timeStart > res.timeEnd){
             myView.timeEndDiv.setTime(res.timeStart);
            res.timeEnd = (new Date(myView.timeEndDiv.getTime())).getTime();
        }
        // myView.timeEndDiv.setTime(res.timeEnd);
        myView.timeStartDiv.setMessage(res.timeStart/1000);
        myView.timeEndDiv.setMessage(res.timeEnd/1000);
        
        return res;
    };

    //------------------------------Controller -> View ------------------------------------
    //// It's intended to update data in GUI for example when we change the research

    this.setNameToGUI = function (name) {
        myView.nameBox.setValue(name);
    };

    this.setColorBackgroundToGUI = function (color) {
        myView.backgroundColorSelector.setColor(color);
    };

    this.setColorBorderToGUI = function (color) {
        myView.borderColorSelector.setColor(color);
    };

    this.setColorPointToGUI = function (color) {
        myView.tweetsColorSelector.setColor(color);
    };

    this.showPolygonsToGUI = function (group) {
        group.eachLayer(function (layer) {
            thisControl.showPolygonToGUI(layer);
        });
    };

    this.showPolygonToGUI = function (layer) {
        thisControl.rois.addLayer(layer);
        layer.setStyle({ stroke: true, fill: true });
        layer.openTooltip();
        if (layer.research == this.editableResearch)
            this.enablePolygon(layer);
    };

    // @function removePolygonsFGUI(LayerGroup): void
    // Remove Layer group passed in param from myView.rois 
    // update the overlay panel
    // used when change current research
    this.removePolygonsFGUI = function (group) {
        group.eachLayer(function (layer) {
            thisControl.rois.removeLayer(layer);
            layer.removeFrom(map);
        });
    };

    this.hidePolygonsFGUI = function (group) {
        group.eachLayer(function (layer) {
            thisControl.hidePolygonFGUI(layer);
        });
    };

    this.hidePolygonFGUI = function (layer) {
        thisControl.rois.removeLayer(layer);
        layer.setStyle({ stroke: false, fill: false });
        layer.closeTooltip();
        this.disablePolygon(layer);
    };

    this.disablePolygons = function (group) {
        group.eachLayer(function (layer) {
            if (layer.editor)
                layer.editor.disable();
            layer.setStyle({ fillOpacity: FILLOPACITY_DISABLED, opacity: 0.8, weight: WEIGHT_ROI });
        });
    };

    this.disablePolygon = function (layer) {
        if (layer.editor)
            layer.editor.disable();
        layer.setStyle({ fillOpacity: FILLOPACITY_DISABLED, opacity: 0.8, weight: WEIGHT_ROI });
    };

    this.enablePolygons = function (group) {
        group.eachLayer(function (layer) {
            if (layer.editor)
                layer.editor.enable();
            layer.bringToFront();
            layer.setStyle({ fillOpacity: FILLOPACITY_ENABLED, opacity: 1.0, weight: WEIGHT_ROI });
        });
    };

    this.enablePolygon = function (layer) {
        if (layer.editor)
            layer.editor.enable();
        layer.bringToFront();
        layer.setStyle({ fillOpacity: FILLOPACITY_ENABLED, opacity: 1.0, weight: WEIGHT_ROI });
    };

    this.removeAllPolygonsFGUI = function () {
        myView.rois.eachLayer(function (layer) {
            layer.eachLayer(function (souslayer) {
                myView.layersPanel.removeLayer(souslayer);
            });
        });
        myView.rois.clearLayers();
    }


    //--------------------------------- Research Controller ---------------------------------- 

    this.getResearchByName = function (name) {
        var res = myModel.researches.find(function (item) {
            return item.nameResearch === name;
        })
        return (res) ? res.research : null;
    };

    this.getIndexByResearch = function (research) {
        for (var i = 0; i < myModel.researches.length; i++) {
            if (myModel.researches[i] === research) {
                return i;
            }
        }
    }

    // change current research to researches[index]
    this.changeEditableResearch = function (index) {
        // Say good bye to previous research
        var researchObsolete = this.editableResearch;
        // disable Editing its polygons
        if (researchObsolete)
            //this.removePolygonsFGUI(researchObsolete.roi);
            this.disablePolygons(researchObsolete.roi);

        // there are no editable research
        if (index == -1) {
            myView.editionDiv.hide();
            myView.editionTitle.hide();
            myView.editionHide.hide();
            this.editableResearch = null;
            return;
        }
        else {
            myView.editionDiv.show();
            myView.editionHide.show();
            myView.editionTitle.show();
            if (myView.searchBar.currentMarker)
                myView.locationResearchButton.display();
            else 
                myView.locationResearchButton.noneDisplay();
            
            if (!myView.searchBar.currentPoly.isEmpty())
                myView.newPolyAdminButton.display();
            else
                myView.newPolyAdminButton.noneDisplay();
            myView.editionHide.setSign("◄");
            myView.editionHide.getContainer().style.left = '25%';
            myView.editionDiv.hideState = true;
            if(this.editableResearch)
                $('#'+myView.hideManagementButton.getId()).trigger("click");  
        }

        // welcome new research
        this.editableResearch = myModel.researches[index];
        myView.editionTitle.getContainer().innerHTML = this.editableResearch.nameResearch;

        //enable its polygons
        this.enablePolygons(this.editableResearch.roi);

        // set value of name Box to current research name 
        ////this.setNameToGUI(this.editableResearch.nameResearch);
        this.setColorBackgroundToGUI(this.editableResearch.colorBackground);
        this.setColorPointToGUI(this.editableResearch.colorPoint);
        this.setColorBorderToGUI(this.editableResearch.colorBorder);
        this.setKeyWordsToGUI(this.editableResearch.words);
        myView.wordsTextBox.setValue("");
        this.showPolygonsToGUI(this.editableResearch.roi);
        this.setTimeGUI(); 
        
        // update interface
        this.actualize();
    };

    // remove researches[i]
    this.removeResearchByIndex = function (index) {
        if (this.editableResearch == myModel.researches[index])
            this.changeEditableResearch(-1);
        myModel.researches.splice(index, 1);
        thisControl.actualize();
    };

    //------------------------------------Actualize--------------------------------
    // @function actualize(): void 
    // often called after a mofification occurs in GUI 
    this.actualize = function () {
        // View -> Model
        // update currentResearch attribut from Interface
        // Check for first call
        ////
        if (this.editableResearch) {
            ////this.editableResearch.nameResearch = this.getNameFGUI();
            this.editableResearch.colorBorder = this.getColorBorderFGUI();
            this.editableResearch.colorPoint = this.getColorPointFGUI();
            this.editableResearch.colorBackground = this.getColorBackgroundFGUI();
            this.editableResearch.timeRange = this.getTimeRange();
            this.editableResearch.words = this.getKeyWords().clone()
            this.updateColor();
        }

        this.checkName();
        
        this.request_data();
  
        // console.log(this.toString());

    };

    Array.prototype.clone = function() {
        return this.slice(0);
    }

    this.checkName = function(){
        // check message box
        var message = "";
        var name = myView.nameBox.getValue();
        if (name == "") {
            message = "Enter a research name";
        }
        else {
            for (var i = 0; i < myModel.researches.length; i++) {
                if (name == myModel.researches[i].nameResearch)
                    ////&& this.editableResearch!= myModel.researches[i].research)
                    message = 'Name existed already';
            }
        }

        if (message) {
            myView.nameBox.disable();
        } else {
            myView.nameBox.enable();
        }
        if (name == "ton nom?")
            message = "Salut, Je suis Tweetsmap !"
        if (name == "ton pere?")
            message = "Sakura"
        if (name == "ta copine?")
            message = "Je suis une fille ..."
        myView.nameBox.setMessage(message);

        message = "";
        var name = myView.wordsTextBox.getValue();
        if (name != "") {
            for (var i = 0; i < myView.wordsTextBox.words.length; i++) {
                if (name == myView.wordsTextBox.words[i])
                    message = 'KeyWord existed already';
            }
        }
        if (message) {
            myView.wordsTextBox.disable();
        } else {
            myView.wordsTextBox.enable();
        }

        myView.wordsTextBox.setMessage(message);

    };

    this.initModel();
    this.checkName();
}
// Override toString methode using for debugging
Controller.prototype.toString = function () {
    var string = "[GUI Infor] " + myModel.researches.length + " researches";
    for (var i = 0; i < myModel.researches.length; i++)
        string += "\n" + myModel.researches[i].toString();
    string += "\n <editable research> : " + this.editableResearch;
    string += "\n rois: "
    this.rois.eachLayer(function (layer) {
        string += layer.namePoly + " ,";
    })
    return string;
};

//-------------------------------------DataBase Connection------------------------//


//----------------------------------------Controller singleton---------------------------------------
var myController = new Controller();


