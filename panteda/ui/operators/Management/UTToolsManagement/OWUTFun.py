#!/usr/bin/python
#Orange Widget developped by Denis B. Oct., 2014., continued 2015, 2016


"""
<name>Fun</name>
<icon>OWUTFun_icons/OWUTFun.svg</icon>
<description>Fun applies user-defined function to the values of an attribute</description>
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

class OWUTFun(OWWidget):
    ### Placer ici la liste de vos configurations                             ###
    ###  - Selection d'Attributs cfgAttChoiceXYZ et cfgKeepAttXYZ             ###
    ### (a re-utiliser lors de la mise en place de l'ihm cf. plus bas.        ###
    ###  - Mom d'Attributs crees cfgNameNewAttXYZ                             ###
    ###  - Valeurs textes, autres, specifiques                                ###
    settingsList = ['configForTheFunDefinition','configExplanation','configInitValue','cfgAttChoice1','cfgKeepAtt1','cfgAttChoice2','cfgKeepAtt2','cfgNameNewAtt1']

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)
        self.data = None
        self.inputs = [("Table", Orange.data.Table, self.setData)]
        self.outputs = [("Fun Table", Orange.data.Table)]
        settings = QSettings()
        val = settings.value("ut-login/login", "unknown")
        self.login = val.toString()
        if self.login != "unknown":
            boxSettings = OWGUI.widgetBox(self.controlArea, "Configuration", addSpace=True)
            ### Definir ici la maquette ihm de votre Operateur              ###
            ###    - Choix des Attributs,                                   ###
            ###    - Definition des valeurs initiales,                      ###
            ###    - Textes explicatifs                                     ###
            ### pour le choix des Attributs : owutAjouteChoixAttribut(boxSettings,self,"cfgAttChoiceXYZ","texte explicatif libre") ###
            ### Attention, utiliser les memes noms cfgAttChoiceXYZ          ###
            ### que dans la liste des configurations cf. plus haut        . ###
            owutAjouteChoixAttribut(boxSettings,self,"cfgAttChoice1","First Attribute ($0)")
            owutAjouteChoixAttribut(boxSettings,self,"cfgAttChoice2","Second Attribute ($1)")
            self.configInitValue = "0"
            self.configForTheFunDefinition = "int($0)+int($1)"
            OWGUI.lineEdit(boxSettings, self, "configInitValue", box="Init value $$ if necessary.")
            OWGUI.lineEdit(boxSettings, self, "configForTheFunDefinition", box="Your function. f($0,$1) = ")
            self.infoArg = OWGUI.widgetLabel(boxSettings, '    $0, $1 stand for the raw - (string) - data')
            self.infoVal = OWGUI.widgetLabel(boxSettings, '    int($0), $I0, float($0), $F0,  ... stand for the integer/float value of the data [when possible]')
            self.infoInitVal = OWGUI.widgetLabel(boxSettings, '    $$, $I, $F stand for the init (/integer/float) value on first calculus and for the previous result after first calculus')
            self.infoFun = OWGUI.widgetLabel(boxSettings, '    n.b.: you can use all python or user-added functions, e.g.: test(c,a,b) which returns a if c is true, or else returns b')
            OWGUI.button(self.controlArea, self, 'Apply', callback=self.compute)
            self.configExplanation = "Your comment/explanation."
            OWGUI.lineEdit(self.controlArea, self, "configExplanation", box="Any comment or explanation about your operation?")
            # Mise en place automatique des onglets input/output pour les donnees en entree/sortie ###
            # et de l'onglet misc avec des exports csv                                             ###
            # des choix experts selon les configurations (reconnues par le format) :               ###
            #     - cfgKeepAttXYZ=> keep AttXYZ or not ?                                          ###
            #     - cfgNameNewAttXYZ => rename new AttXYZ or not ?                                 ###
            owutInitPrevisualisationEntreesSorties(self)
            self.loadSettings()
        else:
            boxConnexion = OWGUI.widgetBox(self.controlArea, "Connection")
            OWGUI.label(boxConnexion, self, "Please connect to UnderTracks first! (File->Log on UT)" + self.login)

    def setData(self, data, id=None):
        self.data = data
        owutSetPrevisualisationEntrees(self,data)
        if self.data != None:
            ### Prevoir ici de (faire) remplir la liste des attributs disponibles dans les listes deroulantes ###
            ### Attention, utiliser les memes noms cfgAttChoiceXYZ que dans la liste des configurations       ###
            ### cf. plus haut.                                                                                ###
            ### n.b.: la liste des attributs (data.domain) peut etre remplacee par une liste adhoc,           ###
            ### ex. ["String","Discrete","Continuous"]                                                        ###
            Attribute1Ok = owutInitChoixAttributEtVerifieConfig(self,"cfgAttChoice1",data.domain)
            Attribute2Ok = owutInitChoixAttributEtVerifieConfig(self,"cfgAttChoice2",data.domain)
            ### Si la configuration enregistree est compatible avec les configurations enregistrees ###
            ### lancer l'execution                                                                  ###
            if Attribute1Ok and Attribute2Ok:
                self.compute()

    def compute(self):
        if self.data != None:
            ### Lors du lancement effectif de l'execution, transmettre les valeurs des choix d'attribut ###
            ### (les noms des attributs selectionnes dans les listes de choix)                          ###
            self.res = mainOWUTFun(owutChoixAttribut(self,"cfgAttChoice1"), self.cfgKeepAtt1, owutChoixAttribut(self,"cfgAttChoice2"), self.cfgKeepAtt2, str(self.configInitValue), str(self.configForTheFunDefinition), str(self.cfgNameNewAtt1), self.data)
            if self.res!=None:
                # Apres execution, enregistrer la configuration, transmettre les resultats et les pre-visualiser
                owutSynchroniseChoixAttribut(self)
                self.saveSettings()
                owutSetPrevisualisationSorties(self,self.res)
                self.send("Fun Table", self.res)

def test(c,a,b):
    if c:
        return a
    else:
        return b

def mainOWUTFun(pAttribute1, pKeepAttribute1, pAttribute2, pKeepAttribute2, pConfigInitValue, pConfigForTheFunction, pNameForNewAttribute, dataIn):
    ### Pour travailler avec les donnees il est plus simple de connaitre les indices de lignes/colonnes, ###
    ### En fonction des noms d'attribut on peut retrouver leur indice avec owutIndiceAttribut            ###
    indAttribute1 = owutIndiceAttribut(pAttribute1,dataIn.domain)
    indAttribute2 = owutIndiceAttribut(pAttribute2,dataIn.domain)
    ### s'il manque un attribut dans les donnees, abandonner le calcul ###
    if (indAttribute1==-1) or (indAttribute2==-1):
        return
    ###     -- Definition des attributs --                                  ###
    ### En cas d'ajout d'attribut (par exemple comme resultat des calculs) :###
    ### choisir un nom par defaut pour ce nouvel attribut, ex : "fun"       ###
    ### ou prendre le nom propose par l'utilisateur (si non vide)           ###
    domains = [d for d in dataIn.domain]
    if pNameForNewAttribute:
        tmpNameForNewAttribute =  pNameForNewAttribute
    else:
        tmpNameForNewAttribute =  owutNormaliseTailleNom("fun")             ###Nom du resultat par defaut, par exemple une constante ici "fun".
        ### Le nom peut aussi etre produit a la volee en fonction des parametres [ex.: "fun("+pAttribute1+","+pAttribute2+")"],
        ### pour ne pas avoir un nom trop long utiliser "owutNormaliseTailleNom"
    domains.append(Orange.feature.String(owutValideNameAttributeFrom(tmpNameForNewAttribute,dataIn.domain)))
    fullDomains = Orange.data.Domain(domains)
    ### -- Keep the input attribute or not in the result? -- ###
    if pKeepAttribute1 and pKeepAttribute2:
        reducedDomain = fullDomains
    elif pKeepAttribute1:
        reducedDomain = Orange.data.Domain(fullDomains[:indAttribute2]+fullDomains[indAttribute2+1:])
    elif pKeepAttribute2:
        reducedDomain = Orange.data.Domain(fullDomains[:indAttribute1]+fullDomains[indAttribute1+1:])
    else:
        reducedDomain = Orange.data.Domain(fullDomains[:min(indAttribute1,indAttribute2)]+fullDomains[min(indAttribute1,indAttribute2)+1:max(indAttribute1,indAttribute2)]+fullDomains[max(indAttribute1,indAttribute2)+1:])
    ### Keep input or not? for only one attribute :                                                                ###
       ###if pKeepAtt1:                                                                                            ###
       ###  reducedDomain = fullDomains                                                                            ###
       ###else:                                                                                                    ###
       ###  reducedDomain = Orange.data.Domain(fullDomains[:indAttChoice1]+fullDomains[indAttChoice1+1:])    ###
    ### -- Debut des calculs --   ###
    resultat = [[x for x in lDataIn] for lDataIn in dataIn]
    previousResult = pConfigInitValue
    for i in range(len(dataIn)):                                  
        ####################################################################################################
        ###   Debut de votre code "Important" ici ! (pour une code ajoutant une valeur sur chaque ligne) ###
        ###        Ajouter ici le calcul de la valeur a ajouter pour la ligne i                          ###
        ###        A disposition, les valeurs en entrees : dataIn[indiceLigne][indiceColonne].value      ###
        ###        Exemple : dataIn[i][indAttribute1].value                                          ###
        ###        Exemple : dataIn[i-1][indAttribute2].value                                       ###
        ####################################################################################################
        toEvaluate = pConfigForTheFunction.replace('$0',"'"+dataIn[i][indAttribute1].value+"'").replace('$I0',"int('"+dataIn[i][indAttribute1].value+"')").replace('$F0',"float('"+dataIn[i][indAttribute1].value+"')").replace('$I1',"int('"+dataIn[i][indAttribute2].value+"')").replace('$F1',"float('"+dataIn[i][indAttribute2].value+"')").replace('$1',"'"+dataIn[i][indAttribute2].value+"'").replace('$$',"'"+previousResult+"'").replace('$I',"int('"+previousResult+"')").replace('$F',"float('"+previousResult+"')")    ### a remplacer par votre code
        createdValueForLineI = str(eval(toEvaluate))               ### a remplacer par votre code
        previousResult = createdValueForLineI                      ### ligne a conserver
        resultat[i].append(createdValueForLineI)                   ### ligne a conserver/transformer (eventuellement) pour faire l'ajout effectif
        ####################################################################################################
        ###       Fin de votre code "Important"                                                          ###
        ####################################################################################################
    tmpOut =  Orange.data.Table(fullDomains, resultat)
    dataOut = Orange.data.Table(reducedDomain, tmpOut)
    return dataOut


################### Variations pour le code de la fonction ###############################
####### version Append/Append
    # resultat = []
    # for i in range(len(dataIn)):                                ## the two lines below are to be replaced by your code
    #     ligneRes = []
    #     for j in range(len(dataIn[i])):
    #         ligneRes.append(dataIn[i][j].value)
    #     toEvaluate = pFirstConfigForTheFunction.replace('$0',"'"+dataIn[i][indFirstAttribute].value+"'").replace('$1',"'"+dataIn[i][indSecondAttribute].value+"'") ## to be replaced by your code
    #     newValue = str(eval(toEvaluate))                                                  ## to be replaced by your code
    #     ligneRes.append(newValue)
    #     resultat.append(ligneRes)
####### version [[[] for x in ...]/resultat[i][j] avec hypothese de matrice rectangulaire
    # resultat = [[[] for i in range(len(dataIn[0])+1)] for l in range(dataIn)]
    # for i in range(len(dataIn)):                                ## the two lines below are to be replaced by your code
    #     for j in range(len(dataIn[0])):
    #         resultat[i][j]=dataIn[i][j]
    #     toEvaluate = pFirstConfigForTheFunction.replace('$0',"'"+dataIn[i][indFirstAttribute].value+"'").replace('$1',"'"+dataIn[i][indSecondAttribute].value+"'")  ## to be replaced by your code
    #     newValue = str(eval(toEvaluate))                                                  ## to be replaced by your code
    #     resultat[i][len(dataIn[0])]=newValue
####### version [x for x in ...]/Append
    # resultat = [[x for x in lDataIn] for lDataIn in dataIn]
    # for i in range(len(dataIn)):                                ## the two lines below are to be replaced by your code
    #     toEvaluate = pFirstConfigForTheFunction.replace('$0',"'"+dataIn[i][indFirstAttribute].value+"'").replace('$1',"'"+dataIn[i][indSecondAttribute].value+"'")   ## to be replaced by your code
    #     newValue = str(eval(toEvaluate))                                                  ## to be replaced by your code
    #     resultat[i].append(newValue)
