"""
UnderTracksLog in widget.

"""

from PyQt4.QtGui import (
    QWidget, QDialog, QLabel, QTextEdit, QCheckBox, QFormLayout,
    QVBoxLayout, QHBoxLayout, QDialogButtonBox, QSizePolicy
)

from PyQt4.QtCore import Qt

from ..gui.lineedit import LineEdit
from ..gui.utils import StyledWidget_paintEvent, StyledWidget


class UTLoginEdit(QWidget):
    """UnderTracks Login widget.
    """
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.__setupUi()

    def __setupUi(self):
        layout = QFormLayout()
        layout.setRowWrapPolicy(QFormLayout.WrapAllRows)
        layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self.login_edit = LineEdit(self)
        self.login_edit.setPlaceholderText(self.tr("Login"))
        self.login_edit.setSizePolicy(  QSizePolicy.Expanding,
                                        QSizePolicy.Fixed)
        
        
        self.password_edit = LineEdit(self)
        self.password_edit.setPlaceholderText(self.tr("Password"))
        self.password_edit.setEchoMode(2)
        self.password_edit.setSizePolicy(   QSizePolicy.Expanding,
                                            QSizePolicy.Fixed)

        layout.addRow(self.tr("Login"), self.login_edit)
        layout.addRow(self.tr("Password"), self.password_edit)

        self.setLayout(layout)

    def paintEvent(self, event):
        return StyledWidget_paintEvent(self, event)

    def login(self):
        return unicode(self.login_edit.text()).strip()

    def setLogin(self,l):
        self.login_edit.setText(self.tr(l))

    def password(self):
        return unicode(self.password_edit.text()).strip()


class UTLoginDialog(QDialog):
    def __init__(self, *args, **kwargs):
        QDialog.__init__(self, *args, **kwargs)
        self.__setupUi()

    def setLogin(self,l):
        """
        Set the login
        """
        self.editor.setLogin(l)
    
    def __setupUi(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.editor = UTLoginEdit(self)
        self.editor.layout().setContentsMargins(10, 10, 10, 10)
        self.editor.layout().setSpacing(10)
        self.editor.setSizePolicy(QSizePolicy.MinimumExpanding,
                                  QSizePolicy.MinimumExpanding)

        heading = self.tr("Enter your Login and password")
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