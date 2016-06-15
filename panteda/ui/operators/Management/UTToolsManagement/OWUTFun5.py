#!/usr/bin/python
#Orange Widget developped by Denis B. Oct., 2014., continued 2015, 2016


"""
<name>Fun5</name>
<icon>OWUTFun5_icons/OWUTFun5.svg</icon>
<description>Function with 5 args</description>
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


class OWUTFun5(OWWidget):
    settingsList = ['configForTheFunDefinition','configExplanation','configInitValue','cfgAttChoice1','cfgKeepAtt1','cfgAttChoice2','cfgKeepAtt2','cfgAttChoice3','cfgKeepAtt3','cfgAttChoice4','cfgKeepAtt4','cfgAttChoice5','cfgKeepAtt5','cfgNameNewAtt1']

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)
        self.data = None
        self.inputs = [("Table", Orange.data.Table, self.setData)]
        self.outputs = [("Fun5", Orange.data.Table)]
        settings = QSettings()
        val = settings.value("ut-login/login", "unknown")
        self.login = val.toString()
        if self.login != "unknown":
            boxSettings = OWGUI.widgetBox(self.controlArea, "Configuration", addSpace=True)
            owutAjouteChoixAttribut(boxSettings,self,"cfgAttChoice1","First Attribute ($0)")
            owutAjouteChoixAttribut(boxSettings,self,"cfgAttChoice2","Second Attribute ($1)")
            owutAjouteChoixAttribut(boxSettings,self,"cfgAttChoice3","Third Attribute ($2)")
            owutAjouteChoixAttribut(boxSettings,self,"cfgAttChoice4","Fourth Attribute ($3)")
            owutAjouteChoixAttribut(boxSettings,self,"cfgAttChoice5","Fifth Attribute ($4)")
            self.configInitValue = "0"
            self.configForTheFunDefinition = "int($0)+int($1)"
            OWGUI.lineEdit(boxSettings, self, "configInitValue", box="Init value $$ if necessary.")
            OWGUI.lineEdit(boxSettings, self, "configForTheFunDefinition", box="Your function. f($0,$1,$2,$3,$4) = ")
            self.infoArg = OWGUI.widgetLabel(boxSettings, '    $0, $1, ... stand for the raw - (string) - data')
            self.infoVal = OWGUI.widgetLabel(boxSettings, '    int($0), $I0, float($0), $F0, ... stand for the integer/float value of the data [when possible]')
            self.infoInitVal = OWGUI.widgetLabel(boxSettings, '    $$, $I, $F stand for the init (/integer/float) value on first calculus and for the previous result after first calculus')
            self.infoFun = OWGUI.widgetLabel(boxSettings, '    n.b.: you can use all python or user-added functions, e.g.: test(c,a,b) which returns a if c is true, or else returns b')
            OWGUI.button(self.controlArea, self, 'Apply', callback=self.compute)
            self.configExplanation = "Your comment/explanation."
            OWGUI.lineEdit(self.controlArea, self, "configExplanation", box="Any comment or explanation about your function?")
            owutInitPrevisualisationEntreesSorties(self)
            self.loadSettings()
        else:
            boxConnexion = OWGUI.widgetBox(self.controlArea, "Connection")
            OWGUI.label(boxConnexion, self, "Please connect to UnderTracks first! (File->Log on UT)" + self.login)

    def setData(self, data, id=None):
        self.data = data
        owutSetPrevisualisationEntrees(self,data)
        if self.data != None:
            firstAttrOk = owutInitChoixAttributEtVerifieConfig(self,"cfgAttChoice1",data.domain)
            secondAttrOk = owutInitChoixAttributEtVerifieConfig(self,"cfgAttChoice2",data.domain)
            thirdAttrOk = owutInitChoixAttributEtVerifieConfig(self,"cfgAttChoice3",data.domain)
            fourthAttrOk = owutInitChoixAttributEtVerifieConfig(self,"cfgAttChoice4",data.domain)
            fifthAttrOk = owutInitChoixAttributEtVerifieConfig(self,"cfgAttChoice5",data.domain)
            if firstAttrOk and secondAttrOk and thirdAttrOk and fourthAttrOk and fifthAttrOk:
                self.compute()

    def compute(self):
        if self.data != None:
            self.res = mainOWUTFun5(owutChoixAttribut(self,"cfgAttChoice1"), self.cfgKeepAtt1, owutChoixAttribut(self,"cfgAttChoice2"), self.cfgKeepAtt2, owutChoixAttribut(self,"cfgAttChoice3"), self.cfgKeepAtt3, owutChoixAttribut(self,"cfgAttChoice4"), self.cfgKeepAtt4, owutChoixAttribut(self,"cfgAttChoice5"), self.cfgKeepAtt5, str(self.configInitValue), str(self.configForTheFunDefinition), str(self.cfgNameNewAtt1), self.data)
            if self.res!=None:
                owutSynchroniseChoixAttribut(self)
                self.saveSettings()
                owutSetPrevisualisationSorties(self,self.res)
                self.send("Fun5", self.res)

def test(c,a,b):
    if c:
        return a
    else:
        return b

def mainOWUTFun5(pFirstAttribute, pKeepFirstAttribute, pSecondAttribute, pKeepSecondAttribute, pThirdAttribute, pKeepThirdAttribute, pFourthAttribute, pKeepFourthAttribute, pFifthAttribute, pKeepFifthAttribute, pConfigInitValue, pConfigForTheFunction, pNameForNewAttribute, dataIn):
    indFirstAttribute = owutIndiceAttribut(pFirstAttribute,dataIn.domain)
    indSecondAttribute = owutIndiceAttribut(pSecondAttribute,dataIn.domain)
    indThirdAttribute = owutIndiceAttribut(pThirdAttribute,dataIn.domain)
    indFourthAttribute = owutIndiceAttribut(pFourthAttribute,dataIn.domain)
    indFifthAttribute = owutIndiceAttribut(pFifthAttribute,dataIn.domain)
    if (indFirstAttribute==-1) or (indSecondAttribute==-1) or (indThirdAttribute==-1) or (indFourthAttribute==-1) or (indFifthAttribute==-1):
        return
    domains = [d for d in dataIn.domain]
    if pNameForNewAttribute:
        tmpNameForNewAttribute =  pNameForNewAttribute
    else:
        tmpNameForNewAttribute =  "fun5"
    domains.append(Orange.feature.String(owutValideNameAttributeFrom(tmpNameForNewAttribute,dataIn.domain)))
    newDomainsInit = Orange.data.Domain(domains)
    doNotKeep = []
    if not pKeepFirstAttribute:
        doNotKeep.append(indFirstAttribute)
    if not pKeepSecondAttribute:
        doNotKeep.append(indSecondAttribute)
    if not pKeepThirdAttribute:
        doNotKeep.append(indThirdAttribute)
    if not pKeepFourthAttribute:
        doNotKeep.append(indFourthAttribute)
    if not pKeepFifthAttribute:
        doNotKeep.append(indFifthAttribute)
    decalage = 0
    newDomainsFinal = newDomainsInit
    for i in sorted(doNotKeep):
        newDomainsFinal = Orange.data.Domain(newDomainsFinal[:i-decalage]+newDomainsFinal[i+1-decalage:])
        decalage = decalage+1
    resultat = [[x for x in lDataIn] for lDataIn in dataIn]
    previousResult = pConfigInitValue
    for i in range(len(dataIn)):
        toEvaluate = pConfigForTheFunction.replace('$0',"'"+dataIn[i][indFirstAttribute].value+"'").replace('$I0',"int('"+dataIn[i][indFirstAttribute].value+"')").replace('$F0',"float('"+dataIn[i][indFirstAttribute].value+"')").\
            replace('$1',"'"+dataIn[i][indSecondAttribute].value+"'").replace('$I1',"int('"+dataIn[i][indSecondAttribute].value+"')").replace('$F1',"float('"+dataIn[i][indSecondAttribute].value+"')").\
            replace('$2',"'"+dataIn[i][indThirdAttribute].value+"'").replace('$I2',"int('"+dataIn[i][indThirdAttribute].value+"')").replace('$F2',"float('"+dataIn[i][indThirdAttribute].value+"')").\
            replace('$3',"'"+dataIn[i][indFourthAttribute].value+"'").replace('$I3',"int('"+dataIn[i][indFourthAttribute].value+"')").replace('$F3',"float('"+dataIn[i][indFourthAttribute].value+"')").\
            replace('$4',"'"+dataIn[i][indFifthAttribute].value+"'").replace('$I4',"int('"+dataIn[i][indFifthAttribute].value+"')").replace('$F4',"float('"+dataIn[i][indFifthAttribute].value+"')").\
            replace('$$',"'"+previousResult+"'").replace('$I',"int('"+previousResult+"')").replace('$F',"float('"+previousResult+"')")
        createdValueForLineI = str(eval(toEvaluate))
        previousResult = createdValueForLineI
        resultat[i].append(createdValueForLineI)
    tmpOut =  Orange.data.Table(newDomainsInit, resultat)
    dataOut = Orange.data.Table(newDomainsFinal, tmpOut)
    return dataOut
