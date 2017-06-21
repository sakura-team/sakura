function create_operator_instance(id){
    ws_request("create_operator_instance",[id],{},function(result){
        Console.log(result.id);
        return result.id;
    });
}

function remove_operator_instance_T(id){
    ws_request("delete_operator_instance",[id],{},function(result){
        Console.log(result.id);        
    });
}

var operators = [];

create_operator_instance(1);

