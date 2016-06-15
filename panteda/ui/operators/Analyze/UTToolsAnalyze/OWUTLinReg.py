#!/usr/bin/python
#Orange Widget developped by Denis B. Oct., 2014., continued 2015, 2016


"""
<name>LinReg</name>
<icon>OWUTLinReg_icons/OWUTLinReg.svg</icon>
<description>Compute linear regression between two attributes</description>
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

class OWUTLinReg(OWWidget):
    settingsList = ['configExplanation','cfgAttChoice1','cfgAttChoice2','cfgAttChoice3','cfgNameNewAtt0','cfgNameNewAtt1','cfgNameNewAtt2','cfgNameNewAtt3','cfgNameNewAtt4','cfgNameNewAtt5']

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
            owutAjouteChoixAttribut(boxSettings,self,"cfgAttChoice1","First Attribute")
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
            self.res = mainOWUTLinReg(owutChoixAttribut(self,"cfgAttChoice1"), owutChoixAttribut(self,"cfgAttChoice2"), owutChoixAttribut(self,"cfgAttChoice3"), str(self.cfgNameNewAtt0), str(self.cfgNameNewAtt1), str(self.cfgNameNewAtt2), str(self.cfgNameNewAtt3), str(self.cfgNameNewAtt4), str(self.cfgNameNewAtt5), self.data)
            if self.res!=None:
                owutSynchroniseChoixAttribut(self)
                self.saveSettings()
                owutSetPrevisualisationSorties(self,self.res)
                self.send("Table", self.res)

def mainOWUTLinReg(pAttribute1, pAttribute2, pAttribute3, pNameForNewAttribute0, pNameForNewAttribute1, pNameForNewAttribute2, pNameForNewAttribute3, pNameForNewAttribute4, pNameForNewAttribute5, dataIn):
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
        tmpNameForNewAttribute1 =  owutNormaliseTailleNom("slope")
    if pNameForNewAttribute2:
        tmpNameForNewAttribute2 =  pNameForNewAttribute2
    else:
        tmpNameForNewAttribute2 =  owutNormaliseTailleNom("intercept")
    if pNameForNewAttribute3:
        tmpNameForNewAttribute3 =  pNameForNewAttribute3
    else:
        tmpNameForNewAttribute3 =  owutNormaliseTailleNom("r_value")
    if pNameForNewAttribute4:
        tmpNameForNewAttribute4 =  pNameForNewAttribute4
    else:
        tmpNameForNewAttribute4 =  owutNormaliseTailleNom("p_value")
    if pNameForNewAttribute5:
        tmpNameForNewAttribute5 =  pNameForNewAttribute5
    else:
        tmpNameForNewAttribute5 =  owutNormaliseTailleNom("std_err")
    features = [Orange.feature.String(tmpNameForNewAttribute0),Orange.feature.String(tmpNameForNewAttribute1),Orange.feature.String(tmpNameForNewAttribute2),Orange.feature.String(tmpNameForNewAttribute3),Orange.feature.String(tmpNameForNewAttribute4),Orange.feature.String(tmpNameForNewAttribute5)]
    domain = Orange.data.Domain(features)
    resultats = []
    tabX = []
    tabY = []
    for i in range(len(dataIn)):
        strX = dataIn[i][indAttribute1].value
        strY = dataIn[i][indAttribute2].value
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
        if (i==(len(dataIn)-1)) or ((not owutEstChoixVide(pAttribute3)) and (dataIn[i][indAttribute3].value!=dataIn[i+1][indAttribute3].value)):
            if len(tabX) != len(tabY):
                return
            slope, intercept, r_value, p_value, std_err = stats.linregress(tabX,tabY)
            if (owutEstChoixVide(pAttribute3)):
                resultats.append(["all_data", str(slope), str(intercept), str(r_value), str(p_value), str(std_err)])
            else:
                resultats.append([dataIn[i][indAttribute3].value, str(slope), str(intercept), str(r_value), str(p_value), str(std_err)])
            tabX = []
            tabY = []
    res = Orange.data.Table(domain,resultats)
    return res

