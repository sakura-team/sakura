/**
 * Author: LE Van Tuan
 * Date: June 29 2017
 * Classes
 */


// Controller
'use strict';
function Controller(){

    var thisControl = this;

    // Created first Research
    this.initModel = function(){
       // increment id 
        myModel.rid ++;
        // create new Research
        myModel.currentResearch = new Research;
        // update id in new Research
        myModel.currentResearch.rid = myModel.rid;
        // add new Research in list research of thisControl
        myModel.researches[0] = 
            {rid: myModel.currentResearch.rid, research: myModel.currentResearch};
        // add roi of current research to myView.rois
        myView.rois.addLayer(myModel.currentResearch.roi);
        // update research list in research box
        myView.researchSelector.addOption(myModel.currentResearch.nameResearch);        
        myView.researchCheckBoxList.addCheckBox(myModel.currentResearch.nameResearch);
        myView.rois.addTo(map);
        this.updateTweetsmap();
        this.actualize();
    };

    //-----------------------------GUI->BD----------------------------
    this.updateTweetsmap = function(){
    
        // get data by operators
        sakura.operator.fire_event(['new_zone'], function (result) {
            // data = {lat: x, lng: y}
            var data = result.tweetsmap;
            // markers layer creation
            for (var i = 0; i < data.lat.length; i++) {
                // Corresponding marker
                var marker = new PruneCluster.Marker(data.lat[i], data.lng[i]);
                // filtre by ROIS
                myModel.allMarkers.RegisterMarker(marker);
            }
            console.log(myModel.allMarkers.GetMarkers().length);
            
        });


    };

    this.updateMarkers = function(){
        // remove all layers in displaed Markers for reupdating
        myView.displayedMarkers.clearLayers();
        var i = 0;
        var listPoly = [];
        var listMarkers = [];
        myView.rois.eachLayer(function(layer){
            layer.eachLayer(function(l){
                if(map.hasLayer(l)){
                    listPoly[i] = l;
                    // List markers corresponding to listPoly[i]
                    listMarkers[i] = new PruneClusterForLeaflet(160);
                    i++;
                }
            });
        });

        var marker;
        for(var i = 0; i < myModel.allMarkers.GetMarkers().length; i++){
            marker = myModel.allMarkers.GetMarkers()[i];
            for(var j=0;j<listPoly.length;j++){
                // Check if there are no selected ROIs or if marker is inside the selected ROIs
                if(this.insideOfAPoly(marker, listPoly[j])){
                    listMarkers[j].RegisterMarker(marker);
                }
            }
        }
        
        for(var j=0;j<listPoly.length;j++){
            myView.displayedMarkers.addLayer(listMarkers[j]);
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
    /**
     *  Event Handling function
     */ 

    // Event when click in checkbox of research checkbox
    // @function displayReseach(int)
    // index = index of to-display Research in the research list
    this.displayResearch = function (index) {
        this.addPolygonsToGUI(myModel.researches[index].research.roi);
    }

    this.hideResearch = function (index) {
        this.removePolygonsFGUI(myModel.researches[index].research.roi);
    }
    // Event when select an item on research selector
    this.selectResearch = function(){
        console.log(myView.researchSelector.getSelect.selectedIndex);
        this.changeCurrentResearch(myView.researchSelector.getSelect().selectedIndex);
    };

    // Event when finish drawing a poly
    this.registrerPoly = function(layer) {
        myModel.currentResearch.roi.addLayer(layer);
        return myModel.currentResearch.roi.getLayers().length;            
    };

    this.resetResearch = function(){
        this.removeAllOverlays();
        myView.nameBox.setValue('');
        myModel.currentResearch.removeAllRoi();
        thisControl.actualize();
    };
    
    // remove current research
    this.removeResearch = function(){
        var indexResearchObsolete = 
            this.getIndexByResearch(myModel.currentResearch);
        
        // remove from research checkboxes
        myView.researchCheckBoxList.removeCheckBox(indexResearchObsolete);
        // remove from research selector
        myView.researchSelector.removeOption(indexResearchObsolete);
        // remove Rois
        this.removePolygonsFGUI(myModel.currentResearch.roi);
        
        myModel.researches.splice(indexResearchObsolete, 1);
        this.addResearch();
    };
    
     // remove current research
    this.removeAllResearch = function(){
        
        // remove all from research checkboxes
        myView.researchCheckBoxList.removeAllCheckboxes();
        // remove all from research selector
        myView.researchSelector.removeAllOptions();
        // remove all Rois
        this.removeAllPolygonsFGUI(myModel.currentResearch.roi);
        
        myModel.researches.splice(0, myModel.researches.length);
        this.addResearch();
    };
    
    //  @function updateRoiColor() called by event 'change' of tweetColorSelector 
    //  Change the roi color  
    //  @see view.js
    this.updateRoiColor = function(){
        myModel.currentResearch.roi.eachLayer(function (layer) {
            layer.setStyle({color : myModel.currentResearch.colorBackground});
        });
    };

    /**
     * @function addOverlays() called by event 'finished drawing' of newPolygonButton
     * layer: ROI 
     * add new overlay with the layer as the inside point of layer
     * @see view.js
     */
    this.addOverlays = function(layer, name){
        myView.layersPanel.addOverlay(layer, name);
    }

    // @function removeAllOverlays()
    this.removeAllOverlays = function(){
        myModel.currentResearch.roi.eachLayer(function(layer){
            myView.layersPanel.removeLayer(layer);
        });
    }

    this.deletePolygons = function(poly){
        myModel.currentResearch.roi.eachLayer(function (layer){
            if(layer.getLatLngs()[0].length==0){
                myModel.currentResearch.roi.removeLayer(layer);
                myView.layersPanel.removeLayer(layer);
                return;
            }
        });
    }

    //---------------------------------View->Model-------------------------------------//
    /**
     *  View -> Model : These functions is intended for getting informations from GUI (FGUI)
     */ 
    // @function getNamFGUI(): String
    // Returns name of research filled in the the name-research text box
    this.getNameFGUI = function(){
        var res = myView.nameBox.getValue();
        return res || "Current Research";
    };

    // @function getColorBoundFGUI(): String
    // Returns color of ROI Bound selected in the color box
    this.getColorBoundFGUI = function(){
        var res = null;
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

    this.setColorPointToGUI = function(color){
        myView.tweetsColorSelector.setColor(color);
    };

    this.addPolygonsToGUI = function(group){
        myView.rois.addLayer(group);
        var i = 0;
        group.eachLayer(function(layer){
            i++;
            myView.layersPanel.addOverlay(layer, layer.namePoly);
        });
   
    };

    // @function removePolygonsFGUI(LayerGroup): void
    // Remove Layer group passed in param from myView.rois 
    // update the overlay panel
    // used when change current research
    this.removePolygonsFGUI = function(group){
        group.eachLayer(function(layer){
            myView.layersPanel.removeLayer(layer);
        });
        myView.rois.removeLayer(group);        
    };

    this.removeAllPolygonsFGUI = function(){
        myView.rois.eachLayer(function(layer){
            layer.eachLayer(function(souslayer){
                myView.layersPanel.removeLayer(souslayer);
            });
        });
        myView.rois.clearLayers();
    }


    //--------------------------------- Controller ---------------------------------- 
    // Its intended to manipulate the research list and current research, 
    // including add/ remove/ research a research , change current research.
    this.addResearch = function(){
        var check = this.getResearchByName("Current Research");
        if(check){
            this.changeCurrentResearch(this.getIndexByResearch(check));
            return;
        }
        // increment id 
        myModel.rid ++;
        // create new Research
        var research = new Research;
        // update id in new Research
        research.rid = myModel.rid;
        var currentLength = myModel.researches.length;
        // add new Research in list research of thisControl
        myModel.researches[currentLength] = 
            {rid: research.rid, research: research};
        // update research select box
        myView.researchSelector.addOption(research.nameResearch);
        // update research checkbox list
        myView.researchCheckBoxList.addCheckBox(research.nameResearch);
        // change current research to research
        this.changeCurrentResearch(this.getIndexByResearch(research));
    };

    this.getResearchByRid = function(rid) {
        var res = myModel.researches.find(function (item){
            return item.rid === rid;
        });

        return (res)?res.research:null;
    };

    this.getResearchByName = function(name) {
        var res = myModel.researches.find(function (item){
            return item.research.nameResearch === name;
        })
        return (res)?res.research:null;
    };

    this.getIndexByResearch = function(research) {
        for(var i = 0; i < myModel.researches.length; i++) {
            if(myModel.researches[i].research === research ){
                return i;
            }
        }
    }

    // change current research to researches[index]
    this.changeCurrentResearch = function(index) {

        // Say good bye to previous research
        var researchObsolete = myModel.currentResearch;
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
            );
            // remove polygons of old research
            this.removePolygonsFGUI(researchObsolete.roi);
        }
    
        myModel.currentResearch = myModel.researches[index].research;
        
        // set value of name Box to current research name 
        this.setNameToGUI(myModel.currentResearch.nameResearch);
        this.setColorBackgroundToGUI(myModel.currentResearch.colorBackground);
        this.setColorPointToGUI(myModel.currentResearch.colorPoint);
        this.addPolygonsToGUI(myModel.currentResearch.roi);
        if(myModel.currentResearch.nameResearch === "Current Research"){
            myView.nameBox.setValue('');
        }
        // update interface
        this.actualize();
    };

    // remove researches[i]
    this.removeResearchByIndex = function(index) {
        var bool= false;
        if(myModel.currentResearch === myModel.researches[index].research){
            myModel.currentResearch = null;
            bool = true;
        }
        myModel.researches.splice(index, 1);
        if(bool)
            thisControl.addResearch();
        else
            thisControl.actualize();
    };

    //------------------------------------Actualize--------------------------------
    // @function actualize(): void 
    // often called after a mofification occurs in GUI 
    this.actualize = function() {
        // View -> Model
        // update currentResearch attribut from Interface
        // Check for first call
        myModel.currentResearch.nameResearch = this.getNameFGUI();
        myModel.currentResearch.colorBound = this.getColorBoundFGUI();
        myModel.currentResearch.colorPoint = this.getColorPointFGUI();
        myModel.currentResearch.colorBackground = this.getColorBackgroundFGUI();
        myModel.currentResearch.timeRange = this.getTimeRange();

        // check message box
        var message = "";
        var name = myModel.currentResearch.nameResearch
        if(name == "Current Research"){
            message = "Enter a research name";
        } 
        else 
        {
            for(var i = 0; i < myModel.researches.length; i++){
                if(name == myModel.researches[i].research.nameResearch
                && myModel.currentResearch!= myModel.researches[i].research)
                    message = 'Name existed already';
            }
        }

        // hide save button when an error occurs
        if(message){
            myView.saveResearchButton.setDisabled(true);
            myView.newPolygonButton.setDisabled(true);
            myView.newRectangleButton.setDisabled(true);
            myView.newCircleButton.setDisabled(true);
            myView.removeResearchButton.setDisabled(true);
        }
        else{
            myView.saveResearchButton.setDisabled(false);  
            myView.newPolygonButton.setDisabled(false);
            myView.newRectangleButton.setDisabled(false);
            myView.newCircleButton.setDisabled(false);
            myView.removeResearchButton.setDisabled(false);
        }
        if(name == "Qui es tu?")
            message = "Salut, Je suis Tweetsmap !"          
        myView.nameBox.setMessage(message);

        this.updateRoiColor();
        
        // update research selectable list box
        myView.researchSelector.setSelectedOption(
            this.getIndexByResearch(myModel.currentResearch)
        );
        myView.researchSelector.setTextOfOption(
            this.getIndexByResearch(myModel.currentResearch), 
            myModel.currentResearch.nameResearch);
        // update research checkbox list
        myView.researchCheckBoxList.setTextOfCheckBox(
            this.getIndexByResearch(myModel.currentResearch),
            myModel.currentResearch.nameResearch);
        // set current research checkbox to be checked
        myView.researchCheckBoxList.setChecked(
            this.getIndexByResearch(myModel.currentResearch),
            true
        );
        // set current reserach checkbox to uncheckable
        myView.researchCheckBoxList.setCheckable(
            this.getIndexByResearch(myModel.currentResearch),
            true
        );

        this.updateMarkers();
        
    };

    this.initModel();
}
// Override toString methode
Controller.prototype.toString = function(){
    var string = "[GUI Infor] " + myModel.researches.length + " researches";
    for(var i = 0; i < myModel.researches.length; i++)
        string +="\n"+ myModel.researches[i].research.toString();
    string +="\n <current research> : " + myModel.currentResearch.toString();
    return string;
};

// The unique GUI
var myController = new Controller();