
function update_plot(data) {
  var chart = new CanvasJS.Chart("plot_div", {
       data: [{
              type: "scatter",
              dataPoints: data.dp
           }]
  });
  chart.render();
}

function init_plot() {

    //Get data
    sakura.apis.operator.fire_event('get_data').then(update_plot);
}
