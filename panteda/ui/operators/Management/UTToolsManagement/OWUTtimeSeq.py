#!/usr/bin/python
#Orange Widget developped by Denis B. Oct., 2014., continued 2015


"""
<name>timeSeq</name>
<icon>OWUTtimeSeq_icons/OWUTtimeSeq.svg</icon>
<description>Construct a sequence of values from an attribute for a fixed time lapse</description>
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
from OWUTData import owutCastContinuous
from OWUTData import owutValideNameAttributeFrom
from OWUTData import owutNormaliseTailleNom


class OWUTtimeSeq(OWWidget):
    settingsList = ['mainAttribute','timeAttribute','lenghtAttribute','groupAttribute','firstConfig','cfgKeepAtt1','cfgKeepAtt2','cfgKeepAtt3','cfgNameNewAtt1']

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)
        self.data = None
        self.inputs = [("Table", Orange.data.Table, self.setData)]
        self.outputs = [("TimeSeq Table", Orange.data.Table)]
        settings = QSettings()
        val = settings.value("ut-login/login", "unknown")
        self.login = val.toString()
        if self.login != "unknown":
            boxSettings = OWGUI.widgetBox(self.controlArea, "Configuration", addSpace=True)
            owutAjouteChoixAttribut(boxSettings,self,"mainAttribute","Sequence for the attribute [default=Action]")
            owutAjouteChoixAttribut(boxSettings,self,"timeAttribute","Time Attribute")
            owutAjouteChoixAttribut(boxSettings,self,"groupAttribute","Attribute group by [default=User]")
            owutAjouteChoixAttribut(boxSettings,self,"lenghtAttribute","Length for the sequence (in sec.)")
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
            fourthAttrOk = owutInitChoixAttributEtVerifieConfig(self,"timeAttribute",data.domain)
            secondAttrOk = owutInitChoixAttributEtVerifieConfig(self,"lenghtAttribute",["10","20","30","60","120","300","600"])
            thirdAttrOk = owutInitChoixAttributEtVerifieConfig(self,"groupAttribute",data.domain)
            if firstAttrOk and secondAttrOk and thirdAttrOk and fourthAttrOk:
                self.compute()

    def compute(self):
        if self.data != None:
            res = mainOWUTTimeSeq(owutChoixAttribut(self,"mainAttribute"), owutChoixAttribut(self,"timeAttribute"), owutChoixAttribut(self,"groupAttribute"), owutChoixAttribut(self,"lenghtAttribute"), str(self.firstConfig), self.cfgKeepAtt1, self.cfgKeepAtt2, self.cfgKeepAtt3,  str(self.cfgNameNewAtt1), self.data)
            if res!=None: # Apres execution, enregistrer la configuration, transmettre les resultats et les pre-visualiser
                owutSynchroniseChoixAttribut(self)
                self.saveSettings()
                self.send("TimeSeq Table", res)
                owutSetPrevisualisationSorties(self,res)


def mainOWUTTimeSeq(pMainAttribute, pTimeAttribute, pGroupAttribute, pLenghtAttribute, pFirstConfig, pKeepAttribute1, pKeepAttribute2, pKeepAttribute3, pNameForNewAttribute, dataIn):
    indMainAttribute = owutIndiceAttribut(pMainAttribute,dataIn.domain)
    indTimeAttribute = owutIndiceAttribut(pTimeAttribute,dataIn.domain)
    indGroupAttribute = owutIndiceAttribut(pGroupAttribute,dataIn.domain)
    valLenghtAttribute = int(pLenghtAttribute)
    if (indMainAttribute==-1) or (indTimeAttribute==-1) or (indGroupAttribute==-1) :
        return
    domains = [d for d in dataIn.domain]
    if pNameForNewAttribute:
        tmpNameForNewAttribute =  pNameForNewAttribute
    else:
        tmpNameForNewAttribute =  owutNormaliseTailleNom("TimeSeq("+pMainAttribute+","+str(valLenghtAttribute)+"s)")
    domains.append(Orange.feature.String(owutValideNameAttributeFrom(tmpNameForNewAttribute,dataIn.domain)))
    newDomainsInit = Orange.data.Domain(domains)
    doNotKeep = []
    if not pKeepAttribute1:
        doNotKeep.append(indMainAttribute)
    if not pKeepAttribute2:
        doNotKeep.append(indTimeAttribute)
    if not pKeepAttribute3:
        doNotKeep.append(indGroupAttribute)
    decalage = 0
    newDomainsFinal = newDomainsInit
    for i in sorted(doNotKeep):
        newDomainsFinal = Orange.data.Domain(newDomainsFinal[:i-decalage]+newDomainsFinal[i+1-decalage:])
        decalage = decalage+1
    resultat = [[x for x in lDataIn] for lDataIn in dataIn]
    Nmax = len(dataIn)
    for i in range(Nmax):
        currentUser = dataIn[i][indGroupAttribute].value
        createdValueForLineI = dataIn[i][indMainAttribute].value + pFirstConfig
        j=1
        start = float(owutCastContinuous(dataIn[i][indTimeAttribute].value))
        while ((i+j)<Nmax) and (currentUser==dataIn[i+j][indGroupAttribute].value) and ((float(owutCastContinuous(dataIn[i+j][indTimeAttribute].value))-start)<valLenghtAttribute):
            createdValueForLineI = createdValueForLineI + dataIn[i+j][indMainAttribute].value + pFirstConfig
            j = j+1
        resultat[i].append(createdValueForLineI)
    tmpOut =  Orange.data.Table(newDomainsInit, resultat)
    dataOut = Orange.data.Table(newDomainsFinal, tmpOut)
    return dataOut

