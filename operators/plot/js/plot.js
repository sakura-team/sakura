
PLOT_REFRESH_DELAY = 0.3

var plot_data = [];
var plot_data_bar = [];

var waiting_icon = '<span class="fa fa-cog fa-spin" style="font-size:20px; color:grey;"></span>';
var finished_icon = '<span class="fa fa-check" style="font-size:20px; color:green;"></span>';
var current_shape = 'scatter';

var main_chart = null

function update_plot(result) {

  let chunk_data = result.dp.map(t => ({'x': t[0], 'y': t[1]}));

  if (!plot_data.length)
      plot_data = chunk_data;
  else {
      Array.prototype.push.apply(plot_data, chunk_data);
  }

  main_chart = new CanvasJS.Chart("plot_div", {
      data: [{
              type: current_shape,
              dataPoints: $.extend( [], plot_data)
           }]
  });
  if (!result.done) {
      sakura.apis.operator.fire_event('continue', PLOT_REFRESH_DELAY).then(update_plot);
  }
  else {
    setTimeout(function(){
        $('#working_icon').css('display', 'none');
    }, 3000);
    $('#working_icon').html(finished_icon);
  }
  main_chart.render();
}

function init_plot() {
    $('#working_icon').html(waiting_icon);
    $('#working_icon').css('display', 'block');

    plot_data = [];
    plot_data_bar = [];
    current_shape = 'line';

    //Get data
    sakura.apis.operator.fire_event('get_data', PLOT_REFRESH_DELAY).then(
        update_plot
    );
}

function change_shape(shape){
    current_shape = shape;
    var p = plot_data;

    if (current_shape == 'bar') {
        if (plot_data_bar.length == 0) {
            plot_data.forEach ( function(p) {
                Array.prototype.push.apply(plot_data_bar, [{'x': p.y, 'y': p.x}]);
            });
        }
        p = plot_data_bar;
    }

    main_chart = new CanvasJS.Chart("plot_div", {
        data: [{
                type: current_shape,
                dataPoints: $.extend( [], p)
             }]
    });
    main_chart.render();
}
