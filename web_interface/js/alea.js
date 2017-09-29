// LIG Sept 2017


/*    Génération aléatoire de base    */
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
    return alea[Math.floor(Math.random() * alea.length)]
}


function numAlea(base,over) {
    return base+(Math.floor(Math.random() * over));
}


function dateAlea() {
    return ''+Math.floor(1+Math.random() * 10.5)+'/'+Math.floor(2000+Math.random() * 17);
}


function fullNameAlea() {
    return firstNamesAlea[Math.floor(Math.random() * firstNamesAlea.length)]+"_"
        + lastNamesAlea[Math.floor(Math.random() * lastNamesAlea.length)]+"_"
        + propsAlea[Math.floor(Math.random() * propsAlea.length)]+"_"
        + lastDigitsAlea[Math.floor(Math.random() * lastDigitsAlea.length)];
}


function fullProcNameAlea() {
    return firstProcNamesAlea[Math.floor(Math.random() * firstProcNamesAlea.length)]
        + lastNamesAlea[Math.floor(Math.random() * lastNamesAlea.length)]+
        + lastDigitsAlea[Math.floor(Math.random() * lastDigitsAlea.length)];
}


function shortTextAlea() {
    return firstWordsAlea[Math.floor(Math.random() * firstWordsAlea.length)]+" "
        + otherWordsAlea[Math.floor(Math.random() * otherWordsAlea.length)]+" "
        + otherWordsAlea[Math.floor(Math.random() * otherWordsAlea.length)]+" "
        + otherWordsAlea[Math.floor(Math.random() * otherWordsAlea.length)]+", "
        + otherWordsAlea[Math.floor(Math.random() * otherWordsAlea.length)]+" "
        + otherWordsAlea[Math.floor(Math.random() * otherWordsAlea.length)]+" "
        + otherWordsAlea[Math.floor(Math.random() * otherWordsAlea.length)]+".";
}


function boolAlea(trueProportion) {
    if (Math.random()<trueProportion) {
        return "true";
    }
    else {
        return "false";
    }
}


/*   Génération aléatoire niveau 2 */

function listStubAlea(n) {
	var result=new Array();
        for(i=0;i<n;i++) {
            result.push({   "name":fullNameAlea(),
                            "id":numAlea(100,100),
                            "tags":aleaAlea(firstNamesAlea),
                            "shortDesc":shortTextAlea(),
                            "date":dateAlea(),
                            "modif":dateAlea(),
                            "owner":aleaAlea(usersAlea),
                            "isViewable":boolAlea(0.7),
                            "isEditable":boolAlea(0.3)});}       
    return result;}

	
function historyStubAlea(n) {
        var result=new Array();
        var d = new Date();
        for(i=0;i<n;i++) {
            result.push({"dateVersion":d.toString(),"userName":aleaAlea(usersAlea),"msgVersion":shortTextAlea()});
            d.setDate(d.getDate()-Math.random());}
    return result;}


function eltStubAlea(elt) {
        eltName = fullNameAlea();
        userName = aleaAlea(usersAlea)
        infos = new Array();
        ninfo = Math.floor(Math.random() * 10);
        infos.push({"name":"Name","value":eltName});
		if (window.location.toString().match(/[A-Za-z]+-[0-9]+/)) {
		  infos.push({"name":elt+"-id","value":window.location.toString().match(/[A-Za-z]+-[0-9]+/)[0].replace(/[A-Za-z]+-([0-9]+)/,"$1")});}
		else {
          infos.push({"name":elt+"-id","value":numAlea(100,100)});}    
        infos.push({"name":"Description","value":shortTextAlea()});
        infos.push({"name":"Owner","value":userName});        
        for(i=0;i<ninfo;i++) {
            infos.push({"name":aleaAlea(propsAlea),"value":aleaAlea(valsAlea)});}        
        datas = new Array();
        ndatas = Math.floor((Math.random() * 4 + Math.random() + 2)/3);
        for(i=0;i<ndatas;i++) {
            datas.push({"name":fullNameAlea()});}        
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
	    desc = shortTextAlea()+' '+shortTextAlea()+' '+shortTextAlea()+' '+shortTextAlea()+'<br /> '+shortTextAlea()+' '+shortTextAlea()+' '+shortTextAlea()+'<br /><br />'
            +shortTextAlea()+' '+shortTextAlea()+' '+shortTextAlea()+' '+shortTextAlea()+' '+shortTextAlea()+'<br />'+shortTextAlea()+' '+shortTextAlea()+' '+shortTextAlea()
			+' '+shortTextAlea()+' '+shortTextAlea()+'<br />'+shortTextAlea()+' '+shortTextAlea()+' '+shortTextAlea()+'<br /><br />'+ '<ul><li>'+shortTextAlea()+'</li><li>'
			+shortTextAlea()+'</li><li>'+shortTextAlea()+'</li></ul>'+shortTextAlea()+' '+shortTextAlea()+' '+shortTextAlea()+' '+shortTextAlea()+' '+shortTextAlea()+'<br />'
			+shortTextAlea()+' '+shortTextAlea()+' '+shortTextAlea()+'<br /><br />';
        var result = {  "name":eltName,"userName":userName,
                        "info":infos, "datas":datas, "process":procs, "results":results, 
                        "comments":comments,"fileSystem":fs,"description":desc};
  return result;}
