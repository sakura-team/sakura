// LIG March 2017

function showDiv(event,dir) {
  if (dir=="") {
    dir="Home";}
  var dirs = dir.split("/");
//show div
  mainDivs=document.getElementsByClassName('classMainDiv');
  for(i=0;i<mainDivs.length;i++) {
	mainDivs[i].style.display='none';}  
  var idDir = "idDiv"+dirs.join("");
  document.getElementById(idDir).style.display='inline';
//activate navbar   
  var d = document.getElementById("navbar_ul");
  for (var i=0; i< d.children.length; i++) {
    d.children[i].className = "";}
  var navBarElt = document.getElementById("idNavBar"+dirs[0])
  if (navBarElt) {
    navBarElt.className = "active";}
//set url
  var stateObj = { foo: "bar" };
  try {  //try catch, car en local, cela soulève une securityError pour des raisons de same origin policy pas gérées de la meme manière  ...
  history.pushState(stateObj, "page 2", "bar.html"); } catch (e) { tmp=0;}
//set breadcrumb
  var bct = "<li><a onclick=\"showDiv(event,'');\" href=\"http://sakura.imag.fr\" title=\"Sakura\">Sakura</a></li>";
  var tmpDir = "";
  for(i=0;i<dirs.length-1;i++) {
	tmpDir = tmpDir + dirs[i] ;
	bct = bct + "<li><a onclick='showDiv(event,\""+tmpDir+"\");' href=\"http://sakura.imag.fr/"+tmpDir+"\" title= \""+tmpDir+"\">"+dirs[i]+"</a></li>";
	tmpDir = tmpDir + "/";}	  
  bct = bct + "<li class='active'>"+dirs[i]+"</li>";
  var d = document.getElementById("breadcrumbtrail");
  d.innerHTML = bct;
  event.preventDefault();}

	
function listRequestStub(n) {
 ws_request('list_nObjets', [10,'etude_'], {}, function (result) {
   s="<ul>"
   for(i=0;i<result.length;i++) {
     s += "<li>Etude : "+result[i].nom+", valeur :"+result[i].valeur+"</li>\n";}
   s+="</ul>"	 
   document.getElementById("dFF").innerHTML = s;
   return ;});
 return ;}