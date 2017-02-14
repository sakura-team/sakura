require_external_css('https://unpkg.com/leaflet@1.0.3/dist/leaflet.css');
require_external_js('https://unpkg.com/leaflet@1.0.3/dist/leaflet.js');

function init_tab(container, op) {
    var markers = op.get_stream('Markers');
    console.log("Container", container);
    //$(div).css('height': '400px');
    
    var label = $('<label>vide</label>');
    container.append(label);
    
    container.append($('<button>Test</button>').click(function () { 
        op.fire_event("toto", function(result) {
            markers.get_range(0, 1000, function (stream) {
                label.text(stream);
            });
        }); 
    }));
}
