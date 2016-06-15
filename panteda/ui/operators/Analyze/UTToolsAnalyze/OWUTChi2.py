#!/usr/bin/python
#from Orange Widget CrossTable developped by Michael ORTEGA - 18/March/2014, puis maintenu par Denis B. Oct. 14, fev. 16

"""
<name>Chi2</name>
<icon>OWUTChi2_icons/OWUTChi2.svg</icon>
<description>Chi2</description>
<priority>41</priority>
"""


import Orange
from OWWidget import *
import OWGUI
import math
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

class OWUTChi2(OWWidget):
    settingsList = ['col1','col2','configExplanation','cfgNameNewAtt1']
    
    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)
        self.data = None
        self.inputs = [("Table", Orange.data.Table, self.dataset)]
        self.outputs = [("Table", Orange.data.Table)]
        settings = QSettings()
        val = settings.value("ut-login/login","unknown")
        self.login = val.toString()
        if self.login != "unknown":
            boxSettings = OWGUI.widgetBox(self.controlArea, "Configuration", addSpace=True)
            owutAjouteChoixAttribut(boxSettings,self,"col1","First Domain")
            owutAjouteChoixAttribut(boxSettings,self,"col2","Second Domain")
            OWGUI.button(self.controlArea, self, 'Apply', callback=self.compute)
            self.configExplanation = "Your comment/explanation."
            OWGUI.lineEdit(self.controlArea, self, "configExplanation", box="Any comment or explanation about your computation?")
            owutInitPrevisualisationEntreesSorties(self)
            self.loadSettings()
        else:
            boxConnexion = OWGUI.widgetBox(self.controlArea, "Connection")
            label = OWGUI.label(boxConnexion,self,"Please connect to UnderTracks first! (File->Log on UT)"+self.login)
            
    def dataset(self, data, id=None):
        self.data = data
        owutSetPrevisualisationEntrees(self,data)
        if self.data != None:
            _col1 = owutInitChoixAttributEtVerifieConfig(self,"col1",self.data.domain)
            _col2 = owutInitChoixAttributEtVerifieConfig(self,"col2",self.data.domain)
            if _col1 and _col2:
                self.compute()
            
    def compute(self):
        if self.data != None:
            _col1 = owutChoixAttribut(self,"col1")
            _col2 = owutChoixAttribut(self,"col2")
            if (_col1 != _col2):
                res = mainOWUTChi2(_col1,_col2, str(self.cfgNameNewAtt1),self.data)
                if res!=None:
                    owutSynchroniseChoixAttribut(self)
                    self.saveSettings()
                    self.send("Table",res)
                    owutSetPrevisualisationSorties(self,res)


def mainOWUTChi2(n1,n2,pNameForNewAttribute,data):

    variable1 = []
    variable2 = []
    nb_variable1 = []
    nb_variable2 = []

    c1 = owutIndiceAttribut(n1,data.domain)
    c2 = owutIndiceAttribut(n2,data.domain)

    if (c1==-1) or (c2==-1):
        return

    if pNameForNewAttribute:
        tmpNameForNewAttribute =  pNameForNewAttribute
    else:
        tmpNameForNewAttribute =  owutNormaliseTailleNom(n1)


    #Searching Values
    for d in data:
        v1 = d[c1]
        v2 = d[c2]
        
        try:
            contain1 = variable1.index(v1)
            nb_variable1[contain1] = nb_variable1[contain1] +1 
        except:
            variable1.append(v1)
            nb_variable1.append(1)
            
        try:
            contain2 = variable2.index(v2)
            nb_variable2[contain2] = nb_variable2[contain2] +1 
        except:
            variable2.append(v2)
            nb_variable2.append(1)

    # General Variables
    nb_total = 0;
    for v in nb_variable1:
        nb_total = nb_total + v

    #Creating Resulting Table
    features = [Orange.feature.String(tmpNameForNewAttribute)]
    for v in variable2:
        features.append(Orange.feature.String(v.value))
    domain = Orange.data.Domain(features)
    
    rows = []
    for v in variable1:
        r_tmp = [v.value]
        for i in variable2:
            r_tmp .append("0")
        rows.append(r_tmp)
    
    res = Orange.data.Table(domain,rows)

    for i in range(len(data)):
        v1 = data[i][c1]
        v2 = data[i][c2]
        
        contain1 = variable1.index(v1)
        contain2 = variable2.index(v2)
        
        res[contain1][contain2+1] = str(int(str(res[contain1][contain2+1]))+int(1))
        
    
    numerateur_chi2 = 0
    freqTh = [] #new String [variable1.size()][variable2.size()-1]
    degLib = int((len(variable1)-1))*int((len(variable2)-1)) #dof
                
    #Frequences observees
    #tableObs2 est un tableau intermediaire utilise pr le calcul du chi2,
    #Il est au meme format que freTh et comporte les donnees de uOut.table
    tableObs2 = [] # new String [variable1.size()][variable2.size()-1]
    for i in range(len(variable1)):
        tableObs2.append([])
        for j in range(len(variable2)):
            tableObs2[i].append("")
        
    for i in range(len(variable1)):
            for j in range(len(variable2)):
                tableObs2[i][j] = float(str(res[i][j+1]))

    #Frequences theoriques
    for i in range(len(variable1)):
        freqTh.append([])
        for j in range(len(variable2)-1):
            freqTh[i].append(float(nb_variable1[i])*float(nb_variable2[j])/float(nb_total))
    
    #Calcul numerateur du Chi2 : somme[(FreqObs-FreqTh)*(FreqObs-FreqTh)/FreqTh]
    for i in range(len(variable1)):
        for j in range(len(variable2)-1):
            a = (tableObs2[i][j]-freqTh[i][j])*(tableObs2[i][j]-freqTh[i][j])/freqTh[i][j]
            numerateur_chi2 = numerateur_chi2 + a

    chi2 = math.floor((numerateur_chi2/degLib) * 100.) / 100.

    # New result Table, that only contains the Chi2 result
    features = [Orange.feature.String("Chi2"),Orange.feature.String("Degree of Freedom")]
    domain = Orange.data.Domain(features)

    rows = [[str(chi2),str(degLib)]]
        
    res = Orange.data.Table(domain,rows)
        
    return res