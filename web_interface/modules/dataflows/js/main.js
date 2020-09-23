//Code started by Michael Ortega for the LIG
//October 10th, 2016


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
    ///////////////DEFAULTS
    jsPlumb.importDefaults({
        PaintStyle : { lineWidth : 3, strokeStyle : "#333333" },
        MaxConnections : 100,
        Endpoint : ["Dot", {radius:6, zindex:20}],
        EndpointStyle : { fillStyle:"black" },
        Container: "sakura_main_div"
    });


    ///////////////LINKS EVENTS
    //This piece of code is for preventing two or more identical links
    jsPlumb.bind("beforeDrop", function(connection) {
        var found = link_exist( parseInt(connection.sourceId.split("_")[2]),
                                parseInt(connection.targetId.split("_")[2]));
        //we test the link existence from our side
        if (found == true) {
            console.log("link already exists !");
            jsPlumb.detach(connection);
            jsPlumb.repaintEverything();
            return false;
        }
        //here we validate the jsPlumb link creation
        return true;
    });

    // jsPlumb.bind("connectionDragStop", function (connection) {
    //     console.log('CONN_DRAG_STOP');
    // });

    //A connection is established
    jsPlumb.bind("connection", function(conn) {
        //link creation on hub and other
        //link existence is tested with 'beforeDrop' event
        if (global_dataflow_jsFlag) {
                create_link(  conn.connection,
                              parseInt(conn.sourceId.split("_")[2]),
                              parseInt(conn.targetId.split("_")[2])   );
        }
    });

    //When the target of a link changes
    jsPlumb.bind("connectionMoved", function(params) {
    });

    jsPlumb.bind("beforeDetach", function (e) {
        if (LOG_INTERACTION_EVENT) {console.log('BEFORE DETACH');}
        //return false; //WARNING !!! Keep this for avoiding deleting connections
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
