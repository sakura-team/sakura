function newopselect(json) {
       $.getJSON("/operator/register/OWSakuraSelect", function(json) {
           var op_id = json['op_id'];
           $('#result').html(
                $('#result').html() + '<br\>' +
                'server: created a new Select operator with id ' + op_id);
       });
}
