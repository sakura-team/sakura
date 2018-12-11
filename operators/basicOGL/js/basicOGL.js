// Michael ORTEGA for PIMLIG/LIG/CNRS- 10/12/2018

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

    update_size();

    //regular asking for the main image
    /*
    setInterval( function() {
    sakura.apis.operator.fire_event("image", {}).then( function(image) {

            var ctx = canvas.getContext("2d");

            console.log('here1');

            var img = new Image();
            img.src = "data:image/jpeg;base64,"+btoa(image);
            console.log(img.src);
            img.onload = function() {
                console.log('here2');
                cxt.drawImage(img, 0, 0);
            }

            update_size();
        });
    }, 100);
    */
}


//Global
var canvas = document.getElementById("basicOGL_canvas");


////////////////////////////////////////////////
//MOUSE INTERACTION
function getMousePos(canvas, evt) {
    var rect = canvas.getBoundingClientRect();
    return {
        x: parseInt(evt.clientX - rect.left),
        y: parseInt(evt.clientY - rect.top)
    };
}

canvas.addEventListener('mousemove', function(evt) {
    var pos = getMousePos(canvas, evt);
    //send('move', [pos.x, pos.y]);
    //console.log('move', [pos.x, pos.y]);

}, false);

canvas.addEventListener('mousedown', function(evt) {
    evt.preventDefault();
    var button = 'right';
    if (evt.button == 0)      {button = 'left';}
    else if (evt.button == 1) {button = 'middle';}
    console.log('click', [button, 'down']);
}, false);

canvas.addEventListener('mouseup', function(evt) {
    evt.preventDefault();
    var button = 'right';
    if (evt.button == 0)      {button = 'left';}
    else if (evt.button == 1) {button = 'middle';}
    //send('click', [button, 'up']);
    console.log('click', [button, 'up']);
}, false);

canvas.addEventListener('contextmenu', function(evt) {
    evt.preventDefault();
}, false);
