/**
 * GLOBAL VARS
 */
var activeTab = "";
var codeTabs = new Array();
var treePath="operateur/mean";

//used for popup
var treeClickedElement;
var mode;
/**
 * INITIALIZATION OF THE TREE
 * INITIALIZATION OF THE EDITOR
 * @type {string}
 */

var editor = ace.edit("editor");
editor.setTheme("ace/theme/xcode");
editor.getSession().setMode("ace/mode/python");

/**
 * INITIALIZATION SORTABLE
 */


$( function() {
    $( "#tabList" ).sortable({
        beforeStop: function () {
            console.log('beforeStart::');
        },
        revert: true,
        update: function( event, ui ) {
            console.log(event);
            console.log(ui);

            console.log("id : " + ui.item[0].attributes['id'].value);
            console.log("file1 : ../operateur/mean/test/file1.txt");

            console.log("code tab : " );
            console.log(codeTabs);

            console.log("code tabs keys: ");
            console.log(Object.keys(codeTabs));

            console.log("code tab [file1]: " );
            console.log(codeTabs["../operateur/mean/test/file1.txt"]);

            console.log("code tab id: " );
            console.log(codeTabs[ui.item[0].attributes['id'].value]);

            console.log("index of id : " + codeTabs.indexOf[ui.item[0].attributes['id'].value]);
            console.log("index of id : " + codeTabs.indexOf["../operateur/mean/test/file1.txt"]);

            console.log("code tabs ../operateur/mean/test/testLongueur02.txt : ");
            console.log(Object.keys(codeTabs).indexOf["../operateur/mean/test/testLongueur02.txt"]);

            console.log("key index of : ");
            console.log(Object.keys(codeTabs).indexOf[ui.item[0].attributes['id'].value]);

            console.log("New position: " + ui.item.index());
        }
    });
    $( "ul, li" ).disableSelection();
} );

/**
 * TREE GENERATION
 */

function generateTree(path){
    try{
        $('#tree').jstree().destroy();
        $('#bar').html("");
    } catch(e){}

    var content = $.ajax("ajax/tree.php?path=" + path)
        .done(function(tree) {
            $('#bar').append(tree);
            $('#tree').jstree({
                'core' : {
                    'check_callback' : true
                },
                /*"plugins": ["sort"],
                'sort': function (a, b) {
                    var nodeA = this.get_node(a);
                    var nodeB = this.get_node(b);
                    var lengthA = nodeA.children.length;
                    var lengthB = nodeB.children.length;
                    if ((lengthA == 0 && lengthB == 0) || (lengthA > 0 && lengthB > 0))
                        return this.get_text(a).toLowerCase() > this.get_text(b).toLowerCase() ? 1 : -1;
                    else
                        return lengthA > lengthB ? -1 : 1;
                }*/
            });

            //$('[data-type="dir"] > .jstree-anchor').append("<i class='fa fa-plus-square' aria-hidden='true'></i>");
            //$('[data-type="dir"] > .jstree-anchor').append("<i class='fa fa-file' aria-hidden='true'></i>");
            //$('[data-type="dir"] > .jstree-anchor').append('<i class="fa fa-folder" aria-hidden="true"></i>');

        });
}
generateTree(treePath);

/**
 * ToolBox init
 */

function generateBootstrap(){
    $("#toolBox").append("</span><span class=\"glyphicon glyphicon-floppy-disk\" aria-hidden=\"true\"></span>");
    $("#toolBox").append("<span class=\"glyphicon glyphicon-plus\" aria-hidden=\"true\"></span><span class=\"glyphicon glyphicon-file\" aria-hidden=\"true\"></span>");
    $("#toolBox").append("<span class=\"glyphicon glyphicon-plus\" aria-hidden=\"true\"></span><span class=\"glyphicon glyphicon-folder-open\" aria-hidden=\"true\"></span>");
    $("#toolBox").append("<span class=\"glyphicon glyphicon-trash\" aria-hidden=\"true\"></span></span>");

	$("li[data-type='file']>a").append("<span class=\"glyphicon glyphicon-file\" aria-hidden=\"true\"></span>");
	$("li[data-type='file']>a i").css("diplay","none");
	$("li[data-type='dir']>a").html("<span class=\"glyphicon glyphicon-folder-open\" aria-hidden=\"true\"></span>");
}

generateBootstrap();

/**
 * ON CLICK FUNCTIONS
 */

$(document).on('click', '.jstree-anchor', function() {openFile($(this)[0]);});

$(document).on('click', '.closeTab', function() {closeTab($(this)[0]);});

$(document).on('click', '.tabListElement', function() {openTab($(this)[0]);});

$(document).on('click', '.glyphicon-floppy-disk', function() {save();});
$(document).on('click', '.fa-floppy-o', function() {save();});
$(document).on('click', '#save', function() {save();});

$(document).on('click', '.glyphicon-file', function() {toolboxNewFile();});
$(document).on('click', '.glyphicon-folder-open', function() {toolboxNewDir();});
$(document).on('click', '.glyphicon-trash', function() {toolboxTrash();});

$(document).on('click', '.glyphicon', function() {
    var t = $(this);
    t.css("color","#c4c4c4");
    setTimeout(function(){
        t.css("color","rgb(144, 144, 144)");
    },250);
});

$(document).on('click', '.glyphicon-play', function() {
    console.log($(".glyphicon-play")[0].attributes["data-state"]);
    if($(".glyphicon-play")[0].attributes["data-state"].value == "o"){
        $(".glyphicon-play").css("transform","rotate(90deg)");
        $(".glyphicon-play").attr("data-state","r");
    }
    else if($(".glyphicon-play")[0].attributes["data-state"].value == "r"){
        $(".glyphicon-play").css("transform","rotate(0deg)");
        $(".glyphicon-play").attr("data-state","o");
    }
});

/*
 EXPAND TABS
 */

function generateExpandedMenu(){
    $("#ExpandMenu").remove();
    strRight = "<div id=\"ExpandMenu\">" +
        "<ul>";
    for (t in codeTabs) {
        strRight += "<li class='ExpandMenuElement' data-path='"+t+"'>" + slashRemover(t) + "</li>";
    }

    strRight += "</ul></div>";

    console.log("d : " + strRight);

    $('#main').append(strRight);

    $("#ExpandMenu").css("display", "initial");
    $("#ExpandMenu").css("top", $("#tabList").height());
    $("#ExpandMenu").css("left", $("#main").width()-$("#ExpandMenu").width());
}

$(document).on('click', '.glyphicon-play', function() {
    //buildBar();
    if($(".glyphicon-play")[0].attributes["data-state"].value == "r") {
        //alert(codeTabs.length);
        console.log(Object.keys(codeTabs).length);
        if(Object.keys(codeTabs).length > 0) {
             generateExpandedMenu();
        }
    }
    else if($(".glyphicon-play")[0].attributes["data-state"].value == "o") {
        $("#ExpandMenu").remove();
    }


    //
    //var type = $(this)[0].parentElement.attributes['data-type'].value;
    //setRigthClickMenu(type);
    //
    //treeClickedElement = $(this)[0].parentElement.attributes['data-path'].value;
    //console.log(treeClickedElement);
    //
    //$("#RightClickMenu").css("display", "initial");
    //$("#RightClickMenu").css("top", event.clientY);
    //$("#RightClickMenu").css("left", event.clientX);
});

$(document).on('click', '.ExpandMenuElement', function() {
    buildBar($(this)[0].attributes['data-path'].value);
    var tab = document.getElementById($(this)[0].attributes['data-path'].value);
    tab.click();
});



/**
 * AJAX
 */

/**
 * add element
 */
function add(path,mode){
    //alert(path);
    var ret = $.ajax("ajax/add.php?mode="+mode+"&path="+path)
        .done(function() {
            generateTree(treePath);
        })
        .fail(function() {
            console.log("errorAdd");
        })
}

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

    //futurTab : name of the tab that will be generated
    //var futurTab = slashRemover(filePath);
    var futurTab = filePath;

    //if tabname not already in codeTabs
    if ($.inArray(futurTab, Object.keys(codeTabs)) == -1) {
        console.log("__________New Tab");
        //if it's a file
        if (fileType == 'file') {
            //get the content of selected file
            var content = $.ajax("ajax/content.php?path=" + filePath)
                .done(function(returnContent) {
                    //save old tab
                    // saveTab();
                    //change the editor content
                    changeContent(returnContent);
                    //get the Extension and change the language
                    var extension = filePath.substring(filePath.indexOf('.') + 1, filePath.length);
                    //changeLanguage(extension);
                    autoChange(filePath);
                    //////////new Active tab/////////
                    activeTab = futurTab;
                    //newTab(activeTab);
                    newTab(filePath);
                    saveTab();
                    setActive(activeTab);
                    buildBar(filePath);
                    if($(".glyphicon-play")[0].attributes["data-state"].value == "r") generateExpandedMenu();
                    console.log("DoneOuvertureFichier");
                })
                .fail(function() {
                    console.log("errorOuvertureFichier");
                })
        }
    }
    //if tab already open
    else {
        console.log("__________Known Tab");
        buildBar(futurTab);
        document.getElementById(futurTab).click();
    }
}

/**
 * Tab suppression
 */
function closeTab(tab){
    var element = tab.parentElement.parentElement.id;
    console.log("__________closeTab");
    console.log(element);
    //Delete the tab from the table
    delete codeTabs[element];
    //if the element deleted was the active one
    if (element === activeTab){
        if(Object.keys(codeTabs).length !== 0){
            document.getElementById(Object.keys(codeTabs)[0]).click();
        }
        else changeContent("");
    }

    document.getElementById(element).remove();
    buildBar(activeTab);
}
/**
 * open a tab
 */
function openTab(tab){
    if($.inArray(tab.id, Object.keys(codeTabs)) !== -1) {
        console.log("__________click on tabListElement");
        var classNames = tab.className;
        if (classNames.includes("inactive")) {
            var element = tab.id;
            console.log(element);

            if (codeTabs[activeTab] != undefined) {
                saveTab();
            }

            activeTab = element;
            console.log("active tab  : " + activeTab);

            if (codeTabs[activeTab] != undefined) {
                changeContent(codeTabs[activeTab]);

                autoChange(activeTab);
                setActive(activeTab);
            }
        }
    }
}

function suppr(path){
    console.log("__________Suppr");
    console.log("ajax/add.php?path="+path);
    var ret = $.ajax("ajax/suppr.php?path="+path)
        .done(function() {
            console.log("Suppr");
            generateTree(treePath);
        })
        .fail(function() {
            console.log("errorSuppr");
        })
}

/**
 * save all open documents
 */
function save(){
    console.log("__________Save");
    saveTab();
    var tabsList = Object.keys(codeTabs);
    for(var i = 0;i<tabsList.length;i++){
        //alert(tabsList[i]);
        //alert(codeTabs[tabsList[i]]);

        var content = encodeURIComponent(codeTabs[tabsList[i]]);


        var save = $.ajax("ajax/save.php?path=" + tabsList[i] + "&content=" + content)
            .done(function(returnVar) {
                //alert(returnVar);
            })
            .fail(function() {
                console.log("error");
            })
            .always(function() {
                console.log("complete");
            });
    }
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
    $('#dialog')[0].title = "Add File";
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
    $('#dialog')[0].title = "Add Directory";
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
 * Add a new tab into the tab div
 * @param tabName
 */
function newTab(tabName) {
    var NewTab = "<li id=\"" + tabName + "\" role=\"presentation\" class=\"inactive tabListElement\"><a>" + slashRemover(tabName) + "<button id=\"tab_" + tabName + "\" class=\"close closeTab\" type=\"button\" >×</button></a></li>";
    console.log(NewTab);
    $("#tabList").append(NewTab);
}

/**
 * Add a new tab in the begining the tab div
 * @param tabName
 */
function newPreTab(tabName) {
    var NewTab = "<li id=\"" + tabName + "\" role=\"presentation\" class=\"inactive tabListElement\"><a>" + slashRemover(tabName) + "<button id=\"tab_" + tabName + "\" class=\"close closeTab\" type=\"button\" >×</button></a></li>";
    console.log(NewTab);
    $("#tabList").prepend(NewTab);
}

/**
 * build the tab bar
 */

function buildBar(tab){
    console.log("__________Build Bar");

    var clickedTab = $(".active")[0].id;


    $("#tabList").html("");
    var tabBarWidth = $("#tabList").width();
    var tabsWidth = 0;

    console.log("tab bar width : " + tabBarWidth);

    var i = 0;
    var b = false;
    if(typeof tab === 'undefined') b=true;
    for(t in codeTabs){
        if(t == tab) b = true;
        if(b) {
            newTab(t);
            tabsWidth += document.getElementById(t).offsetWidth;
            if (tabsWidth > tabBarWidth - 20) {
                $(".tabListElement")[i].remove();
                break;
            }
            i++;
        }
    }
    //alert(tabsWidth + " - " + tabBarWidth);
    //alert(tabsWidth < tabBarWidth - 100);
    if(tabsWidth < tabBarWidth - 180){
        for(var i = Object.keys(codeTabs).indexOf(tab)-1;i>=0 && tabsWidth < tabBarWidth - 100;i--){
    //        alert(i);
            var temp = Object.keys(codeTabs)[i];
            console.log("temp : " + temp);
            newPreTab(temp);
            tabsWidth += document.getElementById(temp).offsetWidth;
        }
       //alert(Object.keys(codeTabs));
    }
    console.log("tabs width : " + tabsWidth);
    if(typeof tab !== 'undefined') {
        //alert(document.getElementById(tab));
        document.getElementById(tab).click();
    }
    else document.getElementById(clickedTab).click();

}
/**
 * save the content of the tab in codeTabs
 */
function saveTab() {
    if (activeTab !== ""){
        codeTabs[activeTab] = editor.getValue();
		console.log("set value: "+activeTab+"=======>"+ editor.getValue());
	}
   // readTab(false);
}

/**
 * read the codeTabs array and display everything in the console
 */
function readTab(b) {
    console.log("__________readTable");
    for (var tabs in codeTabs) {
        var toDisp = tabs;
        if(b){
            toDisp += "=" + codeTabs[tabs];
        }
        console.log(toDisp);
        //console.log(tabs + "=" + codeTabs[tabs]);
    }
}

/**
 * set class active
 * @param activeTab
 */
function setActive(activeTab){
    console.log("__________setActiveTab");
    var list = $("#tabList")[0].children;
    console.log(list);
    //alert(list);
    console.log("active tab : " + activeTab);
    for(var i=0;i<list.length;i++){
        console.log(list[i].id);
        if(list[i].id === activeTab ){
            list[i].className = "active tabListElement";
            console.log("yeah");
        }
        else{
            list[i].className = "inactive tabListElement";
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


/*RIGHT CLICK MENU*/

//$("#toolBox").append("<span class=\"glyphicon glyphicon-floppy-disk\" aria-hidden=\"true\"></span>");
//$("#toolBox").append("<span class=\"glyphicon glyphicon-file\" aria-hidden=\"true\"></span>");
//$("#toolBox").append("<span class=\"glyphicon glyphicon-folder-open\" aria-hidden=\"true\"></span>");
//$("#toolBox").append("<span class=\"glyphicon glyphicon-trash\" aria-hidden=\"true\"></span>");

function setRigthClickMenu(menuMode){
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

$(document).on("contextmenu", ".jstree-anchor", function(e){
    var type = $(this)[0].parentElement.attributes['data-type'].value;
    console.log("_______________________");
    $(".jstree-clicked")[0].classList.remove("jstree-clicked");
    $(this)[0].classList.add("jstree-clicked");
    setRigthClickMenu(type);

    treeClickedElement = $(this)[0].parentElement.attributes['data-path'].value;
    console.log(treeClickedElement);

    $("#RightClickMenu").css("display", "initial");
    $("#RightClickMenu").css("top", event.clientY);
    $("#RightClickMenu").css("left", event.clientX);

    return false;
});

//$(document).on("click","span",function(){});

$(document).on("click",".RightClickMenuElement",function(){
    var menuId = $(this)[0].id;
    switch(menuId){
        case 'NewFile':
            $('#dialog')[0].title = "Add File";
            mode = 'file';
            $( "#dialog" ).dialog();
            break;
        case 'NewDir' :
            $('#dialog')[0].title = "Add Directory";
            mode = 'dir';
            $( "#dialog" ).dialog();
            break;
        case "delete" :
            suppr(treeClickedElement);
            break;
    }
});

//POPUP

/* If the button "add file" on the pop up is clicked */
$(document).on('click', '.btnAddFile', function() {
    var url = treeClickedElement + '/' + $(".inputAddFile")[0].value ;
    add(url,mode);
    $(".inputAddFile")[0].value="";
    $("#dialog").dialog('close');
});

$(document).on("click",document,function(){
    $("#RightClickMenu").css("display","none");
});