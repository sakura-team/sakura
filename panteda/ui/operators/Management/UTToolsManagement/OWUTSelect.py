#!/usr/bin/python
#Orange Widget developped by Denis B. July, 2014.


"""
<name>Select</name>
<icon>OWUTSelect_icons/OWUTSelect.svg</icon>
<description>Select events of a study on the basis of a given set of allowed values of an attribute</description>
<priority>30/priority>
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
from OWUTData import owutUtf2Ascii
from OWUTData import owutAscii2Utf


class ImputeListItemDelegate(QItemDelegate):
    def __init__(self, widget, parent = None):
        QItemDelegate.__init__(self, parent)
        self.widget = widget

    def drawDisplay(self, painter, option, rect, text):
        if self.widget.remplissageListe == 1:
            QItemDelegate.drawDisplay(self, painter, option, rect, text)
        elif self.widget.listValueToSelect.has_key(owutStrUtf(text)):
            if self.widget.listValueToSelect[owutStrUtf(text)]==1:
                QItemDelegate.drawDisplay(self, painter, option, rect, " - "+text)
            else:
                QItemDelegate.drawDisplay(self, painter, option, rect, " + "+text)
        else:
            QItemDelegate.drawDisplay(self, painter, option, rect, " + "+text)


class OWUTSelect(OWWidget):
    settingsList = ['configMainAttribute','configListValueToSelect','configExplanation']

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)
        self.data = None
        self.inputs = [("Table", Orange.data.Table, self.setData)]
        self.outputs = [("Select Table", Orange.data.Table)]
        settings = QSettings()
        val = settings.value("ut-login/login", "unknown")
        self.login = val.toString()
        if self.login != "unknown":
            self.configMainAttribute = '' #'user'
            self.configListValueToSelect = '' # 'item:ut-item:ut-item' pour les items a supprimer
            boxSettings = OWGUI.widgetBox(self.controlArea, "Configuration", addSpace=True)
            tmpBoxMainAttribute = OWGUI.widgetBox(boxSettings, "Attribute to be searched and select or filter", addSpace=True)
            self.cb__configMainAttribute = OWGUI.comboBox(tmpBoxMainAttribute, self, "configMainAttribute", callback=self.setList2b)
            self.listeChoixAttribut = [["configMainAttribute",self.cb__configMainAttribute]]
            boxlistValueToSelect = OWGUI.widgetBox(boxSettings, "Value to Select", addSpace=True)
            self.attrList = OWGUI.listBox(boxlistValueToSelect, self, callback = self.individualSelected)
            self.listValueToSelect = {}
            self.attrList.setItemDelegate(ImputeListItemDelegate(self, self.attrList))
            OWGUI.button(boxSettings, self, 'Set Values', callback=self.setValue)
            OWGUI.button(boxSettings, self, 'Reset Values', callback=self.resetValue)
            OWGUI.button(self.controlArea, self, 'Apply', callback=self.compute)
            self.configExplanation = "Your comment/explanation."
            OWGUI.lineEdit(self.controlArea, self, "configExplanation", box="Any comment or explanation about your function?")
            owutInitPrevisualisationEntreesSorties(self)
            self.loadSettings()
            self.remplissageListe = 0
        else:
            boxConnexion = OWGUI.widgetBox(self.controlArea, "Connection")
            label = OWGUI.label(boxConnexion, self, "Please connect to UnderTracks first! (File->Log on UT)" + self.login)

    def individualSelected(self, i = -1):
        if self.remplissageListe == 0:
            if len(self.attrList.selectedItems())>0:
                if self.listValueToSelect.has_key(owutStrUtf(self.attrList.selectedItems()[0].text())):
                    self.listValueToSelect[owutStrUtf(self.attrList.selectedItems()[0].text())] = 1 - self.listValueToSelect[owutStrUtf(self.attrList.selectedItems()[0].text())]
                else:
                    self.listValueToSelect[owutStrUtf(self.attrList.selectedItems()[0].text())] = 1
                self.attrList.clearSelection()

    def setValue(self):
        if self.remplissageListe == 0:
            self.listValueToSelect = {}
            self.configListValueToSelect = ""
            #for e in self.listValueToSelect.keys():
            #    self.listValueToSelect[e] = 0
            self.setList2b()

    def resetValue(self):
        if self.remplissageListe == 0:
            self.listValueToSelect = {}
            tmpValues = {}
            for ligne in self.data:
                tmpValues[ligne[self.cb__configMainAttribute.currentIndex()].value] = 1
            self.configListValueToSelect = ""
            for k in sorted(tmpValues.keys()):
                self.configListValueToSelect += ":ut-"+owutUtf2Ascii(k)
            self.setList2b()

    def compute(self):
        if self.data != None:
            res = mainOWUTSelect(owutChoixAttribut(self,"configMainAttribute"), self.listValueToSelect, self.data)
            if res!=None:
                owutSynchroniseChoixAttribut(self)
                self.configListValueToSelect = ""
                for i in range(self.attrList.count()):
                    if owutStrUtf(self.attrList.item(i).text()) in self.listValueToSelect:
                        if self.listValueToSelect[owutStrUtf(self.attrList.item(i).text())]==1:
                            self.configListValueToSelect += ":ut-"+owutUtf2Ascii(self.attrList.item(i).text())
                self.saveSettings()
                self.send("Select Table", res)
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
                for ligne in self.data:
                    domaineAttributAlea[ligne[0].value] = 1
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
                    for ligne in self.data:
                        domaineAttributAlea[ligne[0].value] = 1
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
                    if self.configListValueToSelect != None:
                        self.listValueToSelect.clear()
                        elts = self.configListValueToSelect.split(':ut-')[1:]
                        for e in elts:
                            self.listValueToSelect[owutAscii2Utf(e)]=1
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
            if self.configListValueToSelect != None:
                self.listValueToSelect.clear()
                elts = self.configListValueToSelect.split(':ut-')[1:]
                for e in elts:
                    self.listValueToSelect[owutAscii2Utf(e)]=1
            self.remplissageListe = 0


def mainOWUTSelect(mainAttribute, plistValueToSelect, data):
    resultat = []
    indMainAttribute = owutIndiceAttribut(mainAttribute,data.domain)
    if indMainAttribute==-1:
        return
    for i in range(len(data)):
        selected = True
        if plistValueToSelect.has_key(owutStrUtf(data[i][indMainAttribute].value)):
            if plistValueToSelect[owutStrUtf(data[i][indMainAttribute].value)]==1:
                selected = False
        if selected:
            resultat.append(data[i])
    res = Orange.data.Table(data.domain, resultat)
    return res