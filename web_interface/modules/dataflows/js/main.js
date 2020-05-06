//Code started by Michael Ortega for the LIG
//October 10th, 2016


/////////////////////////////////////////////////////////
//Init Functions
var jsPlumbLoaded = false;

function open_dataflow() {
    if (! jsPlumbLoaded)
      $.getScript("/webcache/cdnjs/jsPlumb/2.1.7/jsPlumb.min.js").done( function() {
          jsPlumbLoaded = true;
          jsPlumb_init();
          current_dataflow();
      });
    else
        current_dataflow();
}

function jsPlumb_init() {

    //console.log(jsPlumb);
    ///////////////DEFAULTS
    jsPlumb.importDefaults({
        PaintStyle : { lineWidth : 4, strokeStyle : "#333333" },
        MaxConnections : 100,
        Endpoint : ["Dot", {radius:6, zindex:20}],
        EndpointStyle : { fillStyle:"black" },
        Container: "sakura_main_div"
    });


    ///////////////LINKS EVENTS
    //This piece of code is for preventing two or more identical links
    jsPlumb.bind("beforeDrop", function(params) {
        var found = link_exist(params.sourceId, params.targetId);

        //we test the link existence from our side
        if (found == true) {
            console.log("link already exists !");
            return false;
        }

        //here we validate the jsPlumb link creation
        return true;
    });

    jsPlumb.bind("beforeDetach", function(params) {
        //We do nothing here !!!
    });

    //A connection is established
    jsPlumb.bind("connection", function(params) {
        //link creation on hub and other
        if (global_dataflow_jsFlag)
            create_link( params.connection.id,
                                parseInt(params.sourceId.split("_")[2]),
                                parseInt(params.targetId.split("_")[2]),
                                params.connection );
    });

    //When the target of a link changes
    jsPlumb.bind("connectionMoved", function(params) {
    });

    //On double click we open the link parameters
    jsPlumb.bind("dblclick", function(connection) {
        open_link_params(connection.id);
    });

    //Context Menu is one of the ways for deleting the link
    jsPlumb.bind("contextmenu", function(params, e) {
        e.preventDefault();
        $('#sakura_link_contextMenu').css({
            display: "block",
            left: e.clientX,
            top: e.clientY
        });
        link_focus_id = link_from_id(params.id);
    });
}
