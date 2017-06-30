/**
 * Author: LE Van Tuan
 * Date: June 29 2017
 * Classes
 */


// GUI class that contains:
// - The researches
// - Map layers
'use strict';
function GUI(){

    var gui = this;

    // View -> Controller : These functions is intended for getting informations from GUI (FGUI) 
    this.getNameFGUI = function(){
        return "Current Research";
    };

    this.getColorBoundFGUI = function(){
        return "red";
    };

    this.getColorPointFGUI = function(){
        return "green";
    };

    this.getColorBackgroundFGUI = function(){
        return "back";
    };

    this.getRoiFGUI = function(){
        return null;
    };

    this.getTimeRange = function(){
        return null;
    };
    //// Model : Elements of a GUI
    // list of researches

    this.researches = [];
    this.currentResearch = null;
    // id of research
    this.rid = 0;

    //// Controller : 
    this.addResearch = function(){
        // increment id 
        gui.rid ++;
        // create new Research
        gui.currentResearch = new Research;
        // update id in new Research
        gui.currentResearch.rid = gui.rid;
        var currentLength = gui.researches.length;
        // add new Research in list research of gui
        gui.researches[currentLength] = 
            {rid: gui.currentResearch.rid, research: gui.currentResearch};
        // update interface
        gui.actualize();
    };

    this.getResearchByRid = function(rid) {
        return gui.researches.find(function (item){
            return item.rid === rid;
        }).research;
    };

    // change current research to research of rid
    this.changeCurrentResearchByRid = function(rid) {
        gui.currentResearch = gui.getResearchByRid(rid);
        gui.actualize();
    };

    // change current research to researches[index]
    this.changeCurrentResearch = function(index) {
        gui.actualize();
    };

    // remove researches[i]
    this.removeResearchByIndex = function(index) {
        var bool= false;
        if(gui.currentResearch === gui.researches[index].research){
            gui.currentResearch = null;
            bool = true;
        }
        gui.researches.splice(index, 1);
        if(bool)
            gui.addResearch();
        else
            gui.actualize();
    };

    this.actualize = function() {
        // View -> Model
        //update currentResearch attribut from Interface
        gui.currentResearch.actualize();
    };
}
// Override toString methode
GUI.prototype.toString = function(){
    var string = "[GUI Infor] " + this.researches.length + " researches";
    for(var i = 0; i < this.researches.length; i++)
        string +="\n"+ this.researches[i].research.toString();
    string +="\n <current research> : " + this.currentResearch.toString();
    return string;
};

// Research class that contains:
// - A zone of interst 
// - Time range 
// - Color
// Attention: using GUI.addResearch to create new research.
function Research() {

    var research = this;

    this.rid = null;
    this.nameResearch = myGUI.getNameFGUI();
    this.colorBound = myGUI.getColorBoundFGUI();
    this.colorPoint = myGUI.getColorPointFGUI();
    this.colorBackground = myGUI.getColorBackgroundFGUI();
    this.roi = myGUI.getRoiFGUI();
    this.timeRange = myGUI.getTimeRange();

    this.actualize = function() {
        research.nameResearch = myGUI.getNameFGUI();
        research.colorBound = myGUI.getColorBoundFGUI();
        research.colorPoint = myGUI.getColorPointFGUI();
        research.colorBackground = myGUI.getColorBackgroundFGUI();
        research.roi = myGUI.getRoiFGUI();
        research.timeRange = myGUI.getTimeRange();
    };

}
// override toString()
Research.prototype.toString = function() {
    return "    [Research Infor]rid = " + this.rid + " | name = " + this.nameResearch + " | Bound color = " + this.colorBound
            + " | Point color " + this.colorPoint + " | Background color " + this.colorBackground;
};

// The unique GUI
var myGUI = new GUI();