#!/usr/bin/python
#Orange Widget developped by Denis B. Oct., dec 2015


"""
<name>TJoin</name>
<icon>OWUTTJoin_icons/OWUTTJoin.svg</icon>
<description>Join 2 tables on one attribute</description>
<priority>991</priority>
"""

import Orange
from OWWidget import *
import OWGUI
if not sys.path[len(sys.path)-1].endswith("/Management/UTToolsManagement"):
    tmpSettings = QSettings()
    path = str(tmpSettings.value("ut-path/path", "unknown").toString()+"/Management/UTToolsManagement")
    sys.path.append(path)
from OWUTData import owutAjouteChoixAttribut
from OWUTData import owutChoixAttributDomain
from OWUTData import owutSynchroniseChoixAttribut
from OWUTData import owutInitChoixAttributEtVerifieConfig
from OWUTData import owutIndiceAttribut
from OWUTData import owutValideNameAttributeFrom
from OWUTData import owutNormaliseTailleNom


class OWUTTJoin(OWWidget):
    settingsList = ['primaryKey', 'foreignKey',"skipMissingValue","commentExplanation"]

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)
        self.primaryData = None
        self.foreignData = None
        self.firstAttrOk = False
        self.secondAttrOk = False
        self.inputs = [("Foreign Table - use", Orange.data.Table, self.setForeignData), ("Key Table - define", Orange.data.Table, self.setPrimaryData)]
        self.outputs = [("Joined Table", Orange.data.Table)]
        settings = QSettings()
        val = settings.value("ut-login/login", "unknown")
        self.login = val.toString()
        if self.login != "unknown":
            self.skipMissingValue = False
            boxSettings = OWGUI.widgetBox(self.controlArea, "Configuration", addSpace=True)
            owutAjouteChoixAttribut(boxSettings, self, "foreignKey", "Foreign Key in Foreign table (use)")
            owutAjouteChoixAttribut(boxSettings, self, "primaryKey", "Primary key in Key table (define)")
            OWGUI.checkBox(boxSettings, self, 'skipMissingValue', "Skip foreign value without defined key")
            OWGUI.button(self.controlArea, self, 'Apply', callback=self.compute)
            self.commentExplanation = "Your comment/explanation."
            boxCommentExplanation = OWGUI.lineEdit(self.controlArea, self, "commentExplanation", box="Any comment or explanation?")
            self.loadSettings()
        else:
            boxConnexion = OWGUI.widgetBox(self.controlArea, "Connection")
            label = OWGUI.label(boxConnexion, self, "Please connect to UnderTracks first! (File->Log on UT)" + self.login)

    def setPrimaryData(self, primaryData, id=None):
        self.primaryData = primaryData
        self.firstAttrOk = owutInitChoixAttributEtVerifieConfig(self, "primaryKey", primaryData.domain)
        if (self.primaryData != None) and (self.foreignData != None) and self.firstAttrOk and self.secondAttrOk:
            self.compute()

    def setForeignData(self, foreignData, id=None):
        self.foreignData = foreignData
        self.secondAttrOk = owutInitChoixAttributEtVerifieConfig(self, "foreignKey", foreignData.domain)
        if (self.primaryData != None) and (self.foreignData != None) and self.firstAttrOk and self.secondAttrOk:
            self.compute()

    def compute(self):
        if (self.primaryData != None) and (self.foreignData != None):
            res = mainOWUTTJoin(self.primaryData, self.foreignData, owutChoixAttributDomain(self, "primaryKey", self.primaryData.domain),  owutChoixAttributDomain(self, "foreignKey", self.foreignData.domain), self.skipMissingValue)
            if res != None:
                owutSynchroniseChoixAttribut(self)
                self.saveSettings()
                self.send("Joined Table", res)



def mainOWUTTJoin(primaryData, foreignData, primaryKey, foreignKey, skipMissingValue):
    #recuperation des indices de colonne des attributs
    indPrimaryKey = owutIndiceAttribut(primaryKey, primaryData.domain)
    indForeignKey = owutIndiceAttribut(foreignKey, foreignData.domain)
    if (indPrimaryKey == -1) or (indForeignKey == -1):
        return
    #construction des domaines
    domains = [Orange.feature.String(d.name+"_Foreign") for d in foreignData.domain]
    for d in primaryData.domain:
        domains.append(Orange.feature.String(d.name+"_Primary"))
    #traitement
    if skipMissingValue:
        strVide = "ut__n.a.__tu"
    else:
        strVide = "n.a." #not available
    corespondances = {}
    for i in range(len(primaryData)):
        corespondances[primaryData[i][indPrimaryKey].value] = primaryData[i]
    tmpResultat = [[x.value for x in lForeignData] for lForeignData in foreignData]
    for i in range(len(foreignData)):
        for j in primaryData.domain:
            try:
                tmpResultat[i].append(corespondances[foreignData[i][indForeignKey].value][j].value)
            except:
                tmpResultat[i].append(strVide)
    domain = Orange.data.Domain(domains)
    if skipMissingValue:
        indDataARegarder = len(foreignData.domain)
        resultatFinal = []
        for r in tmpResultat:
            if r[indDataARegarder] != strVide:
                resultatFinal.append(r)
        dataOut = Orange.data.Table(domain, resultatFinal)
    else:
        dataOut = Orange.data.Table(domain, tmpResultat)
    return dataOut

