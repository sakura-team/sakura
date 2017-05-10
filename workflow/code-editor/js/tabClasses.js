class tab{
    constructor(name,path, content){
        this.name = name;
        this.path = path;
        this.content = content;
        this.modified = false;
    }

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

    save(){
        var content = this.content;
        //alert(content);
        sakura.operator.save_file_content(this.path, content, function(ret) {
            console.log("Content saved for " + this.path);
        });
        this.modified = false;
        this.modified = false;
    }
}
class tabList{
    constructor(){
        //this.tabsList = new Array();
        this.tabsList = new Array();
        this.activeTabIndex;
        //console.log(this.tabsList);
    }

    getActiveTabIndex(){
        return this.activeTabIndex;
    }
    setActiveTabIndex(i){
        this.activeTabIndex = i;
    }
    getActiveTab(){
        return this.tabsList[this.activeTabIndex];
    }
    setActiveTab(path){
        for(var i = 0; i<this.tabsList.length;i++){
            if(this.tabsList[i].getPath() == path) this.activeTabIndex = i;
        }
    }
    getList(){
        return this.tabsList;
    }

    addNewTab(newTab){
        this.tabsList.push(newTab);
    }


    supprOnglet(path){
        //alert("");
        for(var i = 0; i<list.length;i++){
            if(list[i].path == path){
                //alert("test");
            }
        }
    }

    pathIsOpen(path){
        var b = false;
        for(var i = 0; i<this.tabsList.length && !b;i++){
			// alert(this.tabsList[i].getPath() + " - " + path);
            if(this.tabsList[i].getPath() == path) b = true;
        }
        return b;
    }

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

    getElementByPath(path){
        for(var i = 0; i<this.tabsList.length;i++){
            if(this.tabsList[i].getPath() == path) return this.tabsList[i];
        }

        return -1;
    }

    getIndexByPath(path){
        for(var i = 0; i<this.tabsList.length;i++){
            if(this.tabsList[i].getPath() == path) return i;
        }

        return -1;
    }

    deleteByIndex(index){
        if (index > -1) {
            this.tabsList.splice(index, 1);
        }

        if(index < this.activeTabIndex){
            this.activeTabIndex --;
        }
    }

    saveContentActive(content){
        this.tabsList[this.getActiveTabIndex()].setContent(content);
    }

    saveCurrent(){
        this.tabsList[this.getActiveTabIndex()].save();
    }

    saveAll(){
        for(var i = 0;i<this.tabsList.length;i++){
            this.tabsList[i].save();
        }
    }
}