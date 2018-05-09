/**
 * GLOBAL VARS
 */
 var list = new tabList();

//Ace Editor
var editor;
// do you want to display logs ?
var debug = !true;

function init(){
    editor = ace.edit("editor");
    editor.setTheme("ace/theme/xcode");
    editor.getSession().setMode("ace/mode/python");
    editor.$blockScrolling = Infinity;
    editor.setFontSize(13);

    (debug?console.log("________________________________________\n\tWelcome in the Debug mode\n"):null);
    /**
     * ON CLICK FUNCTIONS
     */

    /*On a tree element*/
    $(document).on('click', '.jstree-anchor', function() {openFile($(this)[0]);});

    /*on the tab cross*/
    $(document).on('click', '.closeTab', function() {
      // closeTab($(this)[0]);
      var tab = $(this)[0];
      if(tab.parentElement.classList.contains("modified")) {
        //ask confirmation
        canCloseTab = false;
        $("#popupMessage").html("The file <strong>"+tab.parentElement.id+"</strong> is being modified. Are you sure you want to close it ?");
        $("#popup").dialog({
            modal:  true
        });
        $("#btnConfirm").click(function() {
            $("#popup").dialog("close");
            closeTab(tab);
            $("#btnConfirm").unbind("click");
        });
        $("#btnAbort").click(function() {
            $("#popup").dialog("close");
            $("#btnAbort").unbind("click");
        });
      }
      else closeTab(tab);
    });

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
        deleteFunction($(".jstree-clicked")[0].parentElement.attributes['data-type'].value,$(".jstree-clicked")[0].parentElement.attributes['data-path'].value);
    });
    /*on pulice size change*/
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

    ////////////////////////READ ONLY
    editor.setOptions({
        readOnly: true,
        highlightActiveLine: false,
        highlightGutterLine: false
    })
    editor.renderer.$cursorLayer.element.style.opacity=0

    /*click on context menu*/
    /*$(document).on("click",".RightClickMenuElement",function(){
        //type on request
        var menuId = $(this)[0].id;
        switch(menuId){
            case 'NewFile':
                newFileFunction();
                break;
            case 'NewDir' :
                newDirFunction();
                break;
            case "delete" :
                deleteFunction(treeClickedElementType,treeClickedElement);
                break;
            case "rename" :
                $('#dialog')[0].title="Rename";
                $('#dialog').attr("title","Rename");
                $('.ui-dialog-title').html("rename");
                $('#dialogInput').val(slashRemover(treeClickedElement));
                $('.dialogButton').html("Rename");
                mode = 'rename';
                $( "#dialog" ).dialog({
                    modal:  true
                });
                break;
        }
    });*/
    /////////////////////////

    //POPUP
    /*forbidden characters in names*/
    $('#dialogInput').on("change paste keyup",function(e){
      var regex = new RegExp("^.*[/'\"]");
      var matchRegex = $(this)[0].value.search(regex) > -1;
      $(".dialogButton")[0].disabled = matchRegex;
      if(matchRegex){
        $(".dialogButton")[0].title="there's a forbidden character in the string";
        $(".dialogInput")[0].classList.add("forbiddenChar");
        $("#forbiddenCharMessage").css("display","initial");

      }
      else {
        $(".dialogButton")[0].title="click to confirm";
        if($(".dialogInput")[0].classList.contains("forbiddenChar")){
            $(".dialogInput")[0].classList.remove("forbiddenChar");
            $("#forbiddenCharMessage").css("display","none");
        }
      }
    });
    /* If the button "add file" on the pop up is clicked */
    $(document).on('click', '.dialogButton', function() {
        submitPopUp();
    });

    /*hide right click menu*/
    $(document).mouseup(function(event) {
        switch (event.which) {
            case 1:
                //Left Mouse button pressed
                $("#RightClickMenu").css("display","none");
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
    $("#dialogInput").keypress(function(e){
      if(e.which == 13){
        submitPopUp();
      }
    });

    ////////////////////////READ ONLY

    /**
    * On modification in the editor
    */

    /*$('.ace_text-input').bind('input', function() {
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
    */

    /*
    * Drag N Drop on tab
    */
    /*$( function() {
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

    });*/
    ////////////////////////READ ONLY


}

function onReady(){
    init();
    generateTree();
    openOperator();
}

// open the operator.py
function openOperator(){
    if($(".jstree-leaf[data-path='operator.py'] a")[0] != undefined){
      openFile($(".jstree-leaf[data-path='operator.py'] a")[0]);
    }
    else{
        setTimeout(openOperator,100);
    }
}
