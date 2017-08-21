//Code started by Michael Ortega for the LIG
//August, 21st, 2017


function fill_dbms() {
    //first we ask the hub the dbms
    console.log("BEFORE");
    sakura.common.ws_request('list_daemons', [], {}, function (result) {
        console.log("DURING");
        console.log(result);
    });
    console.log("AFTER");
}