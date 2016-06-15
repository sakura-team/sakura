#!/usr/bin/python
#Orange Widget developped by Denis B. Oct., 2014., continued 2015, 2016


"""
<name>NumDesc</name>
<icon>OWUTNumDesc_icons/OWUTNumDesc.svg</icon>
<description>Describes numerical attribute (min, MAX, count, sum, average)</description>
<priority>991</priority>
"""

import sys
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

class OWUTNumDesc(OWWidget):
    settingsList = ['configExplanation','configAddResultsAtEndOfData','cfgAttChoice1','cfgAttChoice2','cfgNameNewAtt0','cfgNameNewAtt1','cfgNameNewAtt2','cfgNameNewAtt3','cfgNameNewAtt4', 'cfgNameNewAtt5']

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
            self.configAddResultsAtEndOfData = False
            owutAjouteChoixAttribut(boxSettings,self,"cfgAttChoice1","Numerical Attribute to be described")
            owutAjouteChoixAttribut(boxSettings,self,"cfgAttChoice2","Group by Attribute")
            OWGUI.checkBox(boxSettings, self, 'configAddResultsAtEndOfData', "Add results at the end of all lines of data")
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
            Attribute2Ok = owutInitChoixAttributAvecChoixVideEtVerifieConfig(self,"cfgAttChoice2",data.domain)
            if Attribute1Ok and Attribute2Ok:
                self.compute()

    def compute(self):
        if self.data != None:
            self.res = mainOWUTNumDesc(self.configAddResultsAtEndOfData,owutChoixAttribut(self,"cfgAttChoice1"), owutChoixAttribut(self,"cfgAttChoice2"), str(self.cfgNameNewAtt0), str(self.cfgNameNewAtt1), str(self.cfgNameNewAtt2), str(self.cfgNameNewAtt3), str(self.cfgNameNewAtt4), str(self.cfgNameNewAtt5), self.data)
            if self.res!=None:
                owutSynchroniseChoixAttribut(self)
                self.saveSettings()
                owutSetPrevisualisationSorties(self,self.res)
                self.send("Table", self.res)

def mainOWUTNumDesc(pAddResultsAtEndOfData,pAttribute1, pAttribute2, pNameForNewAttribute0, pNameForNewAttribute1, pNameForNewAttribute2, pNameForNewAttribute3, pNameForNewAttribute4, pNameForNewAttribute5, dataIn):
    indAttribute1 = owutIndiceAttribut(pAttribute1,dataIn.domain)
    indAttribute2 = owutIndiceAttribut(pAttribute2,dataIn.domain)
    if (indAttribute1==-1) or ((indAttribute2==-1) and (not owutEstChoixVide(pAttribute2))):
        return
    if pNameForNewAttribute0:
        tmpNameForNewAttribute0 =  pNameForNewAttribute0
    elif owutEstChoixVide(pAttribute2):
        tmpNameForNewAttribute0 =  owutNormaliseTailleNom("Group")
    else:
        tmpNameForNewAttribute0 =  owutNormaliseTailleNom(pAttribute2)
    if pNameForNewAttribute1:
        tmpNameForNewAttribute1 =  pNameForNewAttribute0
    else:
        tmpNameForNewAttribute1 =  owutNormaliseTailleNom("min")
    if pNameForNewAttribute2:
        tmpNameForNewAttribute2 =  pNameForNewAttribute0
    else:
        tmpNameForNewAttribute2 =  owutNormaliseTailleNom("MAX")
    if pNameForNewAttribute3:
        tmpNameForNewAttribute3 =  pNameForNewAttribute0
    else:
        tmpNameForNewAttribute3 =  owutNormaliseTailleNom("Card")
    if pNameForNewAttribute4:
        tmpNameForNewAttribute4 =  pNameForNewAttribute0
    else:
        tmpNameForNewAttribute4 =  owutNormaliseTailleNom("Sum")
    if pNameForNewAttribute1:
        tmpNameForNewAttribute5 =  pNameForNewAttribute0
    else:
        tmpNameForNewAttribute5 =  owutNormaliseTailleNom("Avg")
    if pAddResultsAtEndOfData:
        domains = [d for d in dataIn.domain]
        domains.append(Orange.feature.String(owutValideNameAttributeFrom(tmpNameForNewAttribute1,dataIn.domain)))
        domains.append(Orange.feature.String(owutValideNameAttributeFrom(tmpNameForNewAttribute2,dataIn.domain)))
        domains.append(Orange.feature.String(owutValideNameAttributeFrom(tmpNameForNewAttribute3,dataIn.domain)))
        domains.append(Orange.feature.String(owutValideNameAttributeFrom(tmpNameForNewAttribute4,dataIn.domain)))
        domains.append(Orange.feature.String(owutValideNameAttributeFrom(tmpNameForNewAttribute5,dataIn.domain)))
        domain = Orange.data.Domain(domains)
        resultats = [[x for x in lDataIn] for lDataIn in dataIn]
    else:
        features = [Orange.feature.String(tmpNameForNewAttribute0),Orange.feature.String(tmpNameForNewAttribute1),Orange.feature.String(tmpNameForNewAttribute2),Orange.feature.String(tmpNameForNewAttribute3),Orange.feature.String(tmpNameForNewAttribute4),Orange.feature.String(tmpNameForNewAttribute5)]
        domain = Orange.data.Domain(features)
        resultats = []
    init = True
    init_i=0
    for i in range(len(dataIn)):
        if init:
            strV = dataIn[i][indAttribute1].value
            try:
                maxV = int(strV)
                minV = maxV
                cardV = 1
                sumV = maxV
                init=False
            except:
                try:
                    maxV = float(strV)
                    minV = maxV
                    cardV = 1
                    sumV = maxV
                    init=False
                except:
                    pass
        else:
            strV = dataIn[i][indAttribute1].value
            try:
                valV = int(strV)
                if valV>maxV:
                    maxV=valV
                if valV<minV:
                    minV=valV
                cardV = cardV + 1
                sumV = sumV + valV
            except:
                try:
                    valV = float(strV)
                    if valV>maxV:
                        maxV=valV
                    if valV<minV:
                        minV=valV
                    cardV = cardV + 1
                    sumV = sumV + valV
                except:
                    pass
        if (i==(len(dataIn)-1)) or ((not owutEstChoixVide(pAttribute2)) and (dataIn[i][indAttribute2].value!=dataIn[i+1][indAttribute2].value)):
            if init: # cas ou la colonne n'est pas parfaitement numerique et qu'aucune initialisation n'a pu etre efectuee
                if owutEstChoixVide(pAttribute2): # pour tout le monde
                    if pAddResultsAtEndOfData: # par ajout en fin de ligne
                        for k in range(len(resultats)):
                            resultats[k].append(str("n.a."))
                            resultats[k].append(str("n.a."))
                            resultats[k].append(str("n.a."))
                            resultats[k].append(str("n.a."))
                            resultats[k].append(str("n.a."))
                    else:
                        resultats.append(["all_data",str("n.a."),str("n.a."),str("n.a."),str("n.a."),str("n.a.")]) #pourquoi "n.a." ici on connait les valeurs
                else: # par groupe
                    if pAddResultsAtEndOfData: # par ajout en fin de ligne depuis le dernier init ?
                        for k in range(init_i,i+1):
                            resultats[k].append(str("n.a."))
                            resultats[k].append(str("n.a."))
                            resultats[k].append(str("n.a."))
                            resultats[k].append(str("n.a."))
                            resultats[k].append(str("n.a."))
                    else:
                        resultats.append([dataIn[i][indAttribute2].value,str("n.a."),str("n.a."),str("n.a."),str("n.a."),str("n.a.")]) #pourquoi "n.a." ici on connait les valeurs
            else: # cas ou il y a eu des valeurs numeriques (et on peut calculer les valeurs !)
                if cardV!=0:
                    avgV = float(sumV) / cardV
                else:
                    avgV="nan"
                if owutEstChoixVide(pAttribute2):
                    if pAddResultsAtEndOfData:
                        for k in range(len(resultats)):
                            resultats[k].append(str(minV))
                            resultats[k].append(str(maxV))
                            resultats[k].append(str(cardV))
                            resultats[k].append(str(sumV))
                            resultats[k].append(str(avgV))
                    else:
                        resultats.append(["all_data",str(minV),str(maxV),str(cardV),str(sumV),str(avgV)])
                else:
                    if pAddResultsAtEndOfData:
                        for k in range(init_i,i+1):
                            resultats[k].append(str(minV))
                            resultats[k].append(str(maxV))
                            resultats[k].append(str(cardV))
                            resultats[k].append(str(sumV))
                            resultats[k].append(str(avgV))
                    else:
                        resultats.append([dataIn[i][indAttribute2].value,str(minV),str(maxV),str(cardV),str(sumV),str(avgV)])
            init = True
            init_i=i+1
    res = Orange.data.Table(domain,resultats)
    return res

