/**
* Class tab
* a tab is created when an element is opened in the editor
* it represents a file
*/
class tab{
    /**
    * It needs a name, the path of the file and the content
    * the var modified will be put to true when something is written in it and not saved
    */
    constructor(name,path, content){
        this.name = name;
        this.path = path;
        this.content = content;
        this.modified = false;
    }
    /**
    * Getters and setters
    */
    getName(){
        return this.name;
    }

    setName(name){
        this.name = name;
    }

    getContent(){
        return this.content;
    }

    setContent(content){
        this.content = content;
    }

    getPath(){
        return this.path;
    }

    setPath(path){
        this.path = path;
    }
    /**
    * Save the file on the hub
    * uses the API
    */
    save(){
        (debug?console.log("saved : " + this.path ):null);
        var content = this.content;
        sakura.operator.save_file_content(this.path, content, function(ret){});
        this.modified = false;
        updateModifiedTab();
    }
}
/**
* tabList is the interface with the JS application
* is a list of all oped tabs
*/
class tabList{
    /**
    * tabsList -> list of tab
    * activeTabIndex -> the index the the "active" (in the editor) tab
    */
    constructor(){
        this.tabsList = new Array();
        this.activeTabIndex;
    }
    /**
    * Getter
    */
    getList(){
        return this.tabsList;
    }

    /**
    * Add a tab to the list
    */
    addNewTab(newTab){
        this.tabsList.push(newTab);
    }

    /**
    * check if the given path is in the tablist
    *
    * return boolean
    */
    pathIsOpen(path){
        var b = false;
        for(var i = 0; i<this.tabsList.length && !b;i++){
            // alert(this.tabsList[i].getPath() + " - " + path);
            if(this.tabsList[i].getPath() == path) b = true;
        }
        return b;
    }

    /**
    * if the given path is open, return the tab
    * else return -1
    */
    getElementByPath(path){
        for(var i = 0; i<this.tabsList.length;i++){
            if(this.tabsList[i].getPath() == path) return this.tabsList[i];
        }

        return -1;
    }

    /**
    * if the given path is open, return the index
    * else return -1
    */
    getIndexByPath(path){
        for(var i = 0; i<this.tabsList.length;i++){
            if(this.tabsList[i].getPath() == path) return i;
        }

        return -1;
    }

    /**
    * Close tab
    *
    * Remove the closed tab from the list
    */
    deleteByIndex(index){
        if (index > -1) {
            this.tabsList.splice(index, 1);
        }

        if(index < this.activeTabIndex){
            this.activeTabIndex --;
        }
    }

    /**
    * call the save function of all opened tabs
    */
    saveAll(){
        for(var i = 0;i<this.tabsList.length;i++){
            this.tabsList[i].save();
        }
    }

    /**
    * generate the extended menu (button on the right)
    */
    generateExpandedMenu(){
        $("#ExpandMenu").remove();
        var strRight = "<div id=\"ExpandMenu\">" +
            "<ul>";
        for (var i = 0; i<this.tabsList.length;i++) {
            strRight += "<li class='ExpandMenuElement' data-path='"+this.tabsList[i].getPath()+"'>" + this.tabsList[i].getName() + "</li>";
        }
        strRight += "</ul></div>";
        $('#main').append(strRight);
        $("#ExpandMenu").css("display", "initial");
    }

    /**
    * ACTIVE TAB FUNCTIONS
    */

    /**
    * Get the index of the "active" Tab
    */
    getActiveTabIndex(){
        return this.activeTabIndex;
    }
    /**
    * change the active tab for the index of i
    */
    setActiveTabIndex(i){
        this.activeTabIndex = i;
    }
    /**
    * Getter of the "active" Tab
    */
    getActiveTab(){
        return this.tabsList[this.activeTabIndex];
    }
    /**
    * Set the "active" Tab for the
    */
    setActiveTab(path){
        for(var i = 0; i<this.tabsList.length;i++){
            if(this.tabsList[i].getPath() == path) this.activeTabIndex = i;
        }
    }
    /**
    * set the content of the current tab
    */
    saveContentActive(content){
        this.tabsList[this.getActiveTabIndex()].setContent(content);
    }
    /**
    * save the current tab
    */
    saveActiveTab(){
        this.tabsList[this.getActiveTabIndex()].save();
    }

    /**
    * MANIPULATE ORDER
    */

    changePos(tabIndex,posDifferential){
        var t = this.tabsList[tabIndex];
        var activePath = this.getActiveTab().getPath();
        this.deleteByIndex(tabIndex);
        this.tabsList.splice(tabIndex + posDifferential, 0, t);
        list.setActiveTab(activePath);
    }

}
