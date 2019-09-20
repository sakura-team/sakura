
PLOT_REFRESH_DELAY = 0.3

var plot_data = []

function update_plot(result) {

  if (!plot_data.length)
      plot_data = result.dp;
  else {
      Array.prototype.push.apply(plot_data, result.dp);
  }

  var chart = new CanvasJS.Chart("plot_div", {
      data: [{
              type: "scatter",
              dataPoints: plot_data
           }]
  });
  if (!result.done) {
      sakura.apis.operator.fire_event('continue', PLOT_REFRESH_DELAY).then(update_plot);
  }
  else {
      console.log('done');
  }
  chart.render();
}

function init_plot() {
    //Get data
    sakura.apis.operator.fire_event('get_data', PLOT_REFRESH_DELAY).then(
        update_plot
    );
}
