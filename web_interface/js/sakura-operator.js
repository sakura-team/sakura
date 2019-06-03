//Code started by Etienne Dublé for the LIG
//February 16th, 2017

var MOUSE_REPORTING_RATE = 20; // updates per sec
var mouse_prev_date = Date.now()/1000.;

sakura.internal.get_operator_interface = function () {
    // parse the operator instance id from the page url
    var url_path = window.location.pathname;

    if(url_path!=null){
        sakura.internal.debug('sakura-operator.js init...');

        /* parse url to get the operator instance */
        var op_id = this.get_op_id_from_url(url_path);
        /* return the hub API remote object */
        return sakura.apis.hub.operators[op_id]
    }
    else {
        console.error('url_path is null!');
    }
};

sakura.internal.get_op_id_from_url = function (url) {
    var op_id;
    var match= url.match(/opfiles\/([0-9]*)\//);

    if(match!=null){
        /* if url of type .../opfile/[1-9]/[1-9] */
        op_id = parseInt(match[1],10);

    }else{
        /* if url of type .../code-editor/index.html?[1-9] */
        var url_path2 = window.location.href;
        var op_match =url_path2.split("/");
        if(op_match[op_match.length-2]=="code-editor"){
            var op_match2 =op_match[op_match.length-1].split("?");
            var op_id2 = op_match2[1];
            op_id=parseInt(op_id2);
        }
    }
    return op_id;
};

sakura.internal.get_mouse_pos = function(elem, evt) {
    var rect = elem.getBoundingClientRect();
    return {
        x: parseInt(evt.clientX - rect.left),
        y: parseInt(evt.clientY - rect.top)
    };
}

sakura.internal.video = {

    /* If we continue appending fragments without releasing older ones,
       we will get a memory exception.
       We implement hysteris to avoid calling sourceBuffer removal function
       too often (thus the min & max constants below).
       Caution with value of OBSOLETE_FRAGMENT_TIMEOUT_MIN:
       sourceBuffer.remove() will not only remove the selected timerange,
       if will also remove all dependant frames (up to the next keyframe).
       So the input video should not have too long periods between keyframes.
       Use this to check:
       $ ffprobe -loglevel error -skip_frame nokey -select_streams v:0 \
            -show_entries frame=pkt_pts_time -of csv=print_section=0 f.mp4
    */
    OBSOLETE_FRAGMENT_TIMEOUT_MAX: 15.0,
    OBSOLETE_FRAGMENT_TIMEOUT_MIN: 10.0,
    // given by http://download.tsi.telecom-paristech.fr/gpac/mp4box.js/filereader.html
    VIDEO_MIMETYPE: 'video/mp4; codecs="avc1.64000c"; profiles="isom,iso2,avc1,iso6,mp41"',

    bufferUpdate: function(context) {
        if (context.sourceBuffer == null) {
            return; // not ready yet
        }
        // if sourceBuffer is already being updated,
        // wait until we are recalled by event onupdateend.
        if (context.sourceBuffer.updating) {
            return;
        }
        // append next pending chunk if any
        if (context.pendingChunks.length > 0) {
            let chunk = context.pendingChunks.shift();
            context.sourceBuffer.appendBuffer(chunk);
            return;
        }
        // check if at least one chunk was buffered
        let buffered = context.sourceBuffer.buffered;
        if (buffered.length > 0 && buffered.end(0) > 0)
        {
            //console.log(buffered.start(0), buffered.end(0), context.video.currentTime);
            // start playing as soon as first chunk is buffered
            if (context.video.paused) {
                context.video.play();
            }

            // adapt playback rate
            if (context.bufferEnd != null && buffered.end(0) > context.bufferEnd) {
                let rate = (buffered.end(0) - context.video.currentTime) /
                                 (buffered.end(0) - context.bufferEnd);
                if (rate > 4.0) {
                    rate = 4.0;
                }
                context.video.playbackRate = rate;
                //console.log('rate', context.video.playbackRate);
            }
            context.bufferEnd = buffered.end(0); // for next time

            // free memory about obsolete fragments
            let start = buffered.start(0);
            let end = context.video.currentTime;
            if (end - start > sakura.internal.video.OBSOLETE_FRAGMENT_TIMEOUT_MAX) {
                //console.log('release', start, end - sakura.internal.video.OBSOLETE_FRAGMENT_TIMEOUT_MIN);
                context.sourceBuffer.remove(start, end - sakura.internal.video.OBSOLETE_FRAGMENT_TIMEOUT_MIN);
            }
        }
    },

    readLoop: function(context) {
        context.reader.read().then(({ done, value }) => {
            // When no more data needs to be consumed, exit
            if (done) {
              console.log('END OF STREAM');
              context.sourceBuffer.onupdateend = null;
              context.video.pause();
              context.ending_cb();
              return;
            }
            // Enqueue the chunk into our target stream
            //console.log(value.length, context.pendingChunks.length, '+1 chunk')
            context.pendingChunks.push(value);
            sakura.internal.video.bufferUpdate(context);
            sakura.internal.video.readLoop(context); // recurse
        });
    },

    stream_video: function(video, url) {
        let context = { video: video };
        context.mediaSource = new MediaSource();
        context.video.src = window.URL.createObjectURL(context.mediaSource);
        context.video.muted = true;
        context.pendingChunks = [];
        context.sourceBuffer = null;
        context.bufferEnd = null;
        context.mediaSource.addEventListener('sourceopen', function() {
            context.sourceBuffer = context.mediaSource.addSourceBuffer(sakura.internal.video.VIDEO_MIMETYPE);
            context.sourceBuffer.onupdateend = function() {
                sakura.internal.video.bufferUpdate(context);
            };
        });
        // Start fetching the video as a stream
        fetch(url).then(response => {
            context.reader = response.body.getReader();
            context.ending_cb = function(){ stream_video(video, url); };    // restart when disconnected
            sakura.internal.video.readLoop(context);
        });
    }
};

sakura.apis.operator = sakura.internal.get_operator_interface();

sakura.apis.operator.attach_opengl_app = function (opengl_app_id, div_id) {

    let div= document.getElementById(div_id);
    let video= document.createElement("video");
    div.appendChild(video);
    let remote_app = sakura.apis.operator.opengl_apps[opengl_app_id];
    let clicked_buttons = 0;
    let masks = { 'NONE': 0, 'LEFT_CLICKED': 1, 'RIGHT_CLICKED': 4, 'LEFT_OR_RIGHT_CLICKED': 5 };
    video.addEventListener('contextmenu', function(evt) {
        evt.preventDefault();
    }, false);
    video.addEventListener('error', function(e){
        console.error("video element error", e);
    });

    remote_app.info().then(function (app_info) {
        let mouse_move_reporting = app_info.mouse_move_reporting;

        let reconnect = function() {
            // some video codecs require width and height to be even
            let width = div.clientWidth - div.clientWidth % 2;
            let height = div.clientHeight - div.clientHeight % 2;
            if (width <= 0 || height <= 0) {
                // size is not correct yet, wait for next resize event.
                return;
            }
            console.log('reconnect', width, height);
            video.style.width = width + "px";
            video.style.height = height + "px";
            let url = eval('`' + app_info.video_url_pattern + '`');
            sakura.internal.video.stream_video(video, url);
        }

        // when the window is resized, reconnect to get appropriate video size.
        window.addEventListener('resize', reconnect);

        // MOUSE INTERACTION
        let report_move = function(evt) {
            var pos = sakura.internal.get_mouse_pos(video, evt);
            var t = Date.now()/1000.;
            if ((t - mouse_prev_date) >= 1/MOUSE_REPORTING_RATE) {
                mouse_prev_date = t;
                remote_app.fire_event('on_mouse_motion', pos.x, pos.y);
            }
            else {
                console.log('dropped event');
            }
        };

        let update_mouse_reports = function() {
            let should_activate;
            if (mouse_move_reporting == 'ALWAYS') {
                should_activate = 1;
            }
            else {
                let mask = masks[mouse_move_reporting];
                should_activate = clicked_buttons & mask;
            }
            if (should_activate > 0) {
                video.onmousemove = report_move;
            }
            else {
                video.onmousemove = null;
            }
        };

        video.addEventListener('mousedown', function(evt) {
            evt.preventDefault();
            var pos = sakura.internal.get_mouse_pos(video, evt)
            remote_app.fire_event('on_mouse_click', evt.button, 0, pos.x, pos.y);
            clicked_buttons += Math.pow(2, evt.button);
            update_mouse_reports();
        }, false);

        video.addEventListener('mouseup', function(evt) {
            evt.preventDefault();
            var pos = sakura.internal.get_mouse_pos(video, evt)
            remote_app.fire_event('on_mouse_click', evt.button, 1, pos.x, pos.y);
            clicked_buttons -= Math.pow(2, evt.button);
            update_mouse_reports();
        }, false);

        video.addEventListener('wheel', function(evt) {
            evt.preventDefault();
            remote_app.fire_event('on_wheel', evt.deltaY);
        }, false);

        // initialize
        update_mouse_reports();
        reconnect();
    });
    return remote_app;
}
