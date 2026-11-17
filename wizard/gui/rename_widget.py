# coding: utf-8
# Author: Mael PERON
# Contact: maelperon.cg@gmail.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
import logging

# Wizard modules
from wizard.vars import ressources

logger = logging.getLogger(__name__)

class rename_widget(QtWidgets.QDialog):
    def __init__(self, title='Rename',
                 reject_text='Cancel', accept_text='Rename',
                 text: str = "",
                 placeholder: str = "",
                 warning_message: str = "",
                 parent=None):
        super(rename_widget, self).__init__()

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(title)
        self.setModal(True)

        self.title = title
        self.reject_text = reject_text
        self.accept_text = accept_text
        self.placeholder = placeholder
        self.text = text
        self.warning_message = warning_message
        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.setMinimumWidth(450)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed,
                           QtWidgets.QSizePolicy.Policy.Fixed)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.rename_label = QtWidgets.QLabel('New name:')
        self.rename_label.setObjectName('gray_label')
        self.main_layout.addWidget(self.rename_label)

        self.rename_line_edit = QtWidgets.QLineEdit()
        self.rename_line_edit.setText(self.text)
        self.rename_line_edit.setPlaceholderText(self.placeholder)
        self.main_layout.addWidget(self.rename_line_edit)

        if self.warning_message:
            self.warning_label = QtWidgets.QLabel(self.warning_message)
            self.warning_label.setObjectName('warning_label')
            self.warning_label.setVisible(1)
            self.warning_label.setWordWrap(True)
            self.warning_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.warning_label.setStyleSheet('color:#f0605b;font:bold;')
            self.main_layout.addWidget(self.warning_label)

        self.button_box = QtWidgets.QDialogButtonBox()
        self.reject_button = self.button_box.addButton(
            self.reject_text, QtWidgets.QDialogButtonBox.ButtonRole.RejectRole)
        self.accept_button = self.button_box.addButton(
            self.accept_text, QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        self.main_layout.addWidget(self.button_box)

    def connect_functions(self):
        self.reject_button.clicked.connect(self.reject)
        self.accept_button.clicked.connect(self.confirm)

    def confirm(self):
        if self.rename_line_edit.text() == "":
            return logger.warning("The new name is empty")
        
        self.accept()
