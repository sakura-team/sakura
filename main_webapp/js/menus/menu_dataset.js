/*Code started by Michael Ortega for the LIG*/
/*November 15th, 2016*/

open_datasets = [];

function create_dataset_collapse_panel(name) {
    s =  '  <div class="panel panel-default" id="panel_group_' + name + '">';
    s += '      <div class="panel-heading" style="padding: 0px;">\
                    \
                        <table width="100%" padding="0" spacing="0" cellpadding="0"> \
                            <tr> \
                            <td> <a class="btn-xs" data-toggle="collapse" href="#collapseBody'+ name +'">';
    s += '                  '+name+'</a> \
                            <td><button type="button" class="close" onclick="suppress_dataset_panel(\''+name+'\');" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button> \
                        </table>';
    s += '          \
                </div> \
                <div id="collapseBody'+ name + '" class="panel-collapse collapse">';
    s += '      </div> \
            </div>';
    
    var wrapper= document.createElement('div');
    wrapper.classList.add("panel-default");
    wrapper.innerHTML= s;
    var ndiv= wrapper.firstChild;
    return wrapper;
}

function select_data() {
    $.post(sakura_web_site+"/scripts/dataset/datasets.php", function(data, status){
        if (status == "success")
            
            //List of the datasets
            datasets = data.split("_!!_");
            
            //Creation of a modal
            h = '<table class="table table-hover"><thead><tr><th>Name of the dataset<th>Short Description</tr></thead><tbody>';
            datasets.forEach(function (d) {
                h = h +'<tr onclick="add_dataset(\''+d+'\');"><td>'+d + '<td>Blablabla and Blabla !!!';
            });
            h = h +'</tbody</table>';
            
            main_div.append(create_simple_modal('datasets_modal', 'Datasets', h));
            $('#datasets_modal').modal();
    });
}


function add_dataset(dataset) {
    if (open_datasets.indexOf(dataset) == -1) {
        open_datasets.push(dataset);
        left_div.append(create_dataset_collapse_panel(dataset));
        for (var i=0; i<ops.length; i++)
            $("#collapseBody"+ dataset).append(new_static_operator(0, i, i));
    }
}

function suppress_dataset_panel(dataset) {
    not_yet();
}