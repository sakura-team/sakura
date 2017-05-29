// LIG March 2017

function showDiv(event,dir) {
//save mode ?
if (document.getElementById("idEditModeWidget").innerText.match("Save")) {
  res=confirm("Leave edit mode?");
  if (res) {	
    document.getElementById("idEditModeWidget").innerHTML= '<a onclick="editModeSubmitControl(event);"  style="cursor: pointer;">Edit Mode</a>';
    sav=confirm("Save modification (or abort)?");
	  if (sav) {
		//alert("Save");
		}
	  else { 	
        alert("Abort  (not yet impemented)");}}
  else {
    event.preventDefault();
    return;}}
//set url
if (event instanceof PopStateEvent) {
  ; /* rien dans l'history */}
else {
    var stateObj = { where: dir };
    try {  //try catch, car en local, cela soulève une securityError pour des raisons de same origin policy pas gérées de la meme manière  ...
    history.pushState(stateObj, "page", "#"+dir); } catch (e) { tmp=0;}}
//normalize dir
  if ((dir.split("?").length>1) && (dir.split("?")[1].match(/page=(-?\d+)/).length>1)) {
    document.pageElt = +dir.split("?")[1].match(/page=(-?\d+)/)[1];}
  else {
	document.pageElt = 1;}
  dir = dir.split("?")[0];
  if (dir=="") {
    dir="Home";}
  else if (dir.match("tmp")) {
	if (!(dir.match("Work") || dir.match("Historic") || dir.match("Main")))  {
	  dir = dir + "/Main";}}
  var dirs = dir.split("/");
//show div
  mainDivs=document.getElementsByClassName('classMainDiv');
  for(i=0;i<mainDivs.length;i++) {
	mainDivs[i].style.display='none';}  
  var idDir = "idDiv"+dirs.join("");
  if (idDir.match("Main") &&  document.getElementById("idSignInWidget").innerText.match("Hello")){ //todo : ameliorer test hello == test droit en edition
	  document.getElementById("idEditModeWidget").style.display='';}
  else {
	  document.getElementById("idEditModeWidget").style.display='none';}
  document.getElementById(idDir).style.display='inline';
//activate navbar   
  var d = document.getElementById("navbar_ul");
  for (var i=0; i< d.children.length; i++) {
    d.children[i].className = "";}
  var navBarElt = document.getElementById("idNavBar"+dirs[0])
  if (navBarElt) {
    navBarElt.className = "active";}
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
  
/* Divers */

function chgShowColumns(event) {
 showDiv(event,window.location.href.split("#")[1]);
 return;}

function editModeSubmitControl(event) {
  //alert("Entering edit mode.");
  document.getElementById("idEditModeWidget").innerHTML= '<a onclick="saveModeSubmitControl(event);"  style="cursor: pointer;">Save</a>';} 

function saveModeSubmitControl(event) {
    sav=confirm("Save modification (or abort)?");
	  if (sav) {
		//alert("Save")
		;}
	  else {
		 alert("Abort (not yet impemented)");}
  document.getElementById("idEditModeWidget").innerHTML= '<a onclick="editModeSubmitControl(event);"  style="cursor: pointer;">Edit Mode</a>';} 

 function signInSubmitControl(event) {
  if ((document.getElementById("signInEmail").value.length>2) && (document.getElementById("signInEmail").value	== document.getElementById("signInPassword").value)) {
    showDiv(event,'HelloYou');
	$("#signInModal").modal("hide");
	document.getElementById("idSignInWidget").innerHTML= '<a onclick="signOutSubmitControl(event);" href="http://sakura.imag.fr/signOut" style="cursor: pointer;"><span class="glyphicon glyphicon-user" aria-hidden="true"></span> Hello you</a>';
    return;}
  else {
	alert('not yet, try email=password=guest');
    return;	}}

function signOutSubmitControl(event) {
  res=confirm("Sign Out?");
  if (res) {
	document.getElementById("idSignInWidget").innerHTML= '<a class="btn" data-toggle="modal" data-target="#signInModal"><span class="glyphicon glyphicon-user" aria-hidden="true"></span> Sign in</a>';
	showDiv(event,"");
    return;}
  else {
	showDiv(event,'HelloYou');}}

function searchSubmitControl(event,elt) {
  listeInit = document.getElementById("idTBodyList"+elt).innerHTML.replace(/ style="display:none;"/g,"").replace(/ style='display:none;'/g,"");
  listeInit = listeInit.split("<tr");
  searchString = document.getElementById("idInputSearch"+elt).value;
  s="";
  for(i=1;i<listeInit.length;i++) {
	  if (listeInit[i].match(searchString)) {
		s =  s + "<tr"+listeInit[i];}
	  else {
		s = s + "<tr style='display:none;'"+listeInit[i];}}
  document.getElementById("idTBodyList"+elt).innerHTML = s;}

function showDivCGU(event) {
  $("#signInModal").modal("hide");
  showDiv(event,"CGU");}

/*    Génération aléatoire     */
var firstProcNamesAlea=["Avg","Count","Diff","Hist","Viz","Reg","Lin","Stand","Sort","Best","Approx","Plot"];
var firstNamesAlea=["Geom","Math","Plus","Tutor","Class","Copex","Diag","Form","Lab","Mooc","Mood","Smart","Qcm","Tamag","Tit"];
var lastNamesAlea=["Exp","Elec","Aplus","Edit","Eval","Alg","Add","Oct","Hex","Alea","Hist"];
var lastDigitsAlea=["","_bis","_a","_b","7","1","2","3","1.2","2.0","1.0","2.1","1997","2000","2001","2002","2009","2014","2015","2016","2017"];
var usersAlea = ["John W.","Anna B.","Paul A.","Mary M.","Fiona C.","Piotr D."];
var firstWordsAlea = ["Ipse","Ergo","Hinc","Tempus","Non","Fiat","Logos","Gnove","Lorem","Nunc","Cujus","Urbis"];
var otherWordsAlea = ["fugit","est","veni","vidi","vici","etiam","porro","quisquam","qui","dolorem","ipsum","quia","dolor","sit","amet","adipisci","velit"];
var extsAlea = ["pdf","csv","txt","doc","xls","jpg","png","pwt","odt"];
var propsAlea = ["Date","Kind","Domain","Level","Duration","Status","Property","Country","Volume"];
var valsAlea = ["porro","quia","xyz34","####",'n.a.','inf','nspp','','_','see below'];

function aleaAlea(alea) {
return alea[Math.floor(Math.random() * alea.length)]}

function numAlea(base,over) {
return base+(Math.floor(Math.random() * over));}

function dateAlea() {
return ''+Math.floor(1+Math.random() * 10.5)+'/'+Math.floor(2000+Math.random() * 17);}

function fullNameAlea() {
  return firstNamesAlea[Math.floor(Math.random() * firstNamesAlea.length)]+"_"
    + lastNamesAlea[Math.floor(Math.random() * lastNamesAlea.length)]+"_"
    + propsAlea[Math.floor(Math.random() * propsAlea.length)]+"_"
    + lastDigitsAlea[Math.floor(Math.random() * lastDigitsAlea.length)];}
	
function fullProcNameAlea() {
  return firstProcNamesAlea[Math.floor(Math.random() * firstProcNamesAlea.length)]
    + lastNamesAlea[Math.floor(Math.random() * lastNamesAlea.length)]+
    + lastDigitsAlea[Math.floor(Math.random() * lastDigitsAlea.length)];}

function shortTextAlea() {
  return firstWordsAlea[Math.floor(Math.random() * firstWordsAlea.length)]+" "
    + otherWordsAlea[Math.floor(Math.random() * otherWordsAlea.length)]+" "
    + otherWordsAlea[Math.floor(Math.random() * otherWordsAlea.length)]+" "
    + otherWordsAlea[Math.floor(Math.random() * otherWordsAlea.length)]+", "
    + otherWordsAlea[Math.floor(Math.random() * otherWordsAlea.length)]+" "
    + otherWordsAlea[Math.floor(Math.random() * otherWordsAlea.length)]+" "
    + otherWordsAlea[Math.floor(Math.random() * otherWordsAlea.length)]+".";}
	
function boolAlea(trueProportion) {
if (Math.random()<trueProportion) {
  return "true";}
else {
  return "false";}}  


/*       FillStub        */  
function buildListStub(idDiv,result,elt) {
var eltAncetre=elt.split("/")[0];	
s="";
s = s +'<thead><tr>'
      + '<th class="col-text">Name</th>';
if (document.getElementById("cbColSelectTags").checked) {
  s = s + '<th class="col-text"><span class="glyphicon glyphicon-tag" aria-hidden="true"></span></th>';}
if (document.getElementById("cbColSelectId").checked) {
  s = s +  '<th class="col-text">id</th>';}
if (document.getElementById("cbColSelectShortDesc").checked) {
  s = s +  '<th class="col-text">Short Desc.</th>';}
if (document.getElementById("cbColSelectDate").checked) {
  s = s +  '<th class="col-text">Date</th>';}
if (document.getElementById("cbColSelectModification").checked) {
  s = s +  '<th class="col-text">Modif.</th>';}
if (document.getElementById("cbColSelectAuthor").checked) {
  s = s +  '<th class="col-text">Author</th>';}
s = s +  '<th class="col-tools"><span class="glyphicon glyphicon-wrench" aria-hidden="true"></span></th>'
      + '<th class="col-text" style="max-width:3px; overflow:hidden">'
      + '<a class="btn" style="padding:2px;" data-toggle="modal" data-target="#colSelectModal">'
	  + '<span style="left:-10px;" class="glyphicon glyphicon-list" aria-hidden="true"></span></a></th>'
      + '</tr></thead>'
	  + '<tbody id="idTBodyList'+eltAncetre+'">';						
for(i=0;i<result.length;i++) {
  //if (document.getElementById("idInputSearch".eltAncetre).value!="") {}
  s = s + "<tr><td><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\">"+result[i].name+"</a></td>\n";
  if (document.getElementById("cbColSelectTags").checked) {
    s = s + "<td>"+result[i].tags+"</td>";}
  if (document.getElementById("cbColSelectId").checked) {
    s = s + "<td>"+result[i].id+"</td>";} 
  if (document.getElementById("cbColSelectShortDesc").checked) {
    s = s + "<td>"+result[i].shortDesc+"</td>";}  
  if (document.getElementById("cbColSelectDate").checked) {
    s = s + "<td>"+result[i].date+"</td>";}
  if (document.getElementById("cbColSelectModification").checked) {
    s = s + "<td>"+result[i].modif+"</td>";} 
  if (document.getElementById("cbColSelectAuthor").checked) {
    s = s + "<td>"+result[i].author+"</td>";} 	
  s = s	+ "<td colspan='2' align='center' style='padding:2px;'>";
  if ((result[i].isViewable=="true") && (result[i].isEditable=="true")) {
	s = s + "<a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span></a>"
	      + "<a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><img src='media/IconFinder_298785_fork.png'></img></a>"
		  + "<a onclick=\"showDiv(event,'"+elt+"/Work');\" href=\"http://sakura.imag.fr/"+elt+"/Work\" class='btn btn-default'><span class='glyphicon glyphicon-pencil' aria-hidden='true'></span></a>";}
  else if (result[i].isViewable=="true") {
	s = s + "<a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span></a>"
		  + "<a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><img src='media/IconFinder_298785_fork.png'></img></a>";}
  else {
	s = s + "<a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><span class='glyphicon glyphicon-eye-close' aria-hidden='true'></span></a>";}  
  s = s + "</td></tr>";}
s = s + '<a href="javascript:listRequestStub(\''+idDiv+'\',10,\''+elt+'\',false)" class="executeOnShow"> </a>' //TODO : (</div> ?) relance l'affichage aleatoire, à supprimer quand on aura la version avec bd  
      + '</tbody>';
document.getElementById(idDiv).innerHTML = s;
//maj de la pagination
document.pageElt;
s = "<li><a aria-label='Previous' onclick='showDiv(event,\""+eltAncetre+"?page="+(document.pageElt-5)+"\");' href='http://sakura.imag.fr/"+eltAncetre+"?page="+(document.pageElt-5)+"' span aria-hidden='true'>«</span></a></li>"
     + "<li><a onclick='showDiv(event,\""+eltAncetre+"?page="+(document.pageElt-0)+"\");' href='http://sakura.imag.fr/"+eltAncetre+"?page="+(document.pageElt-0)+"'>"+(document.pageElt-0)+"</a></li>"
     + "<li><a onclick='showDiv(event,\""+eltAncetre+"?page="+(document.pageElt+1)+"\");' href='http://sakura.imag.fr/"+eltAncetre+"?page="+(document.pageElt+1)+"'>"+(document.pageElt+1)+"</a></li>"
     + "<li><a onclick='showDiv(event,\""+eltAncetre+"?page="+(document.pageElt+2)+"\");' href='http://sakura.imag.fr/"+eltAncetre+"?page="+(document.pageElt+2)+"'>"+(document.pageElt+2)+"</a></li>"
     + "<li><a onclick='showDiv(event,\""+eltAncetre+"?page="+(document.pageElt+3)+"\");' href='http://sakura.imag.fr/"+eltAncetre+"?page="+(document.pageElt+3)+"'>"+(document.pageElt+3)+"</a></li>"
     + "<li><a onclick='showDiv(event,\""+eltAncetre+"?page="+(document.pageElt+4)+"\");' href='http://sakura.imag.fr/"+eltAncetre+"?page="+(document.pageElt+4)+"'>"+(document.pageElt+4)+"</a></li>"
     + "<li><a aria-label='Next' onclick='showDiv(event,\""+eltAncetre+"?page="+(document.pageElt+5)+"\");' href='http://sakura.imag.fr/"+eltAncetre+"?page="+(document.pageElt+5)+"'><span aria-hidden='true'>»</span></a></li>";
document.getElementById("idDivPagination"+eltAncetre).innerHTML = s;}

function listRequestStub(idDiv,n,elt,bd) {
if (!bd) {  // version local
  result=new Array();
  for(i=0;i<n;i++) {
    result.push({"name":fullNameAlea(),
	  "id":numAlea(100,100),
	  "tags":aleaAlea(firstNamesAlea),
	  "shortDesc":shortTextAlea(),
	  "date":dateAlea(),
	  "modif":dateAlea(),	  
	  "author":aleaAlea(usersAlea),	  
	  "isViewable":boolAlea(0.7),
	  "isEditable":boolAlea(0.3)});}
  buildListStub(idDiv,result,elt);}
else {     // version réseau à faire
  ws_request('list_nObjets', [10,'etude_'], {}, function (idDiv,result) {buildListStub(idDiv,result,elt);});}
return ;}
 
function listRequestStubForRestart(idDiv) {
result=new Array();
s="";
i=0;
result.push({"name":fullNameAlea(),"shortDesc":shortTextAlea(),"isViewable":"true","isEditable":"true"});
elt='Protocols/tmpProtocol';
s = s + "<tr><td><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\">"+result[i].name
      + "</a>&nbsp;&nbsp;<img  width='40px' height='40px' src='media/Simpleicons_Business_notebook.svg.png' alt='CC-BY-3.0 Wikipedia Gears'></img></td>\n"
      + "<td>"+result[i].shortDesc+"</td>"
      + "<td align='center'><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span></a>"
      + "  <a onclick=\"showDiv(event,'"+elt+"/Work');\" href=\"http://sakura.imag.fr/"+elt+"/Work\" class='btn btn-default'><span class='glyphicon glyphicon-pencil' aria-hidden='true'></span></a>"
	  + "  <a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><img src='media/IconFinder_298785_fork.png'></img></a>"
      + "</td></tr>";
i=i+1;
result.push({"name":fullNameAlea(),"shortDesc":shortTextAlea(),"isViewable":"true","isEditable":"true"});
elt='DataSets/tmpDataSet';
s = s + "<tr><td><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\">"+result[i].name
      + "</a>&nbsp;&nbsp;<img  width='40px' height='40px' src='media/Linecons_database.svg.png' alt='CC-BY-3.0 Wikipedia Gears'></img></td>\n"
      + "<td>"+result[i].shortDesc+"</td>"
      + "<td align='center'><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span></a>"
      + "  <a onclick=\"showDiv(event,'"+elt+"/Work');\" href=\"http://sakura.imag.fr/"+elt+"/Work\" class='btn btn-default'><span class='glyphicon glyphicon-pencil' aria-hidden='true'></span></a>"
      + "  <a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><img src='media/IconFinder_298785_fork.png'></img></a>"
	  + "</td></tr>";
i=i+1;
result.push({"name":fullNameAlea(),"shortDesc":shortTextAlea(),"isViewable":"true","isEditable":"true"});
elt='Operators/tmpOperator';
s = s + "<tr><td><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\">"+result[i].name
      + "</a>&nbsp;&nbsp;<img  width='40px' height='40px' src='media/Octicons-gear.svg.png' alt='CC-BY-3.0 Wikipedia Gears'></img></td>\n"
      + "<td>"+result[i].shortDesc+"</td>"
      + "<td align='center'><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span></a>"
      + "  <a onclick=\"showDiv(event,'"+elt+"/Work');\" href=\"http://sakura.imag.fr/"+elt+"/Work\" class='btn btn-default'><span class='glyphicon glyphicon-pencil' aria-hidden='true'></span></a>"
      + "  <a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><img src='media/IconFinder_298785_fork.png'></img></a>"
      + "</td></tr>";
i=i+1;
result.push({"name":fullNameAlea(),"shortDesc":shortTextAlea(),"isViewable":"true","isEditable":"true"});
elt='Analyses/tmpAnalysis';
s = s + "<tr><td><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\">"+result[i].name
      + "</a>&nbsp;&nbsp;<img  width='40px' height='40px' src='media/Share_icon_BLACK-01.svg.png' alt='CC-BY-3.0 Wikipedia Gears'></img></td>\n"
      + "<td>"+result[i].shortDesc+"</td>"
      + "<td align='center'><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span></a>"
      + "  <a onclick=\"showDiv(event,'"+elt+"/Work');\" href=\"http://sakura.imag.fr/"+elt+"/Work\" class='btn btn-default'><span class='glyphicon glyphicon-pencil' aria-hidden='true'></span></a>"
      + "  <a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><img src='media/IconFinder_298785_fork.png'></img></a>"
      + "</td></tr>";
i=i+1;
result.push({"name":fullNameAlea(),"shortDesc":shortTextAlea(),"isViewable":"true","isEditable":"true"});
elt='Results/tmpResult';
s = s + "<tr><td><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\">"+result[i].name
      + "</a>&nbsp;&nbsp;<img  width='40px' height='40px' src='media/Article_icon_cropped.svg.png' alt='CC-BY-3.0 Wikipedia Gears'></img></td>\n"
      + "<td>"+result[i].shortDesc+"</td>"
      + "<td align='center'><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span></a>"
      + "  <a onclick=\"showDiv(event,'"+elt+"/Work');\" href=\"http://sakura.imag.fr/"+elt+"/Work\" class='btn btn-default'><span class='glyphicon glyphicon-pencil' aria-hidden='true'></span></a>"
      + "  <a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><img src='media/IconFinder_298785_fork.png'></img></a>"
      + "</td></tr>";
s = s + '<a href="javascript:listRequestStubForRestart(\''+idDiv+'\')" class="executeOnShow"> </a></div>';
document.getElementById(idDiv).innerHTML = s;
return ;}
 
function buildHistoryStub(idDiv,result,elt) {
s="";
for(i=0;i<result.length;i++) {
  s = s + "<li>On "+result[i].dateVersion+" (<a onclick='javascript:not_yet();'>view</a> / <a onclick='javascript:not_yet();'>revert</a>)<p> Revision message from "+result[i].userName+" : "+result[i].msgVersion+"</li>";}
document.getElementById(idDiv).innerHTML = s;}

function historyRequestStub(idDiv,n,elt,bd) {
if (!bd) {  // version local
  result=new Array();
  var d = new Date();
  for(i=0;i<n;i++) {	  
    result.push({"dateVersion":d.toString(),"userName":aleaAlea(usersAlea),"msgVersion":shortTextAlea()});
	d.setDate(d.getDate()-Math.random());}
  buildHistoryStub(idDiv,result,elt);}
else {     // version réseau à faire
  ws_request('list_nObjets', [10,'etude_'], {}, function (idDiv,result) {buildHistoryStub(idDiv,result,elt);});}
return ;}

function buildEltStub(idDiv,result,elt) {
// menu sign et edition
//if (document.getElementById("idSignInWidget").innerText.match("Hello")) {
 // document.getElementById("idEditModeWidget").style.display='';}   
//contenu general
s = "";
if (elt=="Protocol") {
  imageElt = "Simpleicons_Business_notebook.svg.png";
  imageEltInverse = "Simpleicons_Business_notebook_inverse.svg.png";}
else if (elt=="DataSet") {
  imageElt = "Linecons_database.svg.png";
  imageEltInverse = "Linecons_database_inverse.svg.png";}
else if (elt=="Operator") {
  imageElt = "Octicons-gear.svg.png";
  imageEltInverse = "Octicons-gear_inverse.svg.png";}
else if (elt=="Analysis") {
  imageElt = "Share_icon_BLACK-01.svg.png";
  imageEltInverse = "Share_icon_BLACK-01_inverse.svg.png";}
else {
  imageElt = "Article_icon_cropped.svg.png";
  imageEltInverse = "Article_icon_cropped_inverse.svg.png";}
s = s + '<h3>'+elt+' '+result.name+"&nbsp;&nbsp;<img  width='40px' height='40px' src='media/"+imageElt+"' alt='CC-BY-3.0 Wikipedia Gears'></img></h3>"
      + '<div class="col-md-12" id="studyPageContentMain"><div class="row well">'
      + '<h4 class="">'+elt+' information</h4>'
      + '<dl class="dl-horizontal col-md-6">';
//Informations	  
for(i=0;i<result.info.length;i++) { 
  s = s + '<dt class="description-terms-align-left">'+result.info[i].name+'</dt><dd class="editableDescriptionField">'+result.info[i].value+'</dd>';}
s = s + '<dt></dt><dd></dd>';
if (result.dataSets.length>0) {
  s = s + '<dt class="description-terms-align-left">DataSets</dt><dd class="editableDescriptionField">';
  for(i=0;i<result.dataSets.length;i++) {
    s = s + "<a onclick=\"showDiv(event,'DataSets/tmpDataSet');\" href=\"http://sakura.imag.fr/DataSets/tmpDataSet\">"+result.dataSets[i].name+"</a>, ";}
  s = s + '</dd>';}
if (result.process.length>0) {
  s = s + '<dt class="description-terms-align-left">Analyses processes</dt><dd class="editableDescriptionField">';
  for(i=0;i<result.process.length;i++) {
    s = s + "<a onclick=\"showDiv(event,'Analyses/tmpAnalysis');\" href=\"http://sakura.imag.fr/Analyses/tmpAnalysis\">"+result.process[i].name+"</a>, ";}
  s = s + '</dd>';}
if (result.results.length>0) {
   s = s + '<dt class="description-terms-align-left">Results</dt><dd class="editableDescriptionField">';
  for(i=0;i<result.results.length;i++) {
    s = s + "<a onclick=\"showDiv(event,'Results/tmpResult');\" href=\"http://sakura.imag.fr/Results/tmpResult\">"+result.results[i].name+"</a>, ";}
  s = s + '</dd>';}
s = s + '</dl>'
	  + '<ul class="list-group col-md-6">'
	  +   '<li class="list-group-item list-group-item-info"><strong>About <em>'+result.name+'</em> :</strong></li>'
	  +   '<li class="list-group-item"><strong>Qualitative indicator:</strong> <span class="label label-primary pull-right">5</span></li>'
	  +   '<li class="list-group-item"><strong>Volumetric indicator:</strong> <span class="label label-primary pull-right">5</span></li>'
	  +   '<li class="list-group-item"><strong>Contact:</strong> <span class="label label-primary pull-right">'+result.userName+'@mail.uni</span></li>'
      + '</ul></div>';
// Description
s = s + '<br /><br /><div class="panel panel-primary"><div class="panel-heading">'
      + '<table width="100%"><tbody><tr><td><h4 class="">'
	  + '<font color="#ffffff">Explanation About '+result.name+"&nbsp;&nbsp;<img  width='40px' height='40px' src='media/"+imageEltInverse+"' alt='CC-BY-3.0 Wikipedia Gears'></img></h3>"+'</font></h4></td></tr></tbody></table></div>'
	  + '<div class="panel-body">'+shortTextAlea()+' '+shortTextAlea()+' '+shortTextAlea()+' '+shortTextAlea()+'<br /> '
	                              +shortTextAlea()+' '+shortTextAlea()+' '+shortTextAlea()+'<br /><br />'
	                              +shortTextAlea()+' '+shortTextAlea()+' '+shortTextAlea()+' '+shortTextAlea()+' '+shortTextAlea()+'<br />'
	                              +shortTextAlea()+' '+shortTextAlea()+' '+shortTextAlea()+' '+shortTextAlea()+' '+shortTextAlea()+'<br />'
	                              +shortTextAlea()+' '+shortTextAlea()+' '+shortTextAlea()+'<br /><br />'
								  + '<ul><li>'+shortTextAlea()+'</li><li>'+shortTextAlea()+'</li><li>'+shortTextAlea()+'</li></ul>'
	                              +shortTextAlea()+' '+shortTextAlea()+' '+shortTextAlea()+' '+shortTextAlea()+' '+shortTextAlea()+'<br />'
	                              +shortTextAlea()+' '+shortTextAlea()+' '+shortTextAlea()+'<br /><br />'
	  +'</div></div>';
//FileSystem	  	  
if (result.fileSystem.length>0) {
  s = s + '<br /><br /><div class="well row"><h4 class="">Filesystem related to '+result.name+'</h4>'
        + '<table class="table table-bordered" id="fileBrowser"><thead>'
        + '<tr><th>Name</th><th colspan=2>Description</th></tr></thead><tbody>';
  for(i=0;i<result.fileSystem.length;i++) {
	s = s + '<tr><td><a onclick="not_yet();">'+result.fileSystem[i].filename+'</a></td><td>'+result.fileSystem[i].description+'</td></tr>';}
  s = s + '</tbody></table></div>';}
//Comments
s = s +'<hr style="border-bottom:5px solid;" /><br /><h3>Comments • '+result.comments.length+'</h3>' 
      + '<span class="glyphicon glyphicon-user"></span><form class="form-inline" role="form"><label>Add your Comment: </label><div class="form-group">'
      + '<input class="form-control" type="text" placeholder="Your comments" onclick="not_yet()"/></div>'
      + '<div class="form-group"><button onclick="not_yet();" class="btn btn-default"><span class="glyphicon glyphicon-plus"></span></button></div></form><hr />'
	  + '<ul class="commentList">';
for(i=0;i<result.comments.length;i++) {
	s = s + '<li><div class="commenterImage"><span class="glyphicon glyphicon-user"></span></div>'
	      + '<div class="commentText"><p class="">'+result.comments[i].comment+'</p> '
		  + '<span class="date sub-text">'+result.comments[i].name+' on '+result.comments[i].date+'</span></div></li><br />';}
s = s + '<a href="javascript:eltRequestStub(\''+idDiv+'\',\''+elt+'\',false)" class="executeOnShow"> </a></div>'; //TODO : relance l'affichage aleatoire, à supprimer quand on aura la version avec bd
document.getElementById(idDiv).innerHTML = s;}

function eltRequestStub(idDiv,elt,bd) {
if (!bd) {  // version local
  eltName = fullNameAlea();
  userName = aleaAlea(usersAlea)
  infos = new Array();
  ninfo = Math.floor(Math.random() * 10);
  infos.push({"name":"Name","value":eltName});
  infos.push({"name":elt+"-id","value":numAlea(100,100)});
  infos.push({"name":"Description","value":shortTextAlea()});
  infos.push({"name":"Author","value":userName});
  for(i=0;i<ninfo;i++) {
	  infos.push({"name":aleaAlea(propsAlea),"value":aleaAlea(valsAlea)});}
  dataSets = new Array();
  ndataSets = Math.floor((Math.random() * 4 + Math.random() + 2)/3);
  for(i=0;i<ndataSets;i++) {
	  dataSets.push({"name":fullNameAlea()});}
  procs = new Array();
  nprocs = Math.floor(Math.random() * 6);
  for(i=0;i<nprocs;i++) {
	  procs.push({"name":fullProcNameAlea()});}
  results = new Array();
  nresults = Math.floor(Math.random() * 6);
  for(i=0;i<nresults;i++) {
	  results.push({"name":fullProcNameAlea()});}
  fs = new Array();
  nfs = Math.max(Math.floor(Math.random() * 10 - 3),0);
  for(i=0;i<nfs;i++) {
	  fs.push({"filename":fullNameAlea()+"."+aleaAlea(extsAlea),"description":shortTextAlea()});}
  comments = new Array();
  ncomments = Math.floor(Math.random() * 5);
  for(i=0;i<ncomments;i++) {
	  comments.push({"name":aleaAlea(usersAlea), "date":"March, 2017", "comment":shortTextAlea()+' '+shortTextAlea()+' '+shortTextAlea()});}
  var result = {"name":eltName,"userName":userName,
                "info":infos, "dataSets":dataSets, "process":procs, "results":results, 
				"comments":comments,"fileSystem":fs};
  buildEltStub(idDiv,result,elt);}
else {     // version réseau à faire
  ws_request('list_nObjets', [10,'etude_'], {}, function (idDiv,result) {buildEltStub(idDiv,result,elt);});}
return ;}
