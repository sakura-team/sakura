#!/usr/bin/python
#Orange Widget developped by Denis B. July, 2014.


"""
<name>Join</name>
<icon>OWUTJoin_icons/OWUTJoin.svg</icon>
<description>Join multiple input-attributes to form one extra-attribute (multiConcat)</description>
<priority>20</priority>
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
        if self.widget.remplissageListe == 1:
            QItemDelegate.drawDisplay(self, painter, option, rect, text)
        elif self.widget.listAttributesToJoin.has_key(owutStrUtf(text)):
            if self.widget.listAttributesToJoin[owutStrUtf(text)]==1:
                QItemDelegate.drawDisplay(self, painter, option, rect, " * "+text)
            else:
                QItemDelegate.drawDisplay(self, painter, option, rect, "   "+text)
        else:
            QItemDelegate.drawDisplay(self, painter, option, rect, "   "+text)


class OWUTJoin(OWWidget):
    settingsList = ['configListAttributesToJoin','configSeparator','cfgNameNewAtt1']

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)

        self.data = None
        self.inputs = [("Table", Orange.data.Table, self.setData)]
        self.outputs = [("Join Table", Orange.data.Table)]

        settings = QSettings()
        val = settings.value("ut-login/login", "unknown")
        self.login = val.toString()

        if self.login != "unknown":
            self.configListAttributesToJoin = '' # 'item-ut-item-ut-item'
            self.configSeparator = '' #'/'
            boxSettings = OWGUI.widgetBox(self.controlArea, "Configuration", addSpace=True)
            boxListAttributesToJoin = OWGUI.widgetBox(boxSettings, "Attribute to join", addSpace=True)
            self.attrList = OWGUI.listBox(boxListAttributesToJoin, self, callback = self.individualSelected)
            self.listAttributesToJoin = {}
            self.attrList.setItemDelegate(ImputeListItemDelegate(self, self.attrList))
            self.cbSep = OWGUI.comboBox(boxSettings, self, "Separator")
            self.cbSep.addItem(" ")
            self.cbSep.addItem(":")
            self.cbSep.addItem(";")
            self.cbSep.addItem("|")
            self.cbSep.addItem("_")
            self.cbSep.addItem("/")
            OWGUI.button(self.controlArea, self, 'Apply', callback=self.compute)
            self.configExplanation = "Your comment/explanation."
            OWGUI.lineEdit(self.controlArea, self, "configExplanation", box="Any comment or explanation about your function?")
            self.remplissageListe = 0
            owutInitPrevisualisationEntreesSorties(self)
            self.loadSettings()
        else:
            boxConnexion = OWGUI.widgetBox(self.controlArea, "Connection")
            label = OWGUI.label(boxConnexion, self, "Please connect to UnderTracks first! (File->Log on UT)" + self.login)

    def individualSelected(self, i = -1):
        if self.remplissageListe == 0:
            if len(self.attrList.selectedItems())>0:
                if self.listAttributesToJoin.has_key(owutStrUtf(self.attrList.selectedItems()[0].text())):
                    self.listAttributesToJoin[owutStrUtf(self.attrList.selectedItems()[0].text())] = 1 - self.listAttributesToJoin[owutStrUtf(self.attrList.selectedItems()[0].text())]
                else:
                    self.listAttributesToJoin[owutStrUtf(self.attrList.selectedItems()[0].text())] = 1
                self.attrList.clearSelection ()

    def compute(self):
        if self.data != None:
            _sep = str(self.cbSep.itemText(self.cbSep.currentIndex()))
            _lst = ""
            for e in self.listAttributesToJoin.keys():
                if self.listAttributesToJoin[e]==1:
                  _lst  += ":ut-"+owutUtf2Ascii(e)
            res = mainOWUTJoin(_lst, _sep,  str(self.cfgNameNewAtt1), self.data)
            if res!=None:
                self.configSeparator = _sep
                self.configListAttributesToJoin = _lst
                self.saveSettings()
                self.send("Join Table", res)
                owutSetPrevisualisationSorties(self,res)

    def setData(self, data, id=None):
        self.data = data
        owutSetPrevisualisationEntrees(self,data)
        if self.data != None:
            if self.configSeparator != None:
                for i in range(len(self.cbSep)):
                    if self.cbSep.itemText(i)==self.configSeparator:
                        self.cbSep.setCurrentIndex(i)
                        break
            self.attrList.clear()
            attr = {}
            self.remplissageListe = 1
            for k in  range(len(self.data.domain)):
                self.attrList.addItem(QListWidgetItem(owutStrUtf(self.data.domain[k].name)))
                attr[owutStrUtf(self.data.domain[k].name)]=1
            attributsTousConnus = True
            if self.configListAttributesToJoin != None:
                self.listAttributesToJoin.clear()
                elts = self.configListAttributesToJoin.split(':ut-')[1:]
                for e in elts:
                    self.listAttributesToJoin[owutAscii2Utf(e)]=1
                    attributsTousConnus = attributsTousConnus and attr.has_key(owutAscii2Utf(e))
            self.remplissageListe = 0
            if (self.configListAttributesToJoin != None) and attributsTousConnus:
                self.compute()
            else:
                self.configListAttributesToJoin = ""
                self.listAttributesToJoin.clear()


def mainOWUTJoin(pList, pSep, pNameForNewAttribute, data):
    domains = []
    resultat = []
    for i in range(len(data.domain)):
        domains.append(Orange.feature.String(data.domain[i].name))
    if pNameForNewAttribute:
        tmpNameForNewAttribute =  pNameForNewAttribute
    else:
        tmpNameForNewAttribute =  owutNormaliseTailleNom("Joined attributes")
    domains.append(Orange.feature.String(owutValideNameAttributeFrom(tmpNameForNewAttribute,data.domain)))
    elts = pList.split(':ut-')
    attr = {}
    for e in elts:
        if len(e)>0:
            attr[owutAscii2Utf(e)]=1
    aPrendre = [False for i in data.domain]
    for k in range(len(data.domain)):
        if attr.has_key(owutStrUtf(data.domain[k].name)):
            aPrendre[k]=True
    for n in range(len(data)):
        ligneRes = []
        toBeJoined = []
        for j in range(len(data[n])):
            ligneRes.append(data[n][j].value)
            if aPrendre[j]:
               toBeJoined.append(data[n][j].value)
        ligneRes.append(pSep.join(toBeJoined))
        resultat.append(ligneRes)
    domain = Orange.data.Domain(domains)
    res = Orange.data.Table(domain, resultat)
    return res
