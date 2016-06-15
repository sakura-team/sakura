#!/usr/bin/python

#Orange Widget initiated by Michael ORTEGA - 18/March/2014
#Orange Widget continued by Denis B. - April-June/2014, continued in 2015

"""
<name>Sample</name>
<icon>OWUTSample_icons/OWUTSample.svg</icon>
<description>Sample give a sample of the data logs from a study</description>
<priority>11</priority>
"""

import Orange
from OWWidget import *
import OWGUI
import urllib  as  _u
import urllib2  as  _u2
import bz2    as _bz2
from Orange.feature import String
if not sys.path[len(sys.path)-1].endswith("/Management/UTToolsManagement"):
    tmpSettings = QSettings()
    path = str(tmpSettings.value("ut-path/path","unknown").toString()+"/Management/UTToolsManagement")
    sys.path.append(path)
from OWUTData import owutShowNoTable
from OWUTData import owutUpdateTable
from OWUTData import owutDoNotShowTable
from OWUTData import owutAscii2Utf
from OWUTData import owutStrUtf
from OWUTData import owutInitChoixAttributEtVerifieConfig
from OWUTData import owutIndiceAttribut
from OWUTData import owutUtf2Ascii

class ImputeListItemDelegate(QItemDelegate):
    def __init__(self, widget, parent = None):
        QItemDelegate.__init__(self, parent)
        self.widget = widget

    def drawDisplay(self, painter, option, rect, text):
        if self.widget.remplissageListe == 1:
            QItemDelegate.drawDisplay(self, painter, option, rect, text)
        elif self.widget.listValueToSelect.has_key(owutStrUtf(text)):
            if self.widget.listValueToSelect[owutStrUtf(text)]==1:
                QItemDelegate.drawDisplay(self, painter, option, rect, " + "+text)
            else:
                QItemDelegate.drawDisplay(self, painter, option, rect, " - "+text)
        else:
            QItemDelegate.drawDisplay(self, painter, option, rect, " ? "+text)

class OWUTSample(OWWidget):
    settingsList = ['nomExpe','configListValueToSelect','loadOnInit','offset','limit']

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)
        self.outputs = [("SampleLogs Table", Orange.data.Table),
                        ("Users Table", Orange.data.Table),
                        ("Contexts Table", Orange.data.Table),
                        ("Actions Table", Orange.data.Table)]
        settings = QSettings()
        val = settings.value("ut-login/login", "unknown")
        self.login = val.toString()
        if self.login != "unknown":  # GUI
            self.nomExpe = ''
            self.offset = '0'
            self.limit = '1000'
            self.loadOnInit = False
            self.configListValueToSelect = '' # 'item:ut-item:ut-item' pour les attributs
            self.loadSettings()
            url = "https://undertracks.imag.fr/scripts/OrangeScripts/ExistingExperiences.php"
            data = _u.urlencode({"login": self.login})
            req = _u2.Request(url, data)
            f = _u2.urlopen(req)
            tab = f.read().rstrip().split("_!!_")
            boxConnexion = OWGUI.widgetBox(self.controlArea, "Connection")
            self.cB = OWGUI.comboBox(boxConnexion, self, 'expe', box="Study for your sample", callback=self.majCols)
            boxlistValueToSelect = OWGUI.widgetBox(boxConnexion, "Columns for your sample", addSpace=True)
            self.attrList = OWGUI.listBox(boxlistValueToSelect, self, callback = self.individualSelected)
            self.listValueToSelect = {}
            self.attrList.setItemDelegate(ImputeListItemDelegate(self, self.attrList))
            #self.cF = OWGUI.comboBox(boxConnexion, self, 'Columns')
            boxOffsetConfig = OWGUI.lineEdit(boxConnexion, self, "offset", box="Offset for your sample")
            boxLimitConfig = OWGUI.lineEdit(boxConnexion, self, "limit", box="Limit for your sample")
            OWGUI.button(boxConnexion, self, 'Load', callback=self.compute)
            for i in range(int(tab[0])):
                self.cB.addItem(tab[i + 1])
            if self.nomExpe!=None:
                for i in range(int(tab[0])):
                    if self.cB.itemText(i) == self.nomExpe:
                        self.cB.setCurrentIndex(i)
            self.majCols()
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
            label = OWGUI.label(boxConnexion, self, "Please connect to UnderTracks first! (File->Log on UT)")

    def majCols(self):
        url = "https://undertracks.imag.fr/scripts/OrangeScripts/UTColumnsInAFile.php"
        expeName = str(self.cB.itemText(self.cB.currentIndex()))+'logs'
        data = _u.urlencode({"table": expeName})
        req = _u2.Request(url, data)
        f = _u2.urlopen(req)
        all = f.read().split("_!_") #self.configListValueToSelect.split(':ut-')[1:]
        self.remplissageListe = 1
        self.attrList.clear()
        for k in all:
            self.attrList.addItem(QListWidgetItem(owutStrUtf(k)))
        self.listValueToSelect.clear()
        for i in range(len(self.attrList)):
            self.listValueToSelect[owutStrUtf(self.attrList.item(i).text())] = 0
        if self.configListValueToSelect != None:
            elts = self.configListValueToSelect.split(':ut-')[1:]
            for e in elts:
                self.listValueToSelect[owutAscii2Utf(e)]=1
        self.remplissageListe = 0

    def individualSelected(self, i = -1):
        if self.remplissageListe == 0:
            if len(self.attrList.selectedItems())>0:
                if self.listValueToSelect.has_key(owutStrUtf(self.attrList.selectedItems()[0].text())):
                    self.listValueToSelect[owutStrUtf(self.attrList.selectedItems()[0].text())] = 1 - self.listValueToSelect[owutStrUtf(self.attrList.selectedItems()[0].text())]
                else:
                    self.listValueToSelect[owutStrUtf(self.attrList.selectedItems()[0].text())] = 1
                self.attrList.clearSelection()

    def compute(self):
        expeName = self.cB.itemText(self.cB.currentIndex())
        columnsToSelect = ""
        for i in range(self.attrList.count()):
            if owutStrUtf(self.attrList.item(i).text()) in self.listValueToSelect:
                if self.listValueToSelect[owutStrUtf(self.attrList.item(i).text())]==1:
                    columnsToSelect += ":ut-"+owutUtf2Ascii(self.attrList.item(i).text())
        mainOWUTSample(expeName, self.offset, self.limit, columnsToSelect, True, self)
        self.nomExpe = expeName
        self.configListValueToSelect = columnsToSelect
        self.saveSettings()
        self.updateFullDataTables()
        if hasattr(self,"dataLogs"):
            self.send("SampleLogs Table",self.dataLogs)
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

def mainOWUTSample(expeName, offset, limit, pColumnsToSelect, versionGraphique, gui):
    if expeName==None:
        return
    for t_type, t_name in zip(["logs", "users", "context", "actions"],
                              ["Logs Table", "Users Table", "Contexts Table", "Actions Table"]):
        if versionGraphique:
            pb1 = OWGUI.ProgressBar(gui, iterations=4)
        table = expeName + t_type
        if t_type=="logs":
            url = "https://undertracks.imag.fr/scripts/OrangeScripts/UTDataInAFile.php"
            if not offset.isdigit():
                offset="0"
            if not limit.isdigit():
                limit="1000"
            elts = pColumnsToSelect.split(':ut-')[1:]
            cols='"'
            for e in elts:
                cols = cols + '","' + str(owutAscii2Utf(e))
            cols=cols + '"'
            data = _u.urlencode({"table": table, "offset": offset, "limit": limit, "columns":cols[3:]})
        else:
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
                    for r in tab[0:-1]:
                        if versionGraphique:
                            pb2.advance()
                        rows.append(r)
                    if versionGraphique:
                        pb2.advance()
                        pb2.finish()
                features = []
                if t_type=="logs":
                    for e in elts:
                        features.append(Orange.feature.String(str(owutAscii2Utf(e))))
                else:
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