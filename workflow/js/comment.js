//Code started by Michael Ortega for the LIG
//May 9th, 2017

function context_new_comment() {
    $('#sakura_main_div_contextMenu').css({visibility: "hidden"});
    new_comment();
}


function new_comment() {
    var wrapper = document.createElement('div');
    var id = global_coms.length
                    
    load_from_template(
                    wrapper,
                    "comment.html",
                    {'id': id},
                    function () {
                        var com         = wrapper.firstChild;
                        com.style.left  = ''+(cursorX - main_div.offsetLeft - 90)+'px';
                        com.style.top   = ''+(cursorY - main_div.offsetTop)+'px';
                        com.setAttribute("draggable", "true");
                        main_div.appendChild(com);
                        
                        global_coms.push({  'id': id,
                                            'div': com});
                        save_project();
                    }
    );
}


function comment_from(com) {
    var wrapper = document.createElement('div');
    load_from_template(
                    wrapper,
                    "comment.html",
                    {'id': com.id},
                    function () {
                        var ncom             = wrapper.firstChild;
                        ncom.style.left      = com.left;
                        ncom.style.top       = com.top;
                        ncom.style.width     = com.width;
                        ncom.style.height    = com.height;
                        $('#comment_'+ncom.id+'_title').text(com.title);
                        $('#comment_'+ncom.id+'_body').text(com.body);
                        ncom.setAttribute("draggable", "true");
                        main_div.appendChild(ncom);
                        
                        global_coms.push({  'id': parseInt(com.id),
                                            'div': ncom});
                    }
    );
}


function get_comment_info(com) {
    return {'id': com.id,
            'title':    $('#comment_'+com.id+'_title').text(),
            'body':    $('#comment_'+com.id+'_body').text(),
            'left':        com.div.style.left,
            'top':        com.div.style.top,
            'width':    com.div.style.width,
            'height':   com.div.style.height
            };
}


function remove_comment(id) {
    main_div.removeChild(com_from_id(id).div);
    global_coms.splice(index_from_comment_id(id), 1);
    save_project();
}


function index_from_comment_id(id) {
    return global_coms.findIndex( function (e) {
        return e.id === id;
    });
}


function com_from_id(id) {
    return global_coms.find( function (e) {
        return e.id === id;
    });
}


