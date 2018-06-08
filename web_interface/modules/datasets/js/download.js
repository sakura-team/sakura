//Code started by Michael Ortega for the LIG
//October, 16th, 2017

var stop_downloading  = false;
var timeout = 250;
var current_transfert_id  = null;

function datasets_download(dataset_id) {

    var dataset = $.grep(database_infos.tables, function(e){ return e.table_id == dataset_id; })[0];

    var txt = 'The size of the file is unkown for now.';
    if (dataset.count_estimate)
        txt = 'This dataset has ~'+dataset.count_estimate+' rows.';

    var h = $('#datasets_download_modal_header');
    var b = $('#datasets_download_modal_body');
    var bc = $('#datasets_download_modal_button_csv');
    var bg = $('#datasets_download_modal_button_gzip');

    h.css('background-color', 'rgba(91,192,222)');
    h.html("<h3><font color=\"white\">Dataset Download</font></h3>");
    b.html("<p>"+txt+"</p>");
    bc.attr('onclick', 'datasets_download_start_transfert('+dataset_id+', false);');
    bg.attr('onclick', 'datasets_download_start_transfert('+dataset_id+', true);');

    $('#datasets_download_modal').modal();
}

function datasets_download_start_transfert(dataset_id, gzip) {

  var dataset = $.grep(database_infos.tables, function(e){ return e.table_id == dataset_id; })[0];
  stop_downloading = false;

  sakura.common.ws_request('start_transfer', [], {}, function(transfert_id) {
        current_transfert_id = transfert_id;

        var url = "/tables/"+dataset.table_id+"/export.csv?transfer="+current_transfert_id;
        if (gzip)
            url = "/tables/"+dataset.table_id+"/export.csv.gz?transfer="+current_transfert_id;

        //Create a link from downloading the file
        var element = document.createElement('a');
        element.setAttribute('href', url);
        element.setAttribute('download', dataset.name+'.csv');
        element.style.display = 'none';
        document.body.appendChild(element);

        //Get first transfert status
        sakura.common.ws_request('get_transfer_status', [current_transfert_id], {}, function(status) {
            var pb = null;
            var pb_txt = null;
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


                pb_txt = $('<div></div>', {'text': '0 rows/ 0 bytes'});
                pb_txt.css('position', 'absolute');
                pb_txt.css('text-align', 'center');
                pb_txt.css('width', '100%');

                pb.appendTo(pbdiv);
                pb_txt.appendTo(pbdiv)
                pbdiv.appendTo($('#datasets_progress_bar_modal_body'));
            }

            $('#datasets_progress_bar_modal').modal();
            datasets_download_update_feedback(dataset, pb, pb_txt, new Date());
        });

        element.click();
        document.body.removeChild(element);

    });
}

function datasets_download_update_feedback(dataset, progress_bar, progress_bar_txt, init_date) {

    sakura.common.ws_request('get_transfer_status', [current_transfert_id], {}, function(status) {
        if (status.status == 'waiting' && !stop_downloading) {
          setTimeout(function () {
              datasets_download_update_feedback(dataset, progress_bar, progress_bar_txt, init_date);
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
                var o = datasets_Giga_Mega_Kilo(status.bytes, 'bytes');
                var r = datasets_Giga_Mega_Kilo(status.rows, 'rows');

                progress_bar_txt.html(r.val+' '+r.txt+'/ '+o.val+' '+o.txt);
            }

            setTimeout(function () {
                datasets_download_update_feedback(dataset, progress_bar, progress_bar_txt, init_date);
            }, timeout);
        }
        else {
            $('#datasets_progress_bar_modal').modal('hide');
        }
    });

}

function datasets_Giga_Mega_Kilo(val, txt) {
  r = val;
  r_txt = txt;

  if (r >= 1000000000) {
      r = parseInt(r/1000000000);
      r_txt = 'G'+txt;
  }
  else if (r >= 1000000) {
    r = parseInt(r/1000000);
    r_txt = 'M'+txt;
  }
  else if (r >= 1000) {
    r = parseInt(r/1000);
    r_txt = 'K'+txt;
  }
    return {val: r, txt: r_txt};
}

function datasets_stop_downloading() {
    sakura.common.ws_request('abort_transfer', [current_transfert_id], {}, function(result) {
        stop_downloading = true;
    });
}
