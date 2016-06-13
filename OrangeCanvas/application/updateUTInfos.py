"""
Orange Canvas Update UT Infos Dialog
Michael Ortega, 12 jan 2016
"""

from PyQt4.QtGui import (
    QDialog, QHBoxLayout, QVBoxLayout, QFont, QLabel, QPushButton, QMessageBox
)

from ..gui.lineedit import LineEdit

import sys
import os
import datetime
import urllib as  _u

from ..utils.qtcompat import QSettings

class UpdateUTInfosDialog(QDialog):
    """Information about what in the current UT-Orange is out of date: 
    the canvas itself only for now
    """
    
    def __init__(self, *args, **kwargs):
        QDialog.__init__(self, *args, **kwargs)
    
        
        settings = QSettings()
        
        self.cv = unicode(settings.value("ut-version/current","unknown", type=unicode))
        self.fv = unicode(settings.value("ut-version/forge","unknown", type=unicode))
        self.path = unicode(settings.value("ut-path/path","unknown", type=unicode))
        self.setupUi()
    
    def setupUi(self):
        
        
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(10, 10, 10, 10)
        self.layout().setSpacing(10)
        self.setStyleSheet("background-color:\"#f5f5f5\";");
        
        txt = ""
        if self.cv != self.fv:
            self.setFixedSize(450, 200)
            txt = "<p align=center><font color=\"red\"><b> Your UT-Orange is out of date ! </b></font></p>"
            txt += "<p><font size=1>New version: <i>"+self.fv+"</i></font><br>"
            txt += "<font size=1>Current (your) version: <i>"+self.cv+"</i></font></p>"
            
            self.label = QLabel('<font color="#3a83e6">'+txt+'</font>')
            f = QFont ( "Arial", 20)
            self.label.setFont(f)
            
            self.layout().addWidget(self.label)
            
            
            if sys.platform == "darwin":
                password_label = QLabel("Enter your os password")
                self.password_edit = LineEdit(self)
                self.password_edit.setPlaceholderText(self.tr("Password"))
                self.password_edit.setEchoMode(2)
                self.layout().addWidget(password_label)
                self.layout().addWidget(self.password_edit)
            
            buttons_layout = QHBoxLayout()
            button_cancel = QPushButton("Cancel",self)
            button_update = QPushButton("Update",self)
            
            
            button_cancel.clicked.connect(self.dont_update)
            button_cancel.setMaximumWidth(100);
            buttons_layout.addWidget(button_cancel)
            
            button_update.clicked.connect(self.update_canvas)
            button_update.setMaximumWidth(100);
            buttons_layout.addWidget(button_update)    
            
            self.layout().addLayout(buttons_layout)
            
        else:
            self.setFixedSize(450, 100)
            txt = "<p align=center><b> Your UT-Orange is up of date ! </b></p>"
            
            label = QLabel('<font color="#3a83e6">'+txt+'</font>')
            f = QFont ( "Arial", 20)
            label.setFont(f)
            
            self.layout().addWidget(label)
            
            buttons_layout = QHBoxLayout()
            button_cancel = QPushButton("Ok",self)
            
            button_cancel.clicked.connect(self.dont_update)
            button_cancel.setMaximumWidth(100);
            buttons_layout.addWidget(button_cancel)
            
            self.layout().addLayout(buttons_layout)
        
        
    def update_canvas(self):
        
        try:
            canvas_file = _u.URLopener()
            new_canvas_path = self.path+"\OrangeCanvas_"+self.fv+".zip"
            canvas_file.retrieve('https://forge.imag.fr/scm/viewvc.php/*checkout*/trunk/fat_client/install/OrangeCanvas.zip?revision='+self.fv+'&root=undertracks', new_canvas_path)
            
            #copy current folder
            try:
                d = str(datetime.date.today())
                d = d.replace("/","_")
                t = str(datetime.datetime.now().time())[0:8]
                t = t.replace(":","_") 
                
                main_path = os.path.dirname(__file__)
                app_path = main_path[0:-24]
                src = app_path+"OrangeCanvas"
                dst = app_path+"OrangeCanvas"+"_"+d+"_"+t
            except Exception, e:
                sys.stderr.write("date: "+str(e)+"\n") 
            
            
            import subprocess,getpass
            if sys.platform == "darwin":
                password = str(self.password_edit.text())
                
                try:
                    proc = subprocess.Popen(
                                ['sudo','-p', '', '-S', 'python',main_path+'/UTcopyCanvas.py',src, dst, new_canvas_path, self.fv],
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    proc.stdin.write(password+'\n')
                    
                    proc.stdin.close()
                    proc.wait()
                    
                    msg = ''
                    for l in proc.stdout:
                        msg += l+"\n"
                        
                    if msg.find('update_done\n') != -1:
                        settings = QSettings()
                        settings.setValue("ut-version/current", self.fv)

                        msg = "New Canvas installed !\n\n"
                        msg += "For an eventual retrograde step, the previous version of the Canvas has been saved here\n"+dst
                        reply = QMessageBox.information(self, 'Message', msg, QMessageBox.Ok)
                        
                        msg = "Restart UT-Orange for enjoying this update!!!\n"
                        reply2 = QMessageBox.information(self, 'Message', msg, QMessageBox.Ok)
                        
                    else:
                        reply = QMessageBox.information(self, 'Message', "Bad news"+msg, QMessageBox.Ok)
                    
                    
                except Exception, e:
                    sys.stderr.write("proc: "+str(e)+"\n"+os.path.dirname(__file__)+"\n") 
            else:
                try:
                    proc = subprocess.Popen(
                                ['python',main_path+'/UTcopyCanvas.py',src, dst, new_canvas_path, self.fv],
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    proc.stdin.close()
                    proc.wait()
                    
                    msg = ''
                    for l in proc.stdout:
                        msg += l+"\n"
                        
                    if msg.find('update_done') != -1:
                        settings = QSettings()
                        settings.setValue("ut-version/current", self.fv)

                        msg = "New Canvas installed !\n\n"
                        msg += "For an eventual retrograde step, the previous version of the Canvas has been saved here\n"+dst+"\n\n\n"
                        msg += "Restart UT-Orange for enjoying this update!!!\n"
                        reply2 = QMessageBox.information(self, 'Message', msg, QMessageBox.Ok)
                        
                    else:
                        reply = QMessageBox.information(self, 'Message', "Bad news"+msg, QMessageBox.Ok)
                    
                except Exception, e:
                    sys.stderr.write("proc: "+str(e)+"\n"+os.path.dirname(__file__)+"\n")
        except Exception, e:
            sys.stderr.write("Cannot read canvas from forge: "+str(e)+"\n")        

        self.accept()
        
    def dont_update(self):
        self.reject()
        
        
        
