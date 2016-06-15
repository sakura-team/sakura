#!/usr/bin/python
#Orange Widget developped by Denis B. Oct, 2014., Mars 2015

"""
<name>TransitionMatrix</name>
<icon>OWUTTransitionMatrix_icons/OWUTTransitionMatrix.svg</icon>
<description>Compute transition matrix graphics for an attribute</description>
<priority>52</priority>
"""

import Orange
from OWWidget import *
import OWGUI
from plot.owplot import *
import webbrowser
import os
import zipfile
import random
import string
import mimetypes
import urllib2
import httplib
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



class OWUTTransitionMatrix(OWWidget):
    settingsList = ['configAttribute','configGroupBy','exportResult','savExport']

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
            tabs = OWGUI.tabWidget(self.mainArea)
            tab = OWGUI.createTabPage(tabs, "Plot")
            self.graph = OWPlot(tab)
            self.graph.setAxisAutoScale(xBottom)
            self.graph.setAxisAutoScale(yLeft)
            tab.layout().addWidget(self.graph)
            boxSettings = OWGUI.widgetBox(self.controlArea, "Configuration", addSpace=True)
            owutAjouteChoixAttribut(boxSettings,self,"configAttribute","Attribute for transition calculus (default: action attribute)")
            owutAjouteChoixAttribut(boxSettings,self,"configGroupBy","Group By Attribute (default: user attribute)")
            OWGUI.checkBox(boxSettings, self, 'exportResult', "Export result (/tmp)")
            OWGUI.checkBox(boxSettings, self, 'savExport', "Save Export on server (/etc)")
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
            self.dataResult = mainOWUTTransitionMatrix(_Path, owutChoixAttribut(self,"configAttribute"), owutChoixAttribut(self,"configGroupBy"), self.data)
            owutSynchroniseChoixAttribut(self)
            self.saveSettings()
            self.updateShowResult()
            self.updateExportResult()

    def setData(self, data, id=None):
        self.data = data
        if self.data != None:
            firstAttrOk = owutInitChoixAttributEtVerifieConfig(self,"configAttribute",data.domain)
            secondAttrOk = owutInitChoixAttributEtVerifieConfig(self,"configGroupBy",data.domain)
            if firstAttrOk and secondAttrOk:
                self.compute()

    def updateShowResult(self):
        if self.showResult:
            if hasattr(self,"dataResult") and (len(self.dataResult)==6):
                self.updateShow()
            else:
                self.showNothing()
        else:
            self.doNotShow()

    def updateShow(self):
        self.graph.set_axis_labels(xBottom, self.dataResult[0])
        self.graph.set_axis_labels(yLeft, self.dataResult[0])
        self.graph.set_main_curve_data(self.dataResult[1], self.dataResult[2], color_data=self.dataResult[4], label_data = [], size_data=[10], shape_data = [] )
        self.graph.replot()

    def showNothing(self):
        self.graph.set_axis_labels(xBottom, "Nothing to show")
        self.graph.set_axis_labels(yLeft, "")
        self.graph.set_main_curve_data([],[], color_data=[], label_data = [], size_data=[], shape_data = [] )
        self.graph.replot()

    def doNotShow(self):
        self.graph.set_axis_labels(xBottom, "No show")
        self.graph.set_axis_labels(yLeft, "")
        self.graph.set_main_curve_data([],[], color_data=[], label_data = [], size_data=[], shape_data = [] )
        self.graph.replot()

    def updateExportResult(self):
        if self.exportResult and hasattr(self,"dataResult") and (len(self.dataResult)==6):
                 exportMatrix(self.path,self.dataResult[0],self.dataResult[3],self.dataResult[5],str(self.captionTitle),self.savExport)

def idf_securise(strIn):
    strOut = ""
    for i in range(len(strIn)):
        code = ord(strIn[i])
        if (((code>64)and(code<91))  or ((code>96)and(code<123))  or (code==95) or ((code>47)and(code<58))):
            strOut += strIn[i]
        else:
            strOut += "-"+str(code)+"--"  #codes - et -- a remplacer par &# et ; en cas d'affichage html
    return strOut

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
      return ('--' + boundary,'Content-Disposition: form-data; name="fichier"; filename="TransitionMatrix.zip"','Content-Type: application/zip','', open(filename, 'rb').read())

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

                                                        #modifs/autres/divers(jusqu'a la fin) 8/8 ajout pour visu/export
def exportMatrix(ppath,usersName,levenshteinDisance,distanceMax,nomOperateur,sav):
  fileNomAlea = 'UT_HTML_TransitionMatrix'+str(random.getrandbits(100))
  if sav:
    racine = ppath + os.sep + 'etc'
  else:
    racine = ppath + os.sep + 'tmp'
  try:
    os.mkdir(racine)
  except:
    racineCree = -1
  os.mkdir(racine+os.sep+fileNomAlea.capitalize())
  f = open(racine+os.sep+fileNomAlea.capitalize()+os.sep+fileNomAlea+'.html','w')
  messageEnTete = """<html>
<head>"""
  messageIntermediaire = """
</style>
<script type='text/javascript'>
"""
  lignesMessageData = []
  ligneColle = "','"
  n = 0
  for u in range(len(usersName)):
      coeurMessageData = []
      for v in range(len(usersName)) :
          coeurMessageData.append("%s" % levenshteinDisance[n])
          n = n+1
      ligneData = ligneColle.join(coeurMessageData)
      lignesMessageData.append(ligneData)
  messageColle = "'],\n['"
  messageData = "data = [['" + messageColle.join(lignesMessageData) + "']];\ndistanceMax="+str(distanceMax)+";\nuserName=['"+ligneColle.join(usersName)+"'];\n"
  messageFin = """


function showData() {
var shownData = "<br><div style='line-height: 2px;'>";
for(var i=0;i<data.length;i++) {
  shownData += "<br><br><span style='width:50px; line-height: 12px; overflow:hidden; display:inline-block;'>"+userName[i]+"</span>:";
  for(var j=0;j<data[i].length;j++) {
  shownData += '<span title="dist('+userName[i]+','+userName[j]+')='+data[i][j]+'" style="display : inline-block; background-color: rgb('+
                Math.round(255*data[i][j]/distanceMax)+','+ //red
                Math.round(255-255*data[i][j]/distanceMax)+','+ //green
                0+ //blue
                '); height: 20px; width: 20px;"></span><!-- '+
' -->';}}
document.getElementById('idLevenshteinMatrix').innerHTML = shownData;
return;}
  </script></head>
<body onload='showData()'>
<h1>Transition Matrix</h1>\n"""
  f.write(messageEnTete+messageIntermediaire+messageData+messageFin+"("+nomOperateur+")\n<div id='idLevenshteinMatrix'></div>\n</body>\n</html>\n")
  f.close()
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


def mainOWUTTransitionMatrix(ppath, attributeToShow, groupByAttribute, data):
  indAttributeToShow = owutIndiceAttribut(attributeToShow,data.domain)
  indGroupByAttribute = owutIndiceAttribut(groupByAttribute,data.domain)
  if (indAttributeToShow==-1) or (indGroupByAttribute==-1):
    return
  res = []
  users = []
  usersName = []
  currentUser = []
  x_data = []
  y_data = []
  c_data = []
  namesAttributeToShow = {}
  for l in data:
    namesAttributeToShow[owutUtf2Ascii(l[indAttributeToShow])]=0
  transitionMatrix = {}
  usersName = sorted(namesAttributeToShow.keys())
  for atr1 in usersName:
    transitionMatrix[atr1]= {}
    for atr2 in usersName:
      transitionMatrix[atr1][atr2]=0
  precUser="UTNoUserYet"
  precAttribut = "UtNoAttributeYet"
  for l in data:
    currentUser = str(l[indGroupByAttribute])
    currentAttribut = owutUtf2Ascii(l[indAttributeToShow])
    if currentUser!=precUser:
      if precUser=="UTNoUserYet":
        precAttribut = currentAttribut
      else:
        precAttribut = "UtNoAttributeYet"
      precUser = currentUser
    else:
      if precAttribut != "UtNoAttributeYet":
        transitionMatrix[precAttribut][currentAttribut] = transitionMatrix[precAttribut][currentAttribut]+1
      precAttribut = currentAttribut
  transitionMax = 0
  for u in range(len(usersName)):
    for v in range(len(usersName)) :
      transition = transitionMatrix[usersName[u]][usersName[v]]
      if transition > transitionMax:
        transitionMax = transition
      x_data.append(u)
      y_data.append(v)
      c_data.append(transition)
  m_data = [QColor(255*v/transitionMax,255-255*v/transitionMax,0) for v in c_data]
  res = [usersName,x_data, y_data,c_data,m_data,transitionMax]
  return res
 