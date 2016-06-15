#!/usr/bin/python
#Orange Widget developped by Denis B. Oct., 2014., continued April 2015


"""
<name>DCount</name>
<icon>OWUTDCount_icons/OWUTDCount.svg</icon>
<description>DCount numbers the occurences of values of an attribute</description>
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


class OWUTDCount(OWWidget):
    ### Placer ici la liste des noms de vos configurations (Selection d'Attributs, Valeurs textes) ###
    settingsList = ['firstConfig','cfgAttChoice1','cfgKeepAtt1','cfgNameNewAtt1','configExplanation',]

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)
        self.data = None
        self.inputs = [("In", Orange.data.Table, self.setData)]
        self.outputs = [("DCount", Orange.data.Table)]
        settings = QSettings()
        val = settings.value("ut-login/login", "unknown")
        self.login = val.toString()
        if self.login != "unknown":
            boxSettings = OWGUI.widgetBox(self.controlArea, "Configuration", addSpace=True)
            ### Definir ici la maquette de votre Operateur (Choix des Attributs, Definition des valeurs, Textes) ###
            ### pour le choix des Attributs : owutAjouteChoixAttribut(boxSettings,self,"nomChoixAttribut","texte explicatif libre") ###
            ### Attention, utiliser les memes noms "nomChoixAttribut" que dans la liste des configurations ###
            owutAjouteChoixAttribut(boxSettings,self,"cfgAttChoice1","Which attribute to be numbered?")
            self.firstConfig = "1"
            boxFirstConfig = OWGUI.lineEdit(boxSettings, self, "firstConfig", box="Initial value (int)")
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
            ### Prevoir ici de (faire) remplir la liste des attributs disponibles dans les listes deroulantes ###
            ### Attention, utiliser les memes noms "nomChoixAttribut" que dans la liste des configurations ###
            ### Si la configuration enregistree est compatible, lancer l'execution ###
            firstAttrOk = owutInitChoixAttributEtVerifieConfig(self,"cfgAttChoice1",data.domain)
            if firstAttrOk:
                self.compute()

    def compute(self):
        if self.data != None:
            ### Pour lancer l'execution, transmettre les choix d'attribut (leur nom) ###
            res = mainOWUTDCount(owutChoixAttribut(self,"cfgAttChoice1"), str(self.firstConfig), self.cfgKeepAtt1, str(self.cfgNameNewAtt1), self.data)
            if res!=None: # Apres execution, enregistrer la configuration, transmettre les resultats et les pre-visualiser
                owutSynchroniseChoixAttribut(self)
                self.saveSettings()
                self.send("DCount", res)
                owutSetPrevisualisationSorties(self,res)


def mainOWUTDCount(pAttChoice1, pFirstConfig, pKeepAtt1, pNameNewAtt1, dataIn):
    ### En fonction des noms d'attribut, retrouver leur indice (plus simple pour les retrouver dans les lignes) ###
    indAttChoice1 = owutIndiceAttribut(pAttChoice1,dataIn.domain)
    if (indAttChoice1==-1): #s'il manque un attribut, abandonner
        return
    domains = [d for d in dataIn.domain]
    if pNameNewAtt1:
        tmpNameForNewAttribute =  pNameNewAtt1
    else:
        tmpNameForNewAttribute =  "DCount"
    domains.append(Orange.feature.String(owutValideNameAttributeFrom(tmpNameForNewAttribute,dataIn.domain)))
    fullDomains = Orange.data.Domain(domains)
    if pKeepAtt1:
        reducedDomain = fullDomains
    else:
        reducedDomain = Orange.data.Domain(fullDomains[:indAttChoice1]+fullDomains[indAttChoice1+1:])
    resultat = [[x for x in lDataIn] for lDataIn in dataIn]
    dico = {}
    for i in range(len(dataIn)):                                  ### En cas d'ajout d'attribut, a chaque ligne, prevoir d'ajouter une valeur ###
        if dico.has_key(dataIn[i][indAttChoice1].value):
            dico[dataIn[i][indAttChoice1].value] = str(int(dico[dataIn[i][indAttChoice1].value]) + 1)
        else:
            dico[dataIn[i][indAttChoice1].value] = pFirstConfig
        resultat[i].append(dico[dataIn[i][indAttChoice1].value])
    tmpOut =  Orange.data.Table(fullDomains, resultat)
    dataOut = Orange.data.Table(reducedDomain, tmpOut)
    return dataOut
