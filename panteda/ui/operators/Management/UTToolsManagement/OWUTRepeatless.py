#!/usr/bin/python
#Orange Widget developped by Denis B. July, 2014, continued 2016


"""
<name>Repeatless</name>
<icon>OWUTRepeatless_icons/OWUTRepeatless.svg</icon>
<description>Delete repeated value of an attribute (replace repeated value with empty value)</description>
<priority>35/priority>
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


class OWUTRepeatless(OWWidget):
    settingsList = ['configMainAttribute','configGroupAttribute','configExplanation','skipRepeatedValue','cfgKeepAtt1','cfgKeepAtt2','cfgNameNewAtt1']

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)
        self.data = None
        self.inputs = [("Table", Orange.data.Table, self.setData)]
        self.outputs = [("Repeatless Table", Orange.data.Table)]
        settings = QSettings()
        val = settings.value("ut-login/login", "unknown")
        self.login = val.toString()
        if self.login != "unknown":
            boxSettings = OWGUI.widgetBox(self.controlArea, "Configuration", addSpace=True)
            owutAjouteChoixAttribut(boxSettings,self,"configMainAttribute","Analyzed Attribute [Action?]")
            owutAjouteChoixAttribut(boxSettings,self,"configGroupAttribute","Group Attribute [User?]")
            self.skipRepeatedValue = False
            OWGUI.checkBox(boxSettings, self, 'skipRepeatedValue', "Skip repeated value")
            OWGUI.button(self.controlArea, self, 'Apply', callback=self.compute)
            self.configExplanation = "Your comment/explanation."
            OWGUI.lineEdit(self.controlArea, self, "configExplanation", box="Any comment or explanation about your function?")
            owutInitPrevisualisationEntreesSorties(self)
            self.loadSettings()
        else:
            boxConnexion = OWGUI.widgetBox(self.controlArea, "Connection")
            label = OWGUI.label(boxConnexion, self, "Please connect to UnderTracks first! (File->Log on UT)" + self.login)

    def setData(self, data, id=None):
        self.data = data
        owutSetPrevisualisationEntrees(self,data)
        if self.data != None:
            firstAttrOk = owutInitChoixAttributEtVerifieConfig(self,"configMainAttribute",data.domain)
            secondAttrOk = owutInitChoixAttributEtVerifieConfig(self,"configGroupAttribute",data.domain)
            if firstAttrOk and secondAttrOk:
                self.compute()

    def compute(self):
        if self.data != None:
            res = mainOWUTRepeatless(owutChoixAttribut(self,"configMainAttribute"), owutChoixAttribut(self,"configGroupAttribute"),  self.skipRepeatedValue, self.cfgKeepAtt1, self.cfgKeepAtt2, str(self.cfgNameNewAtt1), self.data)
            if res!=None:
                owutSynchroniseChoixAttribut(self)
                self.saveSettings()
                self.send("Repeatless Table", res)
                owutSetPrevisualisationSorties(self,res)


def mainOWUTRepeatless(mainAttribute, groupAttribute, pSkipRepeatedValue, pKeepAttribute1,  pKeepAttribute2, pNameForNewAttribute, dataIn):
    indMainAttribute = owutIndiceAttribut(mainAttribute,dataIn.domain)
    indGroupAttribute = owutIndiceAttribut(groupAttribute,dataIn.domain)
    if (indMainAttribute==-1) or (indGroupAttribute==-1):
        return
    domains = [d for d in dataIn.domain]
    if pNameForNewAttribute:
        tmpNameForNewAttribute =  pNameForNewAttribute
    else:
        tmpNameForNewAttribute =  owutNormaliseTailleNom(dataIn.domain[indMainAttribute].name+"_Repeatless")
    domains.append(Orange.feature.String(owutValideNameAttributeFrom(tmpNameForNewAttribute,dataIn.domain)))
    fullDomains = Orange.data.Domain(domains)
    if pKeepAttribute1 and pKeepAttribute2:
        reducedDomain = fullDomains
    elif pKeepAttribute1:
        reducedDomain = Orange.data.Domain(fullDomains[:indGroupAttribute]+fullDomains[indGroupAttribute+1:])
    elif pKeepAttribute2:
        reducedDomain = Orange.data.Domain(fullDomains[:indMainAttribute]+fullDomains[indMainAttribute+1:])
    else:
        reducedDomain = Orange.data.Domain(fullDomains[:min(indMainAttribute,indGroupAttribute)]+fullDomains[min(indMainAttribute,indGroupAttribute)+1:max(indMainAttribute,indGroupAttribute)]+fullDomains[max(indMainAttribute,indGroupAttribute)+1:])
    resultat = [[x for x in dataIn[0]]]
    precAttribute = dataIn[0][indMainAttribute].value
    precGroup = dataIn[0][indGroupAttribute].value
    resultat[0].append(dataIn[0][indMainAttribute].value)
    for k in range(1,len(dataIn)):
        NouvelleLigne = (dataIn[k][indMainAttribute].value!=precAttribute) or (dataIn[k][indGroupAttribute].value!=precGroup)
        if NouvelleLigne:
            tmpResultat = [x for x in dataIn[k]]
            precAttribute = dataIn[k][indMainAttribute].value
            precGroup = dataIn[k][indGroupAttribute].value
            tmpResultat.append(dataIn[k][indMainAttribute].value)
            resultat.append(tmpResultat)
        elif not pSkipRepeatedValue:
            tmpResultat = [x for x in dataIn[k]]
            tmpResultat.append("")
            resultat.append(tmpResultat)
    tmpOut =  Orange.data.Table(fullDomains, resultat)
    dataOut = Orange.data.Table(reducedDomain, tmpOut)
    return dataOut