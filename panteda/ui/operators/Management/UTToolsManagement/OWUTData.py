#!/usr/bin/python
#Orange Widget initiated by Michael ORTEGA - 18/March/2014
#Orange Widget continued by Denis B. - April-June/2014, continued in 2015, 2016

"""
<name>Data</name>
<icon>OWUTData_icons/OWUTData.svg</icon>
<description>Recovers an UnderTracks study</description>
<priority>10</priority>
"""

#TODO : resoudre le pb du upload data on init. Le pb : l'affichage attends, il faudrait pouvoir obliger l'affichage, le rendre prioritaire

import Orange
from OWWidget import *
import OWGUI
import urllib  as  _u
import urllib2  as  _u2
import bz2    as _bz2
import zlib
import time
from Orange.feature import String
from PyQt4.QtGui import (QFileDialog, QDesktopServices)
import string
import codecs

class ImputeListItemDelegate(QItemDelegate):
    def __init__(self, widget, parent = None):
        QItemDelegate.__init__(self, parent)
        self.widget = widget

    def drawDisplay(self, painter, option, rect, text):
        QItemDelegate.drawDisplay(self, painter, option, rect, text)

class OWUTData(OWWidget):
    settingsList = ['nomExpe','loadOnInit']

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)
        #self.inputs = [("Data", Orange.data.Table, self.data)]
        self.outputs = [("Logs Table", Orange.data.Table),
                        ("Users Table", Orange.data.Table),
                        ("Contexts Table", Orange.data.Table),
                        ("Actions Table", Orange.data.Table)]
        settings = QSettings()
        val = settings.value("ut-login/login", "unknown")
        self.login = val.toString()
        if self.login != "unknown":  # GUI
            self.nomExpe = ''
            self.loadOnInit = False
            self.loadSettings()
            url = "https://undertracks.imag.fr/scripts/OrangeScripts/ExistingExperiences.php"
            data = _u.urlencode({"login": self.login})
            req = _u2.Request(url, data)
            f = _u2.urlopen(req)
            tab = f.read().rstrip().split("_!!_")
            self.listeStudy = tab[1:]
            boxConnexion = OWGUI.widgetBox(self.controlArea, "Connection")
            selectBox = OWGUI.lineEdit(boxConnexion, self, "nomExpe", box="Study?", callback=self.study_change_callback, callbackOnType=True)
            self.attrList = OWGUI.listBox(boxConnexion, self, callback = self.individualSelected)
            self.attrList.setItemDelegate(ImputeListItemDelegate(self, self.attrList))
            for s in  self.listeStudy:
                self.attrList.addItem(QListWidgetItem(owutStrUtf(s)))
            OWGUI.button(boxConnexion, self, 'See study on web', callback=self.studyOnWeb)
            OWGUI.button(boxConnexion, self, 'Load', callback=self.compute)
            tabs = OWGUI.tabWidget(self.mainArea)
            tab = OWGUI.createTabPage(tabs, "Logs")
            self.tableLogs = OWGUI.table(tab, selectionMode=QTableWidget.NoSelection)
            tab = OWGUI.createTabPage(tabs, "Users")
            self.tableUsers = OWGUI.table(tab, selectionMode=QTableWidget.NoSelection)
            tab = OWGUI.createTabPage(tabs, "Actions")
            self.tableActions = OWGUI.table(tab, selectionMode=QTableWidget.NoSelection)
            tab = OWGUI.createTabPage(tabs, "Contexts")
            self.tableContexts = OWGUI.table(tab, selectionMode=QTableWidget.NoSelection)
            self.resize(500,200)
            self.showData = False
            self.updateFullDataTables()
            self.showData = True
        else:
            boxConnexion = OWGUI.widgetBox(self.controlArea, "Connection")
#            label = OWGUI.label(boxConnexion, self, "Please connect to UnderTracks first! (File->Log on UT)" + self.login)
            label = OWGUI.label(boxConnexion, self, "Please connect to UnderTracks first! (File->Log on UT)")

    def studyOnWeb(self):
        url = QUrl("https://undertracks-dev.imag.fr/php/studies/study.php/"+self.nomExpe)
        QDesktopServices.openUrl(url)

    def individualSelected(self, i = -1):
        if self.attrList.selectedItems():
            self.nomExpe = owutStrUtf(str(self.attrList.selectedItems()[0].text()))


    def study_change_callback(self):
        self.attrList.clear()
        if self.nomExpe=="":
            for s in  self.listeStudy:
                self.attrList.addItem(QListWidgetItem(owutStrUtf(s)))
        else:
            for s in  self.listeStudy:
                if s.upper().find(self.nomExpe.upper())>=0:
                    self.attrList.addItem(QListWidgetItem(owutStrUtf(s)))

    def compute(self):
        mainOWUTData(self.nomExpe, True, self)
        self.saveSettings()
        self.updateFullDataTables()
        if hasattr(self,"dataLogs"):
            self.send("Logs Table",self.dataLogs)
        if hasattr(self,"dataUsers"):
            self.send("Users Table",self.dataUsers)
        if hasattr(self,"dataContexts"):
            self.send("Contexts Table",self.dataContexts)
        if hasattr(self,"dataActions"):
            self.send("Actions Table",self.dataActions)

    def updateFullDataTables(self):
        if self.showData:
          if hasattr(self,"dataLogs"):
            owutUpdateTable(self.dataLogs,self.tableLogs)
          else:
            owutShowNoTable(self.tableLogs)
          if hasattr(self,"dataUsers"):
            owutUpdateTable(self.dataUsers,self.tableUsers)
          else:
            owutShowNoTable(self.tableUsers)
          if hasattr(self,"dataActions"):
            owutUpdateTable(self.dataActions,self.tableActions)
          else:
            owutShowNoTable(self.tableActions)
          if hasattr(self,"dataContexts"):
            owutUpdateTable(self.dataContexts,self.tableContexts)
          else:
            owutShowNoTable(self.tableContexts)
        else:
          owutDoNotShowTable(self.tableLogs)
          owutDoNotShowTable(self.tableUsers)
          owutDoNotShowTable(self.tableActions)
          owutDoNotShowTable(self.tableContexts)


################# code metier de l'operateur OWUTData ######################

def mainOWUTData(expeName, versionGraphique, gui):
    if expeName==None:
        return
    for t_type, t_name in zip(["logs", "users", "context", "actions"],
                              ["Logs Table", "Users Table", "Contexts Table", "Actions Table"]):
        if versionGraphique:
            pb1 = OWGUI.ProgressBar(gui, iterations=4)
        table = expeName + t_type
        url = "https://undertracks.imag.fr/scripts/OrangeScripts/UTTableInAFile.php"
        data = _u.urlencode({"table": table})
        req = _u2.Request(url, data)
        if versionGraphique:
            pb1.advance()
        f = _u2.urlopen(req)
        url_on_UT = f.read()
        if versionGraphique:
            pb1.advance()
        if url_on_UT != "false":
            result = url_on_UT.split("_#_")
            columns = result[0].split("_!_")
            url_tab = result[1].split("_!_")
            tab = []
            rows = []
            if url_on_UT != "false":
                for u in url_tab[0:-1]:
                    sys.stderr.write(u)
                    f = _u2.urlopen(u)
                    res = f.read()
                    if versionGraphique:
                        pb1.advance()
                    res = _bz2.decompress(res)
                    if versionGraphique:
                        pb1.advance()
                    tab = [[c for c in line.split("_!_")] for line in res.split("_#_")]
                    if versionGraphique:
                        pb1.finish()
                        pb2 = OWGUI.ProgressBar(gui, iterations=len(tab))
                    for r in tab[0:-1]:  #TODO ameliorer pour que l'affichage ne soit que 1% du temps, i.e.: decouper la boucle par tranche de 1% du total
                        if versionGraphique:
                            pb2.advance()
                        rows.append(r)
                    if versionGraphique:
                        pb2.advance()
                        pb2.finish()
                features = []
                for i in range(len(columns)):
                    features.append(Orange.feature.String(columns[i]))
                domain = Orange.data.Domain(features)
                if t_type=="logs":
                    gui.dataLogs=Orange.data.Table(domain, rows)
                elif t_type=="users":
                    gui.dataUsers=Orange.data.Table(domain, rows)
                elif t_type=="context":
                    gui.dataContexts=Orange.data.Table(domain, rows)
                elif t_type=="actions":
                    gui.dataActions=Orange.data.Table(domain, rows)
        else:
            if versionGraphique:
                pb1.advance()
                pb1.advance()
                pb1.finish()


################################### codes communs a OWUTData et aux operateurs UT ######################################

## Tables Entrees/Sorties de previsualisation des donnees ##

def owutUpdateTables(gui):
    if gui.showInput:
        if hasattr(gui,"dataInputs"):
            owutUpdateTable(gui.dataInputs,gui.tableInputs)
        else:
            owutShowNoTable(gui.tableInputs)
    else:
        owutDoNotShowTable(gui.tableInputs)
    if gui.showOutput:
        if hasattr(gui,"dataOutputs"):
            owutUpdateTable(gui.dataOutputs,gui.tableOutputs)
        else:
            owutShowNoTable(gui.tableOutputs)
    else:
        owutDoNotShowTable(gui.tableOutputs)

def owutUpdateFullTable(gui):
    if gui.showOutput:
        if hasattr(gui,"dataOutputs"):
            owutUpdateFullTableNow(gui.dataOutputs,gui.tableOutputs)
        else:
            owutShowNoTable(gui.tableOutputs)
    else:
        owutDoNotShowTable(gui.tableOutputs)


def owutInitPrevisualisationEntreesSorties(gui):
    gui.tabs = OWGUI.tabWidget(gui.mainArea)
    tab = OWGUI.createTabPage(gui.tabs, "Inputs")
    gui.tableInputs = OWGUI.table(tab, selectionMode=QTableWidget.NoSelection)
    tab = OWGUI.createTabPage(gui.tabs, "Outputs")
    gui.tableOutputs = OWGUI.table(tab, selectionMode=QTableWidget.NoSelection)
    gui.tabMisc = OWGUI.createTabPage(gui.tabs, "Misc.")
    lKeepAttribute=[]
    lNameForNewAttribute=[]
    for cfg in gui.settingsList:
        if cfg[:10]=="cfgKeepAtt":
            lKeepAttribute.append(cfg)
        if cfg[:13]=="cfgNameNewAtt":
            lNameForNewAttribute.append(cfg)
    if len(lKeepAttribute):
        tmpWidgetBoxKeepAttribute = OWGUI.widgetBox(gui.tabMisc, "Keep attributes?")
        for i, attr in enumerate(lKeepAttribute):
            setattr(gui, attr, True)
            OWGUI.checkBox(tmpWidgetBoxKeepAttribute, gui, attr,"keep attribute "+str(i)+"?")
    if len(lNameForNewAttribute):
        tmpWidgetBoxRenameNewAttribute = OWGUI.widgetBox(gui.tabMisc, "Gives the name for your new attributes.")
        for i, attr in enumerate(lNameForNewAttribute):
            setattr(gui, attr, "")
            OWGUI.lineEdit(tmpWidgetBoxRenameNewAttribute, gui, attr, box="Keep empty if you want automatic naming for new attribute No "+str(i)+".")
    csvOutput = OWGUI.widgetBox(gui.tabMisc, "Export your results as csv file (with the separator given in brackets)", orientation='horizontal')
    OWGUI.button(csvOutput, gui, 'Fast (,)', callback=lambda : owutCsvOutput(gui,",",False))
    OWGUI.button(csvOutput, gui, 'Fast (;)', callback=lambda : owutCsvOutput(gui,";",False))
    OWGUI.button(csvOutput, gui, 'Fast (tab)', callback=lambda : owutCsvOutput(gui,"\t",False))
    OWGUI.button(csvOutput, gui, 'Safe (,)', callback=lambda : owutCsvOutput(gui,",",True))
    OWGUI.button(csvOutput, gui, 'Safe (;)', callback=lambda : owutCsvOutput(gui,";",True))
    OWGUI.button(csvOutput, gui, 'Safe (tab)', callback=lambda : owutCsvOutput(gui,"\t",True))
    gui.showInput = False
    gui.showOutput = False
    owutUpdateTables(gui)
    gui.showInput = True
    gui.showOutput = True

def owutUpdateTable(data,table):
    minPreview = 100
    table.setColumnCount(len(data.domain))
    table.setHorizontalHeaderLabels([owutStrUtf(data.domain[i].name) for i in range(len(data.domain))])
    if len(data)<minPreview:
        table.setRowCount(len(data))
        table.setVerticalHeaderLabels([str(i) for i in range(len(data))])
        for l in range(len(data.domain)):
            for p in range(len(data)):
                OWGUI.tableItem(table, p, l, owutStrUtf(data[p][l].value))
    else:
        table.setRowCount(minPreview)
        verticalHeaderLabels = []
        for i in range(minPreview/2):
          verticalHeaderLabels.append(str(i+1))
        verticalHeaderLabels.append('[...]')
        for i in range(len(data)-minPreview/2,len(data)):
          verticalHeaderLabels.append(str(i+2))
        table.setVerticalHeaderLabels(verticalHeaderLabels)
        for l in range(len(data.domain)):
            for p in range(minPreview/2):
                OWGUI.tableItem(table, p, l, owutStrUtf(data[p][l].value))
            OWGUI.tableItem(table, minPreview/2, l, "...")
            for p in range(len(data)-minPreview/2+1,len(data)):
                OWGUI.tableItem(table, p-len(data)+minPreview, l, owutStrUtf(data[p][l].value))
    for i in range(len(data.domain)):
        table.setColumnWidth(i, 80)
    table.setColumnWidth(len(data.domain)-1, 200)
    table.setColumnWidth(len(data.domain), 200)

def owutUpdateFullTableNow(data,table):
    table.setColumnCount(len(data.domain))
    table.setHorizontalHeaderLabels([owutStrUtf(data.domain[i].name) for i in range(len(data.domain))])
    table.setRowCount(len(data))
    table.setVerticalHeaderLabels([str(i) for i in range(len(data))])
    for l in range(len(data.domain)):
        for p in range(len(data)):
            if owutStrUtf(data[p][l].value).isdigit():
                OWGUI.tableItem(table, p, l, ('         '+owutStrUtf(data[p][l].value))[-9:] ) 
            else:
                OWGUI.tableItem(table, p, l, owutStrUtf(data[p][l].value))

def owutShowNoTable(table):
    table.setColumnCount(1)
    table.setRowCount(1)
    table.setHorizontalHeaderLabels(["-"])
    table.setVerticalHeaderLabels(["-"])
    OWGUI.tableItem(table, 0, 0, "No data")

def owutDoNotShowTable(table):
    table.setColumnCount(1)
    table.setRowCount(1)
    table.setHorizontalHeaderLabels(["-"])
    table.setVerticalHeaderLabels(["-"])
    OWGUI.tableItem(table, 0, 0, "Data not loaded")
    table.setColumnWidth(0, 200)

def owutSetPrevisualisationSorties(gui,table):
    gui.dataOutputs = table
    owutUpdateTables(gui)
#    if hasattr(gui,'nameForTheNewAttribute') and gui.nameForTheNewAttribute:
#        gui.res = Orange.data.Table(Orange.data.Domain(gui.dataOutputs.domain.features[0:(len(gui.dataOutputs.domain)-1)]+[Orange.feature.String(str(gui.nameForTheNewAttribute))]), gui.dataOutputs.native(0))

#pour les cas plus rares ou l'on veut tout voir (cas du count par exemple), i.e. ou le nombre de chose a voir devrait etre raisonnable
def owutSetVisualisationSorties(gui,table):
    gui.dataOutputs = table
    owutUpdateFullTable(gui)

def owutSetPrevisualisationEntrees(gui,table):
    gui.dataInputs = table
    owutUpdateTables(gui)

## API de construction/acces de/a l'interface pour le choix/config/sauv d'un attribut

def owutAjouteChoixAttribut(widget,gui,strConfig,strIHM):
    setattr(gui,strConfig, "")
    tmpWidgetoBox = OWGUI.widgetBox(widget, strIHM, addSpace=True)
    tmpComboBox = OWGUI.comboBox(tmpWidgetoBox, gui, strConfig)
    setattr(gui,'cb__'+strConfig,tmpComboBox)
    if hasattr(gui,'listeChoixAttribut'):
        gui.listeChoixAttribut.append([strConfig,tmpComboBox])
    else:
        gui.listeChoixAttribut = [[strConfig,tmpComboBox]]
    return tmpComboBox

def owutChoixAttributDomain(gui,strConfig,domain):
    if hasattr(gui,'cb__'+strConfig):
        wid = getattr(gui,'cb__'+strConfig)
        tmpValeurDuChoixAPartirDeLInterface = wid.itemText(wid.currentIndex())
        tmpIndiceDuDomain = owutIndiceAttribut(tmpValeurDuChoixAPartirDeLInterface,domain)
        if tmpIndiceDuDomain==-1:
          return owutStrUtf(tmpValeurDuChoixAPartirDeLInterface)
        else:
          return domain[tmpIndiceDuDomain].name
    else:
        raise ValueError('choixAttributInconnu')

def owutChoixAttribut(gui,strConfig):
    return owutChoixAttributDomain(gui,strConfig, gui.data.domain)

def owutSynchroniseChoixAttribut(gui):
    for a in gui.listeChoixAttribut:
        setattr(gui,a[0],owutStrUtf(a[1].itemText(a[1].currentIndex())))

def owutInitChoixAttributAvecChoixVideEtVerifieConfig(gui,strConfig,lNames):
    lNamesComplete = ["_ut__choix_vide_"]
    for i in range(len(lNames)):
        if hasattr(lNames[i],"name"):
            lNamesComplete.append(owutStrUtf(lNames[i].name))
        else:
            lNamesComplete.append(owutStrUtf(lNames[i]))
    return owutInitChoixAttributEtVerifieConfig(gui,strConfig,lNamesComplete)

def owutInitChoixAttributEtVerifieConfig(gui,strConfig,lNames):
    wid = getattr(gui,'cb__'+strConfig)
    wid.clear()
    res = False
    for i in range(len(lNames)):
        if hasattr(lNames[i],"name"):
            wid.addItem(owutStrUtf(lNames[i].name))
        elif lNames[i]=="_ut__choix_vide_":
            wid.addItem("             ") #13 espaces
        else:
            wid.addItem(owutStrUtf(lNames[i]))
    if hasattr(gui,strConfig):
        cfgUtf = owutStrUtf(getattr(gui,strConfig))
        for i in range(len(wid)):
            if owutStrUtf(wid.itemText(i))==cfgUtf:
                wid.setCurrentIndex(i)
                res = True
    return res

def owutIndiceAttribut(strAttribut,lDomain):
    indAttribut = -1
    strUtfAttribut = owutStrUtf(strAttribut)
    for i in range(len(lDomain)):
        if (owutStrUtf(lDomain[i].name)==strUtfAttribut) and (indAttribut==-1):
            indAttribut = i
    return indAttribut

def owutEstChoixVide(str):
    return str=="             " #13 espaces

## Re-Codage des chaines de caracteres ##
#
# les noms d'Attribut (domain) et les valeurs (value) n'acceptent pas d'etre Unicode,
# mais peuvent etre des string (str) avec des caracteres non ascii !!! mais a l'interface ce n'est pas joli
# Pour les afficher, il faut les transtyper en unicode avec owutStrUtf
# Attention, si on recupere une valeur a l'interface elle risque d'etre un QString, pour retrouver une chaine unicode
# il faut utiliser owutStrUtf aussi
# Pour securiser une chaine, par contre, il faut utiliser owutUtf2Ascii qui traduit en qlq chose proche des htmlentities
# Pour forcer le retour a une string (si necessaire pour reconstruire un nom d'attribut ou une valeur en reprenant des
# valeurs qui ont ete transformees en unicode), utiliser str
# Recapitulatif :
#   vers l'interface : owutStrUtf,
#   venant de l'interface : owutStrUtf,
#   vers domain/value si il y a eu un owutStrUtf alors : str
#   vers html : owutUtf2Ascii

def owutStrUtf(vStr):
    try:
        tmpStr = unicode(vStr,"utf-8")
    except:
        try:
            tmpStr = unicode(vStr)
        except:
            tmpStr = vStr
    return tmpStr

def owutUtf2Ascii(vStr):
    strOut = ""
    tmpStr = owutStrUtf(vStr)
    try:
        lentmpStr = len(tmpStr)
    except:
        return ""
    for i in range(lentmpStr):
        code = ord(tmpStr[i])
        if (((code>64)and(code<91))  or ((code>96)and(code<123))  or (code==95) or ((code>47)and(code<58))):
            strOut += tmpStr[i]
        else:
            strOut += "-"+str(code)+"--"  #codes - et -- a remplacer par &# et ; en cas d'affichage html
    return str(strOut)

def owutAscii2Utf(vStr):
    strOut = u""
    indPrec = 0
    ind=vStr.find("-",indPrec)
    while ind!=-1:
        strOut += vStr[indPrec:ind]
        indPrec=ind+1
        ind=vStr.find("--",indPrec)
        if ind!=-1:
            strOut += unichr(int(vStr[indPrec:ind]))
            indPrec = ind+2
            ind = vStr.find("-",indPrec)
        else:
            strOut += unichr(int(vStr[indPrec:]))
            indPrec = len(vStr)
    strOut += vStr[indPrec:]
    return strOut

### cast nombres et temps ###
def owutCastContinuous(pValue):
    if type(pValue) is float:
        return pValue
    elif pValue.isdigit():
        return pValue
    else:
        try:
            tmpValeur = float(pValue.replace(",","."))
            return tmpValeur
        except:
            tmpValeur = owutCastTime(pValue,1)
            if tmpValeur[0] == "0" :
                return str(zlib.crc32(pValue) & 0xffffffff)
            else:
                return tmpValeur[0]


OWUTGlobalPrivateVariableForTimeModule_LastTimeFormat = "%Y-%m-%d %H:%M:%S"
OWUTGlobalPrivateVariableForTimeModule_LastTypeOfTimeFormat = -1
OWUTGlobalPrivateVariableForTimeModule_LastCodeTimeFormat = 0
OWUTGlobalPrivateConstForTimeModule_LastTypeOfTimeFormat = time.strptime("2000/01/01 00:00:00","%Y/%m/%d %H:%M:%S")


def owutCastTime(pTempsOuOrdre, codeTimeFormat):
    global OWUTGlobalPrivateVariableForTimeModule_LastTimeFormat
    global OWUTGlobalPrivateVariableForTimeModule_LastTypeOfTimeFormat
    global OWUTGlobalPrivateVariableForTimeModule_LastCodeTimeFormat
    global OWUTGlobalPrivateConstForTimeModule_LastTypeOfTimeFormat
    tempsCourant = -1
    ordreCourant = -1
    if (codeTimeFormat == OWUTGlobalPrivateVariableForTimeModule_LastCodeTimeFormat) and (OWUTGlobalPrivateVariableForTimeModule_LastTypeOfTimeFormat == 0):
      try:
        tempsCourant = time.strptime(pTempsOuOrdre,OWUTGlobalPrivateVariableForTimeModule_LastTimeFormat)
      except:
        tempsCourant = -1
        OWUTGlobalPrivateVariableForTimeModule_LastTypeOfTimeFormat = -1
    if (tempsCourant == -1) and (OWUTGlobalPrivateVariableForTimeModule_LastTypeOfTimeFormat==1):
      try:
        ordreCourant =  int(pTempsOuOrdre)
      except:
        ordreCourant = -1
        OWUTGlobalPrivateVariableForTimeModule_LastTypeOfTimeFormat = -1
    if (tempsCourant == -1) and (ordreCourant == -1)  and (OWUTGlobalPrivateVariableForTimeModule_LastTypeOfTimeFormat==2):
      try:
        ordreCourant = float(pTempsOuOrdre)
        OWUTGlobalPrivateVariableForTimeModule_LastTypeOfTimeFormat = 2
      except:
        ordreCourant = -1
        OWUTGlobalPrivateVariableForTimeModule_LastTypeOfTimeFormat = -1
    if (tempsCourant == -1) and (ordreCourant == -1):
            if (tempsCourant == -1): # and (codeTimeFormat == 1):
              try:
                tempsCourant = time.strptime(pTempsOuOrdre,"%Y-%m-%dT%H:%M:%SZ") #ISO 8601
                OWUTGlobalPrivateVariableForTimeModule_LastTimeFormat = "%Y-%m-%dT%H:%M:%SZ"
                OWUTGlobalPrivateVariableForTimeModule_LastTypeOfTimeFormat = 0
                OWUTGlobalPrivateVariableForTimeModule_LastCodeTimeFormat = codeTimeFormat
              except:
                tempsCourant = -1
            if (tempsCourant == -1): # and (codeTimeFormat == 1):
              try:
                tempsCourant = time.strptime(pTempsOuOrdre,"%Y-%m-%d %H:%M:%S")
                OWUTGlobalPrivateVariableForTimeModule_LastTimeFormat = "%Y-%m-%d %H:%M:%S"
                OWUTGlobalPrivateVariableForTimeModule_LastTypeOfTimeFormat = 0
                OWUTGlobalPrivateVariableForTimeModule_LastCodeTimeFormat = codeTimeFormat
              except:
                tempsCourant = -1
            if (tempsCourant == -1): # and (codeTimeFormat == 1):
              try:
                tempsCourant = time.strptime(pTempsOuOrdre,"%Y/%m/%d %H:%M:%S")
                OWUTGlobalPrivateVariableForTimeModule_LastTimeFormat = "%Y/%m/%d %H:%M:%S"
                OWUTGlobalPrivateVariableForTimeModule_LastTypeOfTimeFormat = 0
                OWUTGlobalPrivateVariableForTimeModule_LastCodeTimeFormat = codeTimeFormat
              except:
                tempsCourant = -1
            if (tempsCourant == -1): # and (codeTimeFormat == 1):
              try:
                tempsCourant = time.strptime(pTempsOuOrdre,"%d-%m-%Y %H:%M:%S")
                OWUTGlobalPrivateVariableForTimeModule_LastTimeFormat = "%d-%m-%Y %H:%M:%S"
                OWUTGlobalPrivateVariableForTimeModule_LastTypeOfTimeFormat = 0
                OWUTGlobalPrivateVariableForTimeModule_LastCodeTimeFormat = codeTimeFormat
              except:
                tempsCourant = -1
            if (tempsCourant == -1): # and (codeTimeFormat == 1):
              try:
                tempsCourant = time.strptime(pTempsOuOrdre,"%d/%m/%Y %H:%M:%S")
                OWUTGlobalPrivateVariableForTimeModule_LastTimeFormat = "%d/%m/%Y %H:%M:%S"
                OWUTGlobalPrivateVariableForTimeModule_LastTypeOfTimeFormat = 0
                OWUTGlobalPrivateVariableForTimeModule_LastCodeTimeFormat = codeTimeFormat
              except:
                tempsCourant = -1
        #    if tempsCourant == -1:
        #      try:
        #        tempsCourant = time.strptime(pTempsOuOrdre,"%y/%m/%d %H:%M:%S") #ajouter dans la liste des formats renseignes pas l'utilisateur ?
        #        OWUTGlobalPrivateVariableForTimeModule_LastTimeFormat = "%y/%m/%d %H:%M:%S"
        #        OWUTGlobalPrivateVariableForTimeModule_LastTypeOfTimeFormat = 0
        #        OWUTGlobalPrivateVariableForTimeModule_LastCodeTimeFormat = codeTimeFormat
        #      except:
        #        tempsCourant = -1
            if (tempsCourant == -1) and (codeTimeFormat == 1):
              try:
                tempsCourant = time.strptime(pTempsOuOrdre,"%d/%m/%y %H:%M:%S")
                OWUTGlobalPrivateVariableForTimeModule_LastTimeFormat = "%d/%m/%y %H:%M:%S"
                OWUTGlobalPrivateVariableForTimeModule_LastTypeOfTimeFormat = 0
                OWUTGlobalPrivateVariableForTimeModule_LastCodeTimeFormat = codeTimeFormat
              except:
                tempsCourant = -1
            if (tempsCourant == -1): # and (codeTimeFormat == 1):
              try:
                tempsCourant = time.strptime(pTempsOuOrdre,"%d/%m/%y %H:%M")
                OWUTGlobalPrivateVariableForTimeModule_LastTimeFormat = "%d/%m/%y %H:%M"
                OWUTGlobalPrivateVariableForTimeModule_LastTypeOfTimeFormat = 0
                OWUTGlobalPrivateVariableForTimeModule_LastCodeTimeFormat = codeTimeFormat
              except:
                tempsCourant = -1
            if (tempsCourant == -1): # and (codeTimeFormat == 1):
              try:
                tempsCourant = time.strptime(pTempsOuOrdre,"%H:%M:%S")
                OWUTGlobalPrivateVariableForTimeModule_LastTimeFormat = "%H:%M:%S"
                OWUTGlobalPrivateVariableForTimeModule_LastTypeOfTimeFormat = 0
                OWUTGlobalPrivateVariableForTimeModule_LastCodeTimeFormat = codeTimeFormat
              except:
                tempsCourant = -1
            if (tempsCourant == -1): # and (codeTimeFormat == 1):
              try:
                tempsCourant = time.strptime(pTempsOuOrdre,"%H:%M:%S.%f")
                OWUTGlobalPrivateVariableForTimeModule_LastTimeFormat = "%H:%M:%S.%f"
                OWUTGlobalPrivateVariableForTimeModule_LastTypeOfTimeFormat = 0
                OWUTGlobalPrivateVariableForTimeModule_LastCodeTimeFormat = codeTimeFormat
              except:
                tempsCourant = -1
            if (tempsCourant == -1) and (codeTimeFormat == -1):
              try:
                tempsCourant = time.strptime(pTempsOuOrdre,"%m/%d/%Y %H:%M:%S")
                OWUTGlobalPrivateVariableForTimeModule_LastTimeFormat = "%m/%d/%Y %H:%M:%S"
                OWUTGlobalPrivateVariableForTimeModule_LastTypeOfTimeFormat = 0
                OWUTGlobalPrivateVariableForTimeModule_LastCodeTimeFormat = codeTimeFormat
              except:
                tempsCourant = -1
            if (tempsCourant == -1) and (codeTimeFormat == -1):
              try:
                tempsCourant = time.strptime(pTempsOuOrdre,"%m/%d/%y %H:%M:%S")
                OWUTGlobalPrivateVariableForTimeModule_LastTimeFormat = "%m/%d/%y %H:%M:%S"
                OWUTGlobalPrivateVariableForTimeModule_LastTypeOfTimeFormat = 0
                OWUTGlobalPrivateVariableForTimeModule_LastCodeTimeFormat = codeTimeFormat
              except:
                tempsCourant = -1
            if (tempsCourant == -1) and (ordreCourant == -1):
              try:
                ordreCourant =  int(pTempsOuOrdre)
                OWUTGlobalPrivateVariableForTimeModule_LastTypeOfTimeFormat = 1
              except:
                ordreCourant = -1
            if (tempsCourant == -1) and (ordreCourant == -1):
              try:
                ordreCourant = float(pTempsOuOrdre)
                OWUTGlobalPrivateVariableForTimeModule_LastTypeOfTimeFormat = 2
              except:
                ordreCourant = -1
            if (tempsCourant == -1) and (ordreCourant == -1):
              tempsCourant = OWUTGlobalPrivateConstForTimeModule_LastTypeOfTimeFormat
              OWUTGlobalPrivateVariableForTimeModule_LastTypeOfTimeFormat = -1
    if ordreCourant != -1:
      tempsOuOrdreCourant = ordreCourant
      tmpDT = time.gmtime(ordreCourant);
      tempsStd = quatreChiffres(tmpDT.tm_year)+"-"+deuxChiffres(tmpDT.tm_mon)+"-"+deuxChiffres(tmpDT.tm_mday)+" "+deuxChiffres(tmpDT.tm_hour)+":"+deuxChiffres(tmpDT.tm_min)+":"+deuxChiffres(tmpDT.tm_sec)
      tempsIso = quatreChiffres(tmpDT.tm_year)+"-"+deuxChiffres(tmpDT.tm_mon)+"-"+deuxChiffres(tmpDT.tm_mday)+"T"+deuxChiffres(tmpDT.tm_hour)+":"+deuxChiffres(tmpDT.tm_min)+":"+deuxChiffres(tmpDT.tm_sec)+'Z' #ISO 8601
    else:
      tempsOuOrdreCourant = time.mktime(tempsCourant) #(tempsCourant.tm_year - 1970)*365*24*3600 + (tempsCourant.tm_yday-1)*3600*24 + tempsCourant.tm_hour * 3600 + tempsCourant.tm_min * 60 + tempsCourant.tm_sec
      tempsStd = quatreChiffres(tempsCourant.tm_year)+"-"+deuxChiffres(tempsCourant.tm_mon)+"-"+deuxChiffres(tempsCourant.tm_mday)+" "+deuxChiffres(tempsCourant.tm_hour)+":"+deuxChiffres(tempsCourant.tm_min)+":"+deuxChiffres(tempsCourant.tm_sec)
      tempsIso = quatreChiffres(tempsCourant.tm_year)+"-"+deuxChiffres(tempsCourant.tm_mon)+"-"+deuxChiffres(tempsCourant.tm_mday)+"T"+deuxChiffres(tempsCourant.tm_hour)+":"+deuxChiffres(tempsCourant.tm_min)+":"+deuxChiffres(tempsCourant.tm_sec)+'Z' #ISO 8601
    return [str(tempsOuOrdreCourant), tempsStd, tempsIso]

def deuxChiffres(pStr):
    if len(str(pStr))==0:
        return "00"
    elif len(str(pStr))==1:
        return "0"+str(pStr)
    else:
        return str(pStr)

def quatreChiffres(pStr):
    if len(str(pStr))!=4:
        return "2000"
    elif int(pStr)<1980:
        return "2000"
    else:
        return str(pStr)

def owutNormaliseTailleNom(pStr):
    if len(pStr)<45:
        return pStr
    else:
        return pStr[:20]+"::"+str(len(pStr)-40)+"::"+pStr[-20:]

def owutCsvOutput(gui,sep,quot):
  filename = QFileDialog.getSaveFileName(gui, gui.tr("Ouput csv file?"),"/myFile.csv",gui.tr("CSV (*.csv)"))
  if filename and gui.dataOutputs:
    f = codecs.open(filename,'w',"utf-8")
    suc = False
    for n in gui.dataOutputs.domain:
      if suc:
        f.write(sep)
      else:
        suc = True
      if quot:
        f.write('"'+string.replace(owutStrUtf(n.name),'"','""')+'"')
      else:
        f.write(owutStrUtf(n.name))
    f.write("\n")
    for l in range(len(gui.dataOutputs)):
      suc = False
      for e in range(len(gui.dataOutputs.domain)):
        if suc:
          f.write(sep)
        else:
          suc = True
        if quot:
          f.write('"'+string.replace(owutStrUtf(gui.dataOutputs[l][e].value),'"','""')+'"')
        else:
          f.write(owutStrUtf(gui.dataOutputs[l][e].value))
      f.write("\n")
    f.close()
  return

def owutValideNameAttributeFrom(pStr,lDomain):
    nameOk = True
    tmpStr = pStr
    tmpNum = 0
    for name in lDomain:
        nameOk = nameOk and (tmpStr != name.name)
    while not(nameOk):
        nameOk = True
        tmpNum = tmpNum + 1
        tmpStr = pStr + str(tmpNum)
        for name in lDomain:
            nameOk = nameOk and (tmpStr != name.name)
    return tmpStr