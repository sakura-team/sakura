var hideC = false;

function hideConsultation(){
    if(hideC==true){
        document.getElementById("consultation").style.right="-40%";
        document.getElementById("hideConsultation").innerHTML='<i class="fa fa-angle-left" aria-hidden="true"></i>';
    }
    else {
        document.getElementById("consultation").style.right="0px";
        document.getElementById("hideConsultation").innerHTML='<i class="fa fa-angle-right" aria-hidden="true"></i>';    
    }    
    hideC=!hideC;
}
