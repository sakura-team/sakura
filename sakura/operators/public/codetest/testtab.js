
function padding(n)
{
    if (n == 0)
        return '';
    return '&nbsp;' + padding(n-1);
}

function print_dir(entries, depth)
{
    for (var i = 0; i < entries.length; i++) {
        var entry = entries[i];
        $('#ft').append(padding(4*depth) + ' ' + entry.name + '<br>');
        if (entry.is_dir) {
            print_dir(entry.dir_entries, depth+1);
        }
    }
}

function print_file_tree(entries)
{
    // entries obtained with sakura.operator.get_file_tree()
    // are either:
    // - a directory:     { 'name': <dirname>,
    //                      'is_dir': true,
    //                      'dir_entries': [ <entry>, <entry>, <entry>, ... ]
    //                    }
    // - a regular file:  { 'name': <filename>,
    //                      'is_dir': false
    //                    }
    // recursively, directory entries follow the same format.
    $('#ft').html(''); // remove previous content
    print_dir(entries, 0);
}

function print_icon_file_content(content)
{
    $('#fc').text(content);
}

function do_test() {
    // print file tree
    sakura.operator.get_file_tree(print_file_tree);
    // print icon.svg file content
    sakura.operator.get_file_content('icon.svg', print_icon_file_content);
}

sakura.operator.onready(do_test);

