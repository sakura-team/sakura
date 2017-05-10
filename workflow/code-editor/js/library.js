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

function generateTree(path){
    try{
        $('#tree').jstree().destroy();
        $('#bar').html("");
    } catch(e){}
    sakura.operator.onready(do_test);
}


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

function print_file_tree(entries)
{
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
    
    var treeHtmlString = [];
    treeHtmlString.push("<div id='tree' class='tree'><ul>");
    print_dir(entries, treeHtmlString);
    treeHtmlString.push("</ul></div>");
    var i = 0;
    var str = "";
    for(i = 0 ; i < treeHtmlString.length ; i++) {
        str += treeHtmlString[i];
    }
    $("#bar").append(str);

    $('#tree').jstree();
}

function do_test() {
    // print file tree
    console.log("do test");
    sakura.operator.get_file_tree(print_file_tree);
}


/**
 * ToolBox GENERATION
 */

function generateToolbox(){
    $("#toolBox").append("</span><div title=\"Save current file\" class='divToolBox' id='save'><span class=\"glyphicon glyphicon-floppy-disk\" aria-hidden=\"true\"></span></div>");
    $("#toolBox").append("</span><div title=\"Save all files\" class='divToolBox' id='saveAll'><span class=\"back glyphicon glyphicon-floppy-disk\" aria-hidden=\"true\"></span><span class=\"front glyphicon glyphicon-floppy-disk\" aria-hidden=\"true\"></span></div>");
    $("#toolBox").append("<div title=\"New file\" class='divToolBox' id='divNewFile'><span class=\"glyphicon glyphicon-plus\" aria-hidden=\"true\"></span><span class=\"glyphicon glyphicon-file\" aria-hidden=\"true\"></span></div>");
    $("#toolBox").append("<div title=\"New folder\" class='divToolBox' id='divNewDir'><span class=\"glyphicon glyphicon-plus\" aria-hidden=\"true\"></span><span class=\"glyphicon glyphicon-folder-open\" aria-hidden=\"true\"></span></div>");
    $("#toolBox").append("<div title=\"Delete current file\" class='divToolBox'><span class=\"glyphicon glyphicon-trash\" aria-hidden=\"true\"></span></span></div>");

	$("li[data-type='file']>a").append("<span class=\"glyphicon glyphicon-file\" aria-hidden=\"true\"></span>");
	$("li[data-type='file']>a i").css("diplay","none");
	$("li[data-type='dir']>a").html("<span class=\"glyphicon glyphicon-folder-open\" aria-hidden=\"true\"></span>");
}

/*RIGHT CLICK MENU*/

function generateRigthClickMenu(menuMode){
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
}

/**
 * AJAX
 */

/**
 * MANIPULATE FILES
 */

/**
 * add element
 */
function add(path,mode){
    if(mode === "dir") {
        var i = sakura.operator.new_directory(path, function(ret) {
            console.log("Directory creation : " + path);
        });
        generateTree(treePath);
    } else if(mode === "file") {
        var i = sakura.operator.new_file(path, "", function(ret) {//oijoj
            console.log("File creation : " + path);
        });
        generateTree(treePath);
    }
}


/**
 * delete element
 * @param path
 */
function suppr(path){
    sakura.operator.delete_file(path, function(ret) {
        console.log("Removed " + path);
    });
    generateTree(treePath);
}

/**
 * manipulate Tabs
 */
/**
 * click on tree element, open a file
 */
function openFile(fileName){
    ///getPath
    filePath = fileName.parentElement.attributes['data-path'].value;
    fileType = fileName.parentElement.attributes['data-type'].value;
    console.log("__________Path");
    console.log("path : " + filePath);
    console.log("type : " + fileType);

    //if tabname not already in codeTabs
    if (!list.pathIsOpen(filePath)) {
        console.log("__________New Tab");
        //if it's a file
        if (fileType == 'file') {

                var content = sakura.operator.get_file_content(filePath, function(returnContent) {
                console.log("+++++++++++OPENFILE++++++++++");

                    var newtab = new tab(slashRemover(filePath),filePath,returnContent);
                    list.addNewTab(newtab);
                    buildBar(filePath);

                    if($(".glyphicon-collapse-up").length>0){list.generateExpandedMenu();};
                    console.log("DoneOuvertureFichier");

            });
        }
    }
    //if tab already open
    else {
        console.log("__________Known Tab");
		saveTab();
        buildBar(filePath);
        //document.getElementById(filePath).click();
    }
}

/**
 * open a tab
 */
function openTab(tab){
	console.log("__________Open Tab");
    console.log(tab);
	
	// test of the tab is open
    if(list.pathIsOpen(tab.id)) {
        console.log("_____element opened");
        var classNames = tab.className;
		// if the clicked element was inactive
        if (classNames.includes("inactive")) {
            var element = tab.id;
            console.log(element);

            if ($(".active")[0] !== undefined) {
                saveTab();
            }

            list.setActiveTab(element);
            console.log("active tab  : " + list.getActiveTab().getPath());
            //alert(list.getActiveTab().getContent());

            if (list.getActiveTabIndex() != undefined) {
                changeContent(list.getActiveTab().getContent());

                autoChange(list.getActiveTab().getPath());
                setActive(list.getActiveTab().getPath());
            }
        }
    }
}

/**
 * Tab suppression
 */
function closeTab(tab){
    //alert("close");
    console.log("_____________________");
    //console.log($("#tabList").children()[0].click());
    console.log("__________closeTab");
	
	var element = tab.parentElement.id;
    console.log(element);

    var index = list.getIndexByPath(element);
    console.log(index);
	
	console.log( tab.id + "  -  " + "close_" + list.getActiveTab().getPath() );
	
	if(tab.id === "close_"+list.getActiveTab().getPath() || tab.id === "tab_"+list.getActiveTab().getPath()){
		console.log("ok");
		if(list.getList().length > 1){
			var i;
            (index == 0 ? i=1 : i=0);
			console.log("-----" + i);
			$("#tabList").children()[i].getElementsByTagName("a")[0].click()
		}
		else changeContent("");
	}    
    
    //Delete the tab from the table
    list.deleteByIndex(index);
    document.getElementById(element).remove();

    if($(".glyphicon-collapse-up").length>0){list.generateExpandedMenu();};
}

/*
* TOOLBOX
*/

function toolboxNewFile(){
    console.log("__________ToolBox New File");

    var tree_clicked = $(".jstree-clicked")[0].parentElement;
    if(tree_clicked.attributes['data-type'].value != "dir"){
        tree_clicked = tree_clicked.parentElement.parentElement;
    }
    console.log(tree_clicked);
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
    console.log("__________ToolBox New Dir");

    var tree_clicked = $(".jstree-clicked")[0].parentElement;
    if(tree_clicked.attributes['data-type'].value != "dir"){
        tree_clicked = tree_clicked.parentElement.parentElement;
    }
    console.log(tree_clicked);
    treeClickedElement = tree_clicked.attributes['data-path'].value;
    $('#dialog')[0].title="Add Directory";
    $('#dialog').attr("title","Add Directory");
    $('.ui-dialog-title').html("Add Directory");
    $('.inputAddFile').attr("placeholder","Enter directory name");
    $('.btnAddFile').html("Add Directory");
    mode = 'dir';
    $( "#dialog" ).dialog();
}

function toolboxTrash(){
    console.log("__________ToolBox Trash");
    var tree_clicked = $(".jstree-clicked")[0].parentElement.attributes['data-path'].value;
    suppr(tree_clicked);
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
    console.log("__________success : " + returnContent);
    editor.setValue(returnContent);
    editor.clearSelection();
}

/**
 * change the language of the editor
 * @param lang
 */
function autoChange(path){
    console.log("__________autoChange : " + path);
    var modelist = ace.require("ace/ext/modelist");
    var mode = modelist.getModeForPath(path).mode
    editor.session.setMode(mode) // mode now contains "ace/mode/javascript".
}

/**
 * TABS
 */
/**
 * Add a new tab into the tab div
 * @param tabName
 */
function newTab(tabName) {
    var NewTab = "<li id=\"" + tabName + "\" role=\"presentation\" class=\"inactive tabListElement\"><a>" + slashRemover(tabName) + "</a><button id=\"close_" + tabName + "\" class=\"close closeTab\" type=\"button\" >&#215;</button></li>";
    console.log(NewTab);
    $("#tabList").append(NewTab);
}

/**
 * Add a new tab in the begining the tab div
 * @param tabName
 */
function newPreTab(tabName) {
    var NewTab = "<li id=\"" + tabName + "\" role=\"presentation\" class=\"inactive tabListElement\"><a>" + slashRemover(tabName) + "</a><button id=\"tab_" + tabName + "\" class=\"close closeTab\" type=\"button\" >&#215;</button></li>";
    console.log(NewTab);
    $("#tabList").prepend(NewTab);
}

/**
 * build the tab bar
 */

function buildBar(tab){
    console.log("__________Build Bar"+tab);

	//get old Active
    //var clickedTab = $(".active")[0].id;

    console.log(tab);
    // console.log(clickedTab);

	//empty the bar
    $("#tabList").html("");
	//get screen width
    var tabBarWidth = $("#tabList").width();
    var tabsWidth = 0;
	
	list.setActiveTab(tab);
    console.log("tab bar width : " + tabBarWidth);
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
            console.log("temp : " + temp);
			//add a tab at the begining 
            newPreTab(temp);
            tabsWidth += document.getElementById(temp).offsetWidth;
        }
    }
    console.log("tabs width : " + tabsWidth);
    if(typeof tab !== 'undefined') {
        //alert(document.getElementById(tab));
        console.log(tab);
        console.log(document.getElementById(tab));
        document.getElementById(tab).getElementsByTagName("a")[0].click();
    }
    //else document.getElementById(clickedTab).click();
    updateDisplayFilesNotSaved("active");
}
/**
 * save the content of the tab in codeTabs
 */
function saveTab() {
	// alert(list.getActiveTabIndex());
	// console.log(document.getElementsByClassName("active"));
    if (list.getActiveTabIndex() != undefined){
        list.saveContentActive(editor.getValue());
		console.log("set value: "+list.getActiveTab().getPath()+"=======>"+ editor.getValue());
	}
   // readTab(false);
}

/**
 * read the codeTabs array and display everything in the console
 */
function readTab(b) {
    console.log("__________readTable");
    for (var tab in list.getList()) {
        var toDisp = tab.getName();
        if(b){
            toDisp += "=" + tab.getContent();
        }
        console.log(toDisp);
    }
}

/**
 * set class active
 * @param activeTab
 */
function setActive(activeTab){
    console.log("__________setActiveTab");
    console.log(activeTab);
    var openTabList = $("#tabList")[0].children;
    //console.log(openTabList);
    //alert(openTabList);
    console.log("active tab : " + activeTab);
    for(var i=0;i<openTabList.length;i++){
        console.log(openTabList[i].id);
        if(openTabList[i].id === list.getActiveTab().getPath() ){
            openTabList[i].className = "active tabListElement";
            console.log("yeah");
        }
        else{
            openTabList[i].className = "inactive tabListElement";
            console.log("nope");
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
    if (filePathLocal.indexOf("/") > -1) {
        filePathLocal = filePathLocal.substr(filePathLocal.indexOf("/") + 1, filePathLocal.length);
        filePathLocal = slashRemover(filePathLocal)
    }
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
        list.saveCurrent();
        //save();
        //TODO : save only current tab, needs the creation of a function saveCurrentTab()
    }
    
    //Ctrl + W
    //Seems it is impossible to prevent Ctrl+W except with the methode below  (same for Ctrl+T)
});

//Only way to prevent Ctrl+W, but displays an unavoidable alert
/*$(window).on("beforeunload", function(e) {  
    console.log("beforeclose");
    return false;
});*/
