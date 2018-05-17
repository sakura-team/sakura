
function update_plot(data) {
  var chart = new CanvasJS.Chart("plot_div", {
       animationEnabled: true,
       theme: "light1",
       axisY:{
           includeZero: false
          },
       data: [{
              type: "line",
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
