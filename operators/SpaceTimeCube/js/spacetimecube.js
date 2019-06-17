// Michael ORTEGA for PIMLIG/LIG/CNRS- 10/12/2018

var nb_trajectories = 0;

function display_loading(val) {
    var l = [ $('#loading_back_image')[0], $('#loading_div')[0]  ];

    l.forEach( function(elt) {
        elt.style.display = val;
    });
}

function display_info(val) {
    var l  = [$('#info_div')[0],      $('#time_start_div')[0],
              $('#time_end_div')[0],  $('#time_inter_div')[0],
              $('#main_navbar')[0]]

    l.forEach(function(elt) {
      elt.style.display = val;
    });
}

function init() {
    if (navigator.userAgent.indexOf("Chrome") == -1 ) {
        //Not a Chrome browser
        display_info('none');
    }
    else {
        $('#not_Chrome_message')[0].style.display = 'none';

        //Chrome browser
        opengl_app = sakura.apis.operator.attach_opengl_app(0, 'ogl-div');
        opengl_app.subscribe_event('hovered_gps_point', function(evt, tim, lng, lat, ele, tname) {
            var idiv = $('#info_div');
            idiv.empty();
            if (tim != -1) {
                var t = moment.unix(parseInt(tim))._d.toUTCString();
                idiv.append("<b>"+tname+" - </b>"+t+"<b> - lng:</b> "+lng.toFixed(4)+"<b> - lat: </b>"+lat.toFixed(4)+"<b> - ele: </b>"+parseInt(ele));
            }
            else {
                idiv.append("...");
                var inter_div = $('#time_inter_div')[0];
                inter_div.style.bottom   = ''+100000+'px';
            }
        });

        opengl_app.subscribe_event('times_and_positions', function(evt, times) {
            var sta = $('#time_start_div')[0];
            var end = $('#time_end_div')[0];
            var int = $('#time_inter_div')[0];
            var ts = [sta, end, int];

            times.forEach( function(t, i) {
                ts[i].style.left   = ''+t['x']+'px';
                ts[i].style.bottom   = ''+t['y']+'px';
                var d = moment.unix(t['time'])._d.toUTCString();
                d = d.replace(' GMT', '');
                d = d.substring(5);
                ts[i].children[0].innerHTML = d;
            });
        });

        opengl_app.subscribe_event('loading_data_start', function(evt) {
            display_loading('block');
            display_info('none');
        });

        opengl_app.subscribe_event('loading_data_end', function(evt) {
            display_loading('none');
            display_info('block');
        });

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
          var butt_hid = $('<button class="btn btn-default btn-xs" onclick=\'check_trajectory(-1);\'>hide all</button>&nbsp;');
          var butt_sho = $('<button class="btn btn-default btn-xs" onclick=\'check_trajectory(-2);\'>show all</button>');
          butt_hid.innerHTML = 'hide all';
          var table = $('<table width = 100%>');
          //table.append("<tr><td><input type='checkbox' checked id='traj_checkbox_all' onclick='check_trajectory(-1);'></td><td>All</td></tr>");
          result.forEach( function(traj, index) {
              table.append("<tr><td><input type='checkbox' checked id='traj_checkbox_"+index+"' onclick='check_trajectory("+index+");'></td><td>"+traj+"</td></tr>");
          });
          tdd.append(butt_hid);
          tdd.append(butt_sho);
          tdd.append(table);
        });


        var val = document.getElementById('darkness_range').value/100;
        sakura.apis.operator.fire_event("floor_darkness", {'value': val});

        var val = document.getElementById('height_range').value/100;
        sakura.apis.operator.fire_event("cube_height", {'value': val});

        $('#wiggle_checkbox').prop('checked', false);
        $('#wiggle_checkbox').change(function () {
            var wcbv = $('#wiggle_checkbox').is(":checked");
            sakura.apis.operator.fire_event("wiggle", {'value': wcbv});
        });
        sakura.apis.operator.fire_event("wiggle", {'value': false});
    }
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

    var l = [index];
    var func = "hide_trajectories"

    //only one trajectory
    if (index != -1 && index != -2) {
        if ($('#traj_checkbox_'+index).is(":checked"))
            func = "show_trajectories"
    }
    //hide all trajectories
    else {
        var val = false;
        if (index == -2) {
            val = true;
            func = "show_trajectories";
        }
        l = []
        for (var i=0; i< nb_trajectories;i++) {
              $('#traj_checkbox_'+i).each(function(){ this.checked = val; });
              l.push(i);
        }
    }
    sakura.apis.operator.fire_event(func, {'value': l});

}
