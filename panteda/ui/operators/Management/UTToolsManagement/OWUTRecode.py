#!/usr/bin/python
#Orange Widget developped by Denis B. June, 2014.


"""
<name>Recode</name>
<icon>OWUTRecode_icons/OWUTRecode.svg</icon>
<description>Recode all values from an attribute</description>
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
from OWUTData import owutAjouteChoixAttribut # difficle a utiliser ici, la version explicite est employee
from OWUTData import owutChoixAttribut
from OWUTData import owutSynchroniseChoixAttribut
from OWUTData import owutInitChoixAttributEtVerifieConfig
from OWUTData import owutIndiceAttribut
from OWUTData import owutStrUtf
from OWUTData import owutUtf2Ascii
from OWUTData import owutAscii2Utf
from OWUTData import owutValideNameAttributeFrom
from OWUTData import owutNormaliseTailleNom

class ImputeListItemDelegate(QItemDelegate):
    def __init__(self, widget, parent = None):
        QItemDelegate.__init__(self, parent)
        self.widget = widget

    def drawDisplay(self, painter, option, rect, text):
        #text = str(text)
        if self.widget.remplissageListe == 1:
            QItemDelegate.drawDisplay(self, painter, option, rect, text)
        elif self.widget.listValueToReplace.has_key(owutStrUtf(text)):
            QItemDelegate.drawDisplay(self, painter, option, rect, text+" -->> "+self.widget.listValueToReplace[owutStrUtf(text)])
        else:
            QItemDelegate.drawDisplay(self, painter, option, rect, text)


class OWUTRecode(OWWidget):
    settingsList = ['configMainAttribute','configListValueToReplace','newName','cfgKeepAtt1','cfgNameNewAtt1','configExplanation']

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)
        self.data = None
        self.inputs = [("Table", Orange.data.Table, self.setData)]
        self.outputs = [("Recoded Table", Orange.data.Table)]
        settings = QSettings()
        val = settings.value("ut-login/login", "unknown")
        self.login = val.toString()
        if self.login != "unknown":
            self.configMainAttribute=""
            self.configListValueToReplace = '' # 'item-ut-item-ut-item'
            self.newName = 'texteDeRemplacement'
            boxSettings = OWGUI.widgetBox(self.controlArea, "Configuration", addSpace=True)
            tmpBoxMainAttribute = OWGUI.widgetBox(boxSettings, "Attribute to be searched and replaced", addSpace=True)
            self.cb__configMainAttribute = OWGUI.comboBox(tmpBoxMainAttribute, self, "configMainAttribute", callback=self.setList2b)
            self.listeChoixAttribut = [["configMainAttribute",self.cb__configMainAttribute]]
            boxListValueToReplace = OWGUI.widgetBox(boxSettings, "Attribute value to replace", addSpace=True)
            self.attrList = OWGUI.listBox(boxListValueToReplace, self, callback = self.individualSelected)
            self.listValueToReplace = {}
            self.attrList.setItemDelegate(ImputeListItemDelegate(self, self.attrList))
            self.boxLink = OWGUI.lineEdit(boxSettings, self, "newName", box="Recode with")
            OWGUI.button(boxSettings, self, '(re)Set automatically the code', callback=self.autoCode)
            OWGUI.button(self.controlArea, self, 'Apply', callback=self.compute)
            self.configExplanation = "Your comment/explanation."
            OWGUI.lineEdit(self.controlArea, self, "configExplanation", box="Any comment or explanation about your operator?")
            self.remplissageListe = 0
            owutInitPrevisualisationEntreesSorties(self)
            self.loadSettings()
        else:
            boxConnexion = OWGUI.widgetBox(self.controlArea, "Connection")
            label = OWGUI.label(boxConnexion, self, "Please connect to UnderTracks first! (File->Log on UT)" + self.login)

    def individualSelected(self, i = -1):
        if self.remplissageListe == 0:
            if len(self.attrList.selectedItems())>0:
                self.listValueToReplace[owutStrUtf(self.attrList.selectedItems()[0].text())] = self.newName
                self.attrList.clearSelection ()

    def autoCode(self):
        if self.data != None:
            domaineAttributAlea = {}
            indMain = owutIndiceAttribut(owutChoixAttribut(self,"configMainAttribute"),self.data.domain)
            for ligne in self.data:
                domaineAttributAlea[ligne[indMain].value] = 1
            i=0
            self.attrList.clear()
            self.remplissageListe = 1
            for k in sorted(domaineAttributAlea.keys()):
                self.listValueToReplace[k] = "X"+str(i)
                i = i+1
                self.attrList.addItem(QListWidgetItem(owutStrUtf(k)))
            self.remplissageListe = 0

    def compute(self):
        if self.data != None:
            res = mainOWUTRecode(owutChoixAttribut(self,"configMainAttribute"), self.listValueToReplace,  self.cfgKeepAtt1, str(self.cfgNameNewAtt1), self.data)
            if res!=None:
                owutSynchroniseChoixAttribut(self)
                self.configListValueToReplace = ""
                for e in self.listValueToReplace.keys():
                    self.configListValueToReplace += ":ut-"+owutUtf2Ascii(e)+"-->>"+owutUtf2Ascii(self.listValueToReplace[e])
                self.saveSettings()
                self.send("Recoded Table", res)
                owutSetPrevisualisationSorties(self,res)


    def setData(self, data, id=None):
        self.data = data
        owutSetPrevisualisationEntrees(self,data)
        if self.data != None:
            owutInitChoixAttributEtVerifieConfig(self,"configMainAttribute",data.domain)
            self.setList2()

    def setList2(self):
        if self.data != None:
            self.attrList.clear()
            if self.configMainAttribute==None:
                domaineAttributAlea = {}
                indMain = owutIndiceAttribut(owutChoixAttribut(self,"configMainAttribute"),self.data.domain)
                for ligne in self.data:
                    domaineAttributAlea[ligne[indMain].value] = 1
                self.remplissageListe = 1
                for k in sorted(domaineAttributAlea.keys()):
                    self.attrList.addItem(QListWidgetItem(owutStrUtf(k)))
                self.remplissageListe = 0
                self.configMainAttribute = self.data.domain[0].name
                return
            else:
                mainAttrOk = owutInitChoixAttributEtVerifieConfig(self,"configMainAttribute",self.data.domain)
                indAttributSelectionne = owutIndiceAttribut(owutChoixAttribut(self,"configMainAttribute"),self.data.domain)
                if not mainAttrOk:
                    domaineAttributAlea = {}
                    indMain = owutIndiceAttribut(owutChoixAttribut(self,"configMainAttribute"),self.data.domain)
                    for ligne in self.data:
                        domaineAttributAlea[ligne[indMain].value] = 1
                    self.remplissageListe = 1
                    for k in sorted(domaineAttributAlea.keys()):
                        self.attrList.addItem(QListWidgetItem(owutStrUtf(k)))
                    self.remplissageListe = 0
                    return
                else:
                    domainesAttributSelectionne = {}
                    for ligne in self.data:
                        domainesAttributSelectionne[ligne[indAttributSelectionne].value] = 1
                    self.remplissageListe = 1
                    for k in sorted(domainesAttributSelectionne.keys()):
                        self.attrList.addItem(QListWidgetItem(owutStrUtf(k)))
                    if self.configListValueToReplace != None:
                        self.listValueToReplace.clear()
                        elts = self.configListValueToReplace.split(':ut-')[1:]
                        for e in elts:
                            theKey = owutAscii2Utf(e.split("-->>")[0])
                            theValue = owutAscii2Utf(e.split("-->>")[1])
                            self.listValueToReplace[theKey]=theValue
                    self.remplissageListe = 0
                    if mainAttrOk:
                        self.compute()

    def setList2b(self):
        if self.data != None:
            self.attrList.clear()
            domainesAttributSelectionne = {}
            for ligne in self.data:
                domainesAttributSelectionne[ligne[self.cb__configMainAttribute.currentIndex()].value] = 1
            self.remplissageListe = 1
            for k in sorted(domainesAttributSelectionne.keys()):
                self.attrList.addItem(QListWidgetItem(owutStrUtf(k)))
            if self.configListValueToReplace != None:
                self.listValueToReplace.clear()
                elts = self.configListValueToReplace.split(':ut-')[1:]
                for e in elts:
                    theKey = owutAscii2Utf(e.split("-->>")[0])
                    theValue = owutAscii2Utf(e.split("-->>")[1])
                    self.listValueToReplace[theKey]=theValue
            self.remplissageListe = 0


def mainOWUTRecode(mainAttribute, pListValueToReplace, pKeepAttribute1, pNameForNewAttribute, data):
    indMainAttribute = owutIndiceAttribut(mainAttribute,data.domain)
    if indMainAttribute==-1:
        return
    domains = [d for d in data.domain]
    if pNameForNewAttribute:
        tmpNameForNewAttribute =  pNameForNewAttribute
    else:
        tmpNameForNewAttribute =  owutNormaliseTailleNom("Recode("+mainAttribute+")")
    domains.append(Orange.feature.String(owutValideNameAttributeFrom(tmpNameForNewAttribute,data.domain)))
    fullDomains = Orange.data.Domain(domains)
    if pKeepAttribute1:
        reducedDomain = fullDomains
    else:
        reducedDomain = Orange.data.Domain(fullDomains[:indMainAttribute]+fullDomains[indMainAttribute+1:])
    resultat = [[x for x in lDataIn] for lDataIn in data]
    for i in range(len(data)):
        if pListValueToReplace.has_key(owutStrUtf(data[i][indMainAttribute].value)):
            resultat[i].append(str(pListValueToReplace[owutStrUtf(data[i][indMainAttribute].value)]))
        else:
            resultat[i].append(data[i][indMainAttribute].value)
    tmpOut =  Orange.data.Table(fullDomains, resultat)
    dataOut = Orange.data.Table(reducedDomain, tmpOut)
    return dataOut