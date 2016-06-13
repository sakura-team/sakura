"""
Orange Canvas svn message Dialog
Michael Ortega, 16 fev 2016
"""

from PyQt4.QtGui import (
    QDialog, QWidget, QToolButton, QCheckBox, QAction,
    QHBoxLayout, QVBoxLayout, QFont, QSizePolicy,
    QPixmap, QIcon, QPainter, QColor, QBrush, QLabel,
    QPushButton, QMessageBox
)

from PyQt4.QtCore import Qt, QRect, QPoint
from PyQt4.QtCore import pyqtSignal as Signal

from ..canvas.items.utils import radial_gradient
from ..gui.lineedit import LineEdit
from ..registry import NAMED_COLORS

import sys
import os
import time
import datetime
import shutil
import urllib as  _u
import urllib2 as  _u2

from ..utils.qtcompat import QSettings

class UTSvnDialog(QDialog):
    """Information about what in the current UT-Orange is out of date: 
    the canvas itself only for now
    """
    
    def __init__(self, *args, **kwargs):
        QDialog.__init__(self, *args, **kwargs)
        
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(10, 10, 10, 10)
        self.layout().setSpacing(10)
        self.setFixedSize(450, 100)
        
        self.message_label = QLabel("Enter a message for the svn version")
        self.message_edit = LineEdit(self)
        self.layout().addWidget(self.message_label)
        self.layout().addWidget(self.message_edit)
        
        buttons_layout = QHBoxLayout()
        button_cancel = QPushButton("Cancel",self)
        button_update = QPushButton("Ok",self)
        
        
        button_cancel.clicked.connect(self.dont_send)
        button_cancel.setMaximumWidth(100);
        buttons_layout.addWidget(button_cancel)
            
        button_update.clicked.connect(self.send)
        button_update.setMaximumWidth(100);
        buttons_layout.addWidget(button_update)
        
        self.layout().addLayout(buttons_layout)
            
    def send(self):
        self.accept()
        
    def dont_send(self):
        self.reject()
        
        
        
