#!/usr/bin/python
#Orange Widget developped by Denis B. Oct., 2014., continued 2015


"""
<name>Match</name>
<icon>OWUTMatch_icons/OWUTMatch.svg</icon>
<description>Scan an attribute for match with a regular expression</description>
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
import re

class OWUTMatch(OWWidget):
    settingsList = ['firstAttribute','firstConfig','commentExplanation',"skipValueWithoutMatch", 'cfgKeepAtt1', 'cfgNameNewAtt1']

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)
        self.data = None
        self.inputs = [("Table", Orange.data.Table, self.setData)]
        self.outputs = [("Match Table", Orange.data.Table)]
        settings = QSettings()
        val = settings.value("ut-login/login", "unknown")
        self.login = val.toString()
        if self.login != "unknown":
            self.skipValueWithoutMatch = False
            boxSettings = OWGUI.widgetBox(self.controlArea, "Configuration", addSpace=True)
            owutAjouteChoixAttribut(boxSettings,self,"firstAttribute","Attribute for the matching")
            self.firstConfig = "ab*"
            boxFirstConfig = OWGUI.lineEdit(boxSettings, self, "firstConfig", box="Your regular expression")
            self.infoRe10 = OWGUI.widgetLabel(boxSettings, '    a+ matches 1 or more occurrences of a')
            self.infoRe11 = OWGUI.widgetLabel(boxSettings, '    a* matches 0 or more occurrences of a')
            self.infoRe12 = OWGUI.widgetLabel(boxSettings, '    a? matches 0 or 1 occurrences of a')
            self.infoRe2 = OWGUI.widgetLabel(boxSettings, '    a|b matches either a or b')
            self.infoRe31 = OWGUI.widgetLabel(boxSettings, '    . matches any single char')
            self.infoRe32 = OWGUI.widgetLabel(boxSettings, '    [b-e] matches any single char in range from b to e')
            self.infoRe33 = OWGUI.widgetLabel(boxSettings, '    [^b-e] matches any single char except those in range from b to e')
            self.infoRe341 = OWGUI.widgetLabel(boxSettings, '    (...) braces could be used to group elements, but ')
            self.infoRe342 = OWGUI.widgetLabel(boxSettings, '    (?=re) succeed if the text matches re but do not consume the text')
            self.infoRe343 = OWGUI.widgetLabel(boxSettings, '    (?!re) succeed if the text does not match re (just lookahead)')
            self.infoRe4 = OWGUI.widgetLabel(boxSettings, '    e.g.: a.*(b|c) matches when a is followed by b or c, maybe far away.')
            self.infoRe5 = OWGUI.widgetLabel(boxSettings, '    more information on docs.python.org/2/howto/regex.html')
            OWGUI.checkBox(boxSettings, self, 'skipValueWithoutMatch', "Skip value without match")
            OWGUI.button(self.controlArea, self, 'Apply', callback=self.compute)
            self.commentExplanation = "Your comment/explanation."
            boxCommentExplanation = OWGUI.lineEdit(self.controlArea, self, "commentExplanation", box="Any comment or explanation about your regular expression?")
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
            if firstAttrOk:
                self.compute()

    def compute(self):
        if self.data != None:
            res = mainOWUTMatch(owutChoixAttribut(self,"firstAttribute"), str(self.firstConfig), self.skipValueWithoutMatch, self.cfgKeepAtt1,  str(self.cfgNameNewAtt1), self.data)
            if res!=None: # Apres execution, enregistrer la configuration, transmettre les resultats et les pre-visualiser
                owutSynchroniseChoixAttribut(self)
                self.saveSettings()
                self.send("Match Table", res)
                owutSetPrevisualisationSorties(self,res)


def mainOWUTMatch(pFirstAttribute, pFirstConfig, pSkipValueWithoutMatch, pKeepAttribute1, pNameForNewAttribute, dataIn):
    indFirstAttribute = owutIndiceAttribut(pFirstAttribute,dataIn.domain)
    if (indFirstAttribute==-1):
        return
    domains = [d for d in dataIn.domain]
    if pNameForNewAttribute:
        tmpNameForNewAttribute =  pNameForNewAttribute
    else:
        tmpNameForNewAttribute =  owutNormaliseTailleNom("Match("+pFirstAttribute+")")
    domains.append(Orange.feature.String(owutValideNameAttributeFrom(tmpNameForNewAttribute,dataIn.domain)))
    fullDomains = Orange.data.Domain(domains)
    ### -- Keep the input attribute or not in the result? -- ###
    if pKeepAttribute1:
        reducedDomain = fullDomains
    else:
        reducedDomain = Orange.data.Domain(fullDomains[:indFirstAttribute]+fullDomains[indFirstAttribute+1:])
    resultat = []
    #resultat = [[x for x in lDataIn] for lDataIn in dataIn]
    for i in range(len(dataIn)):
        res = re.match(pFirstConfig,dataIn[i][indFirstAttribute].value)
        if res:
            tmp_resultat = [x for x in dataIn[i]]
            tmp_resultat.append(res.group())
            resultat.append(tmp_resultat)
        else:
            if not pSkipValueWithoutMatch:
                tmp_resultat = [x for x in dataIn[i]]
                tmp_resultat.append("")
                resultat.append(tmp_resultat)
    tmpOut =  Orange.data.Table(fullDomains, resultat)
    dataOut = Orange.data.Table(reducedDomain, tmpOut)
    return dataOut

