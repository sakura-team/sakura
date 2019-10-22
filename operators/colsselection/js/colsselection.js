var main_data = { 'headers': ['col1', 'col2', 'col3', 'col4'],
                  'rows': [ ['A','B','C',0],
                            ['D','E','F',1],
                            ['G','H','I',2],
                            ['J','K','L',3]]}

var selected_columns = [];

function init() {
  sakura.apis.operator.fire_event('get_data', 0.0).then( fill_table );
}

function fill_table(result) {

    main_data = result;
    var thead = $('#main_table_head');
    var tbody = $('#main_table_body');
    thead.empty();
    tbody.empty();

    //HEAD
    main_data.headers.forEach( function(key, index){
        var th = $('<th>', {'html': '<font color="black">'+key+'</font>',
                            'onclick': 'select_col('+index+')',
                            'style': 'cursor: pointer; text-align: center;',
                            'bgcolor': 'lightgrey'});
        th.data('selected', false);
        thead.append(th);
    });

    //BODY
    main_data.rows.forEach( function(row){
        var tr = $('<tr>');
        row.forEach( function (elt, index) {
            var td = $('<td>', {'html': '<font color="black">'+elt+'</font>',
                                'onclick': 'select_col('+index+')',
                                'style': 'cursor: pointer; text-align: center; padding: 0px;'});
            tr.append(td);
        });
        tbody.append(tr);
    });

    if (result.more) {
      var tr = $('<tr>');
      main_data.headers.forEach( function (elt, index) {
          var td = $('<td>', {'html': '...',
                              'onclick': 'select_col('+index+')',
                              'style': 'cursor: pointer; text-align: center; padding: 0px;'});
          tr.append(td);
      });
      tbody.append(tr);
    }

    if (result.selected.length != 0)
        result.selected.forEach( function(col) {
             select_col(col)
        });
}

function select_col(col) {
    var tbody = $('#main_table_body');
    var th = $($('#main_table_head').children()[col]);
    th.data('selected', !th.data('selected'));

    if (selected_columns.indexOf(col) == -1) {
        selected_columns.push(col);
    }
    else {
        var i = selected_columns.indexOf(col);
        selected_columns.splice (i, 1);
    }

    if (th.data('selected')) {
        th.attr('bgcolor', '#4285F4');
        th[0].innerHTML = th[0].innerHTML.replace('black', 'white');

        for (var i=0; i<tbody[0].children.length; i++) {
            var cell = $(tbody[0].children[i].cells[col]);
            cell.attr('bgcolor', '#4285F4');
            cell[0].innerHTML = cell[0].innerHTML.replace('black', 'white');
        }
    }
    else {
        th.attr('bgcolor', 'lightgrey');
        th[0].innerHTML = th[0].innerHTML.replace('white', 'black');

        for (var i=0; i<tbody[0].children.length; i++) {
            var cell = $(tbody[0].children[i].cells[col]);
            cell.attr('bgcolor', 'white');
            cell[0].innerHTML = cell[0].innerHTML.replace('white', 'black');
        }
    }
    sakura.apis.operator.fire_event('set_cols', 0.0, {'cols': selected_columns});
}
