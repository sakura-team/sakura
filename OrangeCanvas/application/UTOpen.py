"""
Widget for opening a scheme from UnderTracks Database.

"""

from PyQt4.QtGui import (
    QWidget, QDialog, QLabel, QTextEdit, QCheckBox, QFormLayout,
    QVBoxLayout, QHBoxLayout, QDialogButtonBox, QSizePolicy, QComboBox
)

from PyQt4.QtCore import Qt

from ..gui.lineedit import LineEdit
from ..gui.utils import StyledWidget_paintEvent, StyledWidget

import sys

class UTOpenEdit(QWidget):
    """Widget for opening a scheme from the UnderTracks Database.
    """
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.scheme_index = None
        self.desc_list  = []
        self.__setupUi()

    def __setupUi(self):
        layout = QFormLayout()
        layout.setRowWrapPolicy(QFormLayout.WrapAllRows)
        layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self.name_list = QComboBox(self)
        self.name_list.currentIndexChanged['int'].connect(self.update_desc)
        self.desc_edit = QTextEdit(self)
        self.desc_edit.setTabChangesFocus(True)
        
        layout.addRow(self.tr("Name"),self.name_list)
        layout.addRow(self.tr("Description"), self.desc_edit)
        
        self.setLayout(layout)

    def paintEvent(self, event):
        return StyledWidget_paintEvent(self, event)

    def get_scheme(self):
        return self.scheme_index

    def setSchemeList(self,listN,listD):
        for l in listN:
            self.name_list.addItem(l)
        self.desc_list = listD[:]  
        self.desc_edit.setText(self.desc_list[0])
        self.scheme_index = 0

    def update_desc(self,index):    
        if len(self.desc_list) > 0:
            self.desc_edit.setText(self.desc_list[index])
            self.scheme_index = index
        
        
class UTOpenDialog(QDialog):
    def __init__(self, *args, **kwargs):
        QDialog.__init__(self, *args, **kwargs)
        self.scheme = None
        
        self.__setupUi()

    def __setupUi(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.editor = UTOpenEdit(self)
        self.editor.layout().setContentsMargins(20, 20, 20, 20)
        self.editor.layout().setSpacing(15)
        self.editor.setSizePolicy(QSizePolicy.MinimumExpanding,
                                  QSizePolicy.MinimumExpanding)

        heading = self.tr("List of the UnderTracks processes")
        heading = "<h3>{0}</h3>".format(heading)
        self.heading = QLabel(heading, self, objectName="heading")

        # Insert heading
        self.editor.layout().insertRow(0, self.heading)

        self.buttonbox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal,
            self
            )

        # Insert button box
        self.editor.layout().addRow(self.buttonbox)
        self.buttonbox.accepted.connect(self.accept)
        self.buttonbox.rejected.connect(self.reject)

        layout.addWidget(self.editor, stretch=10)

        self.setLayout(layout)

    def setSchemeList(self, listN,listD):
        """Set the list of the UnderTracks Processes
        """
        self.editor.setSchemeList(listN,listD)