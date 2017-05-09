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
                        
                        global_coms.push({  'id': global_coms.length,
                                            'div': com});
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
                        var com             = wrapper.firstChild;
                        com.style.left      = com.div.style.left;
                        com.style.top       = com.div.style.top;
                        com.style.width     = com.div.style.width;
                        com.style.height    = com.div.style.height;
                        $('#comment_'+com.id+'_title').text(com.title);
                        $('#comment_'+com.id+'_body').text(com.body);
                        com.setAttribute("draggable", "true");
                        main_div.appendChild(com);
                    }
    );
}


function comment_get_info(com) {
    return {'id': com.id,
            'title':    $('#comment_'+com.id+'_title').text(),
            'body':    $('#comment_'+com.id+'_body').text(),
            'x':        com.div.style.left,
            'y':        com.div.style.top,
            'width':    com.div.style.width,
            'height':   com.div.style.height
            };
}