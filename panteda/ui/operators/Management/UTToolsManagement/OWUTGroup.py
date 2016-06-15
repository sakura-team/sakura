#!/usr/bin/python
#Orange Widget developped by Denis B. June, 2014, continued 2016


"""
<name>Group</name>
<icon>OWUTGroup_icons/OWUTGroup.svg</icon>
<description>Group events according to an attribute</description>
<priority>19</priority>
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


class OWUTGroup(OWWidget):
    settingsList = ['configMainKey', 'cfgKeepAtt1']

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)
        self.data = None
        self.inputs = [("Table", Orange.data.Table, self.setData)]
        self.outputs = [("Grouped", Orange.data.Table)]
        settings = QSettings()
        val = settings.value("ut-login/login", "unknown")
        self.login = val.toString()
        if self.login != "unknown":
            self.loadSettings()
            boxSettings = OWGUI.widgetBox(self.controlArea, "Configuration", addSpace=True)
            owutAjouteChoixAttribut(boxSettings,self,"configMainKey","Group key")
            OWGUI.button(self.controlArea, self, 'Apply', callback=self.compute)
            self.configExplanation = "Your comment/explanation."
            OWGUI.lineEdit(self.controlArea, self, "configExplanation", box="Any comment or explanation about your group?")
            owutInitPrevisualisationEntreesSorties(self)
            self.loadSettings()
        else:
            boxConnexion = OWGUI.widgetBox(self.controlArea, "Connection")
            label = OWGUI.label(boxConnexion, self, "Please connect to UnderTracks first! (File->Log on UT)" + self.login)

    def setData(self, data, id=None):
        self.data = data
        owutSetPrevisualisationEntrees(self,data)
        if self.data != None:
            firstAttrOk = owutInitChoixAttributEtVerifieConfig(self,"configMainKey",data.domain)
            if firstAttrOk:
                self.compute()

    def compute(self):
        if self.data != None:
            res = mainOWUTGroup(owutChoixAttribut(self,"configMainKey"), self.cfgKeepAtt1, self.data)
            if res!=None:
                owutSynchroniseChoixAttribut(self)
                self.saveSettings()
                self.send("Grouped", res)
                owutSetPrevisualisationSorties(self,res)



def mainOWUTGroup(mainKey,  pKeepAttribute1, dataIn):
    indFirstAttribute = owutIndiceAttribut(mainKey,dataIn.domain)
    domains = [d for d in dataIn.domain]
    fullDomains = Orange.data.Domain(domains)
    if (indFirstAttribute==-1):
        return
    if pKeepAttribute1:
        reducedDomain = fullDomains
    else:
        reducedDomain = Orange.data.Domain(fullDomains[:indFirstAttribute]+fullDomains[indFirstAttribute+1:])
    groups = {}
    for i in range(len(dataIn)):
        k = dataIn[i][indFirstAttribute].value
        if groups.has_key(k):
            groups[k].append(i)
        else:
            groups[k]=[i]
    resultat = []
    for k in groups.keys():
        for i in groups[k]:
            resultat.append(dataIn[i])
    tmpOut =  Orange.data.Table(fullDomains, resultat)
    dataOut = Orange.data.Table(reducedDomain, tmpOut)
    return dataOut