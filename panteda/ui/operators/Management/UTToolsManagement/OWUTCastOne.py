#!/usr/bin/python
#Orange Widget developped by Denis B. Sept, 2014.

#TODO : pour le cast vers num, se mefier des float avec "," ou "." !!!
#TODO : factoriser le code versNum

"""
<name>CastOne</name>
<icon>OWUTCastOne_icons/OWUTCastOne.svg</icon>
<description>Output = (castOne ) Input</description>
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
from OWUTData import owutAjouteChoixAttribut
from OWUTData import owutChoixAttribut
from OWUTData import owutSynchroniseChoixAttribut
from OWUTData import owutInitChoixAttributEtVerifieConfig
from OWUTData import owutIndiceAttribut
from OWUTData import owutCastContinuous

class OWUTCastOne(OWWidget):
    settingsList = ['cfgAttChoice1','configExplanation','cfgAttChoice2','cfgKeepAtt1']

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)
        self.data = None
        self.inputs = [("Table", Orange.data.Table, self.setData)]
        self.outputs = [("Cast", Orange.data.Table)]
        settings = QSettings()
        val = settings.value("ut-login/login", "unknown")
        self.login = val.toString()
        if self.login != "unknown":
            boxSettings = OWGUI.widgetBox(self.controlArea, "Configuration", addSpace=True)
            owutAjouteChoixAttribut(boxSettings,self,"cfgAttChoice1","Attribut")
            owutAjouteChoixAttribut(boxSettings,self,"cfgAttChoice2","Types")
            OWGUI.button(self.controlArea, self, 'Apply', callback=self.compute)
            self.configExplanation = "Your comment/explanation."
            OWGUI.lineEdit(self.controlArea, self, "configExplanation", box="Any comment or explanation about your operation?")
            owutInitPrevisualisationEntreesSorties(self)
            self.loadSettings()
        else:
            self.boxSettings = OWGUI.widgetBox(self.controlArea, "Connection")
            label = OWGUI.label(self.boxSettings, self,"Please connect to UnderTracks first! (File->Log on UT)" + self.login)

    def setData(self, data, id=None):
        self.data = data
        owutSetPrevisualisationEntrees(self,data)
        if self.data != None:
            attrOk = owutInitChoixAttributEtVerifieConfig(self,"cfgAttChoice1",data.domain)
            typeOk = owutInitChoixAttributEtVerifieConfig(self,"cfgAttChoice2",["String","Discrete","Continuous"])
            if attrOk and typeOk:
                self.compute()

    def compute(self):
        if self.data != None:
            res = mainOWUTCastOne(owutChoixAttribut(self,"cfgAttChoice1"), owutChoixAttribut(self,"cfgAttChoice2"), self.cfgKeepAtt1, self.data)
            if res!=None:
                owutSynchroniseChoixAttribut(self)
                self.saveSettings()
                self.send("Cast", res)
                owutSetPrevisualisationSorties(self,res)

def mainOWUTCastOne(vAtt, vCast, pKeepAttribute, data):
    resultat = []
    domains = []
    indAtt = owutIndiceAttribut(vAtt,data.domain)
    if indAtt==-1:
        return
    if vCast=="Discrete":
        domaineDiscret = {}
        for i in range(len(data)):
            domaineDiscret[data[i][indAtt].value] = 1
    for i in range(len(data.domain)):
        domains.append(data.domain[i])
        if i==indAtt:
            if vCast == "Discrete":
                domains.append(Orange.feature.Discrete(data.domain[i].name+"_Discrete", values=domaineDiscret.keys()))
            elif vCast == "Continuous":
                domains.append(Orange.feature.Continuous(data.domain[i].name+"_Continuous"))
            else:
                domains.append(Orange.feature.String(data.domain[i].name+"_String"))
    for ligne in data:
        ligneRes = []
        for i in range(len(ligne)):
            ligneRes.append(ligne[i].value)
            if i==indAtt:
                if vCast == "Discrete":
                    ligneRes.append(ligne[i].value)
                elif vCast == "Continuous":
                    ligneRes.append(owutCastContinuous(ligne[i].value))
                else:
                    ligneRes.append(ligne[i].value)
        resultat.append(ligneRes)
    fullDomains = Orange.data.Domain(domains)
    if pKeepAttribute:
        reducedDomain = fullDomains
    else:
        reducedDomain = Orange.data.Domain(fullDomains[:indAtt]+fullDomains[indAtt+1:])
    res = Orange.data.Table(reducedDomain, resultat)
    return res
