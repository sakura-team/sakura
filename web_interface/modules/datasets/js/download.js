//Code started by Michael Ortega for the LIG
//October, 16th, 2017

var stop_downloading  = false;
var timeout = 250;
var current_transfert_id  = null;

function datasets_download(dataset_id) {

    var dataset = $.grep(database_infos.tables, function(e){ return e.table_id == dataset_id; })[0];
    stop_downloading = false;

    sakura.common.ws_request('start_transfer', [], {}, function(transfert_id) {
        current_transfert_id = transfert_id;
        var url = "/tables/"+dataset.table_id+"/export.csv?transfer="+current_transfert_id;

        //Create a link from downloading the file
        var element = document.createElement('a');
        element.setAttribute('href', url);
        element.setAttribute('download', dataset.name+'.csv');
        element.style.display = 'none';
        document.body.appendChild(element);

        //Get first transfert status
        sakura.common.ws_request('get_transfer_status', [current_transfert_id], {}, function(status) {
            var pb = null;
            $('#datasets_progress_bar_modal_header').html("<table width=\"100%\"><tr><td><h3>Downloading ...</h3><td align=\"right\"><span class=\"glyphicon glyphicon-refresh glyphicon-refresh-animate\"></span></table>");

            if (status.percent == -1)
                $('#datasets_progress_bar_modal_body').html("<p align=\"center\">0 rows ; 0min:0s</p>");
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
            $('#datasets_progress_bar_modal').modal();
            datasets_download_update_feedback(dataset, pb, new Date());
        });

        element.click();
        document.body.removeChild(element);

    });
}

function datasets_download_update_feedback(dataset, progress_bar, init_date) {
    sakura.common.ws_request('get_transfer_status', [current_transfert_id], {}, function(status) {
        if (status.status == 'waiting' && !stop_downloading) {
          setTimeout(function () {
              datasets_download_update_feedback(dataset, progress_bar, init_date);
          }, timeout);
        }
        else if (status.status != 'done' && !stop_downloading) {
            if (status.percent == -1) {
                var nd = new Date();
                s =  parseInt((nd.getTime() - init_date.getTime())/1000);
                m = parseInt(s/60);
                s = s - (m*60)
                $('#datasets_progress_bar_modal_body').html("<p align=\"center\">"+status.rows+" rows ; "+m+"min:"+s+"s</p>");
            }
            else {
                progress_bar.css("width", ""+status.percent+"%");
                progress_bar.css("aria-valuenow", ""+status.percent);
            }

            setTimeout(function () {
                datasets_download_update_feedback(dataset, progress_bar, init_date);
            }, timeout);
        }
        else {
            $('#datasets_progress_bar_modal').modal('hide');
        }
    });

}

function datasets_stop_downloading() {
    sakura.common.ws_request('abort_transfer', [current_transfert_id], {}, function(result) {
        stop_downloading = true;
    });
}
