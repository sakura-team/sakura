/**
 * GLOBAL VARS
 */
 var list = new tabList();


//Ace Editor
var editor = ace.edit("editor");
editor.setTheme("ace/theme/xcode");
editor.getSession().setMode("ace/mode/python");
editor.$blockScrolling = Infinity;
editor.setFontSize(13);

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
        if($(".jstree-clicked")[0].parentElement.attributes['data-type'].value == "dir")
            $("#popupMessage").html("Are you sure you want to delete the folder <strong>"+$(".jstree-clicked")[0].parentElement.attributes['data-path'].value+"</strong> and its content ?");
        else {
            $("#popupMessage").html("Are you sure you want to delete the file <strong>"+$(".jstree-clicked")[0].parentElement.attributes['data-path'].value+"</strong> ?");
        }
        $("#popup").dialog({
            modal:  true
        });
        $("#btnConfirm").click(function() {
            $("#popup").dialog("close");
            removeElement($(".jstree-clicked")[0].parentElement.attributes['data-path'].value);
            $("#btnConfirm").unbind("click");
        });
        $("#btnAbort").click(function() {
            $("#popup").dialog("close");
            $("#btnAbort").unbind("click");
        });
    });
    $(document).on('change', '#selectFontSize', function() {
            var size = $("#selectFontSize").val();
            editor.setOptions({
                fontSize: size + "pt"
            });
            (debug?console.log(size):null);
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
                if(treeClickedElementType == "dir")
                    $("#popupMessage").html("Are you sure you want to delete the folder <strong>"+treeClickedElement+"</strong> and its content ?");
                else {
                    $("#popupMessage").html("Are you sure you want to delete the file <strong>"+treeClickedElement+"</strong> ?");
                }
                $("#popup").dialog({
                    modal:  true
                });
                $("#btnConfirm").click(function() {
                    $("#popup").dialog("close");
                    removeElement(treeClickedElement);
                    $("#btnConfirm").unbind("click");
                });
                $("#btnAbort").click(function() {
                    console.log("close");
                    $("#popup").dialog("close");
                    $("#btnAbort").unbind("click");
                });
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
          var elementPath =  treeClickedElement.slice(0,treeClickedElement.indexOf(slashRemover(treeClickedElement)));
          //name part of the element (exemple.ex)
          var inputValue = $(".inputAddFile")[0].value;
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
              (debug?console.log("renamed \n________________________________________\n"):null);
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

    /**
    * Drag N Drop on tab
    */
    $( function() {
        var oldPos, newPos;
        $( "#tabList" ).sortable({
            start: function (event, ui) {
                oldPos = ui.item.index();
            },
            revert: true,
            update: function( event, ui ) {
                var selectedId = ui.item[0].attributes["id"].value;
                newPos = ui.item.index();
                (debug?console.log("Moved item : " + selectedId + " - Old Pos : " + oldPos + " - New position: " + newPos):null);
                list.changePos(list.getIndexByPath(selectedId),newPos - oldPos);
                if($(".glyphicon-collapse-up").length>0){list.generateExpandedMenu();};
            }
        });
        $( "ul, li" ).disableSelection();

    });
    /**
    * Drag N Drop in tree
    */
    // $( function() {
    //     $( ".jstree-icon" ).draggable({
    //       stop: function() {
    //             alert("");
    //       }
    //     });
    // });

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
