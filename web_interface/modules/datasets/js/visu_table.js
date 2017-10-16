//Code started by Michael Ortega for the LIG
//October, 10th, 2017


var nb_rows     = 15; //temporary, should be put in a dom element. Soon !


function dataset_visu_table(dataset_id) {
    var dataset     = $.grep(database_infos.tables, function(e){ return e.table_id == dataset_id; })[0];
    
    //HEADER
    var header_txt  = "<h3>"+dataset.name+"</h3>";
    header_txt      += "<h8>"+dataset.description+"</h8>";
    $('#datasets_visu_header').html(header_txt);
    
    //BODY
    var head  = $('#datasets_visu_table_of_rows').find('thead');
    var body  = $('#datasets_visu_table_of_rows').find('tbody');
    head.empty()
    body.empty()
    
    //Header
    var new_h_row = $(head[0].insertRow());
    new_h_row.append("<th>#</th>");
    (dataset.columns).forEach( function (item) {
        new_h_row.append("<th>"+item[0]+"</th>");
    });
    
    //Rows
    var row_start   = 0;
    sakura.common.ws_request('get_rows_from_table', [dataset_id, row_start, row_start + nb_rows], {}, function (rows) {
        datasets_visu_table_fill_rows(body, rows, row_start, dataset);
        
        $('#datasets_visu_table_of_rows').data('row_start', row_start);
        $('#datasets_visu_table_of_rows').data('nb_rows', nb_rows);
        
        $($('#datasets_visu_table_next_top')[0].children[0]).attr('onclick', 'datasets_visu_table_next('+dataset_id+');');
        $($('#datasets_visu_table_next_bottom')[0].children[0]).attr('onclick', 'datasets_visu_table_next('+dataset_id+');');
        $($('#datasets_visu_table_previous_top')[0].children[0]).attr('onclick', 'datasets_visu_table_previous('+dataset_id+');');
        $($('#datasets_visu_table_previous_bottom')[0].children[0]).attr('onclick', 'datasets_visu_table_previous('+dataset_id+');');
        
        $('#datasets_visu_dataset_modal').modal();
    });
}


function datasets_visu_table_fill_rows(body, rows, row_start, dataset) {
    rows.forEach( function(row, index) {
        var new_b_row = $(body[0].insertRow());
        var line = "<td>"+(row_start+index)+"</td>";
        (dataset.columns).forEach( function (item, index) {
            line += "<td> data "+index+" of row "+row+"</td>";
        });
        new_b_row.append(line);
    });
}


function datasets_visu_table_previous(dataset_id) {
    var dataset     = $.grep(database_infos.tables, function(e){ return e.table_id == dataset_id; })[0];
    
    var row_start   = $('#datasets_visu_table_of_rows').data('row_start');
    var nb_rows     = $('#datasets_visu_table_of_rows').data('nb_rows');
    row_start -= nb_rows;
    
    if (row_start < 0) {
        row_start = 0;
    }
    
    sakura.common.ws_request('get_rows_from_table', [dataset_id, row_start, row_start + nb_rows], {}, function (rows) {
        var body  = $('#datasets_visu_table_of_rows').find('tbody');
        body.empty()
        
        datasets_visu_table_fill_rows(body, rows, row_start, dataset);
        
        $('#datasets_visu_table_of_rows').data('row_start', row_start);
        if (row_start == 0) {
            [$('#datasets_visu_table_previous_top'), $('#datasets_visu_table_previous_bottom')].forEach( function(li) {
                li.addClass('disabled');
                $(li[0].children[0]).css('pointer-events', 'none');
            });
        }
        if (!(rows.length < nb_rows)) {
            [$('#datasets_visu_table_next_top'), $('#datasets_visu_table_next_bottom')].forEach( function(li) {
                li.removeClass('disabled');
                $(li[0].children[0]).css('pointer-events', 'auto');
            });
        }
    });
}


function datasets_visu_table_next(dataset_id) {
    var dataset     = $.grep(database_infos.tables, function(e){ return e.table_id == dataset_id; })[0];
    
    var row_start   = $('#datasets_visu_table_of_rows').data('row_start');
    var nb_rows     = $('#datasets_visu_table_of_rows').data('nb_rows');
    row_start += nb_rows;
    
    sakura.common.ws_request('get_rows_from_table', [dataset_id, row_start, row_start + nb_rows], {}, function (rows) {
        var body  = $('#datasets_visu_table_of_rows').find('tbody');
        
        if (rows.length > 0) {
        
            body.empty()
            
            datasets_visu_table_fill_rows(body, rows, row_start, dataset);
            
            $('#datasets_visu_table_of_rows').data('row_start', row_start);
            if (row_start > 0) {
                [$('#datasets_visu_table_previous_top'), $('#datasets_visu_table_previous_bottom')].forEach( function(li) {
                    li.removeClass('disabled');
                    $(li[0].children[0]).css('pointer-events', 'auto');
                });
            }
        }
        if (rows.length < nb_rows) {
            [$('#datasets_visu_table_next_top'), $('#datasets_visu_table_next_bottom')].forEach( function(li) {
                li.addClass('disabled');
                $(li[0].children[0]).css('pointer-events', 'none');
            });
        }
    });
}
