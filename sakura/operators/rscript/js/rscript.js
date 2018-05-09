//Code started by Michael Ortega for the LIG
//Started on: May the 15th, 2017

function call_script() {
    sakura.operator.fire_event(["script", document.getElementById("rscript_script").value],
        function(result) {
            document.getElementById("rscript_result").value = result.out+'\n----------------\n'+result.err;
        });
}