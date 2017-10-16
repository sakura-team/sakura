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
            console.log(results);
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
    
    //Create a link from downloading the file
    var element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent('col1,col2\nval1,val2\nval3,val4'));
    element.setAttribute('download', 'test_download.csv');
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

