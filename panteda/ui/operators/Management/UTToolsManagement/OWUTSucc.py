#!/usr/bin/python
#Orange Widget developped by Denis B. June, 2014.


"""
<name>Succ</name>
<icon>OWUTSucc_icons/OWUTSucc.svg</icon>
<description>Add an extra-attribute with the next value of a given attribute</description>
<priority>30</priority>
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


class OWUTSucc(OWWidget):
    settingsList = ['configMainAttribute','configGroupByAttribute','configExplanation','cfgKeepAtt1','cfgKeepAtt2','cfgNameNewAtt1']

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)
        self.data = None
        self.inputs = [("Table", Orange.data.Table, self.setData)]
        self.outputs = [("Succ Table", Orange.data.Table)]
        settings = QSettings()
        val = settings.value("ut-login/login", "unknown")
        self.login = val.toString()
        if self.login != "unknown":
            boxSettings = OWGUI.widgetBox(self.controlArea, "Configuration", addSpace=True)
            owutAjouteChoixAttribut(boxSettings,self,"configMainAttribute","Attribute to analyse [Default: Action]")
            owutAjouteChoixAttribut(boxSettings,self,"configGroupByAttribute","Group By [Default: User]")
            OWGUI.button(self.controlArea, self, 'Apply', callback=self.compute)
            self.configExplanation = "Your comment/explanation."
            OWGUI.lineEdit(self.controlArea, self, "configExplanation", box="Any comment or explanation about your function?")
            owutInitPrevisualisationEntreesSorties(self)
            self.loadSettings()
        else:
            boxConnexion = OWGUI.widgetBox(self.controlArea, "Connection")
            label = OWGUI.label(boxConnexion, self, "Please connect to UnderTracks first! (File->Log on UT)" + self.login)

    def compute(self):
        if self.data != None:
            res = mainOWUTSucc(owutChoixAttribut(self,"configMainAttribute"), owutChoixAttribut(self,"configGroupByAttribute"), self.cfgKeepAtt1,  self.cfgKeepAtt2, str(self.cfgNameNewAtt1), self.data)
            if res!=None:
                owutSynchroniseChoixAttribut(self)
                self.saveSettings()
                self.send("Succ Table", res)
                owutSetPrevisualisationSorties(self,res)

    def setData(self, data, id=None):
        self.data = data
        owutSetPrevisualisationEntrees(self,data)
        if self.data != None:
            firstAttrOk = owutInitChoixAttributEtVerifieConfig(self,"configMainAttribute",data.domain)
            secondAttrOk = owutInitChoixAttributEtVerifieConfig(self,"configGroupByAttribute",data.domain)
            if firstAttrOk and secondAttrOk:
                self.compute()


def mainOWUTSucc(mainAttribute, groupByAttribute, pKeepAttribute1, pKeepAttribute2, pNameNewAtt1, dataIn):
    indMainAttribute = owutIndiceAttribut(mainAttribute,dataIn.domain)
    indGroupByAttribute = owutIndiceAttribut(groupByAttribute,dataIn.domain)
    if (indMainAttribute==-1) or (indGroupByAttribute==-1):
        return
    emptySuccessor = "()"
    domains = [d for d in dataIn.domain]
    if pNameNewAtt1:
        tmpNameForNewAttribute =  pNameNewAtt1
    else:
        tmpNameForNewAttribute =  "succ("+mainAttribute+")"
    domains.append(Orange.feature.String(owutValideNameAttributeFrom(tmpNameForNewAttribute,dataIn.domain)))
    fullDomains = Orange.data.Domain(domains)
    if pKeepAttribute1 and pKeepAttribute2:
        reducedDomain = fullDomains
    elif pKeepAttribute1:
        reducedDomain = Orange.data.Domain(fullDomains[:indGroupByAttribute]+fullDomains[indGroupByAttribute+1:])
    elif pKeepAttribute2:
        reducedDomain = Orange.data.Domain(fullDomains[:indMainAttribute]+fullDomains[indMainAttribute+1:])
    else:
        reducedDomain = Orange.data.Domain(fullDomains[:min(indMainAttribute,indGroupByAttribute)]+fullDomains[min(indMainAttribute,indGroupByAttribute)+1:max(indMainAttribute,indGroupByAttribute)]+fullDomains[max(indMainAttribute,indGroupByAttribute)+1:])
    resultat = [[x for x in lDataIn] for lDataIn in dataIn]
    for i in range(len(dataIn)):
        if (i<(len(dataIn)-1)) and (dataIn[i][indGroupByAttribute].value==dataIn[i+1][indGroupByAttribute].value):
            resultat[i].append(dataIn[i+1][indMainAttribute].value)
        else:
            resultat[i].append(emptySuccessor)
    tmpOut =  Orange.data.Table(fullDomains, resultat)
    dataOut = Orange.data.Table(reducedDomain, tmpOut)
    return dataOut
