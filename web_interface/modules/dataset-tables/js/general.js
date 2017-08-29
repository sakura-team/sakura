//Code started by Michael Ortega for the LIG
//August, 22nd, 2017


function not_yet() {
    alert("not yet implemented");
}


function recover_tables() {
    var dataset_id = window.location.search.substr(1).split("=")[1];
    console.log("WLOC", window.location);
    console.log("DDDDDDDD", dataset_id);
    sakura.common.ws_request('get_dataset_info', [parseInt(dataset_id)], {}, function (result) {
        var body = $('#table_of_dataset_tables').find('tbody');
        body.empty();
        result['tables'].forEach( function(table) {
            body.append('<tr>   <td>'+table['label']+'</td><td>'+table['short_description']+'</td> \
                                <td align="right"> \
                                    <span title="Upload data in this table" class="glyphicon glyphicon-upload" style="cursor: pointer;" onclick="dataset_table_upload('+dataset_id+','+table['id']+');"> </span> \
                                    <span title="Download the table" class="glyphicon glyphicon-download" style="cursor: pointer;" onclick="dataset_table_download('+dataset_id+','+table['id']+');"> </span> \
                                    <span>&nbsp</span> \
                                    <span title="Look at the table" class="glyphicon glyphicon-eye-open" style="cursor: pointer;" onclick="dataset_table_look_at('+dataset_id+','+table['id']+');"></span> \
                                    <span title="Analytics" class="glyphicon glyphicon-info-sign" style="cursor: pointer;" onclick="dataset_table_analytics('+dataset_id+','+table['id']+');"></span> \
                                    <span>&nbsp</span> \
                                    <span title="delete" class="glyphicon glyphicon-remove" style="cursor: pointer;" onclick="dataset_table_delete('+dataset_id+','+table['id']+');"></span> \
                                </td>\
                        </tr>');
        });
    });
}


function new_dataset_table() {
}


function dataset_table_upload(dataset_id, table_id) {
    not_yet();
}


function dataset_table_download(dataset_id, table_id) {
    not_yet();
}

function dataset_table_look_at(dataset_id, table_id) {
    not_yet();
}


function dataset_table_analytics(dataset_id, table_id) {
    not_yet();
}


function dataset_table_delete(dataset_id, table_id) {
    not_yet();
}
