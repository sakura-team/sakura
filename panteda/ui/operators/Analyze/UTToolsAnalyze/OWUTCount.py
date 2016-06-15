#!/usr/bin/python
#Orange Widget initiated by Michael ORTEGA - 20/May/2014
#Orange Widget continued by Denis B. - June/2014, 2016

"""
<name>Count</name>
<icon>OWUTCount_icons/OWUTCount.svg</icon>
<description>Count the number of each value for an attribute</description>
<priority>40</priority>
"""

import Orange
from OWWidget import *
import OWGUI
if not sys.path[len(sys.path)-1].endswith("/Management/UTToolsManagement"):
    tmpSettings = QSettings()
    path = str(tmpSettings.value("ut-path/path","unknown").toString()+"/Management/UTToolsManagement")
    sys.path.append(path)
from OWUTData import owutInitPrevisualisationEntreesSorties
from OWUTData import owutSetVisualisationSorties
from OWUTData import owutSetPrevisualisationEntrees
from OWUTData import owutAjouteChoixAttribut
from OWUTData import owutChoixAttribut
from OWUTData import owutSynchroniseChoixAttribut
from OWUTData import owutInitChoixAttributEtVerifieConfig
from OWUTData import owutIndiceAttribut
from OWUTData import owutValideNameAttributeFrom

class OWUTCount(OWWidget):
    settingsList = ['configMainAttribute','configExplanation','cfgNameNewAtt0','cfgNameNewAtt1','cfgNameNewAtt2']

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)
        self.data = None
        self.inputs = [("Table", Orange.data.Table, self.setData)]
        self.outputs = [("Count Table", Orange.data.Table),("Aggregated Count Table", Orange.data.Table)]
        settings = QSettings()
        val = settings.value("ut-login/login", "unknown")
        self.login = val.toString()
        if self.login != "unknown":
            boxSettings = OWGUI.widgetBox(self.controlArea, "Configuration", addSpace=True)
            owutAjouteChoixAttribut(boxSettings,self,"configMainAttribute","Count Attribute (default: action attribute)")
            OWGUI.button(self.controlArea, self, 'Apply', callback=self.compute)
            self.configExplanation = "Your comment/explanation."
            OWGUI.lineEdit(self.controlArea, self, "configExplanation", box="Any comment or explanation about your Count?")
            OWGUI.separator(self.controlArea)
            infoBox = OWGUI.widgetBox(self.controlArea, "Info")
            self.infoN = OWGUI.widgetLabel(infoBox, 'No data on input yet.')
            self.infoMin = OWGUI.widgetLabel(infoBox, '')
            self.infoMoy = OWGUI.widgetLabel(infoBox, '')
            self.infoMax = OWGUI.widgetLabel(infoBox, '')
            self.infoSum = OWGUI.widgetLabel(infoBox, '')
            owutInitPrevisualisationEntreesSorties(self)
            self.loadSettings()
        else:
            boxConnexion = OWGUI.widgetBox(self.controlArea, "Connection")
            label = OWGUI.label(boxConnexion, self, "Please connect to UnderTracks first! (File->Log on UT)" + self.login)

    def compute(self):
        if self.data != None:
            res = mainOWUTCount(owutChoixAttribut(self,"configMainAttribute"), str(self.cfgNameNewAtt0), str(self.cfgNameNewAtt1), str(self.cfgNameNewAtt2), self.data)
            if res!=None:
                owutSynchroniseChoixAttribut(self)
                self.saveSettings()
                self.send("Count Table", res[0])
                self.tableOutputs.setSortingEnabled(False)
                owutSetVisualisationSorties(self,res[0])
                self.tableOutputs.setSortingEnabled(True)
                if res[2]==0:
                    self.infoN.setText(str(res[1])+" values (no numerical value)")
                    self.infoMin.setText("")
                    self.infoMoy.setText("")
                    self.infoMax.setText("")
                    self.infoMax.setText("")
                elif res[2]==1:
                    self.infoN.setText(str(res[1])+" values (only one numerical value:"+str(res[3])+")")
                    self.infoMin.setText("")
                    self.infoMoy.setText("")
                    self.infoMax.setText("")
                    self.infoMax.setText("")
                elif res[1]==res[2]:
                    self.infoN.setText(str(res[1])+" values (all are numerical values)")
                    self.infoMin.setText("Min(numerical values) = "+str(res[3]))
                    self.infoMoy.setText("Moy(numerical values) = "+str(res[4]))
                    self.infoMax.setText("Max(numerical values) = "+str(res[5]))
                    self.infoMax.setText("Sum(numerical values) = "+str(res[6]))
                else:
                    self.infoN.setText(str(res[1])+" values (only "+str(res[2])+" numerical values)")
                    self.infoMin.setText("Min(numerical values) = "+str(res[3]))
                    self.infoMoy.setText("Moy(numerical values) = "+str(res[4]))
                    self.infoMax.setText("Max(numerical values) = "+str(res[5]))
                    self.infoMax.setText("Sum(numerical values) = "+str(res[6]))
                aggregFeatures = [Orange.feature.String("Attribute"), Orange.feature.String("NValues"), Orange.feature.String("NNumValues"),Orange.feature.String("MinNumValues"),Orange.feature.String("MoyNumValues"),Orange.feature.String("MaxNumValues"),Orange.feature.String("SumNumValues")]
                aggregDomain = Orange.data.Domain(aggregFeatures)
                aggregRow = [[owutChoixAttribut(self,"configMainAttribute"),str(res[1]),str(res[2]),str(res[3]),str(res[4]),str(res[5]),str(res[6])]]
                aggregTable = Orange.data.Table(aggregDomain, aggregRow)
                self.send("Aggregated Count Table", aggregTable)

    def setData(self, data, id=None):
        self.data = data
        owutSetPrevisualisationEntrees(self,data)
        if self.data != None:
            firstAttrOk = owutInitChoixAttributEtVerifieConfig(self,"configMainAttribute",data.domain)
            if firstAttrOk:
                self.compute()


def mainOWUTCount(mainAttribute, pNameForNewAttribute0, pNameForNewAttribute1, pNameForNewAttribute2, data):
    variables = []
    nb_variables = []
    lN = "n.a."
    lMin = "n.a."
    lMoy = "n.a."
    lMax = "n.a."
    lSum = "n.a."
    indMainAttribute = owutIndiceAttribut(mainAttribute,data.domain)
    if indMainAttribute==-1:
        return
    for d in data:
        v = d[indMainAttribute]
        try:
            contain = variables.index(v)
            nb_variables[contain] = nb_variables[contain] + 1
        except:
            variables.append(v)
            nb_variables.append(1)
        numValue = "n.a."
        if (type(v.value) is float) or (type(v.value) is int):
            numValue = v.value
        elif str(v).isdigit():
            numValue = int(str(v))
        else:
            try:
                numValue = float(str(v))
            except:
                numValue = numValue
        if (lN == "n.a.") and ( (type(numValue) is float) or (type(numValue) is int)):
            lN = 1
            lMin = numValue
            lMax = numValue
            lSum = numValue
        elif (type(numValue) is float) or (type(numValue) is int):
            lN = lN + 1
            if lMin>numValue:
                lMin = numValue
            if lMax<numValue:
                lMax = numValue
            lSum = lSum + numValue
    if 1:
        if pNameForNewAttribute0:
            tmpNameForNewAttribute0 =  pNameForNewAttribute0
        else:
            tmpNameForNewAttribute0 =  mainAttribute
        if pNameForNewAttribute1:
            tmpNameForNewAttribute1 =  pNameForNewAttribute1
        else:
            tmpNameForNewAttribute1 =  "Quantity"
        if pNameForNewAttribute2:
            tmpNameForNewAttribute2 =  pNameForNewAttribute2
        else:
            tmpNameForNewAttribute2 =  "Percent"

        features = [Orange.feature.String(tmpNameForNewAttribute0), Orange.feature.String(tmpNameForNewAttribute1), Orange.feature.String(tmpNameForNewAttribute2)]
        domain = Orange.data.Domain(features)
        rows = []
        n = len(data)
        for v, nb_v in zip(variables, nb_variables):
            rows.append([str(v), str(nb_v), str((nb_v*100)/n)])
        if lN == "n.a.":
            lN = 0
        else:
            lMoy = lSum / lN
        res = [Orange.data.Table(domain, rows),n,lN,lMin,lMoy,lMax,lSum]
    return res