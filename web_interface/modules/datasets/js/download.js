//Code started by Michael Ortega for the LIG
//October, 16th, 2017

var stop_downloading  = false;

function datasets_download_ask_for_rows(dataset_id, starting_date, chunk_index, chunk_size, results) {
    sakura.common.ws_request('get_rows_from_table', [dataset_id, chunk_index*chunk_size, (chunk_index+1)*chunk_size], {}, function (result) {
        if (result.length > 0 && result.length == chunk_size) {
            if (!stop_downloading) {
                results = results.concat(result);
                chunk_index += 1;
                var nd = new Date();
                s =  parseInt((nd.getTime() - starting_date.getTime())/1000);
                m = parseInt(s/60);
                s = s - (m*60)
                $('#datasets_progress_bar_modal_body').html("<p align=\"center\">"+(chunk_size*chunk_index+1)+" rows ; "+m+"min:"+s+"s</p>");
                datasets_download_ask_for_rows(dataset_id, starting_date, chunk_index, chunk_size, results);
            }
            else {
                stop_downloading = false;
                $('#datasets_progress_bar_modal').modal("hide");
            }
        }
        else {
            var nd = new Date();
            s =  parseInt((nd.getTime() - starting_date.getTime())/1000);
            m = parseInt(s/60);
            s = s - (m*60)
            $('#datasets_progress_bar_modal_body').html("<p align=\"center\">"+(chunk_size*chunk_index+1)+" rows ; "+m+"min:"+s+"s</p>");

            if (result.length > 0)
                results = results.concat(result);
            var headers = []
            var dataset = $.grep(database_infos.tables, function(e){ return e.table_id == dataset_id; })[0];
            dataset.columns.forEach( function(column) {
                headers.push(column[0].toString());
            });
            var txt = Papa.unparse({    delimiter: ",",
                                        header: true,
                                        fields: headers,
                                        data: results
                                    });
            //Create a link from downloading the file
            var element = document.createElement('a');
            element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(txt));
            element.setAttribute('download', dataset.name+'.csv');
            element.style.display = 'none';
            document.body.appendChild(element);
            element.click();
            document.body.removeChild(element);

            $('#datasets_progress_bar_modal').modal("hide");
        }
    });
}


function datasets_download(dataset_id) {
    file_text = "";

    var results = [];
    var chunk_size = 5000; //nb rows
    var chunk_index = 0;

    $('#datasets_progress_bar_modal').modal();
    $('#datasets_progress_bar_modal_header').html("<table width=\"100%\"><tr><td><h3>Downloading ...</h3><td align=\"right\"><span class=\"glyphicon glyphicon-refresh glyphicon-refresh-animate\"></span></table>");
    $('#datasets_progress_bar_modal_body').html("<p align=\"center\">0 rows ; 0min:0s</p>");
    datasets_download_ask_for_rows(dataset_id, new Date(), chunk_index, chunk_size, results);
}

function datasets_stop_downloading() {
    stop_downloading = true;
}
