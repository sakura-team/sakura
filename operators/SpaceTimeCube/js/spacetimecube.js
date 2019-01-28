// Michael ORTEGA for PIMLIG/LIG/CNRS- 10/12/2018

function init() {
    sakura.apis.operator.attach_opengl_app(0, 'ogl-img');

    sakura.apis.operator.fire_event("onload").then( function(result) {
      var tdd = $('#trajectories_dropdown')
      console.log(tdd);
      result.forEach( function(traj, index) {
            var nli = $('<li>');
            var na = $("<a onclick='select_trajectory("+index+");'>"+traj+"</a>");
            na.css('cursor', 'pointer');
            nli.append(na);
            tdd.append(nli);
        });
    });

    var val = document.getElementById('darkness_range').value/100;
    sakura.apis.operator.fire_event("floor_darkness", {'value': val});

    var val = document.getElementById('height_range').value/100;
    sakura.apis.operator.fire_event("cube_height", {'value': val});

    $('#wiggle_checkbox').prop('checked', true);
    $('#wiggle_checkbox').change(function () {
        var wcbv = $('#wiggle_checkbox').is(":checked");
        sakura.apis.operator.fire_event("wiggle", {'value': wcbv});
    });
    sakura.apis.operator.fire_event("wiggle", {'value': true});
}

function floor_darkness() {
    var val = document.getElementById('darkness_range').value/100;
    sakura.apis.operator.fire_event("floor_darkness", {'value': val});
}

function cube_height() {
    var val = document.getElementById('height_range').value/100;
    sakura.apis.operator.fire_event("cube_height", {'value': val});
}


function select_trajectory(id) {
    console.log(id);
}
