#!/usr/bin/python
#Orange Widget developped by Denis B. Feb. 2016


"""
<name>Outline</name>
<icon>OWUTOutline_icons/OWUTOutline.svg</icon>
<description>Outline, delinearise linearised data</description>
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
from OWUTData import owutValideNameAttributeFrom
from OWUTData import owutNormaliseTailleNom


class OWUTOutline(OWWidget):
    settingsList = ['firstAttribute','secondAttribute','defaultValueForVoid',"commentExplanation",'cfgNameNewAtt1']

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)
        self.data = None
        self.inputs = [("Table", Orange.data.Table, self.setData)]
        self.outputs = [("Outline Table", Orange.data.Table)]
        settings = QSettings()
        val = settings.value("ut-login/login", "unknown")
        self.login = val.toString()
        if self.login != "unknown":
            boxSettings = OWGUI.widgetBox(self.controlArea, "Configuration", addSpace=True)
            owutAjouteChoixAttribut(boxSettings,self,"firstAttribute","Attribute Name")
            owutAjouteChoixAttribut(boxSettings,self,"secondAttribute","Attribute Value")
            self.defaultValueForVoid="defaultValue"
            boxForVoidValue = OWGUI.lineEdit(self.controlArea, self, "defaultValueForVoid", box="Default value?")
            OWGUI.button(self.controlArea, self, 'Apply', callback=self.compute)
            self.commentExplanation = "Your comment/explanation."
            boxCommentExplanation = OWGUI.lineEdit(self.controlArea, self, "commentExplanation", box="Any comment or explanation?")
            owutInitPrevisualisationEntreesSorties(self)
            self.loadSettings()
        else:
            boxConnexion = OWGUI.widgetBox(self.controlArea, "Connection")
            label = OWGUI.label(boxConnexion, self, "Please connect to UnderTracks first! (File->Log on UT)" + self.login)

    def setData(self, data, id=None):
        self.data = data
        owutSetPrevisualisationEntrees(self,data)
        if self.data != None:
            firstAttrOk = owutInitChoixAttributEtVerifieConfig(self,"firstAttribute",data.domain)
            secondAttrOk = owutInitChoixAttributEtVerifieConfig(self,"secondAttribute",data.domain)
            if firstAttrOk and secondAttrOk:
                self.compute()

    def compute(self):
        if self.data != None:
            res = mainOWUTOutline(owutChoixAttribut(self,"firstAttribute"), owutChoixAttribut(self,"secondAttribute"), str(self.defaultValueForVoid), str(self.cfgNameNewAtt1), self.data)
            if res!=None:
                owutSynchroniseChoixAttribut(self)
                self.saveSettings()
                self.send("Outline Table", res)
                owutSetPrevisualisationSorties(self,res)


def mainOWUTOutline(pFirstAttribute, pSecondAttribute, pDefaultValueForVoid, pNameForNewAttribute, dataIn):
    indFirstAttribute = owutIndiceAttribut(pFirstAttribute,dataIn.domain)
    indSecondAttribute = owutIndiceAttribut(pSecondAttribute,dataIn.domain)
    if (indFirstAttribute==-1) or (indSecondAttribute==-1):
        return
    #construction des domaines (nom des attributs)
    domains = []
    if pNameForNewAttribute:
        tmpNameForNewAttribute =  pNameForNewAttribute
    else:
        tmpNameForNewAttribute =  owutNormaliseTailleNom("Att_")
    for j in range(len(dataIn.domain)):
        if (j != indFirstAttribute) and (j != indSecondAttribute):
            domains.append(dataIn.domain[j])
    lesNouveauxAttributs = {}
    for n in dataIn:
        lesNouveauxAttributs[n[indFirstAttribute].value]=0
    lesNouveauxAttributsTries = sorted(lesNouveauxAttributs.keys())
    nbNouveauxAttributs = len(lesNouveauxAttributsTries)
    nbAnciensAttributs = len(dataIn.domain)-2
    indNouveauxAttributsTries = {}
    for x in range(nbNouveauxAttributs):
        indNouveauxAttributsTries[lesNouveauxAttributsTries[x]]=x+nbAnciensAttributs
    for k in lesNouveauxAttributsTries:
        domains.append(Orange.feature.String(owutValideNameAttributeFrom(tmpNameForNewAttribute+k,dataIn)))
    #construction des valeurs
    resultats = []
    nouvelleLigne = True
    tmp_resultat = []
    for i in range(len(dataIn)):
        next_tmp_resultat = []
        for j in range(len(dataIn.domain)):
            if nouvelleLigne:
                if (j != indFirstAttribute) and (j != indSecondAttribute):
                    tmp_resultat.append(dataIn[i][j].value)
            else:
                if (j != indFirstAttribute) and (j != indSecondAttribute) and (dataIn[i][j] != dataIn[i-1][j]):
                    nouvelleLigne = True
                    resultats.append(tmp_resultat)
                    tmp_resultat = next_tmp_resultat
                    tmp_resultat.append(dataIn[i][j].value)
                elif (j != indFirstAttribute) and (j != indSecondAttribute) and (dataIn[i][j] == dataIn[i-1][j]):
                    next_tmp_resultat.append(dataIn[i][j].value)
        if nouvelleLigne:
            for x in range(nbNouveauxAttributs):
                tmp_resultat.append(pDefaultValueForVoid)
            nouvelleLigne = False
        tmp_resultat[indNouveauxAttributsTries[dataIn[i][indFirstAttribute].value]]=dataIn[i][indSecondAttribute].value
    resultats.append(tmp_resultat)
    domain = Orange.data.Domain(domains)
    dataOut = Orange.data.Table(domain, resultats)
    return dataOut