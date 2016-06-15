#!/usr/bin/python
#Orange Widget developped by Denis B. Oct., 2014., continued 2015, 2016


"""
<name>VarRatio</name>
<icon>OWUTVarRatio_icons/OWUTVarRatio.svg</icon>
<description>VarRatio computes variance ratio (Eta-squared)</description>
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
from OWUTData import owutInitChoixAttributAvecChoixVideEtVerifieConfig
from OWUTData import owutIndiceAttribut
from OWUTData import owutValideNameAttributeFrom
from OWUTData import owutNormaliseTailleNom
from OWUTData import owutEstChoixVide

class OWUTVarRatio(OWWidget):
    settingsList = ['configExplanation','cfgAttChoice1','cfgAttChoice2','cfgAttChoice3','cfgNameNewAtt0','cfgNameNewAtt1','cfgNameNewAtt2','cfgNameNewAtt3']

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)
        self.data = None
        self.inputs = [("Table", Orange.data.Table, self.setData)]
        self.outputs = [("Table", Orange.data.Table)]
        settings = QSettings()
        val = settings.value("ut-login/login", "unknown")
        self.login = val.toString()
        if self.login != "unknown":
            boxSettings = OWGUI.widgetBox(self.controlArea, "Configuration", addSpace=True)
            owutAjouteChoixAttribut(boxSettings,self,"cfgAttChoice1","First numerical Attribute")
            owutAjouteChoixAttribut(boxSettings,self,"cfgAttChoice2","Second Attribute")
            owutAjouteChoixAttribut(boxSettings,self,"cfgAttChoice3","Group by Attribute")
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
            Attribute1Ok = owutInitChoixAttributEtVerifieConfig(self,"cfgAttChoice1",data.domain)
            Attribute2Ok = owutInitChoixAttributEtVerifieConfig(self,"cfgAttChoice2",data.domain)
            Attribute3Ok = owutInitChoixAttributAvecChoixVideEtVerifieConfig(self,"cfgAttChoice3",data.domain)
            if Attribute1Ok and Attribute2Ok and Attribute3Ok:
                self.compute()

    def compute(self):
        if self.data != None:
            self.res = mainOWUTVarRatio(owutChoixAttribut(self,"cfgAttChoice1"), owutChoixAttribut(self,"cfgAttChoice2"), owutChoixAttribut(self,"cfgAttChoice3"), str(self.cfgNameNewAtt0), str(self.cfgNameNewAtt1), str(self.cfgNameNewAtt2), str(self.cfgNameNewAtt3), self.data)
            if self.res!=None:
                owutSynchroniseChoixAttribut(self)
                self.saveSettings()
                owutSetPrevisualisationSorties(self,self.res)
                self.send("Table", self.res)

def mainOWUTVarRatio(pAttribute1, pAttribute2, pAttribute3, pNameForNewAttribute0, pNameForNewAttribute1, pNameForNewAttribute2, pNameForNewAttribute3, dataIn):
    indAttribute1 = owutIndiceAttribut(pAttribute1,dataIn.domain)
    indAttribute2 = owutIndiceAttribut(pAttribute2,dataIn.domain)
    indAttribute3 = owutIndiceAttribut(pAttribute3,dataIn.domain)
    if (indAttribute1==-1) or (indAttribute2==-1) or ((indAttribute3==-1) and (not owutEstChoixVide(pAttribute3))):
        return
    if pNameForNewAttribute0:
        tmpNameForNewAttribute0 =  pNameForNewAttribute0
    elif owutEstChoixVide(pAttribute3):
        tmpNameForNewAttribute0 =  owutNormaliseTailleNom("Group")
    else:
        tmpNameForNewAttribute0 =  owutNormaliseTailleNom(pAttribute3)
    if pNameForNewAttribute1:
        tmpNameForNewAttribute1 =  pNameForNewAttribute1
    else:
        tmpNameForNewAttribute1 =  owutNormaliseTailleNom("Eta2")
    if pNameForNewAttribute2:
        tmpNameForNewAttribute2 =  pNameForNewAttribute2
    else:
        tmpNameForNewAttribute2 =  owutNormaliseTailleNom("SSBetween")
    if pNameForNewAttribute3:
        tmpNameForNewAttribute3 =  pNameForNewAttribute3
    else:
        tmpNameForNewAttribute3 =  owutNormaliseTailleNom("SSTotal")
    features = [Orange.feature.String(tmpNameForNewAttribute0),Orange.feature.String(tmpNameForNewAttribute1),Orange.feature.String(tmpNameForNewAttribute2),Orange.feature.String(tmpNameForNewAttribute3)]
    domain = Orange.data.Domain(features)
    resultats = []
    sumX = 0.0
    tabX = []
    tabY = {}
    for i in range(len(dataIn)):
        strX = dataIn[i][indAttribute1].value
        strY = dataIn[i][indAttribute2].value
        try:
            valX = int(strX)
            tabX.append(valX)
            sumX = sumX + valX
            if tabY.has_key(strY):
                tabY[strY].append(valX)
            else:
                tabY[strY]=[valX]
        except:
            try:
                valX = float(strX)
                tabX.append(valX)
                sumX = sumX + valX
                if tabY.has_key(strY):
                    tabY[strY].append(valX)
                else:
                    tabY[strY]=[valX]
            except:
                pass
        if (i==(len(dataIn)-1)) or ((not owutEstChoixVide(pAttribute3)) and (dataIn[i][indAttribute3].value!=dataIn[i+1][indAttribute3].value)):
            if len(tabX)==0:
                if (owutEstChoixVide(pAttribute3)):
                    resultats.append(["all_data","n.a.","n.a.","n.a."])
                else:
                    resultats.append([dataIn[i][indAttribute3].value,"n.a.","n.a.","n.a."])
            else:
                avgX = float(sumX) / len(tabX)
                varTotal2 = 0.0
                varIntra2 = 0.0
                for x in tabX:
                    varTotal2 = varTotal2 + (x-avgX)*(x-avgX)
                varTotal2 = varTotal2 / len(tabX)
                for y in tabY.keys():
                    sumIntraY = 0.0
                    for x in tabY[y]:
                        sumIntraY = sumIntraY + x
                    avgIntraY = sumIntraY / len(tabY[y])
                    varIntraY2 = 0.0
                    for x in tabY[y]:
                        varIntraY2 = varIntraY2 + (x-avgIntraY)*(x-avgIntraY)
                    varIntra2 = varIntra2 + varIntraY2
                varIntra2 = varIntra2 / len(tabX)
                if varTotal2==0:
                    if (owutEstChoixVide(pAttribute3)):
                        resultats.append(["all_data","n.a.","n.a.","n.a."])
                    else:
                        resultats.append([dataIn[i][indAttribute3].value,"n.a.","n.a.","n.a."])
                else:
                    eta2 = (varTotal2 - varIntra2) / varTotal2
                    if (owutEstChoixVide(pAttribute3)):
                        resultats.append(["all_data",str(eta2),str(varTotal2 - varIntra2),str(varTotal2)])
                    else:
                        resultats.append([dataIn[i][indAttribute3].value,str(eta2),str(varTotal2 - varIntra2),str(varTotal2)])
            sumX = 0.0
            tabX = []
            tabY = {}
    res = Orange.data.Table(domain,resultats)
    return res

