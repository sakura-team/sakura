var list = new tabList();


/**
 * GLOBAL VARS
 */
var treePath="operateur/mean";


var editor = ace.edit("editor");
editor.setTheme("ace/theme/xcode");
editor.getSession().setMode("ace/mode/python");


function init(){
    generateTree(treePath);
    generateToolbox();

    /**
     * ON CLICK FUNCTIONS
     */

    /*On a tree element*/
    $(document).on('click', '.jstree-anchor', function() {openFile($(this)[0]);});

    /*on the tab cross*/
    $(document).on('click', '.closeTab', function() {closeTab($(this)[0]);});
    // $(document).on('click', '.closeTab', function() {alert("close");});

    /*on a tab*/
    // $(document).on('click', '.tabListElement a', function(e) {alert("lien")});
    $(document).on('click', '.tabListElement a', function(e) {openTab($(this)[0].parentElement);});
    // $(document).on('click', '.tabListElement', function(e) {alert("oui");});

    /*on the save all button of the toolbox*/
    $(document).on('click', '#saveAll', function() {
        saveTab();
        list.saveAll();
    });

    /*on the save button of the toolbox*/
    $(document).on('click', '#save', function() {
        //updateDisplayFilesNotSaved("active");
        saveTab();
        list.saveCurrent()
    });

    /*other toolbox element*/
    $(document).on('click', '#divNewFile', function() {toolboxNewFile();});
    $(document).on('click', '#divNewDir', function() {toolboxNewDir();});
    $(document).on('click', '.glyphicon-trash', function() {toolboxTrash();});
    /*any toolbox element : flashing*/
    $(document).on('click', '.divToolBox', function() {
        var t = $(this).children();
        t.each(function() {
            console.log(this);
            t.css("color","#c4c4c4");
            setTimeout(function(){
                t.css("color","rgb(144, 144, 144)");
            },250);
        });
    });

    /*extended list*/
    $(document).on('click', '.glyphicon-collapse-down', function() {
        $(this).attr('class', 'glyphicon glyphicon-collapse-up');
        list.generateExpandedMenu();
    });
    $(document).on('click', '.glyphicon-collapse-up', function() {
        $(this).attr('class', ' glyphicon glyphicon-collapse-down');
        $("#ExpandMenu").remove();
    });
    /*chose an element*/
    $(document).on('click', '.ExpandMenuElement', function() {
        buildBar($(this)[0].attributes['data-path'].value);
        var tab = document.getElementById($(this)[0].attributes['data-path'].value);
        tab.click();
    });

    /*right click on tree*/
    //$(".jstree-anchor").contextmenu(function(e) {
   $(document).on("contextmenu", ".jstree-anchor", function(e){
        var type = $(this)[0].parentElement.attributes['data-type'].value;
        console.log("_______________________");
        if($(".jstree-clicked").length){
            $(".jstree-clicked")[0].classList.remove("jstree-clicked");
        }
        $(this)[0].classList.add("jstree-clicked");
        generateRigthClickMenu(type);

        treeClickedElement = $(this)[0].parentElement.attributes['data-path'].value;
        console.log(treeClickedElement);

        $("#RightClickMenu").css("display", "initial");
        $("#RightClickMenu").css("top", e.clientY);
        $("#RightClickMenu").css("left", e.clientX);

        return false;
    });

    /*click on context menu*/
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

    $(document).mousedown(function(event) {
        switch (event.which) {
            case 1:
                //alert('Left Mouse button pressed.');
                $("#RightClickMenu").css("display","none");
                break;
            case 2:
                //alert('Middle Mouse button pressed.');
                $("#RightClickMenu").css("display","none");
                break;
            case 3:
                //alert('Right Mouse button pressed.');
                break;
            default:
                //alert('You have a strange Mouse!');
        }
    });

    $(document).on('click', '.showList', function() {
        console.log(list);
    });
}


init();