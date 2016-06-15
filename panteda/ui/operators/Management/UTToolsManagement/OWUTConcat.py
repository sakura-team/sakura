#!/usr/bin/python
#Orange Widget developped by Denis B. June, 2014.


"""
<name>Concat</name>
<icon>OWUTConcat_icons/OWUTConcat.svg</icon>
<description>Add an extra-Attribute with value equals the concatenation of the values of two other attributes</description>
<priority>21</priority>
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
from OWUTData import owutNormaliseTailleNom
from OWUTData import owutValideNameAttributeFrom

class OWUTConcat(OWWidget):
    settingsList = ['firstAttributeToConcat','secondAttributeToConcat','linkForConcat','configExplanation','cfgKeepAtt1','cfgKeepAtt2','cfgNameNewAtt1']

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)
        self.data = None
        self.inputs = [("Table", Orange.data.Table, self.setData)]
        self.outputs = [("Concat Table", Orange.data.Table)]
        settings = QSettings()
        val = settings.value("ut-login/login", "unknown")
        self.login = val.toString()
        if self.login != "unknown":
            boxSettings = OWGUI.widgetBox(self.controlArea, "Configuration", addSpace=True)
            owutAjouteChoixAttribut(boxSettings,self,"firstAttributeToConcat","First Attribute to concat")
            self.linkForConcat = "::"
            OWGUI.lineEdit(boxSettings, self, "linkForConcat", box="link between the two attributes")
            owutAjouteChoixAttribut(boxSettings,self,"secondAttributeToConcat","Secund Attribute to concat")
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
            res = mainOWUTConcat(owutChoixAttribut(self,"firstAttributeToConcat"),owutChoixAttribut(self,"secondAttributeToConcat"), str(self.linkForConcat), self.cfgKeepAtt1, self.cfgKeepAtt2,  str(self.cfgNameNewAtt1), self.data)
            if res!=None:
                owutSynchroniseChoixAttribut(self)
                self.saveSettings()
                self.send("Concat Table", res)
                owutSetPrevisualisationSorties(self,res)

    def setData(self, data, id=None):
        self.data = data
        owutSetPrevisualisationEntrees(self,data)
        if self.data != None:
            firstAttrOk = owutInitChoixAttributEtVerifieConfig(self,"firstAttributeToConcat",data.domain)
            secondAttrOk = owutInitChoixAttributEtVerifieConfig(self,"secondAttributeToConcat",data.domain)
            if firstAttrOk and secondAttrOk:
                self.compute()


def mainOWUTConcat(pFirstAttributeToConcat, pSecondAttributeToConcat, pLinkForConcat, pKeepAttribute1, pKeepAttribute2, pNameForNewAttribute, dataIn):
    indFirstAttributeToConcat = owutIndiceAttribut(pFirstAttributeToConcat,dataIn.domain)
    indSecondAttributeToConcat = owutIndiceAttribut(pSecondAttributeToConcat,dataIn.domain)
    if (indFirstAttributeToConcat==-1) or (indSecondAttributeToConcat==-1):
        return
    domains = [d for d in dataIn.domain]
    if pNameForNewAttribute:
        tmpNameForNewAttribute =  pNameForNewAttribute
    else:
        tmpNameForNewAttribute =  owutNormaliseTailleNom("concat("+pFirstAttributeToConcat+pLinkForConcat+pSecondAttributeToConcat+")")
    domains.append(Orange.feature.String(owutValideNameAttributeFrom(tmpNameForNewAttribute,dataIn.domain)))
    fullDomains = Orange.data.Domain(domains)
    if pKeepAttribute1 and pKeepAttribute2:
        reducedDomain = fullDomains
    elif pKeepAttribute1:
        reducedDomain = Orange.data.Domain(fullDomains[:indSecondAttributeToConcat]+fullDomains[indSecondAttributeToConcat+1:])
    elif pKeepAttribute2:
        reducedDomain = Orange.data.Domain(fullDomains[:indFirstAttributeToConcat]+fullDomains[indFirstAttributeToConcat+1:])
    else:
        reducedDomain = Orange.data.Domain(fullDomains[:min(indFirstAttributeToConcat,indSecondAttributeToConcat)]+fullDomains[min(indFirstAttributeToConcat,indSecondAttributeToConcat)+1:max(indFirstAttributeToConcat,indSecondAttributeToConcat)]+fullDomains[max(indFirstAttributeToConcat,indSecondAttributeToConcat)+1:])
    resultat = [[x for x in lDataIn] for lDataIn in dataIn]
    for i in range(len(dataIn)):
        resultat[i].append(dataIn[i][indFirstAttributeToConcat].value+pLinkForConcat+dataIn[i][indSecondAttributeToConcat].value)
    tmpOut =  Orange.data.Table(fullDomains, resultat)
    dataOut = Orange.data.Table(reducedDomain, tmpOut)
    return dataOut
