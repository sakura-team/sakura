"""
UnderTracks updating UT widgets.

"""

from PyQt4.QtGui import (
    QWidget, QFileDialog, QDialog, QLabel, QTextEdit, QCheckBox, QFormLayout,
    QVBoxLayout, QHBoxLayout, QDialogButtonBox, QSizePolicy, QGridLayout,QPushButton, QScrollArea
)

from PyQt4.QtCore import Qt

from ..utils.qtcompat import QSettings
from ..gui.lineedit import LineEdit
from ..gui.utils import StyledWidget_paintEvent, StyledWidget

import os
import sys
import urllib	as	_u
import urllib2 	as  _u2
import zlib     as  _zlib
import zipfile  as  _zfile
from StringIO   import StringIO
import subprocess

def ecrire(s):
    sys.stderr.write(s)

class UTUpdateDialog(QDialog):
    def __init__(self, *args, **kwargs):
        QDialog.__init__(self, *args, **kwargs)
        self.path               = None
        self.login              = None
        self.widgets_to_update  = []
        self.widgets_checkboxes = []
        
        self.__setupUi()

    def __setupUi(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(5,5,5,5)
        layout.setSpacing(10)

        settings = QSettings()
        # 1 - Login test
        login = unicode(settings.value("ut-login/login","unknown"))
        if login == "unknown":
            message_critical("The login is not recognized by UnderTracks!\nPlease check !")
            return QDialog.Accepted

        # 2 - Check for a UT Widget Path
        self.path = unicode(settings.value("ut-path/path","unknown", type=unicode))
        if self.path == "unknown" or not os.path.exists(self.path):
            self.path = QFileDialog.getExistingDirectory(
                self, 
                self.tr("Directory that will contain the UT widgets"),
                "/home",
                QFileDialog.ShowDirsOnly
                )   
            settings.setValue("ut-path/path",self.path)
            self.path = unicode(settings.value("ut-path/path","unknown", type=unicode))

        # 3 - Creation of the Out of date UT Widgets list
        heading = self.tr("Out of date UnderTracks widgets")
        heading = "<h3>{0}</h3>".format(heading)
        self.heading = QLabel(heading, self, objectName="heading")
        layout.addWidget( self.heading)
        
        # 4 - Call the php script that gives the exisiting UT widgets, with their revision
        url     = "https://undertracks.imag.fr/scripts/OrangeScripts/Widgets/ExistingWidgets_tmp.php"
        data    = _u.urlencode({"login":self.login})
        req     = _u2.Request(url,data)
        f       = _u2.urlopen(req)
        res = f.read().split("_!!_")
        
        grid = QGridLayout()
        grid_indice = 0
        prevCategory = ""
        
        for i in range((len(res)-1)/2):
            # Check directory existence
            sp = res[i*2+1].split("/")
            category = sp[0]
            tool_name = sp[1]
                        
            path = self.path+"/"+category+"/UTTools"+category+"/"+tool_name+".py"
            do_it = True
            
            if os.path.isfile(path):
                #Here the directory exists, so we test de tool existence
                
                #We read now the current revision
                f = open(self.path+"/"+category+"/UTTools"+category+"/"+tool_name+".revision","r")
                c_revision = f.readline()
                ecrire("Revision :"+c_revision+"\n")
                f.close()
                
                #Is the Forge revision more recent ?
                if (c_revision >= res[i*2+2]):
                    do_it = False
                    
            if do_it:
                #Creation of the Qt widgets for the operator update
                if prevCategory != category:
                    tmp_label_left = QLabel(category)
                    tmp_label_left.setStyleSheet("QLabel { background-color : grey; color : white; }")
                    grid.addWidget(tmp_label_left,grid_indice,0)

                    grid_indice = grid_indice + 1   
                    prevCategory = category    

                cB = QCheckBox()

                grid.addWidget(QLabel(tool_name),grid_indice,0,Qt.AlignRight)
                cB = QCheckBox()
                grid.addWidget(cB,grid_indice,1)
                cB.setCheckState(2)
                
                self.widgets_to_update.append([res[i*2+1],res[i*2+2]])
                self.widgets_checkboxes.append(cB)
                grid_indice = grid_indice + 1
        
        
        #We add now the widget grid into a new dialog box. 
        ##The latter is then added into a scroll area, that is itself added into the main layout
        dialog2 = QDialog(self); 
        dialog2.setLayout(grid)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True);
        scroll_area.setWidget(dialog2)
                    
        layout.addWidget(scroll_area)

        if len(self.widgets_to_update) == 0:
            middle = self.tr("All your widgets are up-to-date")
            middle = "<h4>{0}</h4>".format(middle)
            self.middle = QLabel(middle, self, objectName="middle")
            self.middle.setStyleSheet("QLabel { color : green; }");
            layout.addWidget( self.middle)
            
        elif sys.platform == "darwin":
            password_label = QLabel("Enter your os password")
            self.password_edit = LineEdit(self)
            self.password_edit.setPlaceholderText(self.tr("Password"))
            self.password_edit.setEchoMode(2)
            layout.addWidget(password_label)
            layout.addWidget(self.password_edit)
        

        buttons_layout = QHBoxLayout()
        button_cancel = QPushButton("Cancel",self)
        button_update = QPushButton("Update",self)
        
        button_cancel.clicked.connect(self.reject)
        buttons_layout.addWidget(button_cancel)

        button_update.clicked.connect(self.update)
        if len(self.widgets_to_update) == 0:
            button_update.setEnabled(False)
        buttons_layout.addWidget(button_update)    
        
        layout.addLayout(buttons_layout)
    
        if len(self.widgets_to_update) != 0:
            ending = self.tr("WARNING !! Restart Orange after updating !")
            ending = "<h3 color=red>{0}</h3>".format(ending)
            self.ending = QLabel(ending, self, objectName="ending")
            self.ending.setStyleSheet("QLabel { color : red; }");
            layout.addWidget( self.ending)
    
        self.setLayout(layout)
    
###UNDERTRACKS###START
    def create_category(self,cat):
            #Here we create the folder for the "path" category
            
            #First we test if the category already exists
            L = os.listdir(self.path)
            found = False
            for i in L:
                if i == cat:
                    return False
            
            os.makedirs(self.path+"/"+cat)
            os.makedirs(self.path+"/"+cat+"/icons")
            os.makedirs(self.path+"/"+cat+"/UTTools"+cat)
            ecrire("Category "+cat+" Created.")
            
            f = open(self.path+"/"+cat+"/setup.py","w")
            f.write('from setuptools import setup\nsetup(name="'+cat+'",packages=["UTTools'+cat+'"],entry_points={"orange.widgets": ("'+cat+' = UTTools'+cat+'")},)')
            f.close()
            
            f = open(self.path+"/"+cat+"/UTTools"+cat+"/__init__.py","w")
            f.write('"""=========\n\n'+cat+'\n\n=========\n\nWidgets for UnderTracks.\n\n"""\n\n# Category description for the widget registry\n\nNAME = "'+cat+ \
                    '"\n\nDESCRIPTION = "Widgets for recovering and analysing UnderTracks data."\n\nBACKGROUND = "#4ebeff"\n\nICON = "../../UnderTracks/icons/UnderTracks.svg"')
            f.close()
            
            return True
###UNDERTRACKS###END
    
    def update(self):
    
        todo = False
        for i in range(len(self.widgets_checkboxes)):
            if self.widgets_checkboxes[i].checkState() == 2:
                todo = True
                
        if not todo:
            self.accept()
            return
            
        L = os.listdir(self.path)
        found = False
        for i in L:
            if i == "UnderTracks":
                found = True
        
        if not found:
            os.makedirs(self.path+"/UnderTracks/")
            os.makedirs(self.path+"/UnderTracks/icons")
            ecrire("Done")
            
            #recover UT icon from the Forge, through a php script on UnderTracks
            ecrire("REQUETE")
            url         = "https://undertracks.imag.fr/scripts/OrangeScripts/Widgets/GiveUTIcon.php"
            req         = _u2.Request(url)
            f           = _u2.urlopen(req)

            widget = _u2.urlopen(f.read())
            zfile = _zfile.ZipFile(StringIO(widget.read()))
            fname = zfile.namelist()[0]

            ecrire("DEZIP")
            ecrire("Taille liste :"+str(len(zfile.namelist())))
            
            data = zfile.read(fname)
            f = open(self.path+"/UnderTracks/icons/"+fname,"w")
            f.write(data)
            f.close()
            
        no_c_dir = False        
        try:
            dir_tmp = os.getcwd()
        except:
            ecrire("No current directory")
            no_c_dir = True        

        category_list = []   
        for i in range(len(self.widgets_checkboxes)):
            if self.widgets_checkboxes[i].checkState() == 2:
                tab         = self.widgets_to_update[i][0].split("/")
                revision    = self.widgets_to_update[i][1] 
                name        = tab[1]
                category    = tab[0]
                
                if category not in category_list:
                    category_list.append(category)
                
                res_create_cat = self.create_category(category)
                
                url         = "https://undertracks.imag.fr/scripts/OrangeScripts/Widgets/GiveWidget.php?category="+category+"&widget="+name
                req         = _u2.Request(url)
                f           = _u2.urlopen(req)
                
                widget = _u2.urlopen(f.read())
                zfile = _zfile.ZipFile(StringIO(widget.read()))
                
                #We copy all the files needed by the widgets
                for fname in zfile.namelist():
                    if fname[0] != "." and fname.find("/.") == -1:
                        if fname[len(fname)-1] == "/":
                            if not os.path.exists(self.path+"/"+category+"/UTTools"+category+"/"+fname):
                                os.makedirs(self.path+"/"+category+"/UTTools"+category+"/"+fname) 
                        else:
                            data = zfile.read(fname)
                            f = open(self.path+"/"+category+"/UTTools"+category+"/"+fname,"w")
                            f.write(data)
                            f.close() 
                            
                #We add the revision file
                f = open(self.path+"/"+category+"/UTTools"+category+"/"+name+".revision","w")
                f.write(revision)
                f.close()         
            
            for cat in category_list:
                os.chdir(self.path+"/"+cat+"/")
                import subprocess,getpass
                if sys.platform == "darwin":
                    password = str(self.password_edit.text())
        
                    proc = subprocess.Popen(
                            ['sudo','-p','','-S','python','setup.py','develop'],
                            stdin=subprocess.PIPE)
                    proc.stdin.write(password+'\n')
                    proc.stdin.close()
                    proc.wait()
                    proc.stdout
                else:
                    python = os.path.dirname(sys.executable)
                    subprocess.call(python+"\python.exe setup.py develop")
        
        if not no_c_dir:
            os.chdir(dir_tmp)
        
        
        layout_end = QVBoxLayout()
        layout_end.setContentsMargins(10,10,10, 10)
        layout_end.setSpacing(10)
        
        self.accept()

        