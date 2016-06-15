#!/usr/bin/python
#Orange Widget developped by Denis B. June, 2014, continued 2016


"""
<name>Sort</name>
<icon>OWUTSort_icons/OWUTSort.svg</icon>
<description>Sort events of a study on the basis of the lexicographic order of values of two attributes</description>
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


class OWUTSort(OWWidget):
    settingsList = ['configMainKey', 'configSecundaryKey', 'cfgKeepAtt1', 'cfgKeepAtt2']

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)
        self.data = None
        self.inputs = [("Table", Orange.data.Table, self.setData)]
        self.outputs = [("Sort Table", Orange.data.Table)]
        settings = QSettings()
        val = settings.value("ut-login/login", "unknown")
        self.login = val.toString()
        if self.login != "unknown":
            self.loadSettings()
            boxSettings = OWGUI.widgetBox(self.controlArea, "Configuration", addSpace=True)
            owutAjouteChoixAttribut(boxSettings,self,"configMainKey","Main key (usually User Attribute)")
            owutAjouteChoixAttribut(boxSettings,self,"configSecundaryKey","Secundary key (usually TimeDate Attribute)")
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
            firstAttrOk = owutInitChoixAttributEtVerifieConfig(self,"configMainKey",data.domain)
            secondAttrOk = owutInitChoixAttributEtVerifieConfig(self,"configSecundaryKey",data.domain)
            if firstAttrOk and secondAttrOk :
                self.compute()

    def compute(self):
        if self.data != None:
            res = mainOWUTSort(owutChoixAttribut(self,"configMainKey"), owutChoixAttribut(self,"configSecundaryKey"), self.cfgKeepAtt1, self.cfgKeepAtt2, self.data)
            if res!=None:
                owutSynchroniseChoixAttribut(self)
                self.saveSettings()
                self.send("Sort Table", res)
                owutSetPrevisualisationSorties(self,res)


def cmpIJ(x,y,i,j):
    if x[i]==y[i]:
        return cmp(x[j],y[j])
    else:
        return cmp(x[i],y[i])

def mainOWUTSort(mainKey, secundaryKey, pKeepAttribute1, pKeepAttribute2, dataIn):
    indFirstAttribute = owutIndiceAttribut(mainKey,dataIn.domain)
    indSecondAttribute = owutIndiceAttribut(secundaryKey,dataIn.domain)
    domains = [d for d in dataIn.domain]
    fullDomains = Orange.data.Domain(domains)
    if (indFirstAttribute==-1) or (indSecondAttribute==-1):
        return
    if pKeepAttribute1 and pKeepAttribute2:
        reducedDomain = fullDomains
    elif pKeepAttribute1:
        reducedDomain = Orange.data.Domain(fullDomains[:indSecondAttribute]+fullDomains[indSecondAttribute+1:])
    elif pKeepAttribute2:
        reducedDomain = Orange.data.Domain(fullDomains[:indFirstAttribute]+fullDomains[indFirstAttribute+1:])
    else:
        reducedDomain = Orange.data.Domain(fullDomains[:min(indFirstAttribute,indSecondAttribute)]+fullDomains[min(indFirstAttribute,indSecondAttribute)+1:max(indFirstAttribute,indSecondAttribute)]+fullDomains[max(indFirstAttribute,indSecondAttribute)+1:])
    resultat = sorted(dataIn,cmp=(lambda x,y: cmpIJ(x,y,indFirstAttribute,indSecondAttribute)))
    tmpOut =  Orange.data.Table(fullDomains, resultat)
    dataOut = Orange.data.Table(reducedDomain, tmpOut)
    return dataOut