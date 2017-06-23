function TweetsmapOperatorInterface(){

    this.op_id = 1;

    this.init = function() {
        op = this;
        ws_request("list_operators_instance_ids",[], {}, function(result){
            // if we haven't created any operators, create it, 
            // so that if op_id != null, it should be 1
            // if(result.length == 0)  {
            //     op.create_operator_instance(1);
            //     op.create_operator_instance(3);
            //     var start = new Date().getTime();
            //     op.create_link(2,1);
            // }
            console.log(result);
            if(op._on_ready_cb != null){
                op._on_ready_cb();
            }
        });
    }

    this.create_link = function(id1, id2) {
        ws_request("create_link", [id1, 0, id2, 0], {}, function(result){
            console.log("ok");
        });
    };

    this.create_operator_instance = function(cls_id){
        ws_request("create_operator_instance",[cls_id],{},function(result){
            op.op_id = result.id;
        });
    };

    this.fire_event = function(event, cb) {
        console.log(this.op_id);
        ws_request("fire_operator_event", [this.op_id, event], {}, cb);
    };

    this.onready = function(cb) {
        this.init();
        if (this.op_id != null){
            cb();
        } else {
            this._on_ready_cb = cb;
        }
    };

}

tweetsmap = {
    operator: new TweetsmapOperatorInterface()
}

