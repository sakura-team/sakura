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
    }

    /**
     *  Handle event function
     */ 
    
    // Event when finish drawing a poly
    this.registrerPoly = function(layer) {
        myModel.currentResearch.roi.addLayer(layer);
        myModel.currentResearch.roi.addTo(map);
        return myModel.currentResearch.roi.getLayers().length;            
    }

    this.resetResearch = function(){
        this.removeAllOverlays();
        myView.nameBox.resetValue();
        myModel.currentResearch.removeAllRoi();
        thisControl.actualize();
    }
    
    
    //  @function updateRoiColor() called by event 'change' of tweetColorSelector 
    //  Change the roi color  
    //  @see view.js
    this.updateRoiColor = function(){
        myModel.currentResearch.roi.eachLayer(function (layer) {
            layer.setStyle({color : myModel.currentResearch.colorBackground});
        });
    }

    /**
     * @function addOverlays() called by event 'finished drawing' of newPolygonButton
     *  add new overlay
     * @see view.js
     */
    this.addOverlays = function(layer, name){
        myView.overlaysPanel.addOverlay(layer, name);
    }

    // @function removeAllOverlays()
    this.removeAllOverlays = function(){
        myModel.currentResearch.roi.eachLayer(function(layer){
            myView.overlaysPanel.removeLayer(layer);
        });
    }

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
        var res = null;
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

    

    //// Controller : 
    this.addResearch = function(){
        // increment id 
        myModel.rid ++;
        // create new Research
        myModel.currentResearch = new Research;
        // update id in new Research
        myModel.currentResearch.rid = myModel.rid;
        var currentLength = myModel.researches.length;
        // add new Research in list research of thisControl
        myModel.researches[currentLength] = 
            {rid: myModel.currentResearch.rid, research: myModel.currentResearch};
        // update interface
        thisControl.actualize();
    };

    this.getResearchByRid = function(rid) {
        return myModel.researches.find(function (item){
            return item.rid === rid;
        }).research;
    };

    // change current research to research of rid
    this.changeCurrentResearchByRid = function(rid) {
        myModel.currentResearch = thisControl.getResearchByRid(rid);
        thisControl.actualize();
    };

    // change current research to researches[index]
    this.changeCurrentResearch = function(index) {
        myModel.currentResearch = myModel.researches[index].research;
        thisControl.actualize();
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

    this.actualize = function() {
        // View -> Model
        // update currentResearch attribut from Interface
        // Check for first call
        if(myModel.currentResearch != null){
            myModel.currentResearch.actualize();
        }
        console.log(this.toString());

        // check message box
        var message = "";
        if(myModel.currentResearch.nameResearch == "Current Research"){
            message = "Name is null";
            
        }
        myView.nameBox.setMessage(message);

        this.updateRoiColor();
        
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