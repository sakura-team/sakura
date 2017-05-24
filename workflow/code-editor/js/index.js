var list = new tabList();

/**
 * GLOBAL VARS
 */

 //used for rename
 var elementPath;
 var inputValue;

//Ace Editor
var editor = ace.edit("editor");
editor.setTheme("ace/theme/xcode");
editor.getSession().setMode("ace/mode/python");
editor.$blockScrolling = Infinity;

// do you want to display logs ?
var debug = !true;

function init(){
    (debug?console.log("________________________________________\n\tWelcome in the Debug mode\n"):null);
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
        list.saveActiveTab();
    });
    /*on the new file button of the toolbox*/
    $(document).on('click', '#divNewFile', function() {toolboxNewFile();});
    /*on the new dir button of the toolbox*/
    $(document).on('click', '#divNewDir', function() {toolboxNewDir();});
    /*on the trash button of the toolbox*/
    $(document).on('click', '#divTrash', function() {
        (debug?console.log("__________ToolBox Trash"):null);
        var canRemoveElement = true;
        //Ask if the user is sure to delete element
        //if it's a dir
        if($(".jstree-clicked")[0].parentElement.attributes["data-type"].value == "dir"){
            canRemoveElement = confirm("Do you want to remove the directory " + $(".jstree-clicked")[0].parentElement.attributes['data-path'].value + " and its content ?");
        }
        else{ //if it's a file
            canRemoveElement = confirm("Do you want to remove the file " + $(".jstree-clicked")[0].parentElement.attributes['data-path'].value + " ?");
        }
        //if validate then remove the element
        if(canRemoveElement) removeElement($(".jstree-clicked")[0].parentElement.attributes['data-path'].value);
    });

    /*extended list*/
    //open
    $(document).on('click', '.glyphicon-collapse-down', function() {
        $(this).attr('class', 'glyphicon glyphicon-collapse-up');
        list.generateExpandedMenu();
    });
    //close
    $(document).on('click', '.glyphicon-collapse-up', function() {
        $(this).attr('class', ' glyphicon glyphicon-collapse-down');
        $("#ExpandMenu").remove();
    });
    //chose an element
    $(document).on('click', '.ExpandMenuElement', function() {
        buildBar($(this)[0].attributes['data-path'].value);
    });

    /*right click on tree*/
   $(document).on("contextmenu", ".jstree-anchor", function(e){
        //information on the clicked element
        treeClickedElement = $(this)[0].parentElement.attributes['data-path'].value;
        treeClickedElementType = $(this)[0].parentElement.attributes['data-type'].value;
        treeClickedElementModified = $(this)[0].parentElement.classList.contains("modified");
        //generate the menu
        generateRigthClickMenu(treeClickedElementType);
        //display the menu and set it on mouse position
        $("#RightClickMenu").css("display", "initial");
        $("#RightClickMenu").css("top", e.clientY);
        $("#RightClickMenu").css("left", e.clientX);
        //do not display normal right click menu
        return false;
    });

    /*click on context menu*/
    $(document).on("click",".RightClickMenuElement",function(){
        //type on request
        var menuId = $(this)[0].id;
        switch(menuId){
            case 'NewFile':
                $('#dialog')[0].title = "Add File";
                mode = 'file';
                console.log($('#inputAddFile').val(""));
                $('#inputAddFile').val("");
                $( "#dialog" ).dialog();
                break;
            case 'NewDir' :
                $('#dialog')[0].title = "Add Directory";
                mode = 'dir';
                $('#inputAddFile').val("");
                $( "#dialog" ).dialog();
                break;
            case "delete" :
                var canRemoveElement = true;
                //Ask if the user is sure to remove element
                if(treeClickedElementType == "dir") canRemoveElement = confirm("Do you want to remove the directory " + treeClickedElement + " and its content ?");
                else canRemoveElement = confirm("Do you want to remove the file " + treeClickedElement + " ?");
                //if confirmed remove
                if(canRemoveElement) removeElement(treeClickedElement);
                break;
            case "rename" :
                $('#dialog')[0].title="Rename";
                $('#dialog').attr("title","Rename");
                $('.ui-dialog-title').html("rename");
                $('#inputAddFile').val(slashRemover(treeClickedElement));
                $('.btnAddFile').html("Rename");
                mode = 'rename';
                $( "#dialog" ).dialog();
                break;
        }
    });

    //POPUP
    /* If the button "add file" on the pop up is clicked */
    $(document).on('click', '.btnAddFile', function() {
        submitPopUp();
    });

    $(document).mousedown(function(event) {
        switch (event.which) {
            case 1:
                //Left Mouse button pressed
                setTimeout(function() {
                    $("#RightClickMenu").css("display","none");
                },250);
                break;
            case 2:
                //Middle Mouse button pressed
                $("#RightClickMenu").css("display","none");
                break;
            case 3:
                //Right Mouse button pressed
                break;
            default:1
                //You have a strange Mouse
        }
    });

    //Press enter while editing the dialog
    $("#inputAddFile").keypress(function(e){
      if(e.which == 13){
        submitPopUp();
      }
    });
    //on submit dialog
    function submitPopUp(){
      switch (mode) {
        case "rename":
          //path part of the element (exemple/exemple/)
          elementPath =  treeClickedElement.slice(0,treeClickedElement.indexOf(slashRemover(treeClickedElement)));
          //name part of the element (exemple.ex)
          inputValue = $(".inputAddFile")[0].value;
          //move and rename is the same function
          sakura.operator.move_file(treeClickedElement,elementPath + inputValue, function(ret) {
              //if the renamed tab is open
              var modifiedTab = $(".tabListElement[id = '"+ treeClickedElement +"']");
              if(modifiedTab.length > 0){
                //act : the active tab === the renamed tab
                var act = list.getActiveTab().getPath() == treeClickedElement;
                //Change the name of the tab object and the editor tab
                list.getElementByPath(treeClickedElement).setName(inputValue);
                modifiedTab.find("a").text(inputValue);
                //Change the path/ID of the Tab object and the editor tab
                list.getElementByPath(treeClickedElement).setPath(elementPath + inputValue);
                modifiedTab.attr("id",elementPath + inputValue);
                //if act change the editor mode (coloration)
                if(act) autoChange(elementPath + inputValue);
              }
              (debug?console.log("moved : " + ret + "\n________________________________________\n"):null);
              generateTree();
              highlightTree();
          });
          break;
        default: //in case of new file and new dir
          var url = treeClickedElement + '/' + $(".inputAddFile")[0].value ;
          createNewElement(url,mode);
          break;
      }
      $("#dialog").dialog('close');
}

    /**
    * On modification in the editor
    */
    $('.ace_text-input').bind('input', function() {
        list.getActiveTab().modified = true;
        updateModifiedTab();
    });
    $('.ace_text-input').keydown(function(e) {
        if (e.keyCode === 8 || e.keyCode === 46){
            (debug?console.warn("Merge the two function \"on modification\""):null);
            list.getActiveTab().modified = true;
            updateModifiedTab();
        }
    });
}

sakura.operator.onready(function(){
    init();
    generateTree();
    openOperator();
});

// open the operator.py
function openOperator(){
    if($(".jstree-leaf[data-path='operator.py'] a")[0] != undefined){
      openFile($(".jstree-leaf[data-path='operator.py'] a")[0]);
    }
    else{setTimeout(openOperator,100);}
}
