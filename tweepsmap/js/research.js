var hideR = false;

function hideResearch(){
    if(hideR ==true){
        document.getElementById("research").style.left="-20%";
        document.getElementById("hideResearch").innerHTML='&nbsp;<i class="fa fa-angle-right" aria-hidden="true"></i>';
    }
    else {
        document.getElementById("research").style.left="0px";
        document.getElementById("hideResearch").innerHTML='&nbsp;<i class="fa fa-angle-left" aria-hidden="true"></i>';    
    }    
    hideR =!hideR;
}
