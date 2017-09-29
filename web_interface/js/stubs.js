/// LIG Sept 2017


function buildListStub(idDiv,result,elt) {
    var eltAncetre=elt.split("/")[0];
    s="";
    s = s +'<thead><tr>'
        + '<th class="col-text">Name</th>';
    if (document.getElementById("cbColSelectTags").checked) {
        s = s + '<th class="col-text"><span class="glyphicon glyphicon-tag" aria-hidden="true"></span></th>';}
    if (document.getElementById("cbColSelectId").checked) {
        s = s +  '<th class="col-text">database_id</th>';}
    if (document.getElementById("cbColSelectShortDesc").checked) {
        s = s +  '<th class="col-text">Short Desc.</th>';}
    if (document.getElementById("cbColSelectDate").checked) {
        s = s +  '<th class="col-text">Date</th>';}
    if (document.getElementById("cbColSelectModification").checked) {
        s = s +  '<th class="col-text">Modif.</th>';}
    if (document.getElementById("cbColSelectOwner").checked) {
        s = s +  '<th class="col-text">Owner</th>';}
    s = s +  '<th class="col-tools"><span class="glyphicon glyphicon-wrench" aria-hidden="true"></span></th>'
        + '<th class="col-text" style="max-width:3px; overflow:hidden">'
        + '<a class="btn" style="padding:2px;" data-toggle="modal" data-target="#colSelectModal">'
        + '<span style="left:-10px;" class="glyphicon glyphicon-list" aria-hidden="true"></span></a></th>'
        + '</tr></thead>'
        + '<tbody id="idTBodyList'+eltAncetre+'">';
    for(i=0;i<result.length;i++) {
		var tmpInitElt = elt;
		if (result[i].hasOwnProperty("database_id")) {
		  elt=elt.replace(/tmp(.*)/,"$1-"+result[i].database_id);}
		else {	// id seulement
		  elt=elt.replace(/tmp(.*)/,"$1-"+result[i].id);}
		if (result[i].hasOwnProperty("database_id")) {
        s = s + "<tr><td><a onclick=\"showDiv(event,'"+elt+"','"+result[i].database_id+"');\" href=\"http://sakura.imag.fr/"+elt+"/"+result[i].database_id+"\">"+result[i].name+"</a></td>\n";
		} else {  // id seulement
		  s = s + "<tr><td><a onclick=\"showDiv(event,'"+elt+"','"+result[i].id+"');\" href=\"http://sakura.imag.fr/"+elt+"/"+result[i].id+"\">"+result[i].name+"</a></td>\n";}
        if (document.getElementById("cbColSelectTags").checked) {
            s = s + "<td>"+result[i].tags+"</td>";}
        if (document.getElementById("cbColSelectId").checked) {
		  if (result[i].hasOwnProperty("database_id")) {
            s = s + "<td>"+result[i].database_id+"</td>";}
		 else {  // id seulement
            s = s + "<td>"+result[i].id+"</td>";}}			
        if (document.getElementById("cbColSelectShortDesc").checked) {
            s = s + "<td>"+result[i].shortDesc+"</td>";}  
        if (document.getElementById("cbColSelectDate").checked) {
            s = s + "<td>"+result[i].date+"</td>";}
        if (document.getElementById("cbColSelectModification").checked) {
            s = s + "<td>"+result[i].modif+"</td>";} 
        if (document.getElementById("cbColSelectOwner").checked) {
            s = s + "<td>"+result[i].owner+"</td>";}
        s = s	+ "<td colspan='2' align='center' style='padding:2px;'>";
        if ((result[i].isViewable=="true") && (result[i].isEditable=="true")) {
            s = s + "<a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span></a>"
                + "<a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><img src='media/IconFinder_298785_fork.png'></img></a>"
                + "<a onclick=\"showDiv(event,'"+elt+"/Work');\" href=\"http://sakura.imag.fr/"+elt+"/Work\" class='btn btn-default'><span class='glyphicon glyphicon-pencil' aria-hidden='true'></span></a>";
        }
        else if (result[i].isViewable=="true") {
            s = s + "<a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span></a>"
                + "<a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><img src='media/IconFinder_298785_fork.png'></img></a>";
        }
        else {
            s = s + "<a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><span class='glyphicon glyphicon-eye-close' aria-hidden='true'></span></a>";
            }
        s = s + "</td></tr>";
		elt = tmpInitElt;
    }
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
    document.getElementById("idDivPagination"+eltAncetre).innerHTML = s;
}


function listRequestStub(idDiv, n, elt, bd) {
    if (elt == 'Datas/tmpDataSet') {
        ws_request('list_databases', [], {}, function (databases) {
            var result = new Array();;
            databases.forEach( function(db, index) {
                if (index != databases.length-1) {
                    ws_request('get_database_info', [db.database_id], {}, function(db_info) {
                        result.push({'name': db_info.label,'id':db.database_id,"owner":db_info.owner});
                    });
                }
                else { 
                    ws_request('get_database_info', [db.database_id], {}, function(db_info) {
                        result.push({'name': db_info.label,'id':db.database_id,"owner":db_info.owner});
                        buildListStub(idDiv,result,elt);
                    });
                }
            });
        });
    }
    else {
        result=listStubAlea(n); // tableau de {"name":_,"id":_,"tags":_,"shortDesc":_,"date":_,"modif":_,"owner":_,"isViewable":_,"isEditable":_} détail : {"name":fullNameAlea(), "id":numAlea(100,100),"tags":aleaAlea(firstNamesAlea),"shortDesc":shortTextAlea(),"date":dateAlea(),"modif":dateAlea(),"owner":aleaAlea(usersAlea),"isViewable":boolAlea(0.7),"isEditable":boolAlea(0.3)}
        buildListStub(idDiv,result,elt);}
    return ;}


function listRequestStubForRestart(idDiv) {
	//TODO : supprimer/deplacer alea
    result=new Array();
    s="";
    i=0;
    result.push({"name":fullNameAlea(),"shortDesc":shortTextAlea(),"isViewable":"true","isEditable":"true"});
    elt='Projects/tmpProject';
    s = s + "<tr><td><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\">"+result[i].name
        + "</a>&nbsp;&nbsp;<img  width='40px' height='40px' src='media/Simpleicons_Business_notebook.svg.png' alt='CC-BY-3.0 Wikipedia Gears'></img></td>\n"
        + "<td>"+result[i].shortDesc+"</td>"
        + "<td align='center'><a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span></a>"
        + "  <a onclick=\"showDiv(event,'"+elt+"/Work');\" href=\"http://sakura.imag.fr/"+elt+"/Work\" class='btn btn-default'><span class='glyphicon glyphicon-pencil' aria-hidden='true'></span></a>"
        + "  <a onclick=\"showDiv(event,'"+elt+"');\" href=\"http://sakura.imag.fr/"+elt+"\" class='btn btn-default'><img src='media/IconFinder_298785_fork.png'></img></a>"
        + "</td></tr>";
    i=i+1;
    result.push({"name":fullNameAlea(),"shortDesc":shortTextAlea(),"isViewable":"true","isEditable":"true"});
    elt='Datas/tmpDataSet';
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
    
    return ;
}


function buildHistoryStub(idDiv,result,elt) {
    s="";
    for(i=0;i<result.length;i++) {
        s = s + "<li>On "+result[i].dateVersion+" (<a onclick='javascript:not_yet();'>view</a> / <a onclick='javascript:not_yet();'>revert</a>)<p> Revision message from "+result[i].userName+" : "+result[i].msgVersion+"</li>";
    }
    document.getElementById(idDiv).innerHTML = s;
}


function historyRequestStub(idDiv,n,elt,bd) {
    if (!bd) {  // version local
        result=historyStubAlea(n);
        buildHistoryStub(idDiv,result,elt);}
    else {     // version réseau à faire
        ws_request('list_nObjets', [10,'etude_'], {}, function (idDiv,result) {buildHistoryStub(idDiv,result,elt);});}
    return ;}


function buildEltStub(idDiv,result,elt) {
    s = "";
    if (elt=="Project") {
        imageElt = "Simpleicons_Business_notebook.svg.png";
        imageEltInverse = "Simpleicons_Business_notebook_inverse.svg.png";
    }
    else if (elt=="DataSet") {
        imageElt = "Linecons_database.svg.png";
        imageEltInverse = "Linecons_database_inverse.svg.png";
    }
    else if (elt=="Operator") {
        imageElt = "Octicons-gear.svg.png";
        imageEltInverse = "Octicons-gear_inverse.svg.png";
    }
    else if (elt=="Analysis") {
        imageElt = "Share_icon_BLACK-01.svg.png";
        imageEltInverse = "Share_icon_BLACK-01_inverse.svg.png";
    }
    else {
        imageElt = "Article_icon_cropped.svg.png";
        imageEltInverse = "Article_icon_cropped_inverse.svg.png";
    }
    s = s + '<h3>'+elt+' '+result.name+"&nbsp;&nbsp;<img  width='40px' height='40px' src='media/"+imageElt+"' alt='CC-BY-3.0 Wikipedia Gears'></img></h3>"
        + '<div class="col-md-12" id="studyPageContentMain"><div class="row well">'
        + '<h4 class="">'+elt+' information</h4>'
        + '<dl class="dl-horizontal col-md-6">';
		
	// MAJ tabs
	if (window.location.toString().match(/[A-Za-z]+-[0-9]+/)) {
		idElt = window.location.toString().match(/[A-Za-z]+-[0-9]+/)[0].replace(/[A-Za-z]+-([0-9]+)/,"$1");
		var ongletsMain = document.getElementById(idDiv).parentElement.querySelectorAll('ul>li>a');
		var ongletWork = document.getElementById(document.getElementById(idDiv).parentElement.id.replace("Main","Work")).querySelectorAll('ul>li>a');;
		var ongletHistoric = document.getElementById(document.getElementById(idDiv).parentElement.id.replace("Main","Historic")).querySelectorAll('ul>li>a');;
		var onglets = Array();
		for(var i=0;i<ongletsMain.length;i++) {
		  onglets.push(ongletsMain[i]);}
		for(var i=0;i<ongletWork.length;i++) {
		  onglets.push(ongletWork[i]);}
		for(var i=0;i<ongletHistoric.length;i++) {
		  onglets.push(ongletHistoric[i]);}
		for(var i=0;i<onglets.length;i++) {
			var tmpOnglet = onglets[i];
			if (tmpOnglet.href.split('/').length<4) {
				continue;}
			dir=tmpOnglet.href.split('/')[3]+'/'+tmpOnglet.href.split('/')[4].replace('tmp','').replace(/-\d+/,'');
			if (tmpOnglet.href.split('/').length<6) {
				numOnglet="";}
			else {
				numOnglet=tmpOnglet.href.split('/')[5];}
			tmpOnglet.href=tmpOnglet.href.replace(/tmp([A-Za-z]+)/,"$1-"+idElt);
		    tmpOnglet.href=tmpOnglet.href.replace(/([A-Za-z]+)-[0-9]+/,"$1-"+idElt);
			var tmpCompleteDir = dir+'-'+idElt;
			if (numOnglet=="Work") {
			  tmpOnglet.onclick=function (event) {showDiv(event,tmpCompleteDir+"/Work");};}
			else if (numOnglet=="Historic") {
				tmpOnglet.onclick=function (event) {showDiv(event,tmpCompleteDir+"/Historic");};}
			else {
				tmpOnglet.onclick=function (event) {showDiv(event,tmpCompleteDir+"/");};}}}
	
    //Informations
    for(i=0;i<result.info.length;i++) { 
        s = s + '<dt class="description-terms-align-left">'+result.info[i].name+'</dt><dd class="editableDescriptionField">'+result.info[i].value;
        if ((result.info[i].name!="Name") && (result.info[i].name!="Project-id") && (result.info[i].name!="DataSet-id")&& (result.info[i].name!="Operator-id")&& (result.info[i].name!="Analysis-id")&& (result.info[i].name!="Result-id")) {
            s = s +'<span class="editZoneContextualMenu"></span>';
        }
        s = s +'</dd>';
    }
    s = s + '<dt></dt><dd></dd>';

    if (result.datas.length>0) {
        s = s + '<dt class="description-terms-align-left">Datas</dt><dd>';
        for(i=0;i<result.datas.length;i++) {
            s = s + "<a onclick=\"showDiv(event,'Datas/tmpDataSet');\" href=\"http://sakura.imag.fr/Datas/tmpDataSet\">"+result.datas[i].name+"</a>, ";
        }
        s = s + '</dd>';
    }

    if (result.process.length>0) {
        s = s + '<dt class="description-terms-align-left">Analyses processes</dt><dd>';
        for(i=0;i<result.process.length;i++) {
            s = s + "<a onclick=\"showDiv(event,'Analyses/tmpAnalysis');\" href=\"http://sakura.imag.fr/Analyses/tmpAnalysis\">"+result.process[i].name+"</a>, ";
        }
        s = s + '</dd>';
    }

    if (result.results.length>0) {
        s = s + '<dt class="description-terms-align-left">Results</dt><dd>';
        for(i=0;i<result.results.length;i++) {
            s = s + "<a onclick=\"showDiv(event,'Results/tmpResult');\" href=\"http://sakura.imag.fr/Results/tmpResult\">"+result.results[i].name+"</a>, ";
        }
        s = s + '</dd>';
    }
    s = s + '<a class="clPlusFieldButton" onclick="addField(this,event);" style="cursor: pointer; display:none;" title="add field"><span style="left:33%;" class="glyphicon glyphicon-plus" aria-hidden="true"></span></a>';
    s = s + '</dl>'
        + '<ul class="list-group col-md-6">'
        +   '<li class="list-group-item list-group-item-info"><strong>About <em>'+result.name+'</em> :</strong></li>'
        +   '<li class="list-group-item"><strong>Qualitative indicator:</strong> <span class="label label-primary pull-right">5</span></li>'
        +   '<li class="list-group-item"><strong>Volumetric indicator:</strong> <span class="label label-primary pull-right">5</span></li>'
        +   '<li class="list-group-item"><strong>Contact:</strong> <span class="label label-primary pull-right">'+result.userName+'@mail.uni</span></li>'
        + '</ul></div>';
		
    //Description
    s = s + '<div id="descriptionModalAbout'+elt+'" class="modal fade" role="dialog"><div class="modal-dialog">'
        + '<div class="modal-content"><div class="modal-header"><button type="button" class="close" data-dismiss="modal">&times;</button>'
        + '<h4 class="modal-title">Edit Explanation About</h4></div><div class="modal-body">';
    s = s + '<form><textarea name="editor1'+elt+'" id="editor1'+elt+'" rows="10" cols="60">'+result.description+'</textarea></form>';
    s = s + '</div><div class="modal-footer"><button type="button" class="btn btn-default" data-dismiss="modal" onClick="not_yet();">Save and close</button></div></div></div></div>'
    s = s + '<br /><br /><div class="panel panel-primary"><div class="panel-heading">'
        + '<table width="100%"><tbody><tr><td><h4 class="">'
        + '<font color="#ffffff">Explanation About '+result.name+"&nbsp;&nbsp;<img  width='40px' height='40px' src='media/"+imageEltInverse+"' alt='CC-BY-3.0 Wikipedia Gears'></img></h3>"+'</font></h4></td>'
        + '<td align="right"><button title="Modification of the Explanation About" class="btn btn-default btn-xs pull-right clPlusFieldButton" style="cursor: pointer; display:none;" data-toggle="modal" data-target="#descriptionModalAbout'+elt+'"><span class=" glyphicon glyphicon-pencil"></span></button></td>'
        + '</tr></tbody></table></div>'
        + '<div id="processShownAboutArea'+elt+'" class="panel-body">'+result.description+'</div></div>';

    //FileSystem
    if (result.fileSystem.length>0) {
        s = s + '<br /><br /><div class="well row"><h4 class="">Filesystem related to '+result.name+'</h4>'
            + '<table class="table table-bordered" id="fileBrowser"><thead>'
            + '<tr><th>Name</th><th colspan=2>Description</th></tr></thead><tbody>';
        for(i=0;i<result.fileSystem.length;i++) {
            s = s + '<tr><td><a onclick="not_yet();">'+result.fileSystem[i].filename+'</a></td><td>'+result.fileSystem[i].description+'</td></tr>';
        }
        s = s + '</tbody></table>';
        s = s + '<a class="clPlusFieldButton" onclick="addFile(this,event);" style="cursor: pointer; display:none;" title="add file"><span style="left:33%;" class="glyphicon glyphicon-plus" aria-hidden="true"></span></a>';
        s = s + '</div>';
    }

    //Comments
    s = s +'<hr style="border-bottom:5px solid;" /><br /><h3>Comments • '+result.comments.length+'</h3>' 
        + '<span class="glyphicon glyphicon-user"></span><form class="form-inline" role="form"><label>Add your Comment: </label><div class="form-group">'
        + '<textarea class="form-control" rows="1" id="comment'+elt+'">Your comments</textarea></div>'
        + '<div class="form-group"><button onclick="addComment(this,event,\'comment'+elt+'\');" class="btn btn-default"><span class="glyphicon glyphicon-plus"></span></button></div></form><hr />'
        + '<ul class="commentList">';
        
    for(i=0;i<result.comments.length;i++) {
        s = s + '<li><div class="commenterImage"><span class="glyphicon glyphicon-user"></span></div>'
            + '<div class="commentText"><p class="">'+result.comments[i].comment+'</p> '
            + '<span class="date sub-text">'+result.comments[i].name+' on '+result.comments[i].date+'</span></div></li><br />';
        }
    s = s + '<a href="javascript:eltRequestStub(\''+idDiv+'\',\''+elt+'\',false)" class="executeOnShow"> </a></div>'; //TODO : relance l'affichage aleatoire, à supprimer quand on aura la version avec bd
    document.getElementById(idDiv).innerHTML = s;
    editorAbout = CKEDITOR.replace( "editor1"+elt);
    editorAbout.on( "change", function( evt ) { 
        sDesc =  editorAbout.getData(); 
        document.getElementById("processShownAboutArea"+elt).innerHTML = sDesc;
    });
}

function eltRequestStub(idDiv,elt,bd) {
	if (elt == 'DataSet') {		
		idElt = window.location.toString().match(/[A-Za-z]+-[0-9]+/)[0].replace(/[A-Za-z]+-([0-9]+)/,"$1");
        ws_request('get_database_info', [+idElt], {}, function(db_info) {
	      var result = {'name': db_info.label, "userName":db_info.owner,
		    "info":[{"name":'DataSet-id',"value":idElt},{"name":"Name","value":db_info.label},{"name":"Owner","value":db_info.owner}],
			"datas":[], "process":[], "results":[], "comments":[],"fileSystem":[]}; 
	      buildEltStub(idDiv,result,elt);} ); }
    else { 
        result = eltStubAlea(elt); // objet {"name":_,"userName":_,"description":_, "info":[...],"datas":[...], "process":[...], "results":[...], "comments":[...],"fileSystem":[...]} détail : {  "name":eltName,"userName":userName,"info":infos, "datas":datas, "process":procs, "results":results, "comments":comments,"fileSystem":fs,"description":desc}
        buildEltStub(idDiv,result,elt);}
    return ;}
