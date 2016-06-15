#!/usr/bin/python
#Orange Widget developped by Denis B. Oct, 2014.

"""
<name>R</name>
<icon>OWUTR_icons/OWUTR.svg</icon>
<description>This operator is for R scripting</description>
<priority>51</priority>
"""

import Orange
from OWWidget import *
import OWGUI
import subprocess

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


class OWUTR(OWWidget):
    settingsList = ['configScript']

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager)
        self.data = None
        self.inputs = [("Entry Table", Orange.data.Table, self.set_data)]
        self.outputs = [("Output Table", Orange.data.Table)]
        settings = QSettings()
        
        
        #######################
        # Test Login
        val = settings.value("ut-login/login", "unknown")
        self.login = val.toString()
        self.path = unicode(settings.value("ut-path/path","unknown").toString())
        
        #######################
        # Login ok
        if self.login != "unknown":

            self.configScript = ""
            self.loadSettings()
            self.pre_script = QPlainTextEdit()
            self.pre_script.setFixedWidth(800)
            self.pre_script.setFixedHeight(20)
            self.pre_script.setReadOnly(True)
            self.pre_script.setPlainText("UTIn <- Entry Table")
            self.script = QPlainTextEdit()
            self.script.setFixedWidth(800)
            self.script.setPlainText(self.configScript)
            
            self.post_script = QPlainTextEdit()
            self.post_script.setFixedWidth(800)
            self.post_script.setFixedHeight(20)
            self.post_script.setReadOnly(True)
            self.post_script.setPlainText("Output Table <- UTOut")
            
            self.console = QTextEdit()
            self.console.setReadOnly(True)
            self.console.setFixedWidth(800)
            
            self.script_box = OWGUI.widgetBox(self.controlArea, "R Script")
            self.script_box.layout().addWidget(self.pre_script)
            self.script_box.layout().addWidget(self.script)
            self.script_box.layout().addWidget(self.post_script)
            
            self.console_box = OWGUI.widgetBox(self.controlArea, "Console Result")
            self.console_box.layout().addWidget(self.console)
            
            
            self.button_box = OWGUI.widgetBox(self.controlArea, None,False,False, "")
            OWGUI.button(self.button_box, self, 'Apply', callback=self.compute)
            clear_b = OWGUI.button(self.button_box, self, 'Clear Console', callback=self.clear_console)
            clear_b.setFixedWidth(120)

        #######################
        # Login not ok
        else:
            boxConnexion = OWGUI.widgetBox(self.controlArea, "Connection")
            label = OWGUI.label(boxConnexion, self, "Please connect to UnderTracks first! (File->Log on UT)" + self.login)

    def set_data(self, data, id=None):
        self.data = data
        sys.stderr.write("loaded")
        if (self.configScript != "") and (self.data != None) :
            self.compute()
        return
        
    def add_to_console(self, text):
        current_console_text = self.console.toPlainText()
        self.console.setPlainText(current_console_text+"\n-------------------------------------------\n"+text)
        self.console.verticalScrollBar().setValue(self.console.verticalScrollBar().maximum())

    def clear_console(self):
        self.console.setPlainText("")

    def compute(self):
        
        if self.data:
            ###################################
            # Create a csv file in self.path
            try:
                os.chdir(self.path)
            except:
                return("Cannot accces directory: " + self.path)
            try:
                os.chdir("UTtemp")
            except:
                os.mkdir("UTtemp")
                os.chdir("UTtemp")

            f = open("data.csv","w")
            for i in range(len(self.data.domain)-1):
                f.write(self.data.domain[i].name+",")
            f.write(self.data.domain[len(self.data.domain)-1].name+"\n")
            for d in self.data:
                for j in range(len(d)-1):
                    f.write(str(d[j])+",")
                f.write(str(d [len(d)-1])+"\n")
            f.close()
            
            ###################################
            # Launch R on the script
            result = mainOWUTR(self.script.toPlainText(), self.path+"/UTtemp", "data.csv")

            self.configScript = self.script.toPlainText()
            self.saveSettings()
            
            ###################################
            # Result table
            res = open("result.txt","r")
            
            #header -> domain
            line = res.readline()
            tab = line.split(chr(30))
            features = []
            for t in tab:
                features.append(Orange.feature.String(t))
            domain = Orange.data.Domain(features)
            
            #data
            rows = []
            line = res.readline()
            while line :
                rows.append(line.split(chr(30)))
                line = res.readline()

            self.send("Output Table", Orange.data.Table(domain,rows))
            self.add_to_console(result)
        else:
            self.add_to_console("No Input Data")

    def setData(self, data, id=None):
        pass


def mainOWUTR(script, path, file):

    ###################################
    # change directory
    try:
        os.chdir(path)
    except:
        return("Cannot accces directory: " + path)

    ###################################
    # Script in a file
    f = open("script.R", 'w')
    f.write("UTIn <- read.csv(\""+file+"\", header = TRUE, sep = \",\")\n")
    f.write("UTOut <- c(0)\n")
    f.write(script+"\n")
    f.write("write.table(UTOut, file = \"result.txt\", row.names=FALSE, sep=intToUtf8(30))")
    #f.write("write.table(UTOut, file = \"result_tab.txt\", row.names=FALSE, sep=\"\\t\")\n")
    #f.write("write.table(UTOut, file = \"result_coma.csv\", row.names=FALSE, sep=\";\")")
    
    f.close()


    ###################################
    # launching the script
    os.system("Rscript script.R > res_console.txt 2>&1")


    ###################################
    # console result
    f = open("res_console.txt", "r")
    console =""
    res = f.readline()
    while res:
        console += res
        res = f.readline()
    f.close()

    return console
    