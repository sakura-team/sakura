//Code started by Michael Ortega for the LIG
//October, 10th, 2017


var nb_rows     = 15; //temporary, should be put in a dom element. Soon !
var current_dataset_id = -1

function datasets_visu_dataset(dataset_id) {
    var dataset     = $.grep(database_infos.tables, function(e){ return e.table_id == dataset_id; })[0];
    current_dataset_id = dataset_id;
    //HEADER
    var header_txt  = "<h3>"+dataset.name+"</h3>";
    if (dataset.short_desc)
        header_txt      += "<h8>"+dataset.short_desc+"</h8>";
    else
        header_txt      += "<h8>No description found</h8>";
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
    sakura.common.ws_request('get_rows_from_table', [current_dataset_id, row_start, row_start + nb_rows], {}, function (rows) {
        datasets_visu_table_fill_rows(body, rows, row_start, dataset);

        $('#datasets_visu_table_of_rows').data('row_start', row_start);
        $('#datasets_visu_table_of_rows').data('nb_rows', nb_rows);

        if ($('#datasets_visu_table_previous_top_1')[0].className.indexOf('disabled') === -1) {
            datasets_visu_enable_disable('previous', false)
        }

        if (rows.length < nb_rows) {
            datasets_visu_enable_disable('next', false)
        }
        else {
            if ($('#datasets_visu_table_previous_top_1')[0].className.indexOf('disabled') != -1) {
                datasets_visu_enable_disable('next', true)
            }
        }

        $('#datasets_visu_dataset_modal').modal();
    });
}


function datasets_visu_table_fill_rows(body, rows, row_start, dataset) {

    var cols = dataset.columns;
    rows.forEach( function(row, r_index) {
        var new_b_row = $(body[0].insertRow());
        new_b_row.append($('<td>', {text: ''+(row_start+r_index)
                                })
                        );
        row.forEach( function(item, c_index) {
            if (this_col_is_a_date(cols[c_index])) {
                var date = moment.unix(parseInt(item));
                new_b_row.append($('<td>', {text: date._d.toLocaleString()
                                    })
                                );
            }
            else
                new_b_row.append($('<td>', {text: item
                                            })
                                );
        });
    });
}


/*function datasets_visu_table_previous(speed) {
    var dataset     = $.grep(database_infos.tables, function(e){ return e.table_id == current_dataset_id; })[0];

    var row_start   = $('#datasets_visu_table_of_rows').data('row_start');
    var nb_rows     = $('#datasets_visu_table_of_rows').data('nb_rows');
    row_start -= nb_rows;

    if (row_start < 0) {
        row_start = 0;
    }

    sakura.common.ws_request('get_rows_from_table', [current_dataset_id, row_start, row_start + nb_rows], {}, function (rows) {
        var body  = $('#datasets_visu_table_of_rows').find('tbody');
        body.empty()

        datasets_visu_table_fill_rows(body, rows, row_start, dataset);

        $('#datasets_visu_table_of_rows').data('row_start', row_start);
        if (row_start == 0) {
            [$('#datasets_visu_table_previous_top_1'), $('#datasets_visu_table_previous_bottom_1')].forEach( function(li) {
                li.addClass('disabled');
                $(li[0].children[0]).css('pointer-events', 'none');
            });
        }
        if (!(rows.length < nb_rows)) {
            [$('#datasets_visu_table_next_top_1'), $('#datasets_visu_table_next_bottom_1')].forEach( function(li) {
                li.removeClass('disabled');
                $(li[0].children[0]).css('pointer-events', 'auto');
            });
        }
    });
}
*/


function datasets_visu_table_next(speed) {
    var dataset     = $.grep(database_infos.tables, function(e){ return e.table_id == current_dataset_id; })[0];

    var row_start   = $('#datasets_visu_table_of_rows').data('row_start');
    //var nb_rows     = $('#datasets_visu_table_of_rows').data('nb_rows');

    row_start += speed*nb_rows;
    if (row_start < 0)
          row_start = 0;

    sakura.common.ws_request('get_rows_from_table', [current_dataset_id, row_start, row_start + nb_rows], {}, function (rows) {
        var body  = $('#datasets_visu_table_of_rows').find('tbody');

        if (rows.length > 0) {

            body.empty()

            datasets_visu_table_fill_rows(body, rows, row_start, dataset);

            $('#datasets_visu_table_of_rows').data('row_start', row_start);
            datasets_visu_enable_disable('next', true);
            datasets_visu_enable_disable('previous', true);

            if (row_start == 0)
                datasets_visu_enable_disable('previous', false);

            if (rows.length < nb_rows)
                datasets_visu_enable_disable('next', false);
        }
        else {
            if (row_start > 0)
                datasets_visu_enable_disable('next', false);
            else
                datasets_visu_enable_disable('previous', false);
        }
    });
}

function datasets_visu_enable_disable(type, enable) {
  [ $('#datasets_visu_table_'+type+'_top_1'),
    $('#datasets_visu_table_'+type+'_top_2'),
    $('#datasets_visu_table_'+type+'_top_3'),
    $('#datasets_visu_table_'+type+'_bottom_1'),
    $('#datasets_visu_table_'+type+'_bottom_2'),
    $('#datasets_visu_table_'+type+'_bottom_3')
    ].forEach( function(li) {
      if (enable)
        li.removeClass('disabled');
      else
        li.addClass('disabled');
      $(li[0].children[0]).css('pointer-events', 'auto');
  });
}
