#!/usr/bin/python
#Orange Widget developped by Denis B. June, 2014.


"""
<name>Replace</name>
<icon>OWUTReplace_icons/OWUTReplace.svg</icon>
<description>Replace one  given input-value of an attribute with another given output-value (for each appearance of the given input-value)</description>
<priority>33</priority>
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
from OWUTData import owutStrUtf
from OWUTData import owutValideNameAttributeFrom
from OWUTData import owutNormaliseTailleNom


class OWUTReplace(OWWidget):
    settingsList = ['configMainAttribute','configValueToFind','newName','cfgKeepAtt1','cfgNameNewAtt1','configExplanation']

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)
        self.data = None
        self.inputs = [("Table", Orange.data.Table, self.setData)]
        self.outputs = [("Replace Table", Orange.data.Table)]
        settings = QSettings()
        val = settings.value("ut-login/login", "unknown")
        self.login = val.toString()
        if self.login != "unknown":
            self.configMainAttribute=""
            self.configValueToFind="" #a priori pas necessaire car owutAjouteChoixAttribut le fait
            self.newName = "newName"
            boxSettings = OWGUI.widgetBox(self.controlArea, "Configuration", addSpace=True)
            tmpBoxMainAttribute = OWGUI.widgetBox(boxSettings, "Attribute to analyse", addSpace=True)
            self.cb__configMainAttribute = OWGUI.comboBox(tmpBoxMainAttribute, self, "configMainAttribute", callback=self.setList2b)
            self.listeChoixAttribut = [["configMainAttribute",self.cb__configMainAttribute]]
            owutAjouteChoixAttribut(boxSettings,self,"configValueToFind","Value to find")
            self.boxLink = OWGUI.lineEdit(boxSettings, self, "newName", box="Replace with")
            OWGUI.button(self.controlArea, self, 'Apply', callback=self.compute)
            self.configExplanation = "Your comment/explanation."
            OWGUI.lineEdit(self.controlArea, self, "configExplanation", box="Any comment or explanation about your operator?")
            owutInitPrevisualisationEntreesSorties(self)
            self.loadSettings()
        else:
            boxConnexion = OWGUI.widgetBox(self.controlArea, "Connection")
            label = OWGUI.label(boxConnexion, self, "Please connect to UnderTracks first! (File->Log on UT)" + self.login)

    def compute(self):
        if self.data != None:
            _newName = self.boxLink.text()
            res = mainOWUTReplace(owutChoixAttribut(self,"configMainAttribute"),owutChoixAttribut(self,"configValueToFind"), str(_newName), self.cfgKeepAtt1, str(self.cfgNameNewAtt1), self.data)
            if res!=None:
                owutSynchroniseChoixAttribut(self)
                self.newName = str(_newName)
                self.saveSettings()
                self.send("Replace Table", res)
                owutSetPrevisualisationSorties(self,res)

    def setData(self, data, id=None):
        self.data = data
        owutSetPrevisualisationEntrees(self,data)
        if self.data != None:
            self.newName = ''
            self.loadSettings()
            owutInitChoixAttributEtVerifieConfig(self,"configMainAttribute",data.domain)
            self.setList2()

    def setList2(self):
        if self.data != None:
            if self.configMainAttribute==None:
                domaineAttributAlea = {}
                for ligne in self.data:
                    domaineAttributAlea[ligne[0].value] = 1
                owutInitChoixAttributEtVerifieConfig(self,"configValueToFind",sorted(domaineAttributAlea.keys()))
                return
            else:
                mainAttrOk = owutInitChoixAttributEtVerifieConfig(self,"configMainAttribute",self.data.domain)
                indAttributSelectionne = owutIndiceAttribut(owutChoixAttribut(self,"configMainAttribute"),self.data.domain)
                if not mainAttrOk:
                    domaineAttributAlea = {}
                    for ligne in self.data:
                        domaineAttributAlea[ligne[0].value] = 1
                    for k in sorted(domaineAttributAlea.keys()):
                        self.cb__configValueToFind.addItem(owutStrUtf(k))
                    return
                else:
                    domainesAttributSelectionne = {}
                    for ligne in self.data:
                        domainesAttributSelectionne[ligne[indAttributSelectionne].value] = 1
                    attrOk = owutInitChoixAttributEtVerifieConfig(self,"configValueToFind",sorted(domainesAttributSelectionne.keys()))
                    if attrOk:
                        self.compute()

    def setList2b(self):
        if self.data != None:
            indAttributSelectionne = owutIndiceAttribut(owutChoixAttribut(self,"configMainAttribute"),self.data.domain)
            domainesAttributSelectionne = {}
            for ligne in self.data:
                domainesAttributSelectionne[ligne[indAttributSelectionne].value] = 1
            attrOk = owutInitChoixAttributEtVerifieConfig(self,"configValueToFind",sorted(domainesAttributSelectionne.keys()))
    
def mainOWUTReplace(mainAttribute, valueToFind, pNewName, pKeepAttribute1, pNameForNewAttribute, data):
    indMainAttribute = owutIndiceAttribut(mainAttribute,data.domain)
    if (indMainAttribute==-1) :
        return
    domains = [d for d in data.domain]
    if pNameForNewAttribute:
        tmpNameForNewAttribute =  pNameForNewAttribute
    else:
        tmpNameForNewAttribute =  owutNormaliseTailleNom("Replace("+mainAttribute+")")
    domains.append(Orange.feature.String(owutValideNameAttributeFrom(tmpNameForNewAttribute,data.domain)))
    fullDomains = Orange.data.Domain(domains)
    if pKeepAttribute1:
        reducedDomain = fullDomains
    else:
        reducedDomain = Orange.data.Domain(fullDomains[:indMainAttribute]+fullDomains[indMainAttribute+1:])
    resultat = [[x for x in lDataIn] for lDataIn in data]
    for i in range(len(data)):
        if owutStrUtf(data[i][indMainAttribute].value)==valueToFind:
            resultat[i].append(str(pNewName))
        else:
            resultat[i].append(data[i][indMainAttribute].value)
    tmpOut =  Orange.data.Table(fullDomains, resultat)
    dataOut = Orange.data.Table(reducedDomain, tmpOut)
    return dataOut
