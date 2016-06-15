#!/usr/bin/python
#Orange Widget developped by Denis B. May, 2014.

#TODO : pour le cast vers num, se mefier des float avec "," ou "." !!!
#TODO : factoriser le code versNum

"""
<name>Cast</name>
<icon>OWUTCast_icons/OWUTCast.svg</icon>
<description>Outputs = (cast ) Inputs</description>
<priority>31</priority>
"""

import Orange
from OWWidget import *
import OWGUI
import zlib
if not sys.path[len(sys.path)-1].endswith("/Management/UTToolsManagement"):
    tmpSettings = QSettings()
    path = str(tmpSettings.value("ut-path/path","unknown").toString()+"/Management/UTToolsManagement")
    sys.path.append(path)
from OWUTData import owutInitPrevisualisationEntreesSorties
from OWUTData import owutSetPrevisualisationSorties
from OWUTData import owutSetPrevisualisationEntrees
from OWUTData import owutStrUtf
from OWUTData import owutCastContinuous
from OWUTData import owutCastTime

class OWUTCast(OWWidget):
    settingsList = ['config','configExplanation']

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)
        self.data = None
        self.inputs = [("Table", Orange.data.Table, self.setData)]
        self.outputs = [("Cast Table", Orange.data.Table)]
        settings = QSettings()
        val = settings.value("ut-login/login", "unknown")
        self.login = val.toString()
        if self.login != "unknown":
            self.boxSettings = OWGUI.widgetBox(self.controlArea, "Configuration : cast all the attributes", addSpace=True)
            #self.boxCasts = OWGUI.widgetBox(self.controlArea, "Casts", addSpace=True)
            self.scrollArea = QScrollArea(self)
            self.boxSettings.layout().addWidget(self.scrollArea)
            self.scrollArea.setWidgetResizable(1)
            self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            self.boxCasts = OWGUI.widgetBox(self.scrollArea, "Casts", addSpace=True)
            self.scrollArea.setWidget(self.boxCasts)
            OWGUI.button(self.controlArea, self, 'Apply', callback=self.compute)
            self.configExplanation = "Your comment/explanation."
            OWGUI.lineEdit(self.controlArea, self, "configExplanation", box="Any comment or explanation about your operation?")
            owutInitPrevisualisationEntreesSorties(self)
            self.loadSettings()
        else:
            self.boxSettings = OWGUI.widgetBox(self.controlArea, "Connection")
            label = OWGUI.label(self.boxSettings, self,
                                "Please connect to UnderTracks first! (File->Log on UT)" + self.login)

    def compute(self):
        if self.data != None:
            nouvConfig = ""
            for i in range(0,len(self.casts)):
                nouvConfig += "_!_" + self.casts[i].itemText(self.casts[i].currentIndex())
            res = mainOWUTCast(self.casts, self.data)
            if res!=None:
                self.config = nouvConfig[3:]
                self.saveSettings()
                self.send("Cast Table", res)
                owutSetPrevisualisationSorties(self,res)

    def setData(self, data, id=None):
        self.data = data
        owutSetPrevisualisationEntrees(self,data)
        if self.data != None:
            self.casts = []
            if hasattr(self,'widgets'):
                for e in self.widgets:
                    e.hide()
            self.widgets = []
            for elt in data.domain:
                tmpDomain = OWGUI.widgetBox(self.boxCasts, owutStrUtf(elt.name), addSpace=True)
                tmpList = OWGUI.comboBox(tmpDomain, self, "Cast " + elt.name)
                self.casts.append(tmpList)
                self.widgets.append(tmpDomain)
                tmpList.addItem("String")
                tmpList.addItem("Discrete")
                tmpList.addItem("Continuous")
            self.config = ''
            self.loadSettings()
            if self.config==None:
                return
            configs = self.config.split("_!_")
            if len(configs)==len(data.domain):
                indiceTmpCast = 0
                for eltConfig in configs:
                    for i in range(0,len(self.casts[indiceTmpCast])):
                        if self.casts[indiceTmpCast].itemText(i)==eltConfig:
                            self.casts[indiceTmpCast].setCurrentIndex(i)
                    indiceTmpCast += 1
                indiceTmpCast = 0
                nouvConfig = ""
                for eltConfig in configs:
                    nouvConfig += "_!_" + self.casts[indiceTmpCast].itemText(self.casts[indiceTmpCast].currentIndex())
                    indiceTmpCast += 1
                nouvelConfig = nouvConfig[3:]
                if nouvelConfig==self.config:
                    self.compute()

def mainOWUTCast(casts, data):
    resultat = []
    domains = []
    domainesDiscrets = [{} for i in range(len(data.domain))]
    for ligne in data:  #une premiere passe pour construire les domaines
        for i in range(len(ligne)):
            if str(casts[i].itemText(casts[i].currentIndex())) == "Discrete":
                domainesDiscrets[i][ligne[i].value] = 1
    for i in range(len(data.domain)):  #et ajouter les noms/types de domaines
        if str(casts[i].itemText(casts[i].currentIndex())) == "Discrete":
            domains.append(Orange.feature.Discrete(data.domain[i].name, values=domainesDiscrets[i].keys()))
        elif str(casts[i].itemText(casts[i].currentIndex())) == "Continuous":
            domains.append(Orange.feature.Continuous(data.domain[i].name))
        else:
            domains.append(Orange.feature.String(data.domain[i].name))
    for ligne in data:  #une seconde passe pour ajouter les donnees
        ligneRes = []
        for i in range(len(ligne)):
            if str(casts[i].itemText(casts[i].currentIndex())) == "Discrete":
                ligneRes.append(ligne[i].value)
            elif str(casts[i].itemText(casts[i].currentIndex())) == "Continuous":
                ligneRes.append(owutCastContinuous(ligne[i].value))
            else:
                ligneRes.append(ligne[i].value)
        resultat.append(ligneRes)
    domain = Orange.data.Domain(domains)
    res = Orange.data.Table(domain, resultat)
    return res
