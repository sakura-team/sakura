var ws = new WebSocket("ws://localhost:10433");
var recover = false;
var canvas = document.getElementById("myCanvas");
var interval_id = -1;
var mouse_move_pre_date = new Date();
var prev_moves = [];
var max_messages_per_seconds = 25;

function init_server() {
    ws.onopen = function(event) {
        console.log('Connection: open');
        refresh();
    }
    ws.onclose = function(event) {
        console.log('Connection closed');
    }
    ws.onmessage = function(event) {
        if (event.data instanceof Blob) {
            var image = new Image();
            image.src = URL.createObjectURL(event.data);

            image.onload = function() {
                var ctx = canvas.getContext("2d");
                ctx.drawImage(image,0,0);
                ctx.restore();
            }
        }
        else {
            var j = JSON.parse(event.data);
            if (j.key == 'resize') {
                send('image');
            }
            else if (j.key == 'data_directories') {
                var dirs = JSON.parse(j.value);
                for (var i in dirs) {
                  var select = document.getElementById("directories_select");
                  var option = document.createElement("option");
                  option.text = dirs[i];
                  option.value = i;
                  select.add(option);
                }
            }
            else if (j.key == 'get_trajectories') {
                fill_trajectories_dd(j.value);
            }
            else if (j.key == 'get_semantic_names') {
                fill_semantics_dd(j.value);
            }
            else if (j.key == 'set_updatable_floor') {
                send('image')
            }
            else if (j.key == 'darkness') {
                send('image');
            }
            else if(j.key == 'select_semantic') {
                send('image');
            }
            else if (j.key == 'dates') {
                update_dates(j.value);
            }
            else if (['click',
                      'move',
                      'wheel',
                      'hide_trajectories',
                      'show_trajectories',
                      'wiggle',
                      'dates',
                      'reset_zoom'].indexOf(j.key) < 0) {
                console.log('Unknown answer:', j);
            }
            else {
                send('dates');
                send('image');
            }
        }
        return;
    }
    $('#wiggle_checkbox').change(function () {
        var wcbv = $('#wiggle_checkbox').is(":checked");
        send('wiggle', [wcbv]);
        if (wcbv) {
            interval_id = setInterval(function(){send('image');}, 50);
        }
        else {
            clearInterval(interval_id);
        }
    });

    $('#dynamic_floor_checkbox').change(function () {
        var wcbv = $('#dynamic_floor_checkbox').is(":checked");
        send('set_updatable_floor', [wcbv]);
    });

    refresh()
}

function refresh() {
    $('#wiggle_checkbox').prop('checked', false);
    send('wiggle', [false]);

    $('#dynamic_floor_checkbox').prop('checked', false);
    send('set_updatable_floor', [false])

    send('get_trajectories');
    send('get_semantic_names');
    canvas.width = 800;
    canvas.height = 600;
    send('resize', [canvas.width, canvas.height]);
    send('reset_zoom');
}

function fill_trajectories_dd(trajs) {
    nb_trajectories = trajs.length;
    var tdd = $('#trajectories_dropdown');
    var butt_hid = $('<button class="btn btn-default btn-xs" onclick=\'check_trajectory(-1);\'>hide all</button>&nbsp;');
    var butt_sho = $('<button class="btn btn-default btn-xs" onclick=\'check_trajectory(-2);\'>show all</button>');
    butt_hid.innerHTML = 'hide all';
    var table = $('<table width = 100%>');

    trajs.forEach( function(traj, index) {
        table.append("<tr><td><input type='checkbox' checked id='traj_checkbox_"+index+"' onclick='check_trajectory("+index+");'></td><td>"+traj+"</td></tr>");
    });

    tdd.append(butt_hid);
    tdd.append(butt_sho);
    tdd.append(table);
}

function check_trajectory(index) {
    var l = [index];
    var func = "hide_trajectories"

    //only one trajectory
    if (index != -1 && index != -2) {
        if ($('#traj_checkbox_'+index).is(":checked"))
            func = "show_trajectories"
    }
    //all trajectories
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
    console.log(func);
    send(func, [l]);
}

function fill_semantics_dd(sems){
    var sdd = $('#semantic_dropdown');
    var table = $('<table width = 100%>');
    sems.forEach( function(sem, index) {
      table.append("<tr><td><button onclick='select_semantic("+index+");'>"+sem+"</button>");
    })
    sdd.append(table);
}

function select_semantic(index) {
    send('select_semantic', [index])
}

function send(key, data) {
    var message = { "key": key, 'data': data};
    ws.send(JSON.stringify(message));
}

function getMousePos(canvas, evt) {
    var rect = canvas.getBoundingClientRect();
    return {
        x: parseInt(evt.clientX - rect.left),
        y: parseInt(evt.clientY - rect.top)
    };
}

function tile_type() {
    select = document.getElementById('tile_type_select');
    send('tile', [select.options[select.selectedIndex].value]);
}

function floor_darkness() {
    var val = document.getElementById('darkness_range').value/100;
    send('darkness', [val]);
}

function select_dir() {
    var select = document.getElementById("directories_select");
    send('data_directory', [select.options[select.selectedIndex].text])
    darkness();
}

function update_dates(times) {
  var sta = $('#time_start_div')[0];
  var end = $('#time_end_div')[0];
  var int = $('#time_inter_div')[0];
  var ts = [sta, end, int];

  ts.forEach( function(t, i) {
      t.style.left   = ''+times[i]['x']+'px';
      var navbar_h = $('#navbar').height();
      var canvas_h = $('#myCanvas').height();
      var h = navbar_h + canvas_h - times[i]['y']
      t.style.top   = ''+h+'px';
      var d = moment.unix(times[i]['time'])._d.toUTCString();
      d = d.replace(' GMT', '');
      d = d.substring(5);
      t.children[0].innerHTML = d;
  });
}

function full_screen() {
    canvas.width = $(window).width();
    canvas.height = $(window).height();
    send('resize', [$(window).width(), $(window).height()]);
}
canvas.addEventListener('mousemove', function(evt) {
    var d = Date.now();
    if ((d - mouse_move_pre_date)/1000 > 1/max_messages_per_seconds) {
        var pos = getMousePos(canvas, evt);
        send('move', [pos.x, pos.y]);
        mouse_move_pre_date = d
    }
}, false);

canvas.addEventListener('mousedown', function(evt) {
    evt.preventDefault();
    var button = 'right';
    var pos = getMousePos(canvas, evt);
    send('click', [evt.button, 0, pos.x, pos.y]);
}, false);

canvas.addEventListener('mouseup', function(evt) {
    evt.preventDefault();
    var button = 'right';
    var pos = getMousePos(canvas, evt);
    send('click', [evt.button, 1, pos.x, pos.y]);
}, false);

canvas.addEventListener('contextmenu', function(evt) {
    evt.preventDefault();
}, false);

canvas.addEventListener('wheel', function(evt) {
    evt.preventDefault();
    send('wheel', [evt.deltaY]);
}, false);
