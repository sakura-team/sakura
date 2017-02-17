//Code started by Denis Bouhineau for the LIG, February 2017

	
function funFun(n) {
 ws_request('list_nObjets', [10,'etude_'], {}, function (result) {
   //alert(result);
   s="<ul>"
   for(i=0;i<result.length;i++) {
     s += "<li>Etude : "+result[i].nom+", valeur :"+result[i].valeur+"</li>\n";}
   s+="</ul>"	 
   document.getElementById("dFF").innerHTML = s;
   return ;});
 return ;}

