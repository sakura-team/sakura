#!/usr/bin/python
#Orange Widget developped by Denis B. May, 2014.

"""
<name>PatternTimeLine</name>
<icon>OWUTPatternTimeLine_icons/OWUTPatternTimeLine.svg</icon>
<description>Compute timeline graphics for pattern found in the sequences of user's actions</description>
<priority>56</priority>
"""

import Orange
from OWWidget import *
import OWGUI
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


class OWUTPatternTimeLine(OWWidget):
    settingsList = ['configTime','configGroupBy','configAttribute','configPattern','configExplanation']

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
            boxSettings = OWGUI.widgetBox(self.controlArea, "Configuration", addSpace=True)
            owutAjouteChoixAttribut(boxSettings,self,"configTime","Time (format: Y/m/d H:M:S)")
            owutAjouteChoixAttribut(boxSettings,self,"configGroupBy","Group By Attribute (default: user attribute)")
            owutAjouteChoixAttribut(boxSettings,self,"configAttribute","Attribute To Show (default: action attribute)")
            owutAjouteChoixAttribut(boxSettings,self,"configPattern","Pattern (default: pattern attribute)")
            OWGUI.button(self.controlArea, self, 'Apply', callback=self.compute)
            self.configExplanation = "Your comment/explanation."
            OWGUI.lineEdit(self.controlArea, self, "configExplanation", box="Any comment or explanation about your visualization?")
            self.loadSettings()
        else:
            boxConnexion = OWGUI.widgetBox(self.controlArea, "Connection")
            label = OWGUI.label(boxConnexion, self, "Please connect to UnderTracks first! (File->Log on UT)" + self.login)

    def compute(self):
        if self.data != None:
            _Path = self.path
            mainOWUTPatternTimeLine(_Path, owutChoixAttribut(self,"configTime"), owutChoixAttribut(self,"configGroupBy"),  owutChoixAttribut(self,"configAttribute"), owutChoixAttribut(self,"configPattern"), self.data)
            owutSynchroniseChoixAttribut(self)
            self.saveSettings()

    def setData(self, data, id=None):
        self.data = data
        if self.data != None:
            configOk1 = owutInitChoixAttributEtVerifieConfig(self,"configTime",data.domain)
            configOk2 = owutInitChoixAttributEtVerifieConfig(self,"configGroupBy",data.domain)
            configOk3 = owutInitChoixAttributEtVerifieConfig(self,"configAttribute",data.domain)
            configOk4 = owutInitChoixAttributEtVerifieConfig(self,"configPattern",data.domain)
            if configOk1 and configOk2 and configOk3 and configOk4:
                self.compute()

# def idf_securise(strIn):
#     strOut = ""
#     for i in range(len(strIn)):
#         code = ord(strIn[i])
#         if (((code>64)and(code<91))  or ((code>96)and(code<123))  or (code==95) or ((code>47)and(code<58))):
#             strOut += strIn[i]
#         else:
#             strOut += "-"+str(code)+"--"  #codes - et -- a remplacer par &# et ; en cas d'affichage html
#     return strOut

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
    
def mainOWUTPatternTimeLine(ppath, timeAttribute, groupByAttribute,  attributeToShow, patternToShow , data):
  indTimeAttribute = owutIndiceAttribut(timeAttribute, data.domain)
  if indTimeAttribute==-1:
    return
  indGroupByAttribute = owutIndiceAttribut(groupByAttribute, data.domain)
  if indGroupByAttribute==-1:
    return
  indAttributeToShow = owutIndiceAttribut(attributeToShow, data.domain)
  if indAttributeToShow==-1:
    return
  indPatternToShow = owutIndiceAttribut(patternToShow, data.domain)
  if indPatternToShow==-1:
    return
  fileNomAlea = 'UT_HTML_patternTimeLine'+str(random.getrandbits(100))
  racine = ppath + os.sep + 'tmp'
  try:
    os.mkdir(racine)
  except:
    racineCree = -1
  os.mkdir(racine+os.sep+fileNomAlea.capitalize())
  f = open(racine+os.sep+fileNomAlea.capitalize()+os.sep+fileNomAlea+'.html','w')
  messageEnTete = """<html>
<head>
<style type='text/css'>
span.lignesDeBaseBlancMoyen {width: 4px; overflow: hidden; display : inline-block; background-color: rgb(255,255,255); height: 2px;}
span.lignesDeBaseBlancEpais {width: 4px; overflow: hidden; display : inline-block; background-color: rgb(255,255,255); height: 4px;}
span.lignesDeBaseNoirFin {width: 4px; overflow: hidden; display : inline-block; background-color: rgb(0,0,0); height: 1px;}
"""
  lesStyles = {}
  for ligne in data: #recuperer les attributs pour faire les styles de attributeToShow
    lesStyles[ligne[indAttributeToShow].value]=1
  messageStyles = " "
  for attribut in lesStyles.keys():
    if attribut=="":
      continue
    tmpRAttribute = random.randint(0,255)
    tmpGAttribute = random.randint(0,255)
    tmpBAttribute = random.randint(0,255)
    messageStyles += """
span.autourDe%s {width: 4px; overflow: hidden; display : inline-block;}
span.valDe%s {display : inline-block; background-color: rgb(%d,%d,%d); height: 20px; width: 4px;}
""" % (owutUtf2Ascii(attribut), owutUtf2Ascii(attribut), tmpRAttribute, tmpGAttribute, tmpBAttribute)
  lesAutresStyles = {}
  for ligne in data: #recuperer les attributs pour faire les styles de pattern
    lesAutresStyles[ligne[indPatternToShow].value]=1
  for pattern in lesAutresStyles.keys():
    if pattern=="":
      continue
    tmpRAttribute = random.randint(0,255)
    tmpGAttribute = random.randint(0,255)
    tmpBAttribute = random.randint(0,255)
    messageStyles += """
span.autourDe%s {width: 4px; overflow: hidden; display : inline-block;}
span.valDe%s {display : inline-block; background-color: rgb(%d,%d,%d); height: 8px; width: 2px;}
""" % (owutUtf2Ascii(pattern), owutUtf2Ascii(pattern), tmpRAttribute, tmpGAttribute, tmpBAttribute)
  messageLegende = "<h2>Legends</h2>\n<h3>Patterns</h3>\n"
  cpt = 0
  for pattern in lesAutresStyles.keys():
    if pattern=="":
      continue
    messageLegende += """
<span class="autourDe%s"><span class="valDe%s" style="width:10px;"></span></span> : %s -
""" % (owutUtf2Ascii(pattern), owutUtf2Ascii(pattern), owutUtf2Ascii(pattern))
    if cpt == 10:
        messageLegende += """
<script>
function changeDisplayPattern() {
if (document.getElementById("ellipsePattern").style["display"]=="inline") {
  document.getElementById("ellipsePattern").style["display"]="none";
  document.getElementById("inExtensoPattern").style["display"]="inline";
  }
else {
  document.getElementById("ellipsePattern").style["display"]="inline";
  document.getElementById("inExtensoPattern").style["display"]="none";}
}
</script>
<div id="ellipsePattern" style="display:inline;"> (<a href="javascript:changeDisplayPattern()">...</a>)</div>
<div id="inExtensoPattern" style="display:none;">
"""
    cpt = cpt+1
  if cpt > 10:
        messageLegende += """
 (<a href="javascript:changeDisplayPattern()">-</a>)</div>
"""
  messageLegende += "<h3>Actions</h3>"
  cpt = 0
  for attribut in lesStyles.keys():
    if attribut=="":
      continue
    messageLegende += """
<span class="autourDe%s"><span class="valDe%s" style="width:10px;"> </span></span> : %s -
""" % (owutUtf2Ascii(attribut), owutUtf2Ascii(attribut), owutUtf2Ascii(attribut))
    if cpt == 10:
        messageLegende += """
<script>
function changeDisplayAction() {
if (document.getElementById("ellipseAction").style["display"]=="inline") {
  document.getElementById("ellipseAction").style["display"]="none";
  document.getElementById("inExtensoAction").style["display"]="inline";
  }
else {
  document.getElementById("ellipseAction").style["display"]="inline";
  document.getElementById("inExtensoAction").style["display"]="none";}
}
</script>
<div id="ellipseAction" style="display:inline;"> (<a href="javascript:changeDisplayAction()">...</a>)</div>
<div id="inExtensoAction" style="display:none;">
"""
    cpt = cpt+1
  if cpt > 10:
        messageLegende += """
 (<a href="javascript:changeDisplayAction()">-</a>)</div>
"""
  messageIntermediaire = """
</style>
<script type='text/javascript'>
"""
  coeurMessageData = []
  precSecs = -1
  secsCourant = 0
  precGroup = data[0][indGroupByAttribute].value
  for ligne in data:
    # try:
    #   tempsCourant = time.strptime(ligne[indTimeAttribute].value,"%Y/%m/%d %H:%M:%S")
    # except:
    #   tempsCourant = -1
    # if tempsCourant == -1:
    #   try:
    #     tempsCourant = time.strptime(ligne[indTimeAttribute].value,"%d/%m/%Y %H:%M:%S")
    #   except:
    #     tempsCourant = -1
    # if tempsCourant == -1:
    #   try:
    #     tempsCourant = time.strptime(ligne[indTimeAttribute].value,"%y/%m/%d %H:%M:%S")
    #   except:
    #     tempsCourant = -1
    # if tempsCourant == -1:
    #   try:
    #     tempsCourant = time.strptime(ligne[indTimeAttribute].value,"%d/%m/%y %H:%M:%S")
    #   except:
    #     tempsCourant = -1
    # if tempsCourant == -1:
    #   try:
    #     tempsCourant = time.strptime(ligne[indTimeAttribute].value,"%m/%d/%Y %H:%M:%S")
    #   except:
    #     tempsCourant = -1
    # if tempsCourant == -1:
    #   tempsCourant = time.strptime("1900/01/01 00:00:00","%Y/%m/%d %H:%M:%S")
    # secsCourant =  tempsCourant.tm_hour * 3600 + tempsCourant.tm_min * 60 + tempsCourant.tm_sec
    # if precSecs == -1:
    #   precSecs = secsCourant -10
    coeurMessageData.append("%s', '%s', '%s', '%s" % (str(secsCourant-precSecs), owutUtf2Ascii(ligne[indGroupByAttribute].value), owutUtf2Ascii(ligne[indAttributeToShow].value), owutUtf2Ascii(ligne[indPatternToShow].value)))
    if precGroup == ligne[indGroupByAttribute].value:
      precSecs = secsCourant
    else:
      precSecs = -1
    precGroup = ligne[indGroupByAttribute].value
  messageColle = "'],\n['"
  messageData = "data = [['" + messageColle.join(coeurMessageData) + "']];"
  messageFin = """

function showData() {
var shownData = "<h2>Timelines</h2> <br><br>"+data[0][1]+":";
for(var i=0;i<data.length;i++) {
  if ((i>0) && data[i][1]!=data[i-1][1]) {
    shownData += "<br><br>"+data[i][1]+":";}
  if (data[i][2]=="") {
    continue;}
  if (data[i][3]=="") {
    shownData += '<span class="autourDe'+data[i][2]+'">'
      + '<span class="lignesDeBaseNoirFin"></span>'
      + '<span class="lignesDeBaseBlancEpais"></span>'
      + '<span title="'+data[i][2]+'" class="valDe'+data[i][2]+'"></span>'
      + '<span class="lignesDeBaseBlancMoyen"></span>'
      + '<span class="lignesDeBaseNoirFin"></span>'
      + '</span><!-- '\n+' -->';}
  else{
    shownData += '<span class="autourDe'+data[i][2]+'">'
      + '<span title="'+data[i][3]+'" class="valDe'+data[i][3]+'"></span>'
      + '<span class="lignesDeBaseBlancMoyen"></span>'
      + '<span class="lignesDeBaseNoirFin"></span>'
      + '<span class="lignesDeBaseBlancEpais"></span>'
      + '<span title="'+data[i][2]+'" class="valDe'+data[i][2]+'"></span>'
      + '<span class="lignesDeBaseBlancMoyen"></span>'
      + '<span class="lignesDeBaseNoirFin"></span>'
      + '</span><!-- '\n+' -->';}}
document.getElementById('idTimelines').innerHTML = shownData;
return;}
  </script></head>
<body onload='showData()'>
<h1>TimeLine</h1>\n"""
  f.write(messageEnTete+messageStyles+messageIntermediaire+messageData+messageFin+messageLegende+"\n<div id='idTimelines'></div>\n</body>\n</html>\n")
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
 