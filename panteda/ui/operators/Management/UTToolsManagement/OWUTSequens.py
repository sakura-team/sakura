#!/usr/bin/python
#Orange Widget developped by Denis B. Oct., 2014., continued 2015


"""
<name>Sequens</name>
<icon>OWUTSequens_icons/OWUTSequens.svg</icon>
<description>Construct a fixed-length sequence of values from an attribute</description>
<priority>991</priority>
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


class OWUTSequens(OWWidget):
    settingsList = ['mainAttribute','lenghtAttribute','groupAttribute','firstConfig','cfgKeepAtt1','cfgKeepAtt2','cfgNameNewAtt1']

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)
        self.data = None
        self.inputs = [("Table", Orange.data.Table, self.setData)]
        self.outputs = [("Sequens Table", Orange.data.Table)]
        settings = QSettings()
        val = settings.value("ut-login/login", "unknown")
        self.login = val.toString()
        if self.login != "unknown":
            boxSettings = OWGUI.widgetBox(self.controlArea, "Configuration", addSpace=True)
            owutAjouteChoixAttribut(boxSettings,self,"mainAttribute","Sequence for the attribute [default=Action]")
            owutAjouteChoixAttribut(boxSettings,self,"groupAttribute","Attribute group by [default=User]")
            owutAjouteChoixAttribut(boxSettings,self,"lenghtAttribute","Length for the sequence")
            self.firstConfig = "_"
            boxFirstConfig = OWGUI.lineEdit(boxSettings, self, "firstConfig", box="Separator (may be empty)")
            OWGUI.button(self.controlArea, self, 'Apply', callback=self.compute)
            self.configExplanation = "Your comment/explanation."
            OWGUI.lineEdit(self.controlArea, self, "configExplanation", box="Any comment or explanation about your operation?")
            owutInitPrevisualisationEntreesSorties(self)
            self.loadSettings()
        else:
            boxConnexion = OWGUI.widgetBox(self.controlArea, "Connection")
            label = OWGUI.label(boxConnexion, self, "Please connect to UnderTracks first! (File->Log on UT)" + self.login)

    def setData(self, data, id=None):
        self.data = data
        owutSetPrevisualisationEntrees(self,data)
        if self.data != None:
            firstAttrOk = owutInitChoixAttributEtVerifieConfig(self,"mainAttribute",data.domain)
            secondAttrOk = owutInitChoixAttributEtVerifieConfig(self,"lenghtAttribute",["2","3","4","5","10"])
            thirdAttrOk = owutInitChoixAttributEtVerifieConfig(self,"groupAttribute",data.domain)
            if firstAttrOk and secondAttrOk and thirdAttrOk:
                self.compute()

    def compute(self):
        if self.data != None:
            res = mainOWUTSequens(owutChoixAttribut(self,"mainAttribute"), owutChoixAttribut(self,"groupAttribute"), owutChoixAttribut(self,"lenghtAttribute"), str(self.firstConfig), self.cfgKeepAtt1, self.cfgKeepAtt2,  str(self.cfgNameNewAtt1), self.data)
            if res!=None: # Apres execution, enregistrer la configuration, transmettre les resultats et les pre-visualiser
                owutSynchroniseChoixAttribut(self)
                self.saveSettings()
                self.send("Sequens Table", res)
                owutSetPrevisualisationSorties(self,res)


def mainOWUTSequens(pMainAttribute, pGroupAttribute, pLenghtAttribute, pFirstConfig, pKeepAttribute1, pKeepAttribute2, pNameForNewAttribute, dataIn):
    indMainAttribute = owutIndiceAttribut(pMainAttribute,dataIn.domain)
    indGroupAttribute = owutIndiceAttribut(pGroupAttribute,dataIn.domain)
    valLenghtAttribute = int(pLenghtAttribute)
    if (indMainAttribute==-1) or (indGroupAttribute==-1):
        return
    domains = [d for d in dataIn.domain]
    if pNameForNewAttribute:
        tmpNameForNewAttribute =  pNameForNewAttribute
    else:
        tmpNameForNewAttribute =  owutNormaliseTailleNom("Sequens("+pMainAttribute+","+str(valLenghtAttribute)+")")
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
    resultat = [[x for x in lDataIn] for lDataIn in dataIn]
    Nmax = len(dataIn)
    for i in range(Nmax):
        currentUser = dataIn[i][indGroupAttribute].value
        createdValueForLineI = dataIn[i][indMainAttribute].value + pFirstConfig
        for j in range(1,valLenghtAttribute):
            if (i+j)<Nmax:
                if (currentUser==dataIn[i+j][indGroupAttribute].value):
                  createdValueForLineI = createdValueForLineI + dataIn[i+j][indMainAttribute].value + pFirstConfig
        resultat[i].append(createdValueForLineI)
    tmpOut =  Orange.data.Table(fullDomains, resultat)
    dataOut = Orange.data.Table(reducedDomain, tmpOut)
    return dataOut

