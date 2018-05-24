
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
    sakura.operator.fire_event(
            ['get_data'],
            update_plot);
}
