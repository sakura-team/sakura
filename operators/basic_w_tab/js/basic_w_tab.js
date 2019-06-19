// Michael ORTEGA for PIMLIG/LIG/CNRS - June 16th 2019

function init() {
    console.log('Init');
}

function send_event() {
    sakura.apis.operator.fire_event("add");
}
