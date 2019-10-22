var main_data = { 'col1': ['A', 'B', 'C'],
                  'col2': ['D', 'E', 'F'],
                  'col3': ['G', 'H', 'I']}

function init() {
    var thead = $('#main_table_head');
    var tbody = $('#main_table_body');
    thead.empty();
    tbody.empty();

    //HEAD
    Object.keys(main_data).forEach( function(key, index){
        var th = $('<th>', {'html': '<font color="black">'+key+'</font>',
                            'onclick': 'select_col(\''+key+'\','+index+')',
                            'style': 'cursor: pointer;',
                            'bgcolor': 'white'});
        th.data('selected', false);
        thead.append(th);
    });

    //BODY
    Object.keys(main_data).forEach( function(key){
        var tr = $('<tr>');
        main_data[key].forEach( function (elt) {
            var td = $('<td>', {'html': '<font color="black">'+elt+'</font>'});
            tr.append(td);
        });
        tbody.append(tr);
    });
}

function select_col(key, index) {
    var tbody = $('#main_table_body');
    var th = $($('#main_table_head').children()[index]);
    th.data('selected', !th.data('selected'));

    if (th.data('selected')) {
        th.attr('bgcolor', '#4285F4');
        th[0].innerHTML = th[0].innerHTML.replace('black', 'white');

        for (var i=0; i<tbody[0].children.length; i++) {
            var cell = $(tbody[0].children[i].cells[index]);
            cell.attr('bgcolor', '#4285F4');
            cell[0].innerHTML = cell[0].innerHTML.replace('black', 'white');
        }
    }
    else {
        th.attr('bgcolor', 'white');
        th[0].innerHTML = th[0].innerHTML.replace('white', 'black');

        for (var i=0; i<tbody[0].children.length; i++) {
            var cell = $(tbody[0].children[i].cells[index]);
            cell.attr('bgcolor', 'white');
            cell[0].innerHTML = cell[0].innerHTML.replace('white', 'black');
        }
    }


}
