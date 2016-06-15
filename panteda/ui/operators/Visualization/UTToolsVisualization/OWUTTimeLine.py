#!/usr/bin/python
#Orange Widget developped by Denis B. May, 2014. continued in 2015

"""
<name>TimeLine</name>
<icon>OWUTTimeLine_icons/OWUTTimeLine.svg</icon>
<description>Compute timeline graphics for sequences of user's actions (or any attribute)</description>
<priority>55</priority>
"""

import Orange
from OWWidget import *
import OWGUI
from plot.owplot import *
import webbrowser
import datetime
import os
import zipfile
import random
import string
import mimetypes
import urllib2
import httplib
import time
if not sys.path[len(sys.path)-1].endswith("/Management/UTToolsManagement"):
    tmpSettings = QSettings()
    path = str(tmpSettings.value("ut-path/path","unknown").toString()+"/Management/UTToolsManagement")
    sys.path.append(path)
from OWUTData import owutAjouteChoixAttribut
from OWUTData import owutChoixAttribut
from OWUTData import owutSynchroniseChoixAttribut
from OWUTData import owutInitChoixAttributEtVerifieConfig
from OWUTData import owutIndiceAttribut
from OWUTData import owutUtf2Ascii
from OWUTData import owutStrUtf



class OWUTTimeLine(OWWidget):
    settingsList = ['configTime','configGroupBy','configAttribute','configOtherInformation','exportResult','savExport','configExplanation']

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)
        self.data = None
        self.inputs = [("Table", Orange.data.Table, self.setData)]
        self.outputs = []
        settings = QSettings()
        val = settings.value("ut-login/login", "unknown")
        self.login = val.toString()
        self.path = unicode(settings.value("ut-path/path","unknown").toString())
        if self.login != "unknown":
            self.exportResult=False
            self.savExport=False
            self.showResult = True
            self.loadSettings()
            tabs = OWGUI.tabWidget(self.mainArea)
            tab = OWGUI.createTabPage(tabs, "Plot")
            self.graph = OWPlot(tab)
            self.graph.setAxisAutoScale(xBottom)
            self.graph.setAxisAutoScale(yLeft)
            tab.layout().addWidget(self.graph)
            tabLegend = OWGUI.createTabPage(tabs, "Legend")
            self.graphLegend = OWPlot(tabLegend)
            self.graphLegend.setAxisAutoScale(xBottom)
            self.graphLegend.setAxisAutoScale(yLeft)
            tabLegend.layout().addWidget(self.graphLegend)
            boxSettings = OWGUI.widgetBox(self.controlArea, "Configuration", addSpace=True)
            owutAjouteChoixAttribut(boxSettings,self,"configTime","Time (format: Y/m/d H:M:S)")
            owutAjouteChoixAttribut(boxSettings,self,"configGroupBy","Group By Attribute (default: user attribute)")
            owutAjouteChoixAttribut(boxSettings,self,"configAttribute","Attribute To Show (default: action attribute)")
            owutAjouteChoixAttribut(boxSettings,self,"configOtherInformation","Attribute for other information (default: parameter attribute)")
            OWGUI.checkBox(boxSettings, self, 'exportResult', "Export result (/tmp)")
            OWGUI.checkBox(boxSettings, self, 'savExport', "Save export on server (/etc)")
            OWGUI.button(self.controlArea, self, 'Apply', callback=self.compute)
            self.configExplanation = "Your comment/explanation."
            OWGUI.lineEdit(self.controlArea, self, "configExplanation", box="Any comment or explanation about your visualization?")
            self.showNothing()
            self.loadSettings()
        else:
            boxConnexion = OWGUI.widgetBox(self.controlArea, "Connection")
            label = OWGUI.label(boxConnexion, self, "Please connect to UnderTracks first! (File->Log on UT)" + self.login)

    def compute(self):
        if self.data != None:
            _Path = self.path
            mainOWUTTimeLine(_Path, owutChoixAttribut(self,"configTime"), owutChoixAttribut(self,"configGroupBy"),  owutChoixAttribut(self,"configAttribute"), owutChoixAttribut(self,"configOtherInformation"), self.data, self, self.exportResult, self.savExport)
            owutSynchroniseChoixAttribut(self)
            self.saveSettings()

    def setData(self, data, id=None):
        self.data = data
        if self.data != None:
            firstAttrOk = owutInitChoixAttributEtVerifieConfig(self,"configTime",data.domain)
            secondAttrOk = owutInitChoixAttributEtVerifieConfig(self,"configGroupBy",data.domain)
            thirdAttrOk = owutInitChoixAttributEtVerifieConfig(self,"configAttribute",data.domain)
            fourthAttrOk = owutInitChoixAttributEtVerifieConfig(self,"configOtherInformation",data.domain)
            if firstAttrOk and secondAttrOk and thirdAttrOk and fourthAttrOk:
                self.compute()

    def showNothing(self):
        self.graph.set_axis_labels(xBottom, "Nothing to show")
        self.graph.set_axis_labels(yLeft, "")
        self.graph.set_main_curve_data([],[], color_data=[], label_data = [], size_data=[], shape_data = [] )
        self.graph.replot()


def zipdir(ppath, pzipf):
    for root, dirs, files in os.walk(unicode(ppath)):
        for f in files:
            pzipf.write(os.path.join(root, f),f)

def random_string(length):
    return ''.join(random.choice(string.letters) for ii in range(length + 1))

def encode_multipart_data(data, files):
    boundary = random_string(30)

    def get_content_type(filename):
      return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

    def encode_field(field_name):
      return ('--' + boundary,'Content-Disposition: form-data; name="%s"' % field_name,'', str(data[field_name]))

    def encode_file(field_name):
      filename = files[field_name]
      return ('--' + boundary,'Content-Disposition: form-data; name="fichier"; filename="timeline.zip"','Content-Type: application/zip','', open(filename, 'rb').read())

    lines = []
    for name in data:
      lines.extend(encode_field(name))
    for name in files:
      lines.extend(encode_file(name))
    lines.extend(('--%s--' % boundary, ''))
    body = '\r\n'.join (lines)
    headers = {'content-type': 'multipart/form-data; boundary=' + boundary,'content-length': str(len(body))}
    return body, headers

def send_post(url, data, files):
    req = urllib2.Request(url)
    connection = httplib.HTTPSConnection(req.get_host())
    connection.request('POST', req.get_selector(), *encode_multipart_data (data, files))
    response = connection.getresponse()
    return response
    
def mainOWUTTimeLine(ppath, timeAttribute, groupByAttribute,  attributeToShow, otherInformation, data, gui, export, sav):
  indTimeAttribute = owutIndiceAttribut(timeAttribute,data.domain)
  indGroupByAttribute = owutIndiceAttribut(groupByAttribute,data.domain)
  indAttributeToShow = owutIndiceAttribut(attributeToShow,data.domain)
  indOtherInformation = owutIndiceAttribut(otherInformation,data.domain)
  if (indTimeAttribute==-1) or (indGroupByAttribute==-1) or (indAttributeToShow==-1) or (indOtherInformation==-1):
    return
  gui.graph.set_axis_labels(xBottom, "Prepare the show (wait end of computation)")
  gui.graph.set_axis_labels(yLeft, "")
  gui.graph.set_main_curve_data([],[], color_data=[], label_data = [], size_data=[], shape_data = [] )
  gui.graph.replot()
  if export:
    fileNomAlea = 'UT_HTML_timeLine'+str(random.getrandbits(100))
    if sav:
        racine = ppath + os.sep + 'etc' #sera conserve sur le serveur
    else:
        racine = ppath + os.sep + 'tmp'
    try:
      os.mkdir(racine)
    except:
      racineCree = -1
    os.mkdir(racine+os.sep+fileNomAlea.capitalize())
    f = open(racine+os.sep+fileNomAlea.capitalize()+os.sep+fileNomAlea+'.html','w')
    messageEnTete = """<html>
<head>
<style type='text/css'>"""
  lesStyles = {}
  lesNomDesCouleurs=[]
  lesValeursDesCouleurs=[]
  lesXDesCouleurs=[]
  lesYDesCouleurs=[]
  unYDeCouleur = 0
  for ligne in data: #recuperer les attributs pour faire les styles de attributeToShow
    lesStyles[ligne[indAttributeToShow].value]=1
  messageStyles = " "
  for attribut in lesStyles.keys():
    if attribut=="":
      continue
    tmpRAttribute = random.randint(0,255)
    tmpGAttribute = random.randint(0,255)
    tmpBAttribute = random.randint(0,255)
    lesStyles[attribut]=[tmpRAttribute,tmpGAttribute,tmpBAttribute]
    lesValeursDesCouleurs.append(QColor(tmpRAttribute,tmpGAttribute,tmpBAttribute))
    lesNomDesCouleurs.append(str(attribut))
    lesXDesCouleurs.append(1)
    unYDeCouleur = unYDeCouleur + 1
    lesYDesCouleurs.append(unYDeCouleur)
    if export:
      messageStyles += """
span.autourDe%s {width: 4px; overflow: hidden; display : inline-block;}
span.valDe%s {display : inline-block; background-color: rgb(%d,%d,%d); height: 20px; width: 4px;}
""" % (owutUtf2Ascii(attribut), owutUtf2Ascii(attribut), tmpRAttribute, tmpGAttribute, tmpBAttribute)
    messageLegende = "<h2>Legend</h2><h3>Actions</h3>"
    numEntite = 0;
    for attribut in lesStyles.keys():
      if attribut=="":
        continue
      messageLegende += """
<span class="autourDe%s"><span class="valDe%s" style="width:10px;"> </span></span> : %s
(<a href='javascript:montreCache(%s)'>visible</a> <span id="idConfigVisible%s"><!--inline-block--></span>,
<a href='javascript:setColor(%s)'>color</a> <span id="idConfigColor%s"><!--inline-block--></span>) -
""" % (owutUtf2Ascii(attribut), owutUtf2Ascii(attribut), owutUtf2Ascii(attribut),str(numEntite),str(numEntite),str(numEntite),str(numEntite))
      numEntite = numEntite + 1
    messageIntermediaire = """
</style>
<script type='text/javascript'>
"""
    coeurMessageData = []
    #precSecs = -1
    #precGroup = data[0][indGroupByAttribute].value
  minTemps = -1
  lesX=[]
  lesY=[]
  lesCouleurs=[]
  #lesNoms=[]
  laListeDesNoms=[]
  unX = 0
  unY = 0
  precUser="UTNoUserYet"
  listeDesFormats = ["%Y-%m-%dT%H:%M:%S","%Y-%m-%d %H:%M:%S","%Y/%m/%d %H:%M:%S","%d-%m-%Y %H:%M:%S","%d/%m/%Y %H:%M:%S","%d/%m/%y %H:%M:%S"]
  #rech format
  infFormatCandidat = -1
  if len(data)>2:
    indFormatsCandidats=[-1 for i in range(3)]
    for i in range(3):
      strTempsCandidatRechFormat = owutStrUtf(data[i][indTimeAttribute].value)
      for j in range(len(listeDesFormats)):
        try:
          tempsCourant = time.strptime(strTempsCandidatRechFormat,listeDesFormats[j])
          indFormatsCandidats[i] = j
          break
        except:
          tempsCourant = -1
    if (indFormatsCandidats[0]==indFormatsCandidats[1]) and (indFormatsCandidats[0]==indFormatsCandidats[2]):
      infFormatCandidat = indFormatsCandidats[0]
    else:
      infFormatCandidat = -1
  for ligne in data:
    tempsCourant = -1
    strTempsCandidat = owutStrUtf(ligne[indTimeAttribute].value)
    if infFormatCandidat!=-1:
      try:
        tempsCourant = time.strptime(strTempsCandidat,listeDesFormats[infFormatCandidat])
      except:
        tempsCourant = -1
        infFormatCandidat = -1
    if (tempsCourant == -1):
      try:
        tempsCourant = time.strptime(strTempsCandidat,"%Y-%m-%dT%H:%M:%S")
      except:
        tempsCourant = -1
    if (tempsCourant == -1):
      try:
        tempsCourant = time.strptime(strTempsCandidat,"%Y-%m-%d %H:%M:%S")
      except:
        tempsCourant = -1
    if tempsCourant == -1:
      try:
        tempsCourant = time.strptime(strTempsCandidat,"%Y/%m/%d %H:%M:%S")
      except:
        tempsCourant = -1
    if (tempsCourant == -1):
      try:
        tempsCourant = time.strptime(strTempsCandidat,"%d-%m-%Y %H:%M:%S")
      except:
        tempsCourant = -1        
    if tempsCourant == -1:
      try:
        tempsCourant = time.strptime(strTempsCandidat,"%d/%m/%Y %H:%M:%S")
      except:
        tempsCourant = -1
    if tempsCourant == -1:
      try:
       tempsCourant = time.strptime(strTempsCandidat,"%d/%m/%y %H:%M:%S")
      except:
        tempsCourant = -1
    if tempsCourant == -1:
      tempsCourant = time.strptime("1900/01/01 00:00:00","%Y/%m/%d %H:%M:%S")
    secsCourant =  tempsCourant.tm_yday*3600*24 + tempsCourant.tm_hour * 3600 + tempsCourant.tm_min * 60 + tempsCourant.tm_sec
    if minTemps == -1:
        minTemps = secsCourant
    elif secsCourant<minTemps:
        minTemps = secsCourant
    #if precSecs == -1:
    #  precSecs = secsCourant -10
    if precUser == "UTNoUserYet":
        unX = 0
        unY = 0
        precUser = ligne[indGroupByAttribute].value
        laListeDesNoms.append(precUser)
    elif ligne[indGroupByAttribute].value == precUser:
        unX = unX +1
    else:
        unX = 0
        unY = unY + 1
        precUser = ligne[indGroupByAttribute].value
        laListeDesNoms.append(precUser)
    #lesNoms.append(ligne[indGroupByAttribute].value)
    if ligne[indAttributeToShow].value!="":
        lesX.append(unX)
        lesY.append(unY)
        lesCouleurs.append(QColor(lesStyles[ligne[indAttributeToShow].value][0],lesStyles[ligne[indAttributeToShow].value][1],lesStyles[ligne[indAttributeToShow].value][2]))
        if export:
            coeurMessageData.append("%s', '%s', '%s', '%s" % (str(secsCourant), owutUtf2Ascii(ligne[indGroupByAttribute].value), owutUtf2Ascii(ligne[indAttributeToShow].value), owutUtf2Ascii(ligne[indOtherInformation].value)))
  gui.graph.set_axis_labels(xBottom, "                  --- tempus fugit --->                                                                        ")
  gui.graph.set_axis_labels(yLeft, laListeDesNoms)
  gui.graph.set_main_curve_data(lesX, lesY, color_data=lesCouleurs, label_data = [], size_data=[10], shape_data = [OWPoint.Rect] )
  gui.graph.replot()
  gui.graphLegend.set_axis_labels(xBottom, "leg.")
  gui.graphLegend.set_axis_labels(yLeft, lesNomDesCouleurs)
  gui.graphLegend.set_main_curve_data(lesXDesCouleurs, lesYDesCouleurs, color_data=lesValeursDesCouleurs, label_data = [], size_data=[10], shape_data = [OWPoint.Rect] )
  gui.graphLegend.replot()
  if export:
    messageColle = "'],\n['"
    messageData = "minTemps="+str(minTemps)+";\ndata = [['" + messageColle.join(coeurMessageData) + "']];"
    messageFin = """

function setColor(NoAt) {
rep=prompt("Hue value (20:Red, 90:Yellow, 120:Green, 240:Blue)?");
if (rep) {
  document.styleSheets[0].cssRules[1+2*NoAt].style["background"]="hsl("+(10*rep+rep*rep)/300+",95%,50%)";
  document.getElementById('idConfigColor'+NoAt).innerHTML= "<!--"+rep+"-->";}
return;}

function setColorInit(NoAt) {
tmpStr = document.getElementById('idConfigColor'+NoAt).innerHTML;
rep = tmpStr.substr(4,tmpStr.length-7);
if (rep!="init") {
  document.styleSheets[0].cssRules[1+2*NoAt].style["background"]="hsl("+(10*rep+rep*rep)/300+",95%,50%)";}
return;}

function montreCache(NoAt) {
if (document.styleSheets[0].cssRules[NoAt*2].style["display"]=="none") {
  modeMontreCache="inline-block";}
else {modeMontreCache="none";}
document.styleSheets[0].cssRules[NoAt*2].style["display"]=modeMontreCache;
document.styleSheets[0].cssRules[1+2*NoAt].style["display"]=modeMontreCache;
document.getElementById('idConfigVisible'+NoAt).innerHTML= "<!--"+modeMontreCache+"-->";
return;}

function setMontreCacheInit(NoAt) {
tmpStr = document.getElementById('idConfigVisible'+NoAt).innerHTML;
modeMontreCache = tmpStr.substr(4,tmpStr.length-7);
document.styleSheets[0].cssRules[NoAt*2].style["display"]=modeMontreCache;
document.styleSheets[0].cssRules[1+2*NoAt].style["display"]=modeMontreCache;}


function placeAvant(noGroupe) {
tmpStr = document.getElementById('idConfigGroupe'+noGroupe).innerHTML;
noDiv = (1*tmpStr.substr(4,tmpStr.length-7));
noGroupeAvant = 0;
for(;noGroupeAvant<nbGroupe;noGroupeAvant++) {
  tmpStr = document.getElementById('idConfigGroupe'+noGroupeAvant).innerHTML;
  if ((noDiv-1) == (1*tmpStr.substr(4,tmpStr.length-7))) {
    break;}}
if (nbGroupe==noGroupeAvant) {
  return;}
if (noDiv>0) {
  var tmpDiv1 = document.getElementById('idDivGroupe'+noDiv).innerHTML;
  var tmpDiv2 = document.getElementById('idDivGroupe'+(noDiv-1)).innerHTML;
  document.getElementById('idDivGroupe'+noDiv).innerHTML = tmpDiv2;
  document.getElementById('idDivGroupe'+(noDiv-1)).innerHTML = tmpDiv1;
  document.getElementById('idConfigGroupe'+noGroupe).innerHTML= "<!--"+(noDiv-1)+"-->";
  document.getElementById('idConfigGroupe'+noGroupeAvant).innerHTML= "<!--"+noDiv+"-->";}
return;}

function placeApres(noGroupe) {
tmpStr = document.getElementById('idConfigGroupe'+noGroupe).innerHTML;
noDiv = (1*tmpStr.substr(4,tmpStr.length-7));
noGroupeApres = 0;
for(;noGroupeApres<nbGroupe;noGroupeApres++) {
  tmpStr = document.getElementById('idConfigGroupe'+noGroupeApres).innerHTML;
  if ((noDiv+1) == (1*tmpStr.substr(4,tmpStr.length-7))) {
    break;}}
if (nbGroupe==noGroupeApres) {
  return;}
if (noDiv<nbGroupe-1) {
  var tmpDiv1 = document.getElementById('idDivGroupe'+noDiv).innerHTML;
  var tmpDiv2 = document.getElementById('idDivGroupe'+(noDiv+1)).innerHTML;
  document.getElementById('idDivGroupe'+noDiv).innerHTML = tmpDiv2;
  document.getElementById('idDivGroupe'+(noDiv+1)).innerHTML = tmpDiv1;
  document.getElementById('idConfigGroupe'+noGroupe).innerHTML= "<!--"+(noDiv+1)+"-->";
  document.getElementById('idConfigGroupe'+noGroupeApres).innerHTML= "<!--"+noDiv+"-->";}
return;}

var nbGroupe = 0;
var nomsGroupes = [];

function showData(modeTimeSpan,modeAlignment,modePassageALaLigne) {
nbGroupe = 0;
if ((modeTimeSpan=="init")&&(modeAlignment=="init")&&(modePassageALaLigne=="init")) {
  for(var i=0;i<document.styleSheets[0].cssRules.length/2;i++) {
    setMontreCacheInit(i);
    setColorInit(i);}}

if (modeTimeSpan=='init') {
  tmpStr = document.getElementById('idConfigTimeSpan').innerHTML;
  modeTimeSpan = tmpStr.substr(4,tmpStr.length-7);}
else {
  document.getElementById('idConfigTimeSpan').innerHTML = "<!--"+modeTimeSpan+"-->";}

if (modeAlignment=='init') {
  tmpStr = document.getElementById('idConfigAlignment').innerHTML;
  modeAlignment = tmpStr.substr(4,tmpStr.length-7);}
else {
  document.getElementById('idConfigAlignment').innerHTML = "<!--"+modeAlignment+"-->";}

if (modePassageALaLigne=='init') {
  tmpStr = document.getElementById('idConfigLineWrap').innerHTML;
  modePassageALaLigne = tmpStr.substr(4,tmpStr.length-7);}
else {
  document.getElementById('idConfigLineWrap').innerHTML = "<!--"+modePassageALaLigne+"-->";}

var shownData = "";
for(var i=0;i<data.length;i++) {
  if ((i==0) || data[i][1]!=data[i-1][1]) {
    if (i>0) {
      shownData += "</div>";}
	if (modePassageALaLigne=="normalWindowWrapped") {
	  shownData += "<div id='idDivGroupe"+nbGroupe+"'>";}
	else {
	  shownData += "<div id='idDivGroupe"+nbGroupe+"' style='display: inline-block; width:10000px;  white-space: nowrap; overflow:hidden;'>";}
    nomsGroupes.push(data[i][1]);
    shownData += '<sup><a style="position: relative; top: -6px; text-decoration:none;" href="javascript:placeAvant('+nbGroupe+')">&#8743;</a></sup><sub style="position: relative; left: -10.5px;"><a style="text-decoration:none;" href="javascript:placeApres('+nbGroupe+')">&#8744;</a></sub>';
    nbGroupe = nbGroupe + 1;
    if (modeAlignment=='sessionStartAligned') {
      tpsPrec = data[i][0]-10;
      shownData += "<span style='display : inline-block; width:100px; overflow:hidden;' title='"+data[i][1]+"'>"+data[i][1]+"</span>:";}
    else {
      tpsPrec = minTemps;
      if ((data[i][0]-tpsPrec)>3600) {
        nH = Math.floor((data[i][0]-tpsPrec)/3600);
        shownData += "<span style='display : inline-block; width:100px; overflow:hidden;' title='"+data[i][1]+"(+"+nH+"h)'>"+data[i][1]+"(+"+nH+"h)</span>:";
        tpsPrec = minTemps+nH*3600;}
      else {
        shownData += "<span style='display : inline-block; width:100px; overflow:hidden;' title='"+data[i][1]+"'>"+data[i][1]+"</span>:";}
      shownData +='<span class="spanDeBut" style="width:'+(data[i][0]-tpsPrec)+'px; height:5px; display : inline-block; background-color: rgb(222,222,222);">&nbsp;</span>';
      tpsPrec = data[i][0]-10;}}
  if (data[i][0]==tpsPrec) {
    data[i][0]=tpsPrec-1;}
  if (data[i][2]=="") {
    continue;}
  if (modeTimeSpan=='events') {
    shownData += '<span class="autourDe'+data[i][2]+'" style="width:5px;"><span title="'+data[i][2]+'('+data[i][3]+')'+'" class="valDe'+data[i][2]+'" style="width:3px;"></span></span><!-- '
+' -->';}
  else if (modeTimeSpan=='timeStampedEvents') {
    shownData += '<span class="autourDe'+data[i][2]+'" style="width:'+(data[i][0]-tpsPrec)+'px;"><span title="'+data[i][2]+'('+data[i][3]+')'+'" class="valDe'+data[i][2]+'" style="width:3px;"></span></span><!-- '
+' -->';}
  else {
    shownData += '<span class="autourDe'+data[i][2]+'" style="width:'+(data[i][0]-tpsPrec)+'px;"><span title="'+data[i][2]+'('+data[i][3]+')'+'" class="valDe'+data[i][2]+'" style="width:'+(data[i][0]-tpsPrec)+'px;"></span></span><!-- '
+' -->';}
  tpsPrec = data[i][0]; }
shownData += "</div>";
document.getElementById('idTimelines').innerHTML = shownData;

var shownGroups = "";
var htmlGroupe = []
var ordreGroupe = []
if (document.getElementById('idDivGroupes').innerHTML.length > 10) { //recuperation des positions des groupes
  for(var i=0;i<nbGroupe;i++) {
    tmpStr = document.getElementById('idConfigGroupe'+i).innerHTML;
    tmpNoGroupe = 1*tmpStr.substr(4,tmpStr.length-7);
    ordreGroupe.push(tmpNoGroupe);
    if (i!=tmpNoGroupe) {
      htmlGroupe.push(document.getElementById('idDivGroupe'+i).innerHTML);}
    else {
      htmlGroupe.push("idem");}}
  for(var i=0;i<nbGroupe;i++) {
    if (i!=ordreGroupe[i]) {
      document.getElementById('idDivGroupe'+ordreGroupe[i]).innerHTML =htmlGroupe[i];}}}
else { //init des positions des groupes
  for(var i=0;i<nbGroupe;i++) {
    shownGroups += nomsGroupes[i]+ '(<a href="javascript:placeAvant('+i+')">&#8656;</a> <a href="javascript:placeApres('+i+')">&#8658;</a>) <span id="idConfigGroupe'+i+'"><!--'+i+'--></span>,';}
  document.getElementById('idDivGroupes').innerHTML = shownGroups;}
  
if (modeTimeSpan=='events')  { //echelle des temps
  baseLine = " ";}
else {
  baseLine = "<span style='display : inline-block; width:10000px; white-space: nowrap; overflow:hidden;'>Time (minute):";
  for(var i=0;i<121;i++) {
    if (i%5==0) {
      baseLine += '<span style="display : inline-block; width:60px;"><span style="display : inline-block; width:1px;">'+i+'</span></span>';}
    else {
      baseLine += '<span style="display : inline-block; width:60px;"><span style="display : inline-block; width:1px; background-color: rgb(111,111,111);">&nbsp;</span></span>';}}
  baseLine += '</span>';}
document.getElementById('idDivBaseLine').innerHTML = baseLine;
return;}
 </script></head>
<body onload='showData("init","init","init")'>
<h1>TimeLine</h1>
<h2>Operations</h2>
<a href="javascript:showData('events','init','init')">Events</a>, 
<a href="javascript:showData('timeStampedEvents','init','init')">TimeStampedEvents</a>, 
<a href="javascript:showData('spannedTimeStampedEvents','init','init')">SpannedTimeStampedEvents</a>.
<span id="idConfigTimeSpan"><!--events--></span><br>
<a href="javascript:showData('init','sessionStartAligned','init')">SessionStartAligned</a>, 
<a href="javascript:showData('init','universalTimeAligned','init')">UniversalTimeAligned</a>, 
<span id="idConfigAlignment"><!--sessionStartAligned--></span><br>
<a href="javascript:showData('init','init','largeWindowOverflowed')">LargeWindowOverflowed</a>, 
<a href="javascript:showData('init','init','normalWindowWrapped')">NormalWindowWrapped</a>, 
<span id="idConfigLineWrap"><!--LargeWindowOverflowed--></span><br>
\n"""
    f.write(messageEnTete+messageStyles+messageIntermediaire+messageData+messageFin+messageLegende+"\n<div id='idDivGroupes' style='display:none;'> </div>\n<h2>TimeLines</h2>\n<div id='idDivBaseLine'> </div>\n<div id='idTimelines'></div>\n</body>\n</html>\n")
    f.close()
    #webbrowser.open_new_tab(racine+os.sep+fileNomAlea.capitalize()+os.sep+fileNomAlea+'.html')
    zipf = zipfile.ZipFile(racine+os.sep+fileNomAlea+'.zip', 'w')
    zipdir(racine+os.sep+fileNomAlea.capitalize()+os.sep, zipf)
    zipf.close()
    post_rep = send_post('https://undertracks.imag.fr/scripts/OrangeScripts/RecordZipFile.php', {"submit": "Envoyer", "folder": fileNomAlea.capitalize()}, {'fichier': racine+os.sep+fileNomAlea+'.zip'})
    webbrowser.open_new_tab('https://undertracks.imag.fr/tmp/'+fileNomAlea.capitalize()+'/'+fileNomAlea+'.html')                                                                                               #"login": self.login, ?
    try:
      os.remove(racine+os.sep+fileNomAlea.capitalize()+os.sep+fileNomAlea+'.html')
      os.rmdir(racine+os.sep+fileNomAlea.capitalize()+os.sep)
      os.remove(racine+os.sep+fileNomAlea+'.zip')
    except:
      print "Unexpected error : unable to clean tmp directory"
  return
 