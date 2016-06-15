#!/usr/bin/python
#Orange Widget initiated by Michael ORTEGA - 18/March/2014
#Orange Widget continued by Denis B. - April-June/2014, continued in 2015

"""
<name>File</name>
<icon>OWUTFile_icons/OWUTFile.svg</icon>
<description>Recover a file from an UnderTracks study</description>
<priority>12</priority>
"""

import Orange
from OWWidget import *
import OWGUI
import urllib  as  _u
import urllib2  as  _u2
from Orange.feature import String
if not sys.path[len(sys.path)-1].endswith("/Management/UTToolsManagement"):
    tmpSettings = QSettings()
    path = str(tmpSettings.value("ut-path/path","unknown").toString()+"/Management/UTToolsManagement")
    sys.path.append(path)
from OWUTData import owutStrUtf

###Important : OWUTFile file from serveur ! not local ! ###
# OWUTFile prends un fichier sur le serveur, (pas en local), cela garantit que l'on puisse rejouer l'operateur
# il ne faut pas changer cela, par exemple pour prendre un fichier local, car alors le script ne serait pas reproductible !
# (sauf a sauvegarder le fichier dans l'operateur mais est-ce une bonne idee ?)


class OWUTFile(OWWidget):
    settingsList = ['nomExpe','nomFile','cfgNameNewAtt1','cfgOpenFileAsCsv','configExplanation']

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)
        self.outputs = [("File", Orange.data.Table)]
        settings = QSettings()
        val = settings.value("ut-login/login", "unknown")
        self.login = val.toString()
        if self.login != "unknown":  # GUI
            self.nomExpe = ''
            self.nomFile = ''
            self.cfgNameNewAtt1=''
            self.cfgOpenFileAsCsv = False
            self.loadSettings()
            url = "https://undertracks.imag.fr/scripts/OrangeScripts/ExistingExperiences.php"
            data = _u.urlencode({"login": self.login})
            req = _u2.Request(url, data)
            f = _u2.urlopen(req)
            tab = f.read().rstrip().split("_!!_")
            boxConnexion = OWGUI.widgetBox(self.controlArea, "Connection")
            self.cB = OWGUI.comboBox(boxConnexion, self, 'expe', callback=self.majFile)
            self.cF = OWGUI.comboBox(boxConnexion, self, 'nomFile')
            OWGUI.checkBox(boxConnexion, self, 'cfgOpenFileAsCsv', "Try to open file as csv file with attributes' names on first line")
            self.infoWarning = OWGUI.widgetLabel(boxConnexion, 'For csv read, try to have a clean file ...')
            OWGUI.button(boxConnexion, self, 'Load', callback=self.compute)
            self.configExplanation = "Your comment/explanation."
            OWGUI.lineEdit(self.controlArea, self, "configExplanation", box="Any comment or explanation about your function?")
            OWGUI.lineEdit(self.controlArea, self, "cfgNameNewAtt1", box="Name for the result (Keep empty if you want automatic naming)")
            for i in range(int(tab[0])):
                self.cB.addItem(tab[i + 1])
            if self.nomExpe!=None:
                for i in range(int(tab[0])):
                    if self.cB.itemText(i) == self.nomExpe:
                        self.cB.setCurrentIndex(i)
                if self.nomExpe == self.cB.itemText(self.cB.currentIndex()):
                    self.majFile()
        else:
            boxConnexion = OWGUI.widgetBox(self.controlArea, "Connection")
            label = OWGUI.label(boxConnexion, self, "Please connect to UnderTracks first! (File->Log on UT)")

    def majFile(self):
        self.cF.clear()
        url = "https://undertracks.imag.fr/php/request/DBQueries/getDescriptionFiles.php"
        expeName = self.cB.itemText(self.cB.currentIndex())
        data = _u.urlencode({"study": expeName})
        req = _u2.Request(url, data)
        f = _u2.urlopen(req)
        all = f.read()[:-2].split("],[")
        for i in range(len(all)):
            if all[i] != '':
                self.cF.addItem(all[i].split("\",\"")[3][:-1])
        for i in range(len(self.cF)):
            if owutStrUtf(self.cF.itemText(i))==self.nomFile:
                self.cF.setCurrentIndex(i)


    def compute(self):
        expeName = self.cB.itemText(self.cB.currentIndex())
        fileName = self.cF.itemText(self.cF.currentIndex())
        [warningLines,dataOut] = mainOWUTFile(expeName, fileName, str(self.cfgNameNewAtt1), self.cfgOpenFileAsCsv)
        if not(warningLines==""):
            self.infoWarning.setText(("Warning, your csv file have lines which are too short (complete with '') and/or too long (ignored):"+warningLines)[0:200]+"...")
        self.nomExpe = expeName
        self.nomFile = fileName
        self.saveSettings()
        self.send("File",dataOut)


################# code metier de l'operateur OWUTFile ######################

def mainOWUTFile(expeName, fileName, pNameForNewAttribute, pOpenFileAsCsv):
    if expeName==None:
        return ["",""]
    url = str("https://undertracks.imag.fr/php/files_description/"+expeName+"/"+fileName)
    data = _u.urlencode({})
    req = _u2.Request(url, data)
    f = _u2.urlopen(req)
    texteFile = f.read()
    lineErrors = ""
    features = []
    if pNameForNewAttribute:
        tmpNameForNewAttribute =  pNameForNewAttribute
    else:
        tmpNameForNewAttribute =  "content"
    if texteFile and pOpenFileAsCsv:
        lines=texteFile.replace('\n\r','\n').replace('\r\n','\n').replace('\r','\n').split('\n')
        attributesNbS=lines[0].count(";")
        attributesNbT=lines[0].count("\t")
        attributesNbC=lines[0].count(",")
        if len(lines)==1:
            if (attributesNbS>0) and (attributesNbS>=attributesNbC) and (attributesNbS>=attributesNbT):
                attributeSep=";"
            elif (attributesNbC>0) and (attributesNbC>attributesNbS) and (attributesNbC>=attributesNbT):
                attributeSep=","
            elif (attributesNbT>0) and (attributesNbT>attributesNbS) and (attributesNbT>=attributesNbC):
                attributeSep="\t"
            else:
                features.append(Orange.feature.String(tmpNameForNewAttribute))
                domain = Orange.data.Domain(features)
                res = Orange.data.Table(domain, [[texteFile]])
                return [lineErrors,res]
            attributes = lines[0].split(attributeSep)
            dataes = []
            for a in attributes:
                features.append(Orange.feature.String(a))
                dataes.append(a)
            domain = Orange.data.Domain(features)
            res = Orange.data.Table(domain, [dataes])
            return [lineErrors,res]
        elif len(lines)==2:
            attributesNbS1=lines[1].count(";")
            attributesNbT1=lines[1].count("\t")
            attributesNbC1=lines[1].count(",")
            if (attributesNbS==attributesNbS1) and (attributesNbS>0) and (attributesNbS>=attributesNbC) and (attributesNbS>=attributesNbT):
                attributeSep=";"
            elif (attributesNbC==attributesNbC1) and (attributesNbC>0) and (attributesNbC>attributesNbS) and (attributesNbC>=attributesNbT):
                attributeSep=","
            elif (attributesNbT==attributesNbT1) and (attributesNbT>0) and (attributesNbT>attributesNbS) and (attributesNbT>=attributesNbC):
                attributeSep="\t"
            else:
                features.append(Orange.feature.String(tmpNameForNewAttribute))
                domain = Orange.data.Domain(features)
                res = Orange.data.Table(domain, [[texteFile]])
                return [lineErrors,res]
            attributes = lines[0].split(attributeSep)
            dataes = []
            dataToFill = lines[1].split(attributeSep)
            for i in range(len(attributes)):
                features.append(Orange.feature.String(attributes[i]))
                dataes.append(dataToFill[i])
            domain = Orange.data.Domain(features)
            res = Orange.data.Table(domain, [dataes])
            return [lineErrors,res]
        else:
            attributesNbS1=lines[1].count(";")
            attributesNbT1=lines[1].count("\t")
            attributesNbC1=lines[1].count(",")
            attributesNbS2=lines[2].count(";")
            attributesNbT2=lines[2].count("\t")
            attributesNbC2=lines[2].count(",")
            if (attributesNbS==attributesNbS1) and (attributesNbS==attributesNbS2) and (attributesNbS>0) and (attributesNbS>=attributesNbC) and (attributesNbS>=attributesNbT):
                attributeSep=";"
            elif (attributesNbC==attributesNbC1) and (attributesNbC==attributesNbC2) and (attributesNbC>0) and (attributesNbC>attributesNbS) and (attributesNbC>=attributesNbT):
                attributeSep=","
            elif (attributesNbT==attributesNbT1) and (attributesNbT==attributesNbT2) and (attributesNbT>0) and (attributesNbT>attributesNbS) and (attributesNbT>=attributesNbC):
                attributeSep="\t"
            else:
                features.append(Orange.feature.String(tmpNameForNewAttribute))
                domain = Orange.data.Domain(features)
                res = Orange.data.Table(domain, [[texteFile]])
                return [lineErrors,res]
            attributes = lines[0].split(attributeSep)
            resultats = []
            for i in range(len(attributes)):
                features.append(Orange.feature.String(attributes[i]))
            for j in range(1,len(lines)):
                if lines[j]=="":
                    continue
                dataToFill = lines[j].split(attributeSep)
                if len(dataToFill)<=len(attributes):
                    ligneRes = []
                    for i in range(len(dataToFill)):
                        e = dataToFill[i]
                        if (e!="") and ((e.startswith('"') and e.startswith('"')) or (e.startswith('"') and e.startswith("'"))):
                            ligneRes.append(e[1:-1])
                        else:
                            ligneRes.append(e)
                    for i in range(len(attributes)-len(dataToFill)):
                        ligneRes.append("")
                        lineErrors = lineErrors+str(j)+", "
                    resultats.append(ligneRes)
                else:
                    lineErrors = lineErrors+str(j)+", "
            domain = Orange.data.Domain(features)
            res = Orange.data.Table(domain, resultats)
            return [lineErrors,res]
    else:
        features.append(Orange.feature.String(tmpNameForNewAttribute))
        domain = Orange.data.Domain(features)
        res = Orange.data.Table(domain, [[texteFile]])
        return [lineErrors,res]
