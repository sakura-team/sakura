// LIG March 2017

function showDiv(event,dir) {
//set url
if (event instanceof PopStateEvent) {
  ; /* rien dans l'history */}
else {
    var stateObj = { where: dir };
    try {  //try catch, car en local, cela soulève une securityError pour des raisons de same origin policy pas gérées de la meme manière  ...
    history.pushState(stateObj, "page", "#"+dir); } catch (e) { tmp=0;}}
//normalize dir
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
function signInSubmitControl(event) {
  if ((document.getElementById("signInEmail").value.length>2) && (document.getElementById("signInEmail").value	== document.getElementById("signInPassword").value)) {
    showDiv(event,'HelloYou');
	$("#signInModal").modal("hide");
	document.getElementById("idSignInHelloYou").innerHTML= '<a onclick="showDiv(event,\'HelloYou\');" href="http://sakura.imag.fr/Restart" style="cursor: pointer;"><span class="glyphicon glyphicon-user" aria-hidden="true"></span> Hello you</a>';
    return;}
  else {
	alert('not yet, try email=password=guest');
    return;	}}
	
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

function numAlea(num) {
return num+(Math.floor(Math.random() * num));}

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
s="";
for(i=0;i<result.length;i++) {
  s = s + "<tr><td><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\">"+result[i].name+"</a></td>\n"
        + "<td>"+result[i].shortDesc+"</td>"
		+ "<td align='center'>";
  if ((result[i].isPublic=="true") && (result[i].isOwner=="true")) {
	s = s + "<a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span></a>"
		  + "<a onclick=\"showDiv(event,'"+elt+"/Work');\" href=\"http://sakura.imag.fr/"+elt+"/Work\" class='btn btn-default'><span class='glyphicon glyphicon-pencil' aria-hidden='true'></span></a>";}
  else if (result[i].isPublic=="true") {
	s = s + "<a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span></a>"
		  + "<a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><img src='media/IconFinder_298785_fork.png'></img></a>";}
  else {
	s = s + "<a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><span class='glyphicon glyphicon-eye-close' aria-hidden='true'></span></a>";}  
  s = s + "</td></tr>";}
document.getElementById(idDiv).innerHTML = s;}

function listRequestStub(idDiv,n,elt,bd) {
if (!bd) {  // version local
  result=new Array();
  for(i=0;i<n;i++) {
    result.push({"name":fullNameAlea(),"shortDesc":shortTextAlea(),"isPublic":boolAlea(0.7),"isOwner":boolAlea(0.3)});}
  buildListStub(idDiv,result,elt);}
else {     // version réseau à faire
  ws_request('list_nObjets', [10,'etude_'], {}, function (idDiv,result) {buildListStub(idDiv,result,elt);});}
return ;}
 
function listRequestStubForRestart(idDiv) {
result=new Array();
s="";
i=0;
result.push({"name":fullNameAlea(),"shortDesc":shortTextAlea(),"isPublic":boolAlea(0.7),"isOwner":"true"});
elt='Protocols/tmpProtocol';
s = s + "<tr><td><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\">"+result[i].name
      + "</a>&nbsp;&nbsp;<img  width='40px' height='40px' src='media/Simpleicons_Business_notebook.svg.png' alt='CC-BY-3.0 Wikipedia Gears'></img></td>\n"
      + "<td>"+result[i].shortDesc+"</td>"
      + "<td align='center'><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span></a>"
      + "  <a onclick=\"showDiv(event,'"+elt+"/Work');\" href=\"http://sakura.imag.fr/"+elt+"/Work\" class='btn btn-default'><span class='glyphicon glyphicon-pencil' aria-hidden='true'></span></a>"
      + "</td></tr>";
i=i+1;
result.push({"name":fullNameAlea(),"shortDesc":shortTextAlea(),"isPublic":boolAlea(0.7),"isOwner":"true"});
elt='DataSets/tmpDataSet';
s = s + "<tr><td><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\">"+result[i].name
      + "</a>&nbsp;&nbsp;<img  width='40px' height='40px' src='media/Linecons_database.svg.png' alt='CC-BY-3.0 Wikipedia Gears'></img></td>\n"
      + "<td>"+result[i].shortDesc+"</td>"
      + "<td align='center'><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span></a>"
      + "  <a onclick=\"showDiv(event,'"+elt+"/Work');\" href=\"http://sakura.imag.fr/"+elt+"/Work\" class='btn btn-default'><span class='glyphicon glyphicon-pencil' aria-hidden='true'></span></a>"
      + "</td></tr>";
i=i+1;
result.push({"name":fullNameAlea(),"shortDesc":shortTextAlea(),"isPublic":boolAlea(0.7),"isOwner":"true"});
elt='Operators/tmpOperator';
s = s + "<tr><td><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\">"+result[i].name
      + "</a>&nbsp;&nbsp;<img  width='40px' height='40px' src='media/Octicons-gear.svg.png' alt='CC-BY-3.0 Wikipedia Gears'></img></td>\n"
      + "<td>"+result[i].shortDesc+"</td>"
      + "<td align='center'><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span></a>"
      + "  <a onclick=\"showDiv(event,'"+elt+"/Work');\" href=\"http://sakura.imag.fr/"+elt+"/Work\" class='btn btn-default'><span class='glyphicon glyphicon-pencil' aria-hidden='true'></span></a>"
      + "</td></tr>";
i=i+1;
result.push({"name":fullNameAlea(),"shortDesc":shortTextAlea(),"isPublic":boolAlea(0.7),"isOwner":"true"});
elt='Analyses/tmpAnalysis';
s = s + "<tr><td><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\">"+result[i].name
      + "</a>&nbsp;&nbsp;<img  width='40px' height='40px' src='media/Share_icon_BLACK-01.svg.png' alt='CC-BY-3.0 Wikipedia Gears'></img></td>\n"
      + "<td>"+result[i].shortDesc+"</td>"
      + "<td align='center'><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span></a>"
      + "  <a onclick=\"showDiv(event,'"+elt+"/Work');\" href=\"http://sakura.imag.fr/"+elt+"/Work\" class='btn btn-default'><span class='glyphicon glyphicon-pencil' aria-hidden='true'></span></a>"
      + "</td></tr>";
i=i+1;
result.push({"name":fullNameAlea(),"shortDesc":shortTextAlea(),"isPublic":boolAlea(0.7),"isOwner":"true"});
elt='Results/tmpResult';
s = s + "<tr><td><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\">"+result[i].name
      + "</a>&nbsp;&nbsp;<img  width='40px' height='40px' src='media/Article_icon_cropped.svg.png' alt='CC-BY-3.0 Wikipedia Gears'></img></td>\n"
      + "<td>"+result[i].shortDesc+"</td>"
      + "<td align='center'><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span></a>"
      + "  <a onclick=\"showDiv(event,'"+elt+"/Work');\" href=\"http://sakura.imag.fr/"+elt+"/Work\" class='btn btn-default'><span class='glyphicon glyphicon-pencil' aria-hidden='true'></span></a>"
      + "</td></tr>";
document.getElementById(idDiv).innerHTML = s;
return ;}
 
function buildHistoryStub(idDiv,result,elt) {
s="";
for(i=0;i<result.length;i++) {
  s = s + "<li>On "+result[i].dateVersion+" (<a onclick='javascript:not_yet();'>view this version</a> or <a onclick='javascript:not_yet();'>set back current version with this version.</a>)<p> Revision message from "+result[i].userName+" : "+result[i].msgVersion+"</li>";}
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
  infos.push({"name":elt+"-id","value":numAlea(100)});
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
