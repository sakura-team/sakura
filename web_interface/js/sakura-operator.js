//Code started by Etienne Dublé for the LIG
//February 16th, 2017

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

sakura.internal.get_mouse_pos = function(img, evt) {
    var rect = img.getBoundingClientRect();
    return {
        x: parseInt(evt.clientX - rect.left),
        y: parseInt(evt.clientY - rect.top)
    };
}

sakura.apis.operator = sakura.internal.get_operator_interface();

sakura.apis.operator.attach_opengl_app = function (opengl_app_id, img_id) {

    let img= document.getElementById(img_id);
    let remote_app = sakura.apis.operator.opengl_apps[opengl_app_id];
    let clicked_buttons = 0;
    let masks = { 'NONE': 0, 'LEFT_CLICKED': 1, 'RIGHT_CLICKED': 4, 'LEFT_OR_RIGHT_CLICKED': 5 };
    img.addEventListener('contextmenu', function(evt) {
        evt.preventDefault();
    }, false);

    remote_app.info().then(function (app_info) {
        let mouse_move_reporting = app_info.mouse_move_reporting;

        let reconnect = function() {
            img.src = app_info.mjpeg_url;
        }

        remote_app.subscribe_event('browser_disconnect', reconnect);

        // RESIZE EVENTS
        let do_resize = function(evt) {
            w = img.width;
            h = img.height;
            if (w <= 0 || h <= 0) {
                w = 50;
                h = 50;
            }
            console.log('opengl_resize', w, h);
            return remote_app.fire_event('on_resize', w, h);
        };
        window.addEventListener('resize', do_resize);

        // MOUSE INTERACTION
        let report_move = function(evt) {
            var pos = sakura.internal.get_mouse_pos(img, evt);
            remote_app.fire_event('on_mouse_motion', pos.x, pos.y);
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
                img.onmousemove = report_move;
            }
            else {
                img.onmousemove = null;
            }
        };

        img.addEventListener('mousedown', function(evt) {
            evt.preventDefault();
            var pos = sakura.internal.get_mouse_pos(img, evt)
            remote_app.fire_event('on_mouse_click', evt.button, 0, pos.x, pos.y);
            clicked_buttons += Math.pow(2, evt.button);
            update_mouse_reports();
        }, false);

        img.addEventListener('mouseup', function(evt) {
            evt.preventDefault();
            var pos = sakura.internal.get_mouse_pos(img, evt)
            remote_app.fire_event('on_mouse_click', evt.button, 1, pos.x, pos.y);
            clicked_buttons -= Math.pow(2, evt.button);
            update_mouse_reports();
        }, false);

        img.addEventListener('wheel', function(evt) {
            evt.preventDefault();
            remote_app.fire_event('on_wheel', evt.deltaY);
        }, false);

        // initialize
        update_mouse_reports();
        do_resize().then(reconnect);
    });
    return remote_app;
}
