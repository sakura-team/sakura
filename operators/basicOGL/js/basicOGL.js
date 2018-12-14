// Michael ORTEGA for PIMLIG/LIG/CNRS- 10/12/2018

function getUrlVars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
        vars[key] = value;
    });
    return vars;
}

function getMousePos(img, evt) {
    var rect = img.getBoundingClientRect();
    return {
        x: parseInt(evt.clientX - rect.left),
        y: parseInt(evt.clientY - rect.top)
    };
}

function update_size() {
    var div   = document.getElementById('basicOGL_div')
    var img= document.getElementById('basicOGL_img')
    w = div.getBoundingClientRect().width;
    h = div.getBoundingClientRect().height;
    if (w != img.width || h != img.height) {
        if (w <= 0 || h <= 0) {
            w = 50;
            h = 50;
        }
        img.width = w;
        img.height = h;
        sakura.apis.operator.fire_event("resize", {'w':w, 'h':h}).then( function(result) {});
    }
}

function close_basicOGL() {
    console.log('unload');
}


function init_basicOGL() {

    console.log(getUrlVars()['op_id'])

    var div   = document.getElementById('basicOGL_div')
    var img= document.getElementById('basicOGL_img')

    sakura.apis.operator.fire_event('init').then(function (init_info) {
        img.src = init_info.mjpeg_url;
    });
    div.addEventListener('focusout', function () {
        console.log('visibility', div.visibilityState);
    });

    ////////////////////////////////////////////////
    //MOUSE INTERACTION
    img.addEventListener('mousemove', function(evt) {
        var pos = getMousePos(img, evt);
        sakura.apis.operator.fire_event('mouse_motion',
                                        {'x': pos.x, 'y': pos.y})
                                        .then( function (result) {});

    }, false);

    img.addEventListener('mousedown', function(evt) {
        evt.preventDefault();
        var pos = getMousePos(img, evt)
        sakura.apis.operator.fire_event('mouse_clicks',
                                        {'button': evt.button, 'state': 0, 'x': pos.x, 'y': pos.y})
                                        .then( function (result) {});
    }, false);

    img.addEventListener('mouseup', function(evt) {
        evt.preventDefault();
        var pos = getMousePos(img, evt)
        sakura.apis.operator.fire_event('mouse_clicks',
                                        {'button': evt.button, 'state': 1, 'x': pos.x, 'y': pos.y})
                                        .then( function (result) {});
    }, false);

    img.addEventListener('contextmenu', function(evt) {
        evt.preventDefault();
    }, false);

    update_size();

    //regular asking for the main image
    setInterval( function() {
    update_size();
    
    /*sakura.apis.operator.fire_event('resize', {}).then( function(result) {
            var ctx = img.getContext("2d");
            var img = new Image();
            img.src = "data:image/jpeg;base64,"+btoa(image);
            img.onload = function() {
                console.log('here2');
                cxt.drawImage(img, 0, 0);
            }
        });
      */
    }, 100);
}
