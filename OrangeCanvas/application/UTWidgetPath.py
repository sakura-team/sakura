"""
UnderTracks changin widgets path.

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

class UTWidgetPath(QDialog):
	def __init__(self, *args, **kwargs):
		QDialog.__init__(self, *args, **kwargs)
		self.__setupUi()

	def __setupUi(self):
		layout = QFormLayout()
		layout.setContentsMargins(10, 10, 10, 10)
		layout.setSpacing(10)

		settings = QSettings()

		#Check for a UT Widget Path
		self.path = QFileDialog.getExistingDirectory(
			self, 
			self.tr("Directory that will contain the UT widgets"),
			"/home",
			QFileDialog.ShowDirsOnly
			)
			
		if (self.path != ""):
			settings.setValue("ut-path/path",self.path)
		
			heading1 = self.tr("Path has been changed to : "+self.path)
			heading2 = self.tr("For avoiding conflicts, please delete all the content of your last directory")
			heading1 = "<h3>{0}</h3>".format(heading1)
		

			self.heading1 = QLabel(heading1, self, objectName="heading1")
			self.heading2 = QLabel(heading2, self, objectName="heading2")
		
			layout.addRow(self.heading1)
			layout.addRow(self.heading2)
		
		else:
			heading1 = self.tr("Your path has not been changed !")
			heading1 = "<h3>{0}</h3>".format(heading1)
		
			self.heading1 = QLabel(heading1, self, objectName="heading1")
		
			layout.addRow(self.heading1)
			
		
		self.buttonbox = QDialogButtonBox(
				QDialogButtonBox.Ok,
				Qt.Horizontal,
				self
				)
		
		layout.addRow(self.buttonbox)
		self.buttonbox.accepted.connect(self.accept)
		
		self.setLayout(layout)