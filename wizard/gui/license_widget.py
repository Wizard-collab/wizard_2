# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard modules
from wizard.vars import ressources

class license_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(license_widget, self).__init__(parent)

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - License")

        self.build_ui()
        self.fill_ui()

    def build_ui(self):
        self.setFixedSize(QtCore.QSize(600,500))
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(8,8,8,8)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.main_textEdit = QtWidgets.QTextEdit()
        self.main_textEdit.setReadOnly(True)
        self.main_textEdit.setObjectName('transparent_widget')
        self.main_layout.addWidget(self.main_textEdit)

    def fill_ui(self):
        with open('ressources/LICENSE', 'r') as f:
            self.main_textEdit.setText(f.read())

    def toggle(self):
        if self.isVisible():
            if not self.isActiveWindow():
                self.show()
                self.raise_()
            else:
                self.hide()
        else:
            self.show()
            self.raise_()

