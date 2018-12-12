// Michael ORTEGA for PIMLIG/LIG/CNRS- 10/12/2018

//Global
var canvas = null;

function getMousePos(canvas, evt) {
    var rect = canvas.getBoundingClientRect();
    return {
        x: parseInt(evt.clientX - rect.left),
        y: parseInt(evt.clientY - rect.top)
    };
}

function update_size() {
    var div = document.getElementById('basicOGL_div');
    w = div.getBoundingClientRect().width;
    h = div.getBoundingClientRect().height;
    if (w != canvas.width || h != canvas.height) {
        if (w <= 0 || h <= 0) {
            w = 50;
            h = 50;
        }
        canvas.width = w;
        canvas.height = h;
        sakura.apis.operator.fire_event("resize", {'w':w, 'h':h}).then( function(result) {});
    }
}

function init_basicOGL() {
    canvas = document.getElementById("basicOGL_canvas");

    ////////////////////////////////////////////////
    //MOUSE INTERACTION
    canvas.addEventListener('mousemove', function(evt) {
        var pos = getMousePos(canvas, evt);
        //send('move', [pos.x, pos.y]);
        //console.log('move', [pos.x, pos.y]);
        sakura.apis.operator.fire_event('mouse_motion',
                                        {'x': pos.x, 'y': pos.y})
                                        .then( function (result) {});

    }, false);

    canvas.addEventListener('mousedown', function(evt) {
        evt.preventDefault();
        var pos = getMousePos(canvas, evt)
        sakura.apis.operator.fire_event('mouse_clicks',
                                        {'button': evt.button, 'state': 0, 'x': pos.x, 'y': pos.y})
                                        .then( function (result) {});
    }, false);

    canvas.addEventListener('mouseup', function(evt) {
        evt.preventDefault();
        var pos = getMousePos(canvas, evt)
        sakura.apis.operator.fire_event('mouse_clicks',
                                        {'button': evt.button, 'state': 1, 'x': pos.x, 'y': pos.y})
                                        .then( function (result) {});
    }, false);

    canvas.addEventListener('contextmenu', function(evt) {
        evt.preventDefault();
    }, false);

    update_size();


    //regular asking for the main image
    setInterval( function() {
    update_size();
    /*sakura.apis.operator.fire_event('resize', {}).then( function(result) {
            var ctx = canvas.getContext("2d");
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
