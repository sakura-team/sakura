// Michael ORTEGA for PIMLIG/LIG/CNRS- 10/12/2018

function getUrlVars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
        vars[key] = value;
    });
    return vars;
}

function getMousePos(canvas, evt) {
    var rect = canvas.getBoundingClientRect();
    return {
        x: parseInt(evt.clientX - rect.left),
        y: parseInt(evt.clientY - rect.top)
    };
}

function update_size(id) {
    var div   = document.getElementById('basicOGL_div'+id)
    var canvas= document.getElementById('basicOGL_canvas'+id)
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

function close_basicOGL() {
    console.log('unload');
}


function init_basicOGL() {

    console.log(getUrlVars()['op_id'])

    var body = document.body;
    body.setAttribute('id', 'basicOGL_body'+getUrlVars()['op_id'])
    var div = document.createElement('div');
    div.setAttribute('style', 'height:100%;');
    div.setAttribute('id', 'basicOGL_div'+getUrlVars()['op_id']);

    var canvas = document.createElement('canvas');
    canvas.setAttribute('id', 'basicOGL_canvas'+getUrlVars()['op_id']);
    canvas.setAttribute('width', 800);
    canvas.setAttribute('height', 800);

    div.appendChild(canvas);
    body.appendChild(div);

    div.addEventListener('focusout', function () {
        console.log('visibility', div.visibilityState);
    });

    ////////////////////////////////////////////////
    //MOUSE INTERACTION
    canvas.addEventListener('mousemove', function(evt) {
        var pos = getMousePos(canvas, evt);
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

    update_size(getUrlVars()['op_id']);

    //regular asking for the main image
    setInterval( function() {
    update_size(getUrlVars()['op_id']);
    
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
