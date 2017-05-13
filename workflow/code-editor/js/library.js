//used for popup
var treeClickedElement;
var mode;


/*
*
* Generation of code sample
*
* */

/**
 * TREE GENERATION
 */
/**
* Function to call to (re)build the tree
*/
function generateTree(){
    //empty the tree section
    try{
        $('#bar').html("");
        $('#tree').jstree().destroy();
    } catch(e){}
    //call the tree builder
    sakura.operator.get_file_tree(print_file_tree);
}
/**
* parameter : - entry : a Json file containing all the elements and infos
*
* build the tree and append it in the bar div
* call the function jstree
*/
function print_file_tree(entries)
{
    (debug?console.log("\n________________________________________\n\tgenerateTree\n"):null);
    // entries obtained with sakura.operator.get_file_tree()
    // are either:
    // - a directory:     { 'name': <dirname>,
    //                      'is_dir': true,
    //                      'dir_entries': [ <entry>, <entry>, <entry>, ... ]
    //                    }
    // - a regular file:  { 'name': <filename>,
    //                      'is_dir': false
    //                    }
    // recursively, directory entries follow the same format.

    // treeHtmlString contains the lines of the tree
    var treeHtmlString = [];
    treeHtmlString.push("<div id='tree' class='tree'><ul>");
    treeHtmlString.push("<li data-type='dir' data-path='/' data-jstree=\"{ 'opened' : true }\">/<ul>");
    //call the recursive function
    print_dir(entries, treeHtmlString);
    treeHtmlString.push("</ul></li>");
    treeHtmlString.push("</ul></li></div>");
    var str = "";
    for(var i = 0 ; i < treeHtmlString.length ; i++) {
        str += treeHtmlString[i];
    }
    (debug?console.log(str):null);
    $("#bar").append(str);

    $('#tree').jstree();

    document.getElementById("tree").children[0].children[0].getElementsByTagName("i")[0].click();
    (debug?console.log("________________________________________\n"):null);
}
/**
* Take a dir in json as a parameter
* complete the treeHtmlString with the content of the dir
*/
function print_dir(entries, treeHtmlString, currentPath = "")
{
    for (var i = 0; i < entries.length; i++) {
        var entry = entries[i];
        if (!entry.is_dir) {    //FILE
            treeHtmlString.push("<li data-type='file' data-path='" + currentPath + entry.name + "' class='file' data-jstree=\"{'icon':'http://www.planetminecraft.com/images/buttons/icon_edit.png'}\">"+entry.name+"</li>");
        } else {    //DIR
            treeHtmlString.push("<li data-type='dir' data-path='" + currentPath + entry.name + "' data-jstree=\"{ 'opened' : true }\">" + entry.name + "<ul>");
            currentPath += entry.name + "/";
            print_dir(entry.dir_entries, treeHtmlString, currentPath); //Prints content of the visited directory
            treeHtmlString.push("</ul></li>");
            if((currentPath.match(/\//g) || []).length == 1) {
                currentPath = "";
            }
            else
                currentPath = currentPath.substr(0, currentPath.lastIndexOf("/") + 1);
        }
    }
    return treeHtmlString;
}

/*RIGHT CLICK MENU*/

/**
* Generate the menu on the right click on a tree element depending on if it's a dir or a file
*/
function generateRigthClickMenu(menuMode){
    (debug?console.log("\n________________________________________\n\tgenerateRigthClickMenu"):null);
    $("#RightClickMenu").remove();
    var strRight;
    switch (menuMode){
        case "dir" :
            strRight = "<div id=\"RightClickMenu\">" +
                "<ul>" +
                "<li class='RightClickMenuElement' id='NewFile'><span class=\"glyphicon glyphicon-file\" aria-hidden=\"true\"></span>  New File</li>" +
                "<li class='RightClickMenuElement' id='NewDir'><span class=\"glyphicon glyphicon-folder-open\" aria-hidden=\"true\"></span>  New Directory</li>" +
                "<li class='RightClickMenuElement' id='delete'><span class=\"glyphicon glyphicon-trash\" aria-hidden=\"true\"></span> Delete</li>" +
                "" +
                "</ul>" +
                "</div>";
            break;
        case "file" :
            strRight = "<div id=\"RightClickMenu\">" +
                "<ul>" +
                "<li class='RightClickMenuElement' id='delete'><span class=\"glyphicon glyphicon-trash\" aria-hidden=\"true\"></span> Delete</li>" +
                "" +
                "</ul>" +
                "</div>";
            break;
    };
    $('#main').append(strRight);

    (debug?console.log("mode :" + menuMode + "\n" + strRight):null);
    (debug?console.log("________________________________________\n"):null);
}

/**
 * MANIPULATE FILES
 */

/**
 * create new element in remote
 */
function createNewElement(path,mode){
    (debug?console.log("\n________________________________________\n\tcreateNewElement"):null);
    if(path.indexOf("//") > -1) path = path.split("//")[1];
    (debug?console.log("Path : " + path):null);
    (debug?console.log("Mode : " + mode):null);

    if(mode === "dir") {
        var i = sakura.operator.new_directory(path, function(ret) {
            (debug?console.log("\nDirectory successfully created : " + path):null);
        });
        generateTree();
    } else if(mode === "file") {
        var i = sakura.operator.new_file(path, "", function(ret) {
            (debug?console.log("\nFile successfully created : " + path):null);
        });
        generateTree();
    }
}


/**
 * delete elementin remote
 * @param path
 */
function removeElement(path){
    (debug?console.log("\n________________________________________\n\tremoveElement"):null);
    sakura.operator.delete_file(path, function(ret) {
        (debug?console.log("\nRemoved : " + path + "\n________________________________________\n"):null);
    });
    generateTree();
}

/**
 * manipulate Tabs
 */

/**
 * click on tree element, open a file
 */
function openFile(fileName){
    (debug?console.log("\n________________________________________\n\topenFile"):null);
    ///getPath
    filePath = fileName.parentElement.attributes['data-path'].value;
    fileType = fileName.parentElement.attributes['data-type'].value;
    (debug?console.log("path : " + filePath):null);
    (debug?console.log("type : " + fileType):null);
    //if tabname not already in codeTabs
    if (!list.pathIsOpen(filePath)) {
        (debug?console.log("New file : " + filePath):null);
        //if it's a file
        if (fileType == 'file') {
            var content = sakura.operator.get_file_content(filePath, function(returnContent) {
                (debug?console.log("\n_______________open remote file"):null);

                var newtab = new tab(slashRemover(filePath),filePath,returnContent);
                list.addNewTab(newtab);
                buildBar(filePath);

                if($(".glyphicon-collapse-up").length>0){list.generateExpandedMenu();};
                (debug?console.log("__________DoneOuvertureFichier__________"):null);
            });
        }
    }
    //if tab already open
    else {
        (debug?console.log("Already opened file : " + filePath):null);
		    saveTab();
        buildBar(filePath);
        (debug?console.log("________________________________________"):null);
    }
}

/**
 * open a tab
 */
function openTab(tab){
	(debug?console.log("__________Open Tab : " + tab.id):null);
	// test of the tab is open
    if(list.pathIsOpen(tab.id)) {
        //console.log("_____element opened");
        var classNames = tab.className;
		    // if the clicked element was inactive
        if (classNames.includes("inactive")) {
            var element = tab.id;
            if ($(".active")[0] !== undefined) {
                saveTab();
            }
            //set the tab as the active one
            list.setActiveTab(element);
            if (list.getActiveTabIndex() != undefined) {
                //set the content of the editor
                changeContent(list.getActiveTab().getContent());
                //change the configuration of the colorization
                autoChange(list.getActiveTab().getPath());
                //gives the class active to the active tab and inactive to the others
                setActive(list.getActiveTab().getPath());
            }
        }
    }
}

/**
 * Tab suppression
 */
function closeTab(tab){
    (debug?console.log("__________closeTab______________________"):null);
	  var element = tab.parentElement.id;
    var index = list.getIndexByPath(element);
    (debug?console.log("Element : " + element + " -  index : " + index):null);
	  if(tab.id === "close_"+list.getActiveTab().getPath() || tab.id === "tab_"+list.getActiveTab().getPath()){
		    if(list.getList().length > 1){
			       var i;
             (index == 0 ? i=1 : i=0);
    	       $("#tabList").children()[i].getElementsByTagName("a")[0].click()
        }
	      else changeContent("");
    }
    //Delete the tab from the table
    list.deleteByIndex(index);
    document.getElementById(element).remove();

    if($(".glyphicon-collapse-up").length>0){list.generateExpandedMenu();};
}

/**
 * build the tab bar
 */
function buildBar(tab){
    (debug?console.log("__________Build Bar "+tab):null);

	  //empty the bar
    $("#tabList").html("");
	  //get screen width
    var tabBarWidth = $("#tabList").width();
    var tabsWidth = 0;
    list.setActiveTab(tab);
    //from the active until the end of the list
    for(var i = list.getActiveTabIndex();i<list.getList().length;i++){
        var t = list.getList()[i].getPath();
		    //add a tab at the end
        newTab(t);
		    //edit width var
        tabsWidth += document.getElementById(t).offsetWidth;
		    //break if too large
        if (tabsWidth > tabBarWidth - 20) {
            $(".tabListElement")[i].remove();
            break;
        }
    }
	//if there is still room
    if(tabsWidth < tabBarWidth - 180){
		//going backward
        for(var i = list.getActiveTabIndex()-1;i>=0 && tabsWidth < tabBarWidth - 100;i--){
            var temp = list.getList()[i].getPath();
			      //add a tab at the begining
            newPreTab(temp);
            tabsWidth += document.getElementById(temp).offsetWidth;
        }
    }
    if(typeof tab !== 'undefined') {
        document.getElementById(tab).getElementsByTagName("a")[0].click();
    }
    updateDisplayFilesNotSaved("active");
    (debug?console.log("_________"):null);
}
/**
 * save the content of the tab in codeTabs
 */
function saveTab() {
    (debug?console.log("\n__________saveTab " + list.getActiveTab().getPath()):null);
    if (list.getActiveTabIndex() != undefined){
        list.saveContentActive(editor.getValue());
	  }
}

/**
 * Add a new tab into the tab div
 * @param tabName
 */
function newTab(tabName) {
    var NewTab = "<li id=\"" + tabName + "\" role=\"presentation\" class=\"inactive tabListElement\"><a>" + slashRemover(tabName) + "</a><button id=\"close_" + tabName + "\" class=\"close closeTab\" type=\"button\" >&#215;</button></li>";
    $("#tabList").append(NewTab);
}

/**
 * Add a new tab in the begining the tab div
 * @param tabName
 */
function newPreTab(tabName) {
    var NewTab = "<li id=\"" + tabName + "\" role=\"presentation\" class=\"inactive tabListElement\"><a>" + slashRemover(tabName) + "</a><button id=\"tab_" + tabName + "\" class=\"close closeTab\" type=\"button\" >&#215;</button></li>";
    $("#tabList").prepend(NewTab);
}

/*
* TOOLBOX
*/

function toolboxNewFile(){
    (debug?console.log("__________ToolBox New File"):null);
    //tree_clicked : the clicked element on the tree
    var tree_clicked = $(".jstree-clicked")[0].parentElement;
    //if you selected element is a file, get the dir root
    if(tree_clicked.attributes['data-type'].value != "dir"){
        tree_clicked = tree_clicked.parentElement.parentElement;
    }
    (debug?console.log(tree_clicked):null);
    treeClickedElement = tree_clicked.attributes['data-path'].value;
    $('#dialog')[0].title="Add File";
    $('#dialog').attr("title","Add File");
    $('.ui-dialog-title').html("Add File");
    $('.inputAddFile').attr("placeholder","Enter file name");
    $('.btnAddFile').html("Add File");
    mode = 'file';
    $( "#dialog" ).dialog();
}

function toolboxNewDir(){
    (debug?console.log("__________ToolBox New Dir"):null);
    //tree_clicked : the clicked element on the tree
    var tree_clicked = $(".jstree-clicked")[0].parentElement;
    //if you selected element is a file, get the dir root
    if(tree_clicked.attributes['data-type'].value != "dir"){
        tree_clicked = tree_clicked.parentElement.parentElement;
    }
    (debug?console.log(tree_clicked):null);
    treeClickedElement = tree_clicked.attributes['data-path'].value;
    $('#dialog')[0].title="Add Directory";
    $('#dialog').attr("title","Add Directory");
    $('.ui-dialog-title').html("Add Directory");
    $('.inputAddFile').attr("placeholder","Enter directory name");
    $('.btnAddFile').html("Add Directory");
    mode = 'dir';
    $( "#dialog" ).dialog();
}

/**
 * UTILITY FUNCTIONS
 */
/**
 * EDITOR
 */

/**
 * change the content of the editor
 * @param returnContent
 */
function changeContent(returnContent) {
    (debug?console.log("__________changeContent"):null);
    editor.setValue(returnContent);
    editor.clearSelection();
}

/**
 * change the language of the editor
 * used for colorisation
 * @param lang
 */
function autoChange(path){
    (debug?console.log("__________autoChange : " + path.split(".")[1]):null);
    var modelist = ace.require("ace/ext/modelist");
    var mode = modelist.getModeForPath(path).mode
    editor.session.setMode(mode)
}
/**
 * set class active
 * @param activeTab
 */
function setActive(activeTab){
    (debug?console.log("__________setActiveTab : " + activeTab):null);
    var openTabList = $("#tabList")[0].children;
    for(var i=0;i<openTabList.length;i++){
        if(openTabList[i].id === list.getActiveTab().getPath() ){
            openTabList[i].className = "active tabListElement";
        }
        else{
            openTabList[i].className = "inactive tabListElement";
        }
    }
}
/**
 * TOOL
 */

/**
 * take a string in parameters (a path)
 * remove the slash and everything before it
 * @param filePathLocal
 * @returns {*}
 */
function slashRemover(filePathLocal) {
    if (filePathLocal.indexOf("/") > -1) filePathLocal = slashRemover(filePathLocal.substr(filePathLocal.indexOf("/") + 1, filePathLocal.length));
    return filePathLocal;
}

/*Scroll speed*/
/*if (document.getElementById('tab').addEventListener) document.getElementById('tab').addEventListener('DOMMouseScroll', wheel, false);
document.getElementById('tab').onmousewheel = document.getElementById('tab').onmousewheel = wheel;

function wheel(event) {
    var delta = 0;
    if (event.wheelDelta) delta = event.wheelDelta / 120;
    else if (event.detail) delta = -event.detail / 3;

    handle(delta);
    if (event.preventDefault) event.preventDefault();
    event.returnValue = false;
}

function handle(delta) {
    var time = 500;
    var distance = 21;

    $('#tab').stop().animate({
        scrollTop: $('#tab').scrollTop() - (distance * delta)
    }, time );
}*/
function updateDisplayFilesNotSaved(type) {

    /*if(type == "active") {
        if(codeTabs[activeTab] != editor.getValue()) {  //File's content differs from editor's content
                $("li.jstree-node.file.jstree-leaf").each(function() {
					if(this.attributes['data-path'].value == activeTab) {
				        if($(this).find("a i+span").length<1) {
                            $(this).find("a i").after("<span>*</span>");
                        }else{
							$(this).find("a i+span").html("*");
						}
					}
						console.log("down");
						if($(this).find("a i+span").html()=="*"){

							var nameFileTree=$(this).find("a").clone().children().remove().end().text();

							$("#tabList li").each(function() {
								var nameFileTab= $(this).find("a").clone().children().remove().end().text();

								console.log("down 55 "+nameFileTab);

								if(nameFileTree==nameFileTab){
									console.log("down 66 "+nameFileTab);
									if($(this).find("a:first span").length<1){
										$(this).find("a:first").html("<span>*</span>" + $(this).find("a:first").html());
									}else{
										$(this).find("a:first span").html("*");
									}
								}
							});
						}

				//	}
                });
        } else {  //Reset original name
            $("li.jstree-node.file.jstree-leaf").each(function() {
					if(this.attributes['data-path'].value == activeTab) {
				        if($(this).find("a i+span").length<1) {
                            $(this).find("a i").after("<span> </span>");
                        }else{
							$(this).find("a i+span").html(" ");
						}
					}

						if($(this).find("a i+span").html()=="*"){

							var nameFileTree=$(this).find("a").clone().children().remove().end().text();

							$("#tabList li").each(function() {
								var nameFileTab= $(this).find("a").clone().children().remove().end().text();

								if(nameFileTree==nameFileTab){
									if($(this).find("a:first span").length<1){
										$(this).find("a:first").html("<span>*</span>" + $(this).find("a:first").html());
									}else{
										$(this).find("a:first span").html("*");
									}
								}
							});
						}else{
							var nameFileTree=$(this).find("a").clone().children().remove().end().text();

							$("#tabList li").each(function() {
								var nameFileTab= $(this).find("a").clone().children().remove().end().text();

								if(nameFileTree==nameFileTab){
									if($(this).find("a:first span").length<1){
										$(this).find("a:first").html("<span> </span>" + $(this).find("a:first").html());
									}else{
										$(this).find("a:first span").html(" ");
									}
								}
							});

						}
            });
        }
    }
    else {
        //TODO : iterer sur tous les onglets ouverts
    }
    */
}


/*******************************************
Shortcuts : Ctrl+W, T and S (also OSX version)
********************************************/
var appleKey = [224,17,91,93];
$(window).keydown(function(e) {
    //alert(appleKey.indexOf(e.keyCode));
    //if((e.keyCode == 16 && e.keyCode == 17 )) {alert("");}

    //console.log(e);
    //console.log(e.keyCode);
    //Ctrl + S
    if((e.ctrlKey || e.keyCode == 224 || e.keyCode == 17 || e.keyCode == 91 || e.keyCode == 93) && e.keyCode == 83) {
        e.preventDefault();
        console.log("saving");
        list.saveActiveTab();
        //save();
        //TODO : save only current tab, needs the creation of a function saveActiveTab()
    }

    //Ctrl + W
    //Seems it is impossible to prevent Ctrl+W except with the methode below  (same for Ctrl+T)
});

//Only way to prevent Ctrl+W, but displays an unavoidable alert
/*$(window).on("beforeunload", function(e) {
    console.log("beforeclose");
    return false;
});*/
