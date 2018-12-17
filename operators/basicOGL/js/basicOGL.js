// Michael ORTEGA for PIMLIG/LIG/CNRS- 10/12/2018

function getMousePos(img, evt) {
    var rect = img.getBoundingClientRect();
    return {
        x: parseInt(evt.clientX - rect.left),
        y: parseInt(evt.clientY - rect.top)
    };
}

function close_basicOGL() {
    console.log('unload');
}

function onresize() {
    var img= document.getElementById('basicOGL_img');
    w = img.width;
    h = img.height;
    if (w <= 0 || h <= 0) {
        w = 50;
        h = 50;
    }
    console.log('onresize', img.width, img.height);
    sakura.apis.operator.fire_event("resize", {'w':w, 'h':h});
}

function init_basicOGL() {

    var img= document.getElementById('basicOGL_img')

    sakura.apis.operator.fire_event('init').then(function (init_info) {
        img.src = init_info.mjpeg_url;
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
        sakura.apis.operator.fire_event('mouse_click',
                                        {'button': evt.button, 'state': 0, 'x': pos.x, 'y': pos.y})
                                        .then( function (result) {});
    }, false);

    img.addEventListener('mouseup', function(evt) {
        evt.preventDefault();
        var pos = getMousePos(img, evt)
        sakura.apis.operator.fire_event('mouse_click',
                                        {'button': evt.button, 'state': 1, 'x': pos.x, 'y': pos.y})
                                        .then( function (result) {});
    }, false);

    img.addEventListener('contextmenu', function(evt) {
        evt.preventDefault();
    }, false);
}
