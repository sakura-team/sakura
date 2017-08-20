/**
 * Author: LE Van Tuan
 * Date: June 29 2017
 * Classes
 */


// Controller
'use strict';
// var HEATMAP_REFRESH_DELAY = 0.0002;

function Controller(){

    var thisControl = this;

    // Created first Research
    this.initModel = function(){
        // L.LayerGroup contains all polygons displayed actually
        this.rois = new L.LayerGroup(); 
       // increment id 
        /////myModel.rid ++;
        // create new Research
        ////this.editableResearch = new Research;
        // update id in new Research
        ////this.editableResearch.rid = myModel.rid;
        // add new Research in list research of thisControl
        ////myModel.researches[0] = 
            ////{rid: this.editableResearch.rid, research: this.editableResearch};
        // add roi of current research to myView.rois
        ////myView.rois.addLayer(this.editableResearch.roi);
        // update research list in research box
        //myView.researchSelector.addOption(this.editableResearch.nameResearch);        
        //myView.researchCheckBoxList.addCheckBox(this.editableResearch.nameResearch);
        //myView.rois.addTo(map);
        //this.updateTweetsmap();
		myView.maplayersSelector.check(myModel.mapLayers.getDefault());
		this.changeEditableResearch(-1);
        this.actualize();
    };

    //-----------------------------GUI->BD----------------------------
    
    var HEATMAP_RADIUS = 15;
    var HEATMAP_REFRESH_DELAY = 0.3;
    var heatmap_layer = null
    function update_heatmap_callback(result) {
        var infobox = thisControl.infobox
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
        // expand compressed data
        var heatmap_values = expand_heatmap_values(result.heatmap);
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
        console.log('map update: ' + ((t1 - thisControl.t0)/1000.0) + " seconds");
    }
    
    function request_heatmap() {
    
        var t0 = new Date().getTime();
        thisControl.t0 = t0;
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
        // console.log(info);
        var listPoly = [];
        
        var listMarkers = [];
        var westlng_poly = 180.0;
        var eastlng_poly = -180.0;
        var southlat_poly = 85.0;
        var northlat_poly = -85.0;

        thisControl.rois.eachLayer(function(layer){
            // check if polygon is currently in geo_bounds
            var bound_poly = layer.getBounds();
            console.log(info);
            console.log(bound_poly);

            if(bound_poly.intersects(geo_bounds)){
                listPoly.push(thisControl.convertPolygonToArray(layer));
                if(bound_poly.getWest() < westlng_poly) westlng_poly = bound_poly.getWest();
                if(bound_poly.getSouth() < southlat_poly) southlat_poly = bound_poly.getSouth();
                if(bound_poly.getEast() > eastlng_poly) eastlng_poly = bound_poly.getEast();
                if(bound_poly.getNorth() > northlat_poly) northlat_poly = bound_poly.getNorth();
            }
                
        });
        var len = listPoly.length;
        if(len == 0 || westlng_poly < geo_sw.lng) westlng_poly = geo_sw.lng;
        if(len == 0 || eastlng_poly > geo_ne.lng) eastlng_poly = geo_ne.lng;
        if(len == 0 || southlat_poly < geo_sw.lat) southlat_poly = geo_sw.lat;
        if(len == 0 || northlat_poly < geo_ne.lat) northlat_poly = geo_ne.lat;

        var info_poly = {
            'westlng': westlng_poly,
            'eastlng': eastlng_poly,
            'southlat': southlat_poly,
            'northlat': northlat_poly,
            'disable': thisControl.rois.getLayers().length !=0 && listPoly.length == 0
        }
        
        // send event, then update map
        sakura.operator.fire_event(
                ["map_move", HEATMAP_REFRESH_DELAY, info, listPoly, info_poly],
                update_heatmap_callback);
    }
    
    var infobox = L.control();
    this.infobox = infobox;
    
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

    map.on('moveend', request_heatmap);

    function updateTweetsmapCallback(result){
        if(result.done) {
            myView.pointNumber.hide();
        }
        else
        {
            sakura.operator.fire_event(["abc", HEATMAP_REFRESH_DELAY], updateTweetsmapCallback);
            myView.pointNumber.update(myModel.allMarkers.GetMarkers().length + " points loaded ..");
        } 

        // data = {lat: x, lng: y}
        var data = result.tweetsmap;
        // markers layer creation
        for (var i = 0; i < data.lat.length; i++) {
            // Corresponding marker
            var marker = new PruneCluster.Marker(data.lat[i], data.lng[i]);
            // filtre by ROIS
            myModel.allMarkers.RegisterMarker(marker);
        }
    };

    


    this.updateTweetsmap = function(){
    
        // get data by operators
        sakura.operator.fire_event(['new_zone', HEATMAP_REFRESH_DELAY], 
            updateTweetsmapCallback);
        
        myModel.allMarkers.addTo(map);
        myView.overlaysPanel.addOverlay(myModel.allMarkers, "All");


    };


    // @function updateMarkersUnit 
    //              send a polygon to server and receive the point inside of the poly
    // @param markers The markers container
    // @param poly The shape of polygon
    this.updateMarkersUnit = function(markers, poly){
        sakura.operator.fire_event(["polyons_update", poly.typeROI, poly] 
                , function(result){
                    // data = {lat: x, lng: y}
                    var data = result.tweetsmap;
                    // markers layer creation
                    for (var i = 0; i < data.lat.length; i++) {
                        // Corresponding marker
                        var marker = new PruneCluster.Marker(data.lat[i], data.lng[i]);
                        // filtre by ROIS
                        markers.RegisterMarker(marker);
                    }
                    myView.displayedMarkers.addLayer(markers);
                });
    }

    this.updateMarkers = function(){
        // remove all layers in displaed Markers for reupdating
        myView.displayedMarkers.clearLayers();
        var i = 0;
        var listPoly = [];
        // var listPoly = myView.rois;
        
        var listMarkers = [];
        thisControl.rois.eachLayer(function(layer){
            // layer.eachLayer(function(l){
                // if(map.hasLayer(l)){
                    //listPoly[i] = l;
                    listPoly.push(thisControl.convertPolygonToArray(layer));
                    // List markers corresponding to listPoly[i]
                    listMarkers[i] = new PruneClusterForLeaflet(160);
                    myView.displayedMarkers.addLayer(listMarkers[i]);
                    // i++;
                // }
            // });
        });
        var nbPoint = 0;

        function updateMarkersCallback(result){
            console.log(result);
            if(result.done) {
                // myView.pointNumber.hide();
                null
            }
            else
            {
                sakura.operator.fire_event(["abc", HEATMAP_REFRESH_DELAY, listPoly], updateMarkersCallback);
                // myView.pointNumber.update(nbPoint + " points loaded ..");
            } 

            for(var i = 0 ; i < result.tweetsmap.length;i++){
                var marker = null;
                for(var j = 0; j< result.tweetsmap[i].length;j++){
                    marker = new PruneCluster.Marker(
                    result.tweetsmap[i][j][0], result.tweetsmap[i][j][1]);
                    listMarkers[i].RegisterMarker(marker);
                    nbPoint++;
                }
                listMarkers[i].ProcessView();
            }
        }

        if(listPoly.length != 0) {
        console.log('ok');
        // sakura.operator.fire_event(["polygons_update", HEATMAP_REFRESH_DELAY, listPoly ]
        //         , updateMarkersCallback);
        }
    
    };

    //----------------------------------Data Filtering--------------------------------
    
    /** @function insideOfAPoly void
    * @param marker L.Marker representing the point
    * @param poly L.Poly representing the zone of intesrest
    * checking a point if it is located inside zone using the Ray Casting Method
    */   
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
    /**
     *  @function convertPolygonToArray void
     *  @param poly L.polygon polygon to be converted
     *  
     */
    this.convertPolygonToArray = function(poly){
        var res = [];
        var data;
        var type;
        if(poly instanceof L.Rectangle || poly instanceof L.Polygon) {
            type = "polygon";
        
            //res.push("polygon");
            var latlngPoly = poly.getLatLngs();
            // exemple a triangle:  [[1, 2], [3, 4], [5, 6]]  
            // latlngPoly.length = 1, polyPoints.length =3
            for(var i = 0; i < latlngPoly.length; i++){
                var polyPoints = latlngPoly[i];
                for(var j = 0; j < polyPoints.length; j++){
                    res.push([polyPoints[j].lat, polyPoints[j].lng]);
                }
            }
            data = [res];
        }
        else if (poly instanceof L.Circle){
            type = 'circle';
            data = {'center': { 'lat': poly.getLatLng().lat, 
                                'lng': poly.getLatLng().lng}, 
                'radius': poly.getRadius()};
        }
        
        return {'type' : type, 'data' : data};
    }

    this.getMarkers = function(layer) {
        var res = new PruneClusterForLeaflet(160);
        var marker;
        for(var i = 0; i < myModel.allMarkers.GetMarkers().length; i++){
            marker = myModel.allMarkers.GetMarkers()[i];
            // Check if there are no selected ROIs or if marker is inside the selected ROIs
            if(this.insideOfAPoly(marker, layer)){
                res.RegisterMarker(marker);
            }
        }
        layer.markers.addTo(map);

    };


    //----------------------------------Event Handling-------------------------------------
    
	// @function setBasemap(layerName string)
	// change the basemap which is determined by layerName as its key in mapLayers
	this.setBasemap = function(layerName){
		if(this.baseMap) 
			map.removeLayer(this.baseMap);
		this.baseMap = myModel.mapLayers.dict[layerName].addTo(map);
	};

    this.addResearch = function(){

        /*var check = this.getResearchByName("Current Research");
        if(check){
            this.changeCurrentResearch(this.getIndexByResearch(check));
            return;
        }*/
        // increment id 
        ////myModel.rid ++;
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

    // this.hideResearch = function (index) {
    //     this.removePolygonsFGUI(myModel.researches[index].roi);
    //     this.updateMarkers();
    // }
    // // Event when select an item on research selector
    // this.selectResearch = function(){
    //     this.changeEditableResearch(myView.researchSelector.getSelect().selectedIndex);
    //     this.updateMarkers();
    // };

    // Event when finish drawing a poly
    this.registerPoly = function(layer) {
        this.editableResearch.roi.addLayer(layer);
        layer.research = this.editableResearch;
        if(!this.editableResearch.roi.currentIndex)
            this.editableResearch.roi.currentIndex = 0;
        var index = ++this.editableResearch.roi.currentIndex;
        var namePoly = this.editableResearch.nameResearch + " " + index;
        layer.namePoly = namePoly;
        this.rois.addLayer(layer);
        // add to researched panel
        myView.researchesPanel.addUnderRow(this.editableResearch,layer);
    };

    // this.resetResearch = function(){
    //     this.removeAllOverlays();
    //     myView.nameBox.setValue('');
    //     this.editableResearch.removeAllRoi();
    //     thisControl.actualize();
    //     this.updateMarkers();
    // };
    
    // remove current research
    this.removeResearch = function(index){
        var research = myModel.researches[index];
        if(this.editableResearch == research) 
            this.changeEditableResearch(-1);
        if(research.locationMarker)
            research.locationMarker.removeFrom(map);
        ////var indexResearchObsolete = 
            /////this.getIndexByResearch(this.editableResearch);
        
        // remove from research checkboxes
        ////myView.researchCheckBoxList.removeCheckBox(indexResearchObsolete);
        // remove from research selector
        ////myView.researchSelector.removeOption(indexResearchObsolete);
        // remove Rois
        ////this.removePolygonsFGUI(this.editableResearch.roi);
        this.removePolygonsFGUI(research.roi);
        
        myModel.researches.splice(index, 1);

        //this.addResearch();
        // this.updateMarkers();
    };
    
     // remove current research
    this.removeAllResearch = function(){
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
    this.updateColor = function(){
        this.editableResearch.roi.eachLayer(function (layer) {
            layer.setStyle({color : thisControl.editableResearch.colorBorder
                     ,fillColor: thisControl.editableResearch.colorBackground,
                     fillOpacity: 0.2,  weight: WEIGHT_ROI});
        });
        
        myView.researchesPanel.changeBackground(this.editableResearch, 
            this.editableResearch.colorBackground);
        myView.editionTitle.getContainer().style.color = 
            this.editableResearch.colorBackground;
    };

    /**
     * @function addOverlays() called by event 'finished drawing' of newPolygonButton
     * layer: ROI 
     * add new overlay with the layer as the inside point of layer
     * @see view.js
     */
    this.addOverlays = function(layer, name){
        //myView.layersPanel.addOverlay(layer, name);
    };

    // @function removeAllOverlays()
    this.removeAllOverlays = function(){
        this.editableResearch.roi.eachLayer(function(layer){
            myView.layersPanel.removeLayer(layer);
        });
    };

    this.deletePolygon = function(poly){
        this.editableResearch.roi.eachLayer(function (layer){
            if(((layer instanceof L.Polygon || layer instanceof L.Rectangle ) 
                && layer.getLatLngs()[0].length==0) || layer == poly){
                layer.removeFrom(map);
                layer.closeTooltip();
                thisControl.editableResearch.roi.removeLayer(layer);
                myView.researchesPanel.removeUnderRow(thisControl.editableResearch, layer);
                thisControl.rois.removeLayer(layer);
            }
        });
        // this.updateMarkers();
    }

    //---------------------------------View->Model-------------------------------------//
    /**
     *  View -> Model : These functions is intended for getting informations from GUI (FGUI)
     */ 
    // @function getNamFGUI(): String
    // Returns name of research filled in the the name-research text box
    this.getNameFGUI = function(){
        var res = myView.nameBox.getValue();
        return res ;
    };

    // @function getColorBorderFGUI(): String
    // Returns color of ROI border selected in the color box
    this.getColorBorderFGUI = function(){
        var res = myView.borderColorSelector.getColor();
        return res || "red";
    };

    // @function getColorPointFGUI(): String
    // Returns color of ROI Point selected in the color box
    this.getColorPointFGUI = function(){
        var res = myView.tweetsColorSelector.getColor();
        return res || "green";
    };

    // @function getColorBackgroundFGUI(): String
    // Returns color of ROI Background selected in the color box
    this.getColorBackgroundFGUI = function(){
        var res = myView.backgroundColorSelector.getColor();
        return res || "red";
    };

    // @function getRoiFGUI(): String
    // Returns polygon of ROI selected on the map
    this.getRoiFGUI = function(){
        var res = null;

        return res || null;
    };

    this.getTimeRange = function(){
        var res = null;

        var resDefault = {};
        resDefault.startDate = new Date();
        resDefault.endDate = new Date();
        
        return res || resDefault;
    };

    //------------------------------Model -> View ------------------------------------
    //// It's intended to update data in GUI for example when we change the research

    this.setNameToGUI = function (name){
        myView.nameBox.setValue(name);
    };

    this.setColorBackgroundToGUI = function(color){
        myView.backgroundColorSelector.setColor(color);
    };
    
    this.setColorBorderToGUI = function(color){
        myView.borderColorSelector.setColor(color);
    };

    this.setColorPointToGUI = function(color){
        myView.tweetsColorSelector.setColor(color);
    };

    this.showPolygonsToGUI = function(group){
        group.eachLayer(function(layer){
            thisControl.showPolygonToGUI(layer);
        });   
    };

    this.showPolygonToGUI = function(layer){
        thisControl.rois.addLayer(layer);
        layer.setStyle({stroke: true, fill: true});
        layer.openTooltip();
        if(layer.research == this.editableResearch)
            this.enablePolygon(layer);
    };

    // @function removePolygonsFGUI(LayerGroup): void
    // Remove Layer group passed in param from myView.rois 
    // update the overlay panel
    // used when change current research
    this.removePolygonsFGUI = function(group){
        group.eachLayer(function(layer){
            thisControl.rois.removeLayer(layer);
            layer.removeFrom(map);
        });   
    };

    this.hidePolygonsFGUI = function(group){
        group.eachLayer(function(layer){
            thisControl.hidePolygonFGUI(layer);
        });   
    };
    
    this.hidePolygonFGUI = function(layer){
        thisControl.rois.removeLayer(layer);
        layer.setStyle({stroke: false, fill: false});
        layer.closeTooltip();
        this.disablePolygon(layer);
    };

    this.disablePolygons = function(group){
        group.eachLayer(function(layer){
            if(layer.editor)
                layer.editor.disable();
            layer.setStyle({fillOpacity: 0.4, opacity: 0.8, weight: WEIGHT_ROI});
        });       
    };

    this.disablePolygon = function(layer){
        if(layer.editor)
            layer.editor.disable();
        layer.setStyle({fillOpacity: 0.4, opacity: 0.8, weight: WEIGHT_ROI});
    };
    
    this.enablePolygons = function(group){
        group.eachLayer(function(layer){
            if(layer.editor)
                layer.editor.enable();
            layer.bringToFront();
            layer.setStyle({fillOpacity: 0.2, opacity: 1.0, weight: WEIGHT_ROI});
        });       
    };

    this.enablePolygon = function(layer){
        if(layer.editor)
            layer.editor.enable();
        layer.bringToFront();
        layer.setStyle({fillOpacity: 0.2, opacity: 1.0, weight: WEIGHT_ROI});
    };

    this.removeAllPolygonsFGUI = function(){
        myView.rois.eachLayer(function(layer){
            layer.eachLayer(function(souslayer){
                myView.layersPanel.removeLayer(souslayer);
            });
        });
        myView.rois.clearLayers();
    }


    //--------------------------------- Research Controller ---------------------------------- 
    // Its intended to manipulate the research list and current research, 
    this.getResearchByRid = function(rid) {
        var res = myModel.researches.find(function (item){
            return item.rid === rid;
        });

        return (res)?res.research:null;
    };

    this.getResearchByName = function(name) {
        var res = myModel.researches.find(function (item){
            return item.nameResearch === name;
        })
        return (res)?res.research:null;
    };

    this.getIndexByResearch = function(research) {
        for(var i = 0; i < myModel.researches.length; i++) {
            if(myModel.researches[i] === research ){
                return i;
            }
        }
    }

    // change current research to researches[index]
    this.changeEditableResearch = function(index) {
        // Say good bye to previous research
        var researchObsolete = this.editableResearch;
        // disable Editing its polygons
        if(researchObsolete)
            //this.removePolygonsFGUI(researchObsolete.roi);
            this.disablePolygons(researchObsolete.roi);
            
        // there are no editable research
        if(index == -1){
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
            myView.newPolyAdminButton.noneDisplay();
            myView.locationResearchButton.noneDisplay();
            myView.editionHide.setSign("◄");
            myView.editionHide.getContainer().style.left = '25%';
            myView.editionDiv.hideState = true;
        }
            

        
        ////
        // Check if next-currentResearch is checked or not
        /*var nextCurrentResearchChecked = myView.researchCheckBoxList.getChecked(index);
        // If previos research is still in the research list
        if(this.getIndexByResearch(researchObsolete) != null) 
        {
            // set research checkbox of above research to checkable and unchecked
            myView.researchCheckBoxList.setCheckable(
                this.getIndexByResearch(researchObsolete),
                false);
            myView.researchCheckBoxList.setChecked(
                this.getIndexByResearch(researchObsolete),
                false
            ); */
        // remove polygons of old research 
        
        
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
        this.showPolygonsToGUI(this.editableResearch.roi);
        // update interface
        this.actualize();
    };

    // remove researches[i]
    this.removeResearchByIndex = function(index) {
        if(this.editableResearch == myModel.researches[index])
            this.changeEditableResearch(-1);
        myModel.researches.splice(index, 1);
        thisControl.actualize();
    };

    //------------------------------------Actualize--------------------------------
    // @function actualize(): void 
    // often called after a mofification occurs in GUI 
    this.actualize = function() {
        // View -> Model
        // update currentResearch attribut from Interface
        // Check for first call
        ////
        if(this.editableResearch){
            ////this.editableResearch.nameResearch = this.getNameFGUI();
            this.editableResearch.colorBorder = this.getColorBorderFGUI();
            this.editableResearch.colorPoint = this.getColorPointFGUI();
            this.editableResearch.colorBackground = this.getColorBackgroundFGUI();
            this.editableResearch.timeRange = this.getTimeRange();
            this.updateColor();
		}
        // check message box
        var message = "";
        var name = myView.nameBox.getValue();
        if(name == ""){
            message = "Enter a research name";
        } 
        else 
        {
            for(var i = 0; i < myModel.researches.length; i++){
                if(name == myModel.researches[i].nameResearch)
                ////&& this.editableResearch!= myModel.researches[i].research)
                    message = 'Name existed already';
            }
        }
      
        if(message){
            myView.nameBox.disable();
        } else {
            myView.nameBox.enable();
        }
        if(name == "ton nom?")
            message = "Salut, Je suis Tweetsmap !"
        if(name == "ton pere?")
            message = "Sakura"
        if(name == "ta copine?")
            message = "Je suis une fille ..."          
        myView.nameBox.setMessage(message);

        //console.log(this.toString());
        
        /** update research selectable list box
        ////myView.researchSelector.setSelectedOption(
        ////    this.getIndexByResearch(this.editableResearch)
        ////);
        ////myView.researchSelector.setTextOfOption(
        ////    this.getIndexByResearch(this.editableResearch), 
            this.editableResearch.nameResearch);
        // update research checkbox list
        myView.researchCheckBoxList.setTextOfCheckBox(
            this.getIndexByResearch(this.editableResearch),
            this.editableResearch.nameResearch);
        // set current research checkbox to be checked
        myView.researchCheckBoxList.setChecked(
            this.getIndexByResearch(this.editableResearch),
            true
        );
        // set current reserach checkbox to uncheckable
        myView.researchCheckBoxList.setCheckable(
            this.getIndexByResearch(this.editableResearch),
            true
        );
**/
        // this.updateMarkers(); 
        // console.log(this.toString());
        
    };

    this.initModel();
}
// Override toString methode using for debugging
Controller.prototype.toString = function(){
    var string = "[GUI Infor] " + myModel.researches.length + " researches";
    for(var i = 0; i < myModel.researches.length; i++)
        string +="\n"+ myModel.researches[i].toString();
    string +="\n <editable research> : " + this.editableResearch;
    string +="\n rois: "
    this.rois.eachLayer(function(layer){
       string += layer.namePoly + " ,"; 
    });
    return string;
};

//-------------------------------------DataBase Connection------------------------//


//----------------------------------------Controller singleton---------------------------------------
var myController = new Controller();


