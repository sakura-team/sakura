var stop_downloading  = false;
var timeout = 250;
var current_transfert_id  = null;

function giga_mega_kilo(val, txt) {
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

function stop_download() {
    push_request('transfers_abort');
    sakura.apis.hub.transfers[current_transfert_id].abort().then(function(result) {
        pop_request('transfers_abort');
        stop_downloading = true;
    });
}

function download_start_transfert(object) {
    //Get first transfert status
    push_request('transfers_get_status');
    sakura.apis.hub.transfers[current_transfert_id].get_status().then(function(status) {
        pop_request('transfers_get_status');
        let pb = null;
        let pb_txt = null;
        $('#'+object+'s_progress_bar_modal_header').html("<table width=\"100%\"><tr><td><h3>Downloading ...</h3><td align=\"right\"><span class=\"glyphicon glyphicon-refresh glyphicon-refresh-animate\"></span></table>");

        if (status.percent == -1)
            $('#'+object+'s_progress_bar_modal_body').html("<p align=\"center\">0 rows ; 0min:0s</p>");
        else {
            $('#'+object+'s_progress_bar_modal_body').empty();

            let pbdiv = $('<div></div>', {'id': object+"s_download_progress_bar_div",
                              'class': "progress" });

            pb = $('<div></div>', { 'id': object+"s_download_progress_bar",
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
            pbdiv.appendTo($('#'+object+'s_progress_bar_modal_body'));
        }

        $('#'+object+'s_progress_bar_modal').modal();
        download_update_feedback(object, pb, pb_txt, new Date());
    });
}

function download_update_feedback(object, progress_bar, progress_bar_txt, init_date) {

    push_request('transfers_get_started');
    sakura.apis.hub.transfers[current_transfert_id].get_status().then(function(status) {
        pop_request('transfers_get_started');
        if (status.status == 'waiting' && !stop_downloading) {
          setTimeout(function () {
              download_update_feedback(object, progress_bar, progress_bar_txt, init_date);
          }, timeout);
        }
        else if (status.status != 'done' && !stop_downloading) {
            if (status.percent == -1) {
                let nd = new Date();
                s =  parseInt((nd.getTime() - init_date.getTime())/1000);
                m = parseInt(s/60);
                s = s - (m*60)
                $('#'+object+'s_progress_bar_modal_body').html("<p align=\"center\">"+status.rows+" rows ; "+m+"min:"+s+"s</p>");
            }
            else {
                let o = giga_mega_kilo(status.bytes, 'bytes');
                let r = giga_mega_kilo(status.rows, 'rows');

                progress_bar_txt.html(r.val+' '+r.txt+'/ '+o.val+' '+o.txt);
                progress_bar.css("width", ""+status.percent+"%");
                progress_bar.css("aria-valuenow", ""+status.percent);
            }

            setTimeout(function () {
                download_update_feedback(object, progress_bar, progress_bar_txt, init_date);
            }, timeout);
        }
        else {
            $('#'+object+'s_progress_bar_modal').modal('hide');
        }
    });
}
