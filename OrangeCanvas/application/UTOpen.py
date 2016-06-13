"""
Widget for opening a scheme from UnderTracks Database.

"""

from PyQt4.QtGui import (
    QWidget, QDialog, QLabel, QTextEdit, QFormLayout, QListWidget, QLineEdit,
    QVBoxLayout, QDialogButtonBox, QSizePolicy,
)

from PyQt4.QtCore import Qt

from ..gui.utils import StyledWidget_paintEvent

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
        self.name = QLineEdit(self)
        self.name.textEdited.connect(self.name_changed)
        self.names = QListWidget(self)
        self.names.resize(300,120)
        self.names.itemClicked.connect(self.names_clicked)
        self.names.currentItemChanged.connect(self.names_clicked)
        self.desc_edit = QTextEdit(self)
        self.desc_edit.setTabChangesFocus(True)
        layout.addRow(self.tr("Name"),self.name)
        layout.addRow("",self.names)
        layout.addRow(self.tr("Description"), self.desc_edit)
        self.setLayout(layout)

    def paintEvent(self, event):
        return StyledWidget_paintEvent(self, event)

    def get_scheme(self):
        return self.scheme_index

    def setSchemeList(self,listN,listD):
        self.study_list = listN[:]
        self.desc_list = listD[:]
        for n in self.study_list:
            self.names.addItem(n)

    def name_changed(self):
        self.names.clear()
        s=str(self.name.text())
        if s=="":
            for n in self.study_list:
                self.names.addItem(n)
        else:
            self.scheme_index=None
            self.desc_edit.setText("")
            for i,n in enumerate(self.study_list):
                if n.upper().find(s.upper())>=0:
                    self.names.addItem(n)
                if n==s:
                    self.scheme_index=i
                    self.desc_edit.setText(self.desc_list[self.scheme_index])

    def names_clicked(self,item):
        if item:
            s = str(item.text())
            self.scheme_index=None
            self.desc_edit.setText("")
            for i,n in enumerate(self.study_list):
                if n==s:
                    self.name.setText(s)
                    self.scheme_index=i
                    self.desc_edit.setText(self.desc_list[self.scheme_index])

        
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