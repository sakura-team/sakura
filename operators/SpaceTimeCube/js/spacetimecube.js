// Michael ORTEGA for PIMLIG/LIG/CNRS- 10/12/2018

var nb_trajectories = 0

function init() {
    sakura.apis.operator.attach_opengl_app(0, 'ogl-img');

    //possible map layers
    sakura.apis.operator.fire_event("get_map_layers", {}).then( function(layers) {
        var tdd = $('#maps_dropdown');
        var table = $("<table width = 100%>");
        layers.forEach( function(map) {
            table.append("<tr><td><a style='cursor: pointer;' onclick='change_map(\""+map+"\");'>"+map+"</a></td></tr>");
        });
        tdd.append(table);
    });

    sakura.apis.operator.fire_event("onload").then( function(result) {
      nb_trajectories = result.length;
      var tdd = $('#trajectories_dropdown');

      var table = $("<table width = 100%>");
      table.append("<tr><td><input type='checkbox' id='traj_checkbox_all' onclick='check_trajectory(-1);'></td><td>All</td></tr>");
      result.forEach( function(traj, index) {
          table.append("<tr><td><input type='checkbox' id='traj_checkbox_"+index+"' onclick='check_trajectory("+index+");'></td><td>"+traj+"</td></tr>");
      });
      tdd.append(table);
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

function change_map(map) {
    sakura.apis.operator.fire_event("set_map_layer", {'value': map}).then( function(result) {
        if (result)   console.log(result);
    });
}

function check_trajectory(index) {
    if (index != -1) {
        var val = $('#traj_checkbox_'+index).is(":checked");
        if (val)
            sakura.apis.operator.fire_event("select_trajectories", {'value': [index]});
        else
            sakura.apis.operator.fire_event("unselect_trajectories", {'value': [index]});
    }
    else {
        //display
        var l = [];
        for (i=0; i< nb_trajectories;i++) {
            var cb = $('#traj_checkbox_'+i);
            if ($('#traj_checkbox_all').is(':checked')) {
                cb.each(function(){ this.checked = true; });
                l.push(i);
            }
            else {
                cb.each(function(){ this.checked = false; });
                l.push(i);
            }
        }
        //sending to operator
        if ($('#traj_checkbox_all').is(':checked')) {
            sakura.apis.operator.fire_event("select_trajectories", {'value': l});
        }
        else {
            sakura.apis.operator.fire_event("unselect_trajectories", {'value': l});
        }

    }
}
