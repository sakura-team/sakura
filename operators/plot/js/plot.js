
PLOT_REFRESH_DELAY = 0.3

var plot_data = []

var waiting_icon = '<span class="fa fa-cog fa-spin" style="font-size:20px; color:grey;"></span>';
var finished_icon = '<span class="fa fa-check" style="font-size:20px; color:green;"></span>';
var current_shape = 'scatter';

var main_chart = null

function update_plot(result) {

  if (!plot_data.length)
      plot_data = result.dp;
  else {
      Array.prototype.push.apply(plot_data, result.dp);
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

    //Get data
    sakura.apis.operator.fire_event('get_data', PLOT_REFRESH_DELAY).then(
        update_plot
    );
}

function change_shape(shape){
    current_shape = shape;
    main_chart = new CanvasJS.Chart("plot_div", {
        data: [{
                type: current_shape,
                dataPoints: $.extend( [], plot_data )
             }]
    });
    main_chart.render();
}
