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
  var actionsOnShow=document.getElementById(idDir).getElementsByClassName("executeOnShow");
  for(i=0;i<actionsOnShow.length;i++) {
	eval(actionsOnShow[i].href);}
  event.preventDefault();}

function buildListStub(idDiv,result) {
/* s="<ul>"; for(i=0;i<result.length;i++) {
   s = s + "<li>Experiment <a onclick=\"showDiv(event,'Protocols/tmpProtocol');\" href=\"http://sakura.imag.fr/Protocols/tmpProtocol\">tmpProtocol_"+result[i].nom+"</a></li>";}
   s+="</ul>"; */
s="";
for(i=0;i<result.length;i++) {
  if (result[i].isPublic=="true") {
    eyeIcon = "glyphicon-eye-open";}
  else {
	eyeIcon = "glyphicon-eye-close";}  
  s = s + "<tr><td><a onclick=\"showDiv(event,'Protocols/tmpProtocol');\" href=\"http://sakura.imag.fr/Protocols/tmpProtocol\">"+result[i].name+"</a></td>\n"
        + "<td>"+result[i].shortDesc+"</td>"
		+ "<td align='center'><a onclick=\"showDiv(event,'Protocols/tmpProtocol');\" href=\"http://sakura.imag.fr/Protocols/tmpProtocol\" class='btn btn-default'><span class='glyphicon "+eyeIcon+"' aria-hidden='true'></span></a></td>"
        + "</tr>";}
document.getElementById(idDiv).innerHTML = s;}

var firstNamesAlea=["Geom","Math","Plus","Tutor","Class","Copex","Diag","Form","Lab","Mooc","Mood","Smart","Qcm","Tamag","Tit"];
var lastNamesAlea=["Exp","Elec","Aplus","Edit","Eval","Alg","Add"];
var lastDigitsAlea=["","7","1","2","3","1.2","2.0","1.0","2.1","1997","2000","2001","2002","2009","2014","2015","2016","2017"];

function fullNameAlea() {
  return firstNamesAlea[Math.floor(Math.random() * firstNamesAlea.length)]
    + lastNamesAlea[Math.floor(Math.random() * lastNamesAlea.length)]+
    + lastDigitsAlea[Math.floor(Math.random() * lastDigitsAlea.length)];}
	
var firstWordsAlea = ["Ipse","Ergo","Hinc","Tempus","Non","Fiat","Logos","Gnove","Lorem"];
var otherWordsAlea = ["fugit","est","veni","vidi","vici","etiam","porro","quisquam","qui","dolorem","ipsum","quia","dolor","sit","amet","adipisci","velit"];

function shortTextAlea() {
  return firstWordsAlea[Math.floor(Math.random() * firstWordsAlea.length)]+" "
    + otherWordsAlea[Math.floor(Math.random() * otherWordsAlea.length)]+" "
    + otherWordsAlea[Math.floor(Math.random() * otherWordsAlea.length)]+" "
    + otherWordsAlea[Math.floor(Math.random() * otherWordsAlea.length)]+", "
    + otherWordsAlea[Math.floor(Math.random() * otherWordsAlea.length)]+" "
    + otherWordsAlea[Math.floor(Math.random() * otherWordsAlea.length)]+" "
    + otherWordsAlea[Math.floor(Math.random() * otherWordsAlea.length)]+".";}
	
function publicAlea() {
if (Math.random()>0.2) {
  return "true";}
else {
  return "false";}}  

var usersAlea = ["John W.","Anna B.","Paul A.","Mary M.","Fiona C.","Piotr D."];

function userAlea() {
return usersAlea[Math.floor(Math.random() * usersAlea.length)]}


function listRequestStub(idDiv,n,bd) {
if (!bd) {  // version local
  result=new Array();
  for(i=0;i<n;i++) {
    result.push({"name":fullNameAlea(),"shortDesc":shortTextAlea(),"isPublic":publicAlea()});}
  buildListStub(idDiv,result);}
else {     // version réseau à faire
  ws_request('list_nObjets', [10,'etude_'], {}, function (idDiv,result) {buildListStub(result);});}
return ;}
 
 
function buildHistoryStub(idDiv,result) {
s="";
for(i=0;i<result.length;i++) {
  s = s + "<li><a onclick=\"showDiv(event,'Protocols/tmpProtocol');\" href=\"http://sakura.imag.fr/Protocols/tmpProtocol\">"+result[i].dateVersion+"</a> "+result[i].userName+" : "+result[i].msgVersion+". (<a onclick='javascript:not_yet();'>Undo</a>)</li>";}
document.getElementById(idDiv).innerHTML = s;}

 
function historyRequestStub(idDiv,n,bd) {
if (!bd) {  // version local
  result=new Array();
  var d = new Date();
  for(i=0;i<n;i++) {	  
    result.push({"dateVersion":d.toString(),"userName":userAlea(),"msgVersion":shortTextAlea()});
	d.setDate(d.getDate()-Math.random());}
  buildHistoryStub(idDiv,result);}
else {     // version réseau à faire
  ws_request('list_nObjets', [10,'etude_'], {}, function (idDiv,result) {buildHistoryStub(result);});}
return ;}
 