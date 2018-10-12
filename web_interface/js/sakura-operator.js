//Code started by Etienne Dublé for the LIG
//February 16th, 2017

sakura.internal.get_operator_interface = function () {
    // parse the operator instance id from the page url
    var url_path = window.location.pathname;

    if(url_path!=null){
        sakura.internal.debug('sakura-operator.js init...');

        /* parse url to get the operator instance */
        var op_id = this.get_op_id_from_url(url_path);
        /* return the hub API remote object */
        return sakura.apis.hub.operators[op_id]
    }
    else {
        console.error('url_path is null!');
    }
};

sakura.internal.get_op_id_from_url = function (url) {
    var op_id;
    var match= url.match(/opfiles\/([0-9]*)\//);

    if(match!=null){
        /* if url of type .../opfile/[1-9]/[1-9] */
        op_id = parseInt(match[1],10);

    }else{
        /* if url of type .../code-editor/index.html?[1-9] */
        var url_path2 = window.location.href;
        var op_match =url_path2.split("/");
        if(op_match[op_match.length-2]=="code-editor"){
            var op_match2 =op_match[op_match.length-1].split("?");
            var op_id2 = op_match2[1];
            op_id=parseInt(op_id2);
        }
    }
    return op_id;
};

sakura.apis.operator = sakura.internal.get_operator_interface()

