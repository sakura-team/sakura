#!/usr/bin/python
#Orange Widget developped by Denis B. Oct, 2014.

"""
<name>LevenshteinDistance</name>
<icon>OWUTLevenshteinDistance_icons/OWUTLevenshteinDistance.svg</icon>
<description>Compute Levenshtein distance for sequences of user's actions for each pair user x user</description>
<priority>51</priority>
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

class OWUTLevenshteinDistance(OWWidget):
    settingsList = ['configAttribute','configGroupBy','configExplanation','applyAutomatically','cfgNameNewAtt1','cfgNameNewAtt2','cfgNameNewAtt3'] #emergencyStop ?

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)
        self.data = None
        self.inputs = [("Table", Orange.data.Table, self.setData)]
        self.outputs = [("LevenshteinDistance Table", Orange.data.Table)]
        settings = QSettings()
        val = settings.value("ut-login/login", "unknown")
        self.login = val.toString()
        self.path = unicode(settings.value("ut-path/path","unknown").toString())
        if self.login != "unknown":
            self.applyAutomatically = False
            boxSettings = OWGUI.widgetBox(self.controlArea, "Configuration", addSpace=True)
            owutAjouteChoixAttribut(boxSettings,self,"configAttribute","Attribute for distance calculus (default: action attribute)")
            owutAjouteChoixAttribut(boxSettings,self,"configGroupBy","Group By Attribute (default: user attribute)")
            OWGUI.checkBox(boxSettings, self, 'applyAutomatically', "Apply automatically (when possible)")
            OWGUI.button(self.controlArea, self, 'Apply', callback=self.compute)
            self.configExplanation = "Your comment/explanation."
            OWGUI.lineEdit(self.controlArea, self, "configExplanation", box="Any comment or explanation about your operation?")
            owutInitPrevisualisationEntreesSorties(self)
            self.loadSettings()
        else:
            boxConnexion = OWGUI.widgetBox(self.controlArea, "Connection")
            label = OWGUI.label(boxConnexion, self, "Please connect to UnderTracks first! (File->Log on UT)" + self.login)

    def setData(self, data, id=None):
        self.data = data
        owutSetPrevisualisationEntrees(self,data)
        if self.data != None:
            firstAttrOk = owutInitChoixAttributEtVerifieConfig(self,"configAttribute",data.domain)
            secondAttrOk = owutInitChoixAttributEtVerifieConfig(self,"configGroupBy",data.domain)
            if firstAttrOk and secondAttrOk:
                if self.applyAutomatically:
                    self.compute()

    def compute(self):
        if self.data != None:
            res=mainOWUTLevenshteinDistance(self.path, owutChoixAttribut(self,"configAttribute"), owutChoixAttribut(self,"configGroupBy"),  str(self.cfgNameNewAtt1),  str(self.cfgNameNewAtt2), str(self.cfgNameNewAtt3), self.data, True, self) ##1
            if res!=None:
                owutSynchroniseChoixAttribut(self)
                self.saveSettings()
                self.send("LevenshteinDistance Table", res)
                owutSetPrevisualisationSorties(self,res)


def levenshtein(s1,s2):
    if len(s1) > len(s2):
        s1,s2 = s2,s1
    distances = range(len(s1) + 1)
    for index2,char2 in enumerate(s2):
        newDistances = [index2+1]
        for index1,char1 in enumerate(s1):
            if char1 == char2:
                newDistances.append(distances[index1])
            else:
                newDistances.append(1 + min((distances[index1],distances[index1+1],newDistances[-1])))
        distances = newDistances
    return distances[-1]

def mainOWUTLevenshteinDistance(ppath, attributeToShow, groupByAttribute, pNameForNewAttribute1, pNameForNewAttribute2, pNameForNewAttribute3, data, versionGraphique, gui): ##2
  resultat = []
  domains = []
  if versionGraphique:
      gui.warning()
  indGroupByAttribute = owutIndiceAttribut(groupByAttribute,data.domain)
  if indGroupByAttribute==-1:
    return
  indAttributeToShow = owutIndiceAttribut(attributeToShow,data.domain)
  if indAttributeToShow==-1:
    return
  if pNameForNewAttribute1:
    tmpNameForNewAttribute1 =  pNameForNewAttribute1
  else:
    tmpNameForNewAttribute1 =  owutNormaliseTailleNom(data.domain[indGroupByAttribute].name+"_1")
  domains.append(Orange.feature.String(owutValideNameAttributeFrom(tmpNameForNewAttribute1,data.domain)))
  if pNameForNewAttribute2:
    tmpNameForNewAttribute2 =  pNameForNewAttribute2
  else:
    tmpNameForNewAttribute2 =  owutNormaliseTailleNom(data.domain[indGroupByAttribute].name+"_2")
  domains.append(Orange.feature.String(owutValideNameAttributeFrom(tmpNameForNewAttribute2,data.domain)))
  if pNameForNewAttribute3:
    tmpNameForNewAttribute3 =  pNameForNewAttribute3
  else:
    tmpNameForNewAttribute3 =  owutNormaliseTailleNom("Lev(1,2)")
  domains.append(Orange.feature.String(owutValideNameAttributeFrom(tmpNameForNewAttribute3,data.domain)))
  users = [] #pour les sequences d'actions associees a un user
  usersName = []
  currentUser = []
  precUsers="UTNoUserYetForLevenshtein"
  for l in data:
    if l[indGroupByAttribute].value!=precUsers:
      if  precUsers!="UTNoUserYetForLevenshtein":
        if usersName.__contains__(precUsers):
            gui.warning("Disparate value, your data should be sorted.")
        users.append(currentUser)
        usersName.append(precUsers)
      currentUser = []
      precUsers=l[indGroupByAttribute].value
    currentUser.append(l[indAttributeToShow].value)
  users.append(currentUser)
  usersName.append(precUsers)
  if versionGraphique:
      pb1 = OWGUI.ProgressBar(gui, iterations=len(users)) ##3
  for i in range(len(users)) :
      coeurMessageData = []
      for j in range(len(users)) :
          distanceUser = levenshtein(users[i],users[j])
          ligneRes = []
          ligneRes.append(usersName[i])
          ligneRes.append(usersName[j])
          ligneRes.append(str(distanceUser))
          resultat.append(ligneRes)
      if versionGraphique:
          pb1.advance() ##4
  if versionGraphique:
      pb1.finish() ##5
  domain = Orange.data.Domain(domains)
  res = Orange.data.Table(domain, resultat)
  return res

 