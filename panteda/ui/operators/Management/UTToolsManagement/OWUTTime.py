#!/usr/bin/python
#Orange Widget developped by Denis B. May, 2014.

#TODO : verifier que toutes les dates sont analysees selon le meme format, renvoyer une alerte quand ce n'est pas le cas,

# pour information, quelques dates rencontrees :
# annotation        : 00:08:05                   => hh:mm:ss
# copexchimie2010   : 00:08:05                   => hh:mm:ss
# paces             : 26/09/11 00:00             => jj/mm/aa 00:00
# formid            : 21/20/11 15:25             => jj/mm/aa hh:mm
# hysteresis        : 10/10/08 00:03:15          => indetermine entre jj/mm/aa et l'inverse
# sci_10_1          : 23/06/14 15:36:49          => jj/mm/aa hh:mm:ss
# edit22013France   : 06/23/14 15:36:49          risque de conflit avec le prec. ! faut-il ajouter un menu expres ?
# copexchimie2013   : 06/23/14 15:36:49          risque de conflit avec le prec. ! faut-il ajouter un menu expres ?
# labbook           : 2013/02/24 16:02:36        => aaaa/mm/jj hh:mm:ss
# tamago            : 2014-03-28 12:05:39        => aaaa-mm-jj hh:mm:ss
# moodlePLC         : 2010 decembre 1 16:43
# aplusix           : 29-09-2003 10:29:28        => jj-mm-aaaa hh:mm:ss
# smartlearning     : 20-10-2014 13:58:38:165
# formid            : 20140311_140904.024
##################################################
# pour reference et rappel :                     #
# format iso 8601   : 2014-10-20T13:58:38Z       #
##################################################
"""
<name>Time</name>
<icon>OWUTTime_icons/OWUTTime.svg</icon>
<description>Time operator works on time format</description>
<priority>30</priority>
"""

import Orange
from OWWidget import *
import OWGUI
import time
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
from OWUTData import owutStrUtf
from OWUTData import owutCastTime
from OWUTData import owutNormaliseTailleNom
from OWUTData import owutValideNameAttributeFrom



class OWUTTime(OWWidget):
    settingsList = ['configTimeAttribute','configTimeFormat','configExplanation','cfgKeepAtt1','cfgNameNewAtt1','cfgNameNewAtt2','cfgNameNewAtt3']

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)
        self.data = None
        self.inputs = [("Table", Orange.data.Table, self.setData)]
        self.outputs = [("Time Table", Orange.data.Table)]
        settings = QSettings()
        val = settings.value("ut-login/login", "unknown")
        self.login = val.toString()
        if self.login != "unknown":
            boxSettings = OWGUI.widgetBox(self.controlArea, "Configuration", addSpace=True)
            owutAjouteChoixAttribut(boxSettings,self,"configTimeAttribute","Attribute giving date/time/order")
            owutAjouteChoixAttribut(boxSettings,self,"configTimeFormat","Time Format")
            OWGUI.button(self.controlArea, self, 'Apply', callback=self.compute)
            self.configExplanation = "Your comment/explanation."
            OWGUI.lineEdit(self.controlArea, self, "configExplanation", box="Any comment or explanation about your function?")
            owutInitPrevisualisationEntreesSorties(self)
            self.loadSettings()
        else:
            boxConnexion = OWGUI.widgetBox(self.controlArea, "Connection")
            label = OWGUI.label(boxConnexion, self, "Please connect to UnderTracks first! (File->Log on UT)" + self.login)

    def setData(self, data, id=None):
        self.data = data
        owutSetPrevisualisationEntrees(self,data)
        if self.data != None:
            firstAttrOk = owutInitChoixAttributEtVerifieConfig(self,"configTimeAttribute",data.domain)
            secondAttrOk = owutInitChoixAttributEtVerifieConfig(self,"configTimeFormat",["Normal Time or Order Format YYYY/mm/dd HH:MM:SS or similar","Special mm/dd/YY hh:mm:ss"])
            if firstAttrOk and secondAttrOk:
                self.compute()

    def compute(self):
        if self.data != None:
            res = mainOWUTTime(owutChoixAttribut(self,"configTimeAttribute"), owutChoixAttribut(self,"configTimeFormat"), self.cfgKeepAtt1, str(self.cfgNameNewAtt1), str(self.cfgNameNewAtt2), str(self.cfgNameNewAtt3), self.data)
            if res!=None:
                owutSynchroniseChoixAttribut(self)
                self.saveSettings()
                self.send("Time Table", res)
                owutSetPrevisualisationSorties(self,res)


def mainOWUTTime(timeAttribute, timeFormat, pKeepAttribute1, pNameForNewAttribute1, pNameForNewAttribute2, pNameForNewAttribute3, dataIn):
    indTimeAttribute = owutIndiceAttribut(timeAttribute,dataIn.domain)
    if (indTimeAttribute==-1):
        return
    domains = [d for d in dataIn.domain]
    if pNameForNewAttribute1:
        tmpNameForNewAttribute1 =  pNameForNewAttribute1
    else:
        tmpNameForNewAttribute1 =  owutNormaliseTailleNom("Time(sec)")
    domains.append(Orange.feature.String(owutValideNameAttributeFrom(tmpNameForNewAttribute1,dataIn.domain)))
    if pNameForNewAttribute2:
        tmpNameForNewAttribute2 =  pNameForNewAttribute2
    else:
        tmpNameForNewAttribute2 =  owutNormaliseTailleNom("Time(std)")
    domains.append(Orange.feature.String(owutValideNameAttributeFrom(tmpNameForNewAttribute2,dataIn.domain)))
    if pNameForNewAttribute3:
        tmpNameForNewAttribute3 =  pNameForNewAttribute3
    else:
        tmpNameForNewAttribute3 =  owutNormaliseTailleNom("Time(iso)")
    domains.append(Orange.feature.String(owutValideNameAttributeFrom(tmpNameForNewAttribute3,dataIn.domain)))
    fullDomains = Orange.data.Domain(domains)
    ### -- Keep the input attribute or not in the result? -- ###
    if pKeepAttribute1:
        reducedDomain = fullDomains
    else:
        reducedDomain = Orange.data.Domain(fullDomains[:indTimeAttribute]+fullDomains[indTimeAttribute+1:])
    resultat = [[x for x in lDataIn] for lDataIn in dataIn]
    if timeFormat=="Special mm/dd/YY hh:mm:ss":
        codeTimeFormat = -1
    else:
        codeTimeFormat = 1
    for i in range(len(dataIn)):                                  ## the two lines below are to be replaced by your code
        nbsEtDateStd = owutCastTime(owutStrUtf(dataIn[i][indTimeAttribute].value), codeTimeFormat)
        resultat[i].append(nbsEtDateStd[0])
        resultat[i].append(nbsEtDateStd[1])
        resultat[i].append(nbsEtDateStd[2])
    tmpOut =  Orange.data.Table(fullDomains, resultat)
    dataOut = Orange.data.Table(reducedDomain, tmpOut)
    return dataOut