#!/usr/bin/python
#Orange Widget developped by Denis B. Oct., 2014., continued 2015, 2016


"""
<name>TTest</name>
<icon>OWUTTTest_icons/OWUTTTest.svg</icon>
<description>computes Student's t-test</description>
<priority>991</priority>
"""

import Orange
from OWWidget import *
import OWGUI
if not sys.path[len(sys.path)-1].endswith("/Management/UTToolsManagement"):
    tmpSettings = QSettings()
    path = str(tmpSettings.value("ut-path/path","unknown").toString()+"/Management/UTToolsManagement")
    sys.path.append(path)
from scipy import stats
from OWUTData import owutInitPrevisualisationEntreesSorties
from OWUTData import owutSetPrevisualisationSorties
from OWUTData import owutSetPrevisualisationEntrees
from OWUTData import owutAjouteChoixAttribut
from OWUTData import owutChoixAttribut
from OWUTData import owutSynchroniseChoixAttribut
from OWUTData import owutInitChoixAttributEtVerifieConfig
from OWUTData import owutInitChoixAttributAvecChoixVideEtVerifieConfig
from OWUTData import owutIndiceAttribut
from OWUTData import owutValideNameAttributeFrom
from OWUTData import owutNormaliseTailleNom
from OWUTData import owutEstChoixVide

class OWUTTTest(OWWidget):
    settingsList = ['configExplanation','cfgAgainstMean','givenMean','againstIndAttr','againstDepAttr','cfgAttChoiceMain','cfgAttChoiceInd','cfgAttChoiceDep','cfgAttChoiceGroup']

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)
        self.data = None
        self.inputs = [("Table", Orange.data.Table, self.setData)]
        self.outputs = [("Table", Orange.data.Table)]
        settings = QSettings()
        val = settings.value("ut-login/login", "unknown")
        self.login = val.toString()
        if self.login != "unknown":
            owutAjouteChoixAttribut(self.controlArea,self,"cfgAttChoiceMain","Compare Attribute")
            boxAgainst = OWGUI.widgetBox(self.controlArea, "Against", addSpace=True)
            self.cfgAgainstMean=True
            boxMean = OWGUI.widgetBox(boxAgainst, "Mean", addSpace=True)
            OWGUI.checkBox(boxMean, self, 'cfgAgainstMean', "against mean selected")
            self.givenMean = "0.0"
            OWGUI.lineEdit(boxMean, self, "givenMean", box="Mean value")
            boxInd = OWGUI.widgetBox(boxAgainst, "Independant Attribute", addSpace=True)
            self.againstIndAttr=False
            OWGUI.checkBox(boxInd, self, 'againstIndAttr', "against ind. att. selected")
            owutAjouteChoixAttribut(boxInd,self,"cfgAttChoiceInd","Independant Attribute Choice")
            boxDep = OWGUI.widgetBox(boxAgainst, "Dependant Attribute", addSpace=True)
            self.againstDepAttr=False
            OWGUI.checkBox(boxDep, self, 'againstDepAttr', "against dep. att. selected")
            owutAjouteChoixAttribut(boxDep,self,"cfgAttChoiceDep","Dependant Attribute Choice")
            owutAjouteChoixAttribut(self.controlArea,self,"cfgAttChoiceGroup","Attribute Group choice (leave empty if no group segmentation)")
            OWGUI.button(self.controlArea, self, 'Apply', callback=self.compute)
            self.configExplanation = "Your comment/explanation."
            OWGUI.lineEdit(self.controlArea, self, "configExplanation", box="Any comment or explanation about your operation?")
            owutInitPrevisualisationEntreesSorties(self)
            self.loadSettings()
        else:
            boxConnexion = OWGUI.widgetBox(self.controlArea, "Connection")
            OWGUI.label(boxConnexion, self, "Please connect to UnderTracks first! (File->Log on UT)" + self.login)

    def setData(self, data, id=None):
        self.data = data
        owutSetPrevisualisationEntrees(self,data)
        if self.data != None:
            AttributeMainOk = owutInitChoixAttributEtVerifieConfig(self,"cfgAttChoiceMain",data.domain)
            AttributeIndOk = owutInitChoixAttributEtVerifieConfig(self,"cfgAttChoiceInd",data.domain)
            AttributeDepOk = owutInitChoixAttributEtVerifieConfig(self,"cfgAttChoiceDep",data.domain)
            AttributeGroupOk = owutInitChoixAttributAvecChoixVideEtVerifieConfig(self,"cfgAttChoiceGroup",data.domain)
            if AttributeMainOk and AttributeIndOk and AttributeDepOk and AttributeGroupOk:
                self.compute()

    def compute(self):
        if self.data != None:
            self.res = mainOWUTTTest(owutChoixAttribut(self,"cfgAttChoiceMain"), self.cfgAgainstMean, str(self.givenMean), self.againstIndAttr, owutChoixAttribut(self,"cfgAttChoiceInd"), self.againstDepAttr, owutChoixAttribut(self,"cfgAttChoiceDep"), owutChoixAttribut(self,"cfgAttChoiceGroup"), self.data)
            if self.res!=None:
                owutSynchroniseChoixAttribut(self)
                self.saveSettings()
                owutSetPrevisualisationSorties(self,self.res)
                self.send("Table", self.res)

def mainOWUTTTest(pAttributeMain, pAgainstMean, pGivenMean, pAgainstIndAttr, pAttributeInd, pAgainstDepAttr, pAttributeDep, pAttributeGroup, dataIn):
    indAttributeMain = owutIndiceAttribut(pAttributeMain,dataIn.domain)
    indAttributeInd = owutIndiceAttribut(pAttributeInd,dataIn.domain)
    indAttributeDep = owutIndiceAttribut(pAttributeDep,dataIn.domain)
    indAttributeGroup = owutIndiceAttribut(pAttributeGroup,dataIn.domain)
    if (indAttributeMain==-1) or (indAttributeInd==-1) or (indAttributeDep==-1) or ((indAttributeGroup==-1) and (not owutEstChoixVide(pAttributeGroup))):
        return
    if owutEstChoixVide(pAttributeGroup):
        tmpNameForNewAttribute0 =  owutNormaliseTailleNom("Group")
    else:
        tmpNameForNewAttribute0 =  owutNormaliseTailleNom(pAttributeGroup)
    tmpNameForNewAttribute1 =  owutNormaliseTailleNom("ScoreAgainstMean")
    tmpNameForNewAttribute2 =  owutNormaliseTailleNom("pvalueAgainstMean")
    tmpNameForNewAttribute3 =  owutNormaliseTailleNom("ScoreAgainstIndAttr")
    tmpNameForNewAttribute4 =  owutNormaliseTailleNom("pvalueAgainstIndAttr")
    tmpNameForNewAttribute5 =  owutNormaliseTailleNom("ScoreAgainstDepAttr")
    tmpNameForNewAttribute6 =  owutNormaliseTailleNom("pvalueAgainstDepAttr")
    features = [Orange.feature.String(tmpNameForNewAttribute0)]
    if pAgainstMean:
        try:
            valMean = int(pGivenMean)
        except:
            try:
                valMean = float(pGivenMean)
            except:
                pAgainstMean = False
    if pAgainstMean:
        features.append(Orange.feature.String(tmpNameForNewAttribute1))
        features.append(Orange.feature.String(tmpNameForNewAttribute2))
    if pAgainstIndAttr:
        features.append(Orange.feature.String(tmpNameForNewAttribute3))
        features.append(Orange.feature.String(tmpNameForNewAttribute4))
    if pAgainstDepAttr:
        features.append(Orange.feature.String(tmpNameForNewAttribute5))
        features.append(Orange.feature.String(tmpNameForNewAttribute6))
    domain = Orange.data.Domain(features)
    resultats = []
    tabX = []
    tabY = []
    for i in range(len(dataIn)):
        strX = dataIn[i][indAttributeMain].value
        strY = dataIn[i][indAttributeInd].value
        try:
            valX = int(strX)
            valY = int(strY)
            tabX.append(valX)
            tabY.append(valY)
        except:
            try:
                valX = float(strX)
                valY = float(strY)
                tabX.append(valX)
                tabY.append(valY)
            except:
                pass
        if (i==(len(dataIn)-1)) or ((not owutEstChoixVide(pAttributeGroup)) and (dataIn[i][indAttributeGroup].value!=dataIn[i+1][indAttributeGroup].value)):
            if len(tabX) != len(tabY):
                return
            if (owutEstChoixVide(pAttributeGroup)):
                resultat=["all_data"]
            else:
                resultat=[dataIn[i][indAttributeGroup].value]
            if pAgainstMean:
                scoreAgainstMean, p_valueAgainstMean = stats.ttest_1samp(tabX,valMean)
                resultat.append(str(scoreAgainstMean))
                resultat.append(str(p_valueAgainstMean))
            if pAgainstIndAttr:
                scoreAgainstIndAttr, p_valueAgainstIndAttr = stats.ttest_ind(tabX,tabY)
                resultat.append(str(scoreAgainstIndAttr))
                resultat.append(str(p_valueAgainstIndAttr))
            if pAgainstDepAttr:
                scoreAgainstDepAttr, p_valueAgainstDepAttr = stats.ttest_rel(tabX,tabY)
                resultat.append(str(scoreAgainstDepAttr))
                resultat.append(str(p_valueAgainstDepAttr))
            resultats.append(resultat)
            tabX = []
            tabY = []
    res = Orange.data.Table(domain,resultats)
    return res

