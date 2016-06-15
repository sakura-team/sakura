#!/usr/bin/python
#Orange Widget developped by Denis B. May, 2014, continued 2016.


"""
<name>Split</name>
<icon>OWUTSplit_icons/OWUTSplit.svg</icon>
<description>Split an input-attribute intro multiple extra-attributes</description>
<priority>20</priority>
"""

import Orange
from OWWidget import *
import OWGUI
if not sys.path[len(sys.path)-1].endswith("/Management/UTToolsManagement"):
    tmpSettings = QSettings()
    path = str(tmpSettings.value("ut-path/path","unknown").toString()+"/Management/UTToolsManagement")
    sys.path.append(path)
from OWUTData import owutInitPrevisualisationEntreesSorties
from OWUTData import owutSetPrevisualisationSorties
from OWUTData import owutSetPrevisualisationEntrees
from OWUTData import owutAjouteChoixAttribut
from OWUTData import owutChoixAttribut
from OWUTData import owutSynchroniseChoixAttribut
from OWUTData import owutInitChoixAttributEtVerifieConfig
from OWUTData import owutIndiceAttribut
from OWUTData import owutValideNameAttributeFrom
from OWUTData import owutNormaliseTailleNom

class OWUTSplit(OWWidget):
    settingsList = ['configAttribute','configSeparator','cfgKeepAtt1','cfgNameNewAtt1']

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)
        self.data = None
        self.inputs = [("Table", Orange.data.Table, self.setData)]
        self.outputs = [("Split Table", Orange.data.Table)]
        settings = QSettings()
        val = settings.value("ut-login/login", "unknown")
        self.login = val.toString()
        if self.login != "unknown":
            boxSettings = OWGUI.widgetBox(self.controlArea, "Configuration", addSpace=True)
            owutAjouteChoixAttribut(boxSettings,self,"configAttribute","Attribute")
            owutAjouteChoixAttribut(boxSettings,self,"configSeparator","Separator")
            OWGUI.button(self.controlArea, self, 'Apply', callback=self.compute)
            owutInitPrevisualisationEntreesSorties(self)
            self.loadSettings()
        else:
            boxConnexion = OWGUI.widgetBox(self.controlArea, "Connection")
            label = OWGUI.label(boxConnexion, self, "Please connect to UnderTracks first! (File->Log on UT)" + self.login)

    def setData(self, data, id=None):
        self.data = data
        owutSetPrevisualisationEntrees(self,data)
        if self.data != None:
            firstAttrOk = owutInitChoixAttributEtVerifieConfig(self,"configAttribute",data.domain)
            secondAttrOk = owutInitChoixAttributEtVerifieConfig(self,"configSeparator",[" ",":",";","|","/"])
            if firstAttrOk and secondAttrOk:
                self.compute()

    def compute(self):
        if self.data != None:
            res = mainOWUTSplit(owutChoixAttribut(self,"configAttribute"), owutChoixAttribut(self,"configSeparator"), self.cfgKeepAtt1, str(self.cfgNameNewAtt1), self.data)
            if res!=None:
                owutSynchroniseChoixAttribut(self)
                self.saveSettings()
                self.send("Split Table", res)
                owutSetPrevisualisationSorties(self,res)


def mainOWUTSplit(colName, sep, pKeepAttribute1, pNameForNewAttribute, data):
    strSep = str(sep) #pour travailler en str et non pas en utf ...
    colIndex = owutIndiceAttribut(colName,data.domain)
    if (colIndex==-1):
        return
    nbSousCol =len(data[0][colIndex].value.split(strSep))
    if pNameForNewAttribute:
        tmpNameForNewAttribute =  pNameForNewAttribute
    else:
        tmpNameForNewAttribute =  owutNormaliseTailleNom(colName)
    domains = [d for d in data.domain]
    for i in range(nbSousCol):
        domains.append(Orange.feature.String(owutValideNameAttributeFrom(tmpNameForNewAttribute+"_"+str(i),data.domain)))
    fullDomains = Orange.data.Domain(domains)
    if pKeepAttribute1:
        reducedDomain = fullDomains
    else:
        reducedDomain = Orange.data.Domain(fullDomains[:colIndex]+fullDomains[colIndex+1:])
    resultat = [[x for x in lDataIn] for lDataIn in data]
    for i in range(len(data)):
        cellules = data[i][colIndex].value.split(strSep)
        for c in cellules:
            resultat[i].append(c)
    tmpOut =  Orange.data.Table(fullDomains, resultat)
    dataOut = Orange.data.Table(reducedDomain, tmpOut)
    return dataOut
