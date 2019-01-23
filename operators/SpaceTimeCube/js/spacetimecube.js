// Michael ORTEGA for PIMLIG/LIG/CNRS- 10/12/2018

function init() {
    sakura.apis.operator.attach_opengl_app(0, 'ogl-img');
    sakura.apis.operator.fire_event("onload");

    var btn = document.getElementById('wiggle_btn');
    btn.onclick=function(e) {
        sakura.apis.operator.fire_event("wiggle");
    }

    var val = document.getElementById('darkness_range').value/100;
    sakura.apis.operator.fire_event("floor_darkness", {'value': .5});
}

function floor_darkness() {
    var val = document.getElementById('darkness_range').value/100;
    sakura.apis.operator.fire_event("floor_darkness", {'value': val});
}
