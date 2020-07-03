//Code started by Michael Ortega for the LIG
//November 14th, 2016

//main
var main_div = document.getElementById('sakura_main_div');
var cursorX;
var cursorY;


instances_waiting_for_creation = [];
waiting_gui = null;

document.onmousemove = function(e){
    cursorX = e.pageX;
    cursorY = e.pageY;
}


function not_yet(s = '') {
    if (s == '')
        alert('Not implemented yet');
    else
        alert('Not implemented yet: '+ s);
}


//send the index of the row where arr[row][col] == e
function index_in_array_of_tuples(arr, col, e) {
    for (var i = 0; i< arr.length; i++)
        if (arr[i][col] == e)
            return i;
    return -1;
}


function tuple_in_array_of_tuples(arr, tuple) {
    for (var i = 0; i< arr.length; i++) {

        var is_the_one = true;
        for (var j = 0; j< tuple.length; j++)
            if (arr[i][j] != tuple[j])
                is_the_one = false;

        if (is_the_one)
            return i;
    }
    return -1;
}

function svg_round_square(id) {
    return '<svg width="24" height="24" viewBox="0 0 24 24" id="'+id+'" name="'+id+'"> \
                <rect x="2" y="2" width="20" height="20" rx="4" ry="4" \
                    style="fill: grey; stroke: black; stroke-width: 2"/> \
            </svg>';
}


function svg_round_square_crossed(id) {
    return '<svg width="24" height="24" viewBox="0 0 24 24" id="'+id+'" name="'+id+'"> \
                <rect x="2" y="2" width="20" height="20" rx="4" ry="4" \
                    style="fill: grey; stroke: black; stroke-width: 2"/> \
                <line x1="3" y1="3" x2="21" y2="21" \
                    style="fill: grey; stroke: black; stroke-width: 2"/> \
                <line x1="3" y1="21" x2="21" y2="3" \
                    style="fill: grey; stroke: black; stroke-width: 2"/> \
            </svg>';
}


function escapeHtml(text) {
    return text.replace(/[\"&<>]/g, function (a) {
        return { '"': '&quot;', '&': '&amp;', '<': '&lt;', '>': '&gt;' }[a];
    });
}


function load_from_template(elem, template_file, params, cb) {
    $(elem).load("/modules/dataflows/templates/" + template_file, { 'params': JSON.stringify(params) }, cb);
}


function s_sleep(milliseconds) {
    var start = new Date().getTime();
    for (var i = 0; i < 1e7; i++) {
        if ((new Date().getTime() - start) > milliseconds){
            break;
        }
    }
}

function dataflows_download_table(id_out, in_out) {
    var h     = $('#dataflows_download_modal_header');
    var bcsv  = $('#dataflows_download_modal_button_csv');
    var bgzip = $('#dataflows_download_modal_button_gzip');

    h.css('background-color', 'rgba(91,192,222)');
    if (in_out == 'output')
        h.html('<h3><font color="white">Downloading</font> '+current_instance_info.outputs[id_out].label+'</h3>');
    else
        h.html('<h3><font color="white">Downloading</font> '+current_instance_info.inputs[id_out].label+'</h3>');

    bcsv.attr('onclick', 'dataflows_download_start_transfert('+id_out+', \''+in_out+'\', false);');
    bgzip.attr('onclick', 'dataflows_download_start_transfert('+id_out+', \''+in_out+'\',true);');

    $('#dataflows_download_modal').modal('show');
}

function dataflows_download_start_transfert(id_in_out, in_out, gzip) {

    stop_downloading = false;
    sakura.apis.hub.transfers.start().then(function(transfert_id) {

        current_transfert_id = transfert_id;

        var url = "/streams/"+current_instance_info.op_id+"/"+in_out+"/"+id_in_out+"/export.csv?transfer="+current_transfert_id;
        if (gzip)
            url = "/streams/"+current_instance_info.op_id+"/"+in_out+"/"+id_in_out+"/export.csv.gz?transfer="+current_transfert_id;

        //Create a link from downloading the file
        var element = document.createElement('a');
        element.setAttribute('href', url);
        if (in_out == 'output')
            element.setAttribute('download', current_instance_info.outputs[id_in_out].label+'.csv');
        else
            element.setAttribute('download', current_instance_info.inputs[id_in_out].label+'.csv');
        element.style.display = 'none';
        document.body.appendChild(element);

        download_start_transfert('dataflow');

        element.click();
        document.body.removeChild(element);
    });
}
