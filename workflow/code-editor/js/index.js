var list = new tabList();

/**
 * GLOBAL VARS
 */
var editor = ace.edit("editor");
editor.setTheme("ace/theme/xcode");
editor.getSession().setMode("ace/mode/python");
editor.$blockScrolling = Infinity;

// do you want to display logs ?
var debug = true;

function init(){
    (debug?console.log("________________________________________\n\tWelcome in the Debug mode\n"):null);
    generateTree();

    /**
     * ON CLICK FUNCTIONS
     */

    /*On a tree element*/
    $(document).on('click', '.jstree-anchor', function() {openFile($(this)[0]);});

    /*on the tab cross*/
    $(document).on('click', '.closeTab', function() {closeTab($(this)[0]);});

    /*on a tab*/
    $(document).on('click', '.tabListElement a', function(e) {openTab($(this)[0].parentElement);});

    /*on the save all button of the toolbox*/
    $(document).on('click', '#saveAll', function() {
        saveTab();
        list.saveAll();
    });
    /*on the save button of the toolbox*/
    $(document).on('click', '#save', function() {
        saveTab();
        list.saveActiveTab()
    });
    /*other toolbox element*/
    $(document).on('click', '#divNewFile', function() {toolboxNewFile();});
    $(document).on('click', '#divNewDir', function() {toolboxNewDir();});
    $(document).on('click', '#divTrash', function() {
        (debug?console.log("__________ToolBox Trash"):null);
        removeElement($(".jstree-clicked")[0].parentElement.attributes['data-path'].value);
    });
    /*any toolbox element : flashing*/
    $(document).on('click', '.divToolBox', function() {
        var t = $(this).children();
        t.each(function() {
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
    });

    /*right click on tree*/
   $(document).on("contextmenu", ".jstree-anchor", function(e){
        var type = $(this)[0].parentElement.attributes['data-type'].value;
        if($(".jstree-clicked").length){
            $(".jstree-clicked")[0].classList.remove("jstree-clicked");
        }
        $(this)[0].classList.add("jstree-clicked");
        generateRigthClickMenu(type);

        treeClickedElement = $(this)[0].parentElement.attributes['data-path'].value;

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
                removeElement(treeClickedElement);
                break;
        }
    });

    //POPUP
    /* If the button "add file" on the pop up is clicked */
    $(document).on('click', '.btnAddFile', function() {
        var url = treeClickedElement + '/' + $(".inputAddFile")[0].value ;
        createNewElement(url,mode);
        $(".inputAddFile")[0].value="";
        $("#dialog").dialog('close');
    });

    $(document).mousedown(function(event) {
        switch (event.which) {
            case 1:
                //alert('Left Mouse button pressed.');
                setTimeout(function() {
                    $("#RightClickMenu").css("display","none");
                },250);
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
}

sakura.operator.onready(function(){
    init();

    // Open the operator.py by default
    var leafs = document.getElementsByClassName("jstree-leaf");
    setTimeout(function() {
        for(var i=0;i<leafs.length;i++){
            if(leafs[i].attributes['data-path'].value === "operator.py"){
                leafs[i].getElementsByTagName("a")[0].click();
            }
        }
    }, 1000);
});
