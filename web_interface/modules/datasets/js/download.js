//Code started by Michael Ortega for the LIG
//October, 16th, 2017


function sleep(milliseconds) {
  var start = new Date().getTime();
  for (var i = 0; i < 1e7; i++) {
    if ((new Date().getTime() - start) > milliseconds){
      break;
    }
  }
}

function datasets_upload_ask_for_rows(dataset_id, chunk_index, chunk_size, results) {
    sakura.common.ws_request('get_rows_from_table', [dataset_id, chunk_index*chunk_size, (chunk_index+1)*chunk_size], {}, function (result) {
        if (result.length > 0 && result.length == chunk_size) {
            results = results.concat(result);
            chunk_index += 1;
            datasets_upload_ask_for_rows(dataset_id, chunk_index, chunk_size, results);
        }
        else {
            var headers = []
            var dataset = $.grep(database_infos.tables, function(e){ return e.table_id == dataset_id; })[0];
            dataset.columns.forEach( function(column) {
                headers.push(column[0].toString());
            });
            var txt = Papa.unparse({    delimiter: ",", 
                                        header: true,
                                        fields: headers,
                                        data: results
                                    });
            
            //Create a link from downloading the file
            var element = document.createElement('a');
            element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(txt));
            element.setAttribute('download', dataset.name+'.csv');
            element.style.display = 'none';
            document.body.appendChild(element);
            element.click();
            document.body.removeChild(element);
        }
    });
}


function dataset_download(dataset_id) {
    file_text = "";
    
    var results = [];
    var chunk_size = 50;
    var chunk_index = 0;
    var stop        = false;
    var wait        = false;
    
    datasets_upload_ask_for_rows(dataset_id, chunk_index, chunk_size, results);
}

