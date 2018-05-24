//Code started by Michael Ortega for the LIG
//October, 16th, 2017

var stop_downloading  = false;
var datasets_download_chunk_size = 5000; //nb rows

function datasets_download_ask_for_rows(dataset_id, starting_date, chunk_index, chunk_size, data, nb_rows, p_bar) {

    var dataset = $.grep(database_infos.tables, function(e){ return e.table_id == dataset_id; })[0];

    if (data.length == 0) {
        var headers = []
        dataset.columns.forEach( function(column) {
            headers.push(column[0].toString());
        });

        data = 'data:text/plain;charset=utf-8,' +
                encodeURIComponent(Papa.unparse({    delimiter: ",",
                                    header: false,
                                    data: headers
                                    }) + "\n");
    }

    sakura.common.ws_request('get_rows_from_table', [dataset_id, chunk_index*chunk_size, (chunk_index+1)*chunk_size], {}, function (result) {
        if (result.length > 0 && result.length == chunk_size) {
            if (!stop_downloading) {
                data +=  encodeURIComponent(Papa.unparse({    delimiter: ",",
                                            header: false,
                                            data: result
                                            }) + "\n");

                //Filling modal
                chunk_index += 1;
                var nd = new Date();
                s =  parseInt((nd.getTime() - starting_date.getTime())/1000);
                m = parseInt(s/60);
                s = s - (m*60)
                if (!nb_rows) {
                    $('#datasets_progress_bar_modal_body').html("<p align=\"center\">"+(chunk_size*chunk_index+1)+" rows ; "+m+"min:"+s+"s</p>");
                }
                else {
                  var perc = (chunk_size*chunk_index+1)/nb_rows*100;
                  p_bar.css("width", ""+perc+"%");
                  p_bar.css("aria-valuenow", ""+perc);
                }

                //Next request
                datasets_download_ask_for_rows(dataset_id, starting_date, chunk_index, chunk_size, data, nb_rows, p_bar);
            }
            else {
                stop_downloading = false;
                $('#datasets_progress_bar_modal').modal("hide");
            }
        }
        else {
            var nd = new Date();
            /*s = parseInt((nd.getTime() - starting_date.getTime())/1000);
            m = parseInt(s/60);
            s = s - (m*60)
            $('#datasets_progress_bar_modal_body').html("<p align=\"center\">"+(chunk_size*chunk_index+1)+" rows ; "+m+"min:"+s+"s</p>");
            */

            if (result.length > 0) {
                data += encodeURIComponent(Papa.unparse({    delimiter: ",",
                                            header: false,
                                            data: result
                                            }));
            }

            //Create a link from downloading the file
            var element = document.createElement('a');
            element.setAttribute('href', data);
            element.setAttribute('download', dataset.name+'.csv');
            element.style.display = 'none';
            document.body.appendChild(element);
            element.click();
            document.body.removeChild(element);
            console.log(element);

            $('#datasets_progress_bar_modal').modal("hide");
        }
    });
}


function datasets_download(dataset_id) {

    sakura.common.ws_request('get_table_info', [dataset_id], {}, function(result) {

        var pb = null;
        $('#datasets_progress_bar_modal').modal();
        $('#datasets_progress_bar_modal_header').html("<table width=\"100%\"><tr><td><h3>Downloading ...</h3><td align=\"right\"><span class=\"glyphicon glyphicon-refresh glyphicon-refresh-animate\"></span></table>");

        if (!result.count_estimate) {
            $('#datasets_progress_bar_modal_body').html("<p align=\"center\">0 rows ; 0min:0s</p>");
        }
        else {
            $('#datasets_progress_bar_modal_body').empty();

            var pbdiv = $('<div></div>', {'id': "datasets_download_progress_bar_div",
                              'class': "progress" });

            pb = $('<div></div>', { 'id': "datasets_download_progress_bar",
                                    'class': "progress-bar progress-bar-striped progress-bar-animated bg-success",
                                    'role': "progressbar",
                                    'style': "width: 0%;",
                                    'aria-valuenow': "25",
                                    'aria-valuemin': "0",
                                    'aria-valuemax': "100"
                                  });

            pb.appendTo(pbdiv);
            pbdiv.appendTo($('#datasets_progress_bar_modal_body'));
        }

        datasets_download_ask_for_rows(dataset_id, new Date(), 0, datasets_download_chunk_size, [], result.count_estimate, pb);

    });
}

function datasets_stop_downloading() {
    stop_downloading = true;
}
